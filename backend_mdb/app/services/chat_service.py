import os
import json
import logging
from typing import List, Dict
from fastapi import HTTPException
from qdrant_client import models

from app.core.lifespan import models_cache
from app.schema.chat_schema import QueryRequest, Source
from app.models.conversation import Message

from app.prompts.chat_prompts import (
    COMBINED_PROMPT,
    PROMPT_RAG_TEMPLATE,
    CHITCHAT_RESPONSE_TEMPLATE,
    OUT_OF_DOMAIN_RESPONSE_TEMPLATE,
)
from app.services import conversation_service

# Thiết lập logging cơ bản
logging.basicConfig(level=logging.INFO)


def _format_sources(sources_list: List[List[Source]]) -> str:
    """
    Chuyển đổi danh sách nguồn thành một chuỗi Markdown có thể đọc được.
    """
    if not sources_list:
        return ""

    unique_sources = {}
    for source_group in sources_list:
        for source in source_group:
            if isinstance(source, Source):
                key = (source.name, source.url)
                if key not in unique_sources:
                    unique_sources[key] = source

    if not unique_sources:
        return ""

    header = "\n\n---\n**Nguồn tham khảo:**\n"
    source_lines = []
    for i, source in enumerate(unique_sources.values()):
        if source.url and source.url != "local_file":
            source_lines.append(f"{i+1}. [{source.name}]({source.url})")
        else:
            source_lines.append(f"{i+1}. {source.name}")

    return header + "\n".join(source_lines)


async def process_chat_request(request: QueryRequest) -> dict:
    embedding_model = models_cache["embedding_model"]
    qdrant_client = models_cache["qdrant_client"]
    llm_rag = models_cache["llm_rag"]
    llm_fast = models_cache["llm_fast"]
    collection_name = os.getenv("QDRANT_COLLECTION_NAME")

    conv_id = request.conversation_id
    user_question = request.question

    # --- Lấy lịch sử (Cập nhật để lấy retrieved_doc_ids) ---
    current_history: List[Dict] = []
    retrieved_doc_ids: List[str] = []  # <-- Biến mới

    if conv_id:
        conversation = await conversation_service.get_conversation_by_id(conv_id)
        if conversation:
            current_history = [
                {"role": msg["sender"], "content": msg["content"]}
                for msg in conversation.get("messages", [])
            ]
            # Lấy danh sách ID đã xem từ DB
            retrieved_doc_ids = conversation.get("retrieved_doc_ids", [])
    else:
        new_conv_data = {"user_id": request.user_id, "messages": []}
        conv_id = await conversation_service.create_conversation(new_conv_data)

    current_history_limited = current_history[-5:]
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

    # =================================================================
    # === BƯỚC 1: GỘP (PHÂN LOẠI, LẤY Ý ĐỊNH, VIẾT LẠI) ===
    # =================================================================
    combined_prompt = COMBINED_PROMPT.format(
        chat_history=chat_history_str, question=user_question
    )

    question_category = "NONG_NGHIEP"
    search_question = user_question
    user_intent = "NEW_TOPIC"  # <-- THÊM BIẾN MỚI

    try:
        response = await llm_fast.generate_content_async(combined_prompt)
        json_response_str = response.text.strip()

        if json_response_str.startswith("```json"):
            json_response_str = json_response_str[7:-3].strip()

        logging.info(f"Phản hồi JSON gộp từ LLM: {json_response_str}")
        result_json = json.loads(json_response_str)

        question_category = result_json.get("loai", "NONG_NGHIEP").upper()
        user_intent = result_json.get("intent", "NEW_TOPIC").upper()  # <-- LẤY Ý ĐỊNH
        search_question = result_json.get("cau_hoi_tim_kiem", user_question)

        logging.info(
            f"Phân loại: {question_category} | Ý định: {user_intent} | Câu hỏi: {search_question}"
        )

    except Exception as e:
        logging.error(f"Lỗi khi gọi LLM gộp: {e}. Dùng mặc định.")
    # =================================================================
    # === KẾT THÚC THAY ĐỔI ===
    # =================================================================

    answer = ""
    parsed_sources: List[List[Source]] = []
    final_answer_to_save = ""

    # === BƯỚC 2: XỬ LÝ DỰA TRÊN LOẠI CÂU HỎI ===
    if question_category == "NONG_NGHIEP":
        logging.info(f"Xử lý RAG với câu hỏi: {search_question}")

        try:
            text_to_search = "query: " + search_question
            query_vector = embedding_model.encode(text_to_search).tolist()

            # ==========================================================
            # === BẮT ĐẦU THAY ĐỔI: LOGIC LỌC THÔNG MINH ===
            # ==========================================================

            rag_filter = None  # Mặc định không lọc

            # CHỈ LỌC nếu người dùng muốn KHÁM PHÁ CÁI MỚI
            if user_intent == "EXPLORE_NEW" and retrieved_doc_ids:
                logging.info(
                    f"Ý định: EXPLORE_NEW. Lọc bỏ {len(retrieved_doc_ids)} doc_id đã xem."
                )
                rag_filter = models.Filter(
                    must_not=[
                        models.FieldCondition(
                            key="doc_id", match=models.MatchAny(any=retrieved_doc_ids)
                        )
                    ]
                )
            else:
                logging.info(f"Ý định: {user_intent}. Không lọc doc_id.")

            search_results = qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=request.top_k,
                query_filter=rag_filter,  # <-- ÁP DỤNG BỘ LỌC (có thể là None)
            )

            # ==========================================================
            # === KẾT THÚC THAY ĐỔI ===
            # ==========================================================

            context = ""
            retrieved_sources_str = set()
            new_doc_ids_found = []  # <-- Biến mới để lưu ID vừa tìm thấy

            if search_results:
                top_hit = search_results[0]
                if top_hit.payload and "source" in top_hit.payload:
                    retrieved_sources_str.add(top_hit.payload["source"])
                else:
                    logging.warning(
                        f"Kết quả top 1 (ID {top_hit.id}) thiếu payload 'source'."
                    )

                for result in search_results:
                    if result.payload and "content" in result.payload:
                        context += result.payload["content"] + "\n---\n"
                        if "doc_id" in result.payload:
                            new_doc_ids_found.append(result.payload["doc_id"])
                    else:
                        logging.warning(
                            f"Kết quả tìm kiếm ID {result.id} thiếu payload 'content'. Bỏ qua context."
                        )
            else:
                logging.info("Không tìm thấy kết quả NÀO MỚI trong Qdrant (đã lọc).")

            final_prompt = PROMPT_RAG_TEMPLATE.format(
                chat_history=chat_history_str, context=context, question=user_question
            )
            response_from_llm = await llm_rag.generate_content_async(final_prompt)
            answer_text_only = response_from_llm.text

            # ... (Code xử lý nguồn giữ nguyên) ...
            for source_json_string in list(retrieved_sources_str):
                try:
                    list_of_source_dicts = json.loads(source_json_string)
                    if isinstance(list_of_source_dicts, list):
                        source_objects = [
                            Source(**data)
                            for data in list_of_source_dicts
                            if isinstance(data, dict)
                        ]
                        if source_objects:
                            parsed_sources.append(source_objects)
                except Exception as e:
                    logging.warning(
                        f"Bỏ qua source không hợp lệ: {source_json_string}. Lỗi: {e}"
                    )

            formatted_sources_str = _format_sources(parsed_sources)

            if (
                "tôi đang cập nhật thêm thông tin" not in answer_text_only.lower()
                and "tôi chưa tìm thấy thông tin" not in answer_text_only.lower()
            ):
                final_answer_to_save = answer_text_only + formatted_sources_str

                # --- THAY ĐỔI: Vẫn lưu các ID vừa tìm thấy ---
                # Bất kể ý định là gì, chúng ta đều lưu ID vừa dùng
                # để chuẩn bị cho câu hỏi "EXPLORE_NEW" tiếp theo
                if conv_id and new_doc_ids_found:
                    await conversation_service.update_retrieved_docs(
                        conv_id, new_doc_ids_found
                    )
            else:
                final_answer_to_save = answer_text_only

            answer = final_answer_to_save

        except Exception as e:
            print(f"Lỗi xử lý RAG: {e}")
            answer = "Đã có lỗi xảy ra trong quá trình xử lý yêu cầu của bạn. Vui lòng thử lại sau."
            final_answer_to_save = answer

    # ... (Các khối elif CHAO_HOI, NGOAI_LE, và LƯU TIN NHẮN giữ nguyên) ...
    elif question_category == "CHAO_HOI":
        chitchat_prompt = CHITCHAT_RESPONSE_TEMPLATE.format(question=user_question)
        try:
            chitchat_response = await llm_fast.generate_content_async(chitchat_prompt)
            answer = chitchat_response.text
        except Exception as e:
            answer = "Chào bạn! Tôi có thể giúp gì về cây lúa hoặc cây xoài ạ?"
        final_answer_to_save = answer

    elif question_category == "NGOAI_LE":
        ood_prompt = OUT_OF_DOMAIN_RESPONSE_TEMPLATE.format(question=user_question)
        try:
            ood_response = await llm_fast.generate_content_async(ood_prompt)
            answer = ood_response.text
        except Exception as e:
            answer = "Xin lỗi, kiến thức của tôi chỉ tập trung vào cây lúa và cây xoài. Tôi không thể giúp về chủ đề này ạ."
        final_answer_to_save = answer

    else:
        logging.warning(
            f"Không nhận dạng được loại câu hỏi: {question_category}. Mặc định từ chối."
        )
        answer = "Xin lỗi, tôi chưa hiểu rõ câu hỏi của bạn hoặc nó nằm ngoài phạm vi kiến thức về lúa và xoài của tôi."
        final_answer_to_save = answer

    if not final_answer_to_save:
        logging.error("Biến 'final_answer_to_save' rỗng trước khi lưu tin nhắn!")
        final_answer_to_save = "Đã có lỗi xảy ra, không thể tạo câu trả lời."

    user_message = Message(sender="user", content=user_question)
    bot_message = Message(sender="bot", content=final_answer_to_save)

    if conv_id:
        try:
            await conversation_service.add_message(conv_id, user_message.model_dump())
            await conversation_service.add_message(conv_id, bot_message.model_dump())
            logging.info(f"Đã lưu tin nhắn vào cuộc trò chuyện ID: {conv_id}")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Lỗi khi lưu trữ cuộc trò chuyện."
            )
    else:
        raise HTTPException(
            status_code=500, detail="Không thể xác định hoặc tạo cuộc trò chuyện."
        )

    return {
        "answer": final_answer_to_save,
        "sources": parsed_sources,
        "conversation_id": conv_id,
    }
