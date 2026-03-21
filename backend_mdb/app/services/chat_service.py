import os
import json
import logging
from typing import List, Dict, Optional
from fastapi import HTTPException
from qdrant_client import models

from app.core.lifespan import models_cache
from app.schema.chat_schema import Source
from app.models.conversation import Message
from app.classification.classify import classify_image_from_bytes

from app.prompts.chat_prompts import (
    COMBINED_PROMPT,
    PROMPT_RAG_TEMPLATE,
    CHITCHAT_RESPONSE_TEMPLATE,
    OUT_OF_DOMAIN_RESPONSE_TEMPLATE,
    IMAGE_DISEASE_PROMPT,
)
from app.services import conversation_service

logging.basicConfig(level=logging.INFO)

# Tên loại cây tiếng Việt
PLANT_TYPE_VI = {
    "mango": "Cây xoài",
    "rice": "Cây lúa",
}


def _format_sources(sources_list: List[List[Source]]) -> str:
    if not sources_list:
        return ""
    unique_sources = {}
    for source_group in sources_list:
        for source in source_group:
            if isinstance(source, Source):
                key = (source.name, source.url)
                if key in unique_sources:
                    continue
                if source.url and (
                    source.url.startswith("http://")
                    or source.url.startswith("https://")
                ):
                    unique_sources[key] = source
                elif source.url and source.url == "local_file":
                    if source.name and source.name.lower().endswith(".pdf"):
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


async def process_chat_request(
    user_id: str,
    question: str,
    conversation_id: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
    top_k: int = 10,
) -> dict:
    """
    Xử lý yêu cầu chat:
    - Nếu có image_bytes: phân loại bệnh bằng CNN, sinh câu trả lời dựa trên kết quả CNN
    - Nếu không có ảnh: xử lý RAG/chitchat bình thường
    """
    llm_rag = models_cache["llm_rag"]
    llm_fast = models_cache["llm_fast"]
    embedding_model = models_cache["embedding_model"]
    qdrant_client = models_cache["qdrant_client"]
    collection_name = os.getenv("QDRANT_COLLECTION_NAME")
    VECTOR_DIMENSION = models_cache["vector_dimension"]

    conv_id = conversation_id
    user_question = question if question else ""

    # ---- Lấy lịch sử trò chuyện ----
    current_history: List[Dict] = []
    retrieved_doc_ids: List[str] = []
    if conv_id:
        conversation = await conversation_service.get_conversation_by_id(conv_id)
        if conversation:
            current_history = [
                {"role": msg["sender"], "content": msg["content"]}
                for msg in conversation.get("messages", [])
            ]
            retrieved_doc_ids = conversation.get("retrieved_doc_ids", [])
    else:
        new_conv_data = {"user_id": user_id, "messages": []}
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

    answer = ""
    parsed_sources: List[List[Source]] = []
    final_answer_to_save = ""
    disease_info = None

    # ================================================================
    # NHÁNH 1: Có ảnh -> Phân loại bệnh bằng CNN
    # ================================================================
    if image_bytes:
        logging.info("Phát hiện ảnh đính kèm. Chạy phân loại CNN...")
        try:
            disease_info = classify_image_from_bytes(image_bytes)
            logging.info(f"Kết quả CNN: {disease_info}")

            plant_type_vi = PLANT_TYPE_VI.get(disease_info["plant_type"], disease_info["plant_type"])

            # Nếu người dùng không nhập câu hỏi, dùng câu mặc định
            display_question = user_question if user_question.strip() else "Hãy cho tôi biết thông tin về bệnh này."

            image_prompt = IMAGE_DISEASE_PROMPT.format(
                plant_type_vi=plant_type_vi,
                disease_name_vi=disease_info["disease_name_vi"],
                confidence=disease_info["confidence"],
                chat_history=chat_history_str,
                question=display_question,
            )

            response_from_llm = await llm_rag.generate_content_async(image_prompt)
            answer = response_from_llm.text
            final_answer_to_save = answer

        except FileNotFoundError as e:
            logging.error(f"Không tìm thấy model CNN: {e}")
            answer = (
                "⚠️ Xin lỗi, tôi chưa thể phân tích ảnh lúc này vì model nhận dạng chưa được cài đặt. "
                "Vui lòng mô tả triệu chứng bệnh bằng văn bản để tôi tư vấn."
            )
            final_answer_to_save = answer
        except Exception as e:
            logging.error(f"Lỗi khi phân loại ảnh: {e}", exc_info=True)
            answer = (
                "⚠️ Đã xảy ra lỗi khi phân tích ảnh. "
                "Vui lòng thử lại hoặc mô tả triệu chứng bằng văn bản."
            )
            final_answer_to_save = answer

    # ================================================================
    # NHÁNH 2: Không có ảnh -> Xử lý RAG / Chitchat bình thường
    # ================================================================
    else:
        # Bước 1: Gộp phân loại, ý định, viết lại
        combined_prompt = COMBINED_PROMPT.format(
            chat_history=chat_history_str, question=user_question
        )
        question_category = "NONG_NGHIEP"
        search_question = user_question
        user_intent = "NEW_TOPIC"
        try:
            response = await llm_fast.generate_content_async(combined_prompt)
            json_response_str = response.text.strip()
            if json_response_str.startswith("```json"):
                json_response_str = json_response_str[7:-3].strip()
            result_json = json.loads(json_response_str)
            question_category = result_json.get("loai", "NONG_NGHIEP").upper()
            user_intent = result_json.get("intent", "NEW_TOPIC").upper()
            search_question = result_json.get("cau_hoi_tim_kiem", user_question)
            logging.info(
                f"Phân loại: {question_category} | Ý định: {user_intent} | Câu hỏi: {search_question}"
            )
        except Exception as e:
            logging.error(f"Lỗi khi gọi LLM gộp: {e}. Dùng mặc định.")

        if question_category == "NONG_NGHIEP":
            logging.info(f"Xử lý RAG với câu hỏi: {search_question}")

            try:
                text_to_search = "query: " + search_question
                query_vector = embedding_model.encode(text_to_search).tolist()

                rag_filter = None
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

                keyword_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="content", match=models.MatchText(text=search_question)
                        )
                    ],
                    must_not=rag_filter.must_not if rag_filter else None,
                )
                vector_results = qdrant_client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    query_filter=rag_filter,
                    with_payload=True,
                )

                keyword_results = qdrant_client.search(
                    collection_name=collection_name,
                    query_vector=[0.0] * VECTOR_DIMENSION,
                    query_filter=keyword_filter,
                    limit=top_k,
                    with_payload=True,
                )

                fused_scores = {}
                k = 60  # Hằng số RRF

                for i, point in enumerate(vector_results):
                    rank = i + 1
                    score = 1.0 / (k + rank)
                    if point.id not in fused_scores:
                        fused_scores[point.id] = {"score": 0.0, "point": point}
                    fused_scores[point.id]["score"] += score

                for i, point in enumerate(keyword_results):
                    rank = i + 1
                    score = 1.0 / (k + rank)
                    if point.id not in fused_scores:
                        fused_scores[point.id] = {"score": 0.0, "point": point}
                    fused_scores[point.id]["score"] += score

                sorted_fused_results = sorted(
                    fused_scores.values(), key=lambda x: x["score"], reverse=True
                )

                search_results = [
                    item["point"] for item in sorted_fused_results[:top_k]
                ]

                logging.info(
                    f"Kết quả Vector: {len(vector_results)}, Keyword: {len(keyword_results)}, Hợp nhất: {len(search_results)}"
                )

                context = ""
                retrieved_sources_str = set()
                new_doc_ids_found = []
                found_priority_source = False
                fallback_source = None

                if search_results:
                    for i, result in enumerate(search_results):
                        if result.payload and "content" in result.payload:
                            context += result.payload["content"] + "\n---\n"
                            if "doc_id" in result.payload:
                                new_doc_ids_found.append(result.payload["doc_id"])

                        if result.payload and "source" in result.payload:
                            raw_source = result.payload["source"]
                            is_docx = (
                                ".docx" in raw_source.lower()
                                or ".doc" in raw_source.lower()
                            )
                            is_url = "http://" in raw_source or "https://" in raw_source

                            if not found_priority_source:
                                if is_url or (not is_docx):
                                    retrieved_sources_str.add(raw_source)
                                    found_priority_source = True
                                else:
                                    if fallback_source is None:
                                        fallback_source = raw_source
                else:
                    logging.info("Không tìm thấy kết quả nào trong Qdrant.")

                final_prompt = PROMPT_RAG_TEMPLATE.format(
                    chat_history=chat_history_str, context=context, question=user_question
                )
                response_from_llm = await llm_rag.generate_content_async(final_prompt)
                answer_text_only = response_from_llm.text

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
                    if conv_id and new_doc_ids_found:
                        await conversation_service.update_retrieved_docs(
                            conv_id, new_doc_ids_found
                        )
                else:
                    final_answer_to_save = answer_text_only

                answer = final_answer_to_save

            except Exception as e:
                logging.warning(f"Lỗi xử lý RAG (Qdrant không khả dụng): {e}. Fallback sang LLM-only.")
                try:
                    # Fallback: trả lời bằng LLM mà không có RAG context
                    fallback_prompt = (
                        f"Lịch sử trò chuyện:\n{chat_history_str}\n\n"
                        f"Câu hỏi của người dùng: {user_question}\n\n"
                        "Hãy trả lời dựa trên kiến thức của bạn về nông nghiệp, cây lúa và cây xoài. "
                        "Nếu không đủ thông tin, hãy nói thẳng và gợi ý người dùng tham khảo thêm nguồn."
                    )
                    fallback_response = await llm_rag.generate_content_async(fallback_prompt)
                    answer = fallback_response.text
                except Exception as fallback_e:
                    logging.error(f"Lỗi LLM fallback: {fallback_e}")
                    answer = "Đã có lỗi xảy ra trong quá trình xử lý yêu cầu của bạn. Vui lòng thử lại sau."
                final_answer_to_save = answer

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

    # ---- Kiểm tra và lưu tin nhắn ----
    if not final_answer_to_save:
        logging.error("Biến 'final_answer_to_save' rỗng trước khi lưu tin nhắn!")
        final_answer_to_save = "Đã có lỗi xảy ra, không thể tạo câu trả lời."

    # Tạo nội dung lưu cho tin nhắn user (thêm ghi chú nếu có ảnh)
    user_content = user_question
    if image_bytes and disease_info:
        user_content = (
            f"[Ảnh đính kèm - Phát hiện: {disease_info['disease_name_vi']}] "
            + (user_question if user_question.strip() else "")
        ).strip()

    user_message = Message(sender="user", content=user_content)
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
        "disease_info": disease_info,
    }
