import os
import json
import logging
from typing import List, Dict
from fastapi import HTTPException

from app.core.lifespan import models_cache
from app.schema.chat_schema import QueryRequest, Source
from app.models.conversation import Message

# Import các prompt mới
from app.prompts.chat_prompts import (
    QUERY_REWRITE_TEMPLATE,
    PROMPT_RAG_TEMPLATE,
    QUESTION_CLASSIFICATION_TEMPLATE,
    CHITCHAT_RESPONSE_TEMPLATE,
    OUT_OF_DOMAIN_RESPONSE_TEMPLATE,
)
from app.services import conversation_service

# Thiết lập logging cơ bản
logging.basicConfig(level=logging.INFO)


async def process_chat_request(request: QueryRequest) -> dict:
    embedding_model = models_cache["embedding_model"]
    qdrant_client = models_cache["qdrant_client"]
    llm_rag = models_cache["llm_rag"]
    llm_fast = models_cache["llm_fast"]  # Dùng cho phân loại và trả lời nhanh
    collection_name = os.getenv("QDRANT_COLLECTION_NAME")

    conv_id = request.conversation_id
    user_question = request.question

    # --- Lấy lịch sử (logic cũ giữ nguyên) ---
    current_history: List[Dict] = []
    if conv_id:
        conversation = await conversation_service.get_conversation_by_id(conv_id)
        if conversation:
            current_history = [
                {"role": msg["sender"], "content": msg["content"]}
                for msg in conversation.get("messages", [])
            ]
    else:
        new_conv_data = {"user_id": request.user_id, "messages": []}
        conv_id = await conversation_service.create_conversation(new_conv_data)

    current_history_limited = current_history[-5:]  # Giới hạn 5 tin nhắn gần nhất
    chat_history_str = "\n".join(
        [
            (
                f"Người dùng: {msg['content']}"
                if msg["role"] == "user"
                else f"Trợ lý: {msg['content']}"
            )
            for msg in current_history_limited
        ]
    )

    # =============================================================
    # === BƯỚC 1: PHÂN LOẠI CÂU HỎI ===
    # =============================================================
    classification_prompt = QUESTION_CLASSIFICATION_TEMPLATE.format(
        question=user_question
    )
    try:
        classification_response = await llm_fast.generate_content_async(
            classification_prompt
        )
        question_category = classification_response.text.strip().upper()
        logging.info(
            f"Phân loại câu hỏi: '{user_question}' -> Loại: {question_category}"
        )
    except Exception as e:
        question_category = "NONG_NGHIEP"  # Mặc định xử lý RAG nếu phân loại lỗi

    answer = ""
    parsed_sources: List[List[Source]] = []

    # =============================================================
    # === BƯỚC 2: XỬ LÝ DỰA TRÊN LOẠI CÂU HỎI ===
    # =============================================================

    if question_category == "NONG_NGHIEP":
        logging.info("Xử lý câu hỏi NONG_NGHIEP bằng RAG...")
        # --- Phần RAG (logic cũ giữ nguyên) ---
        search_question = user_question
        # Optional: Query rewriting (có thể bật lại nếu cần)
        # if current_history_limited:
        #     rewrite_prompt = QUERY_REWRITE_TEMPLATE.format(
        #         chat_history=chat_history_str, question=user_question
        #     )
        #     try:
        #         response = await llm_fast.generate_content_async(rewrite_prompt)
        #         search_question = response.text.strip()
        #         logging.info(f"Câu hỏi được viết lại: {search_question}")
        #     except Exception as e:
        #          logging.warning(f"Lỗi khi viết lại câu hỏi: {e}. Sử dụng câu hỏi gốc.")
        #          search_question = user_question

        try:
            text_to_search = "query: " + search_question
            query_vector = embedding_model.encode(text_to_search).tolist()
            search_results = qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=request.top_k,
            )

            context = ""
            retrieved_sources_str = set()
            if search_results:
                for result in search_results:
                    # Kiểm tra xem payload có tồn tại và có 'content', 'source' không
                    if (
                        result.payload
                        and "content" in result.payload
                        and "source" in result.payload
                    ):
                        context += result.payload["content"] + "\n---\n"
                        retrieved_sources_str.add(result.payload["source"])
                    else:
                        logging.warning(
                            f"Kết quả tìm kiếm ID {result.id} thiếu payload 'content' hoặc 'source'. Bỏ qua."
                        )
            else:
                logging.info("Không tìm thấy kết quả nào trong Qdrant.")

            # Xử lý trường hợp không có context nhưng vẫn hỏi LLM (tuỳ chiến lược)
            # if not context:
            #     answer = "Xin lỗi, tôi chưa tìm thấy thông tin cụ thể về vấn đề này trong tài liệu hiện có."
            # else:
            final_prompt = PROMPT_RAG_TEMPLATE.format(
                chat_history=chat_history_str, context=context, question=user_question
            )
            response_from_llm = await llm_rag.generate_content_async(final_prompt)
            answer = response_from_llm.text

            # Xử lý nguồn
            for source_json_string in list(retrieved_sources_str):
                try:
                    list_of_source_dicts = json.loads(source_json_string)
                    # Đảm bảo list_of_source_dicts là list
                    if isinstance(list_of_source_dicts, list):
                        source_objects = [
                            Source(**data)
                            for data in list_of_source_dicts
                            if isinstance(data, dict)
                        ]
                        if source_objects:  # Chỉ thêm nếu có đối tượng hợp lệ
                            parsed_sources.append(source_objects)
                    else:
                        logging.warning(
                            f"Source JSON không phải là list: {source_json_string}"
                        )
                except (
                    json.JSONDecodeError,
                    TypeError,
                    ValueError,
                ) as e:
                    logging.warning(
                        f"Bỏ qua source không hợp lệ: {source_json_string}. Lỗi: {e}"
                    )
                    continue

        except Exception as e:
            answer = "Đã có lỗi xảy ra trong quá trình xử lý yêu cầu của bạn. Vui lòng thử lại sau."

    elif question_category == "CHAO_HOI":
        chitchat_prompt = CHITCHAT_RESPONSE_TEMPLATE.format(question=user_question)
        try:
            chitchat_response = await llm_fast.generate_content_async(chitchat_prompt)
            answer = chitchat_response.text
        except Exception as e:
            answer = "Chào bạn! Tôi có thể giúp gì về cây lúa hoặc cây xoài ạ?"  # Trả lời mặc định

    elif question_category == "NGOAI_LE":
        ood_prompt = OUT_OF_DOMAIN_RESPONSE_TEMPLATE.format(question=user_question)
        try:
            ood_response = await llm_fast.generate_content_async(ood_prompt)
            answer = ood_response.text
        except Exception as e:
            answer = "Xin lỗi, kiến thức của tôi chỉ tập trung vào cây lúa và cây xoài. Tôi không thể giúp về chủ đề này ạ."  # Trả lời mặc định

    else:
        logging.warning(
            f"Không nhận dạng được loại câu hỏi: {question_category}. Mặc định từ chối."
        )
        answer = "Xin lỗi, tôi chưa hiểu rõ câu hỏi của bạn hoặc nó nằm ngoài phạm vi kiến thức về lúa và xoài của tôi."

    # =============================================================
    # === BƯỚC 3: LƯU TIN NHẮN VÀ TRẢ VỀ ===
    # =============================================================
    if not answer:
        logging.error("Biến 'answer' rỗng trước khi lưu tin nhắn!")
        answer = "Đã có lỗi xảy ra, không thể tạo câu trả lời."

    user_message = Message(sender="user", content=user_question)
    bot_message = Message(sender="bot", content=answer)  # Đảm bảo sender là "bot"

    # Chỉ lưu nếu conv_id hợp lệ
    if conv_id:
        try:
            await conversation_service.add_message(conv_id, user_message.model_dump())
            await conversation_service.add_message(conv_id, bot_message.model_dump())
            logging.info(f"Đã lưu tin nhắn vào cuộc trò chuyện ID: {conv_id}")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Lỗi khi lưu trữ cuộc trò chuyện.")
    else:
        raise HTTPException(status_code=500, detail="Không thể xác định hoặc tạo cuộc trò chuyện.")

    return {
        "answer": answer,
        "sources": parsed_sources,  # Sẽ rỗng nếu là chit-chat hoặc OOD
        "conversation_id": conv_id,  # ID cuộc trò chuyện
    }
