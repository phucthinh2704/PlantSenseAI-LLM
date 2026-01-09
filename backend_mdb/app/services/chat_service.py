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

logging.basicConfig(level=logging.INFO)


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


async def process_chat_request(request: QueryRequest) -> dict:
    embedding_model = models_cache["embedding_model"]
    qdrant_client = models_cache["qdrant_client"]
    llm_rag = models_cache["llm_rag"]
    llm_fast = models_cache["llm_fast"]
    collection_name = os.getenv("QDRANT_COLLECTION_NAME")
    VECTOR_DIMENSION = models_cache["vector_dimension"]

    conv_id = request.conversation_id
    user_question = request.question

    # Lấy lịch sử
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

    answer = ""
    parsed_sources: List[List[Source]] = []
    final_answer_to_save = ""

    if question_category == "NONG_NGHIEP":
        logging.info(f"Xử lý RAG với câu hỏi: {search_question}")

        try:
            text_to_search = "query: " + search_question
            query_vector = embedding_model.encode(text_to_search).tolist()

            # 1. Tạo bộ lọc (filter) chung
            # Bộ lọc này chỉ dùng để loại bỏ các doc đã xem
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

            # 2. Gửi 2 YÊU CẦU TÌM KIẾM

            # Query 1: Vector Search (Semantic)
            vector_request = models.SearchRequest(
                vector=query_vector,
                filter=rag_filter,
                limit=request.top_k,
                with_payload=True,
            )

            # Query 2: Keyword Search (Full-text trên trường 'content')
            keyword_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="content", match=models.MatchText(text=search_question)
                    )
                ],
                must_not=rag_filter.must_not if rag_filter else None,
            )

            # Lưu ý: Tìm kiếm keyword không dùng vector, nên ta set vector rỗng và filter
            # Đây là một mẹo để dùng chung batch search
            # Một cách khác tốt hơn là dùng `recommend_batch` hoặc logic re-rank riêng

            # Gửi 2 request riêng biệt
            vector_results = qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=request.top_k,
                query_filter=rag_filter,
                with_payload=True,
            )

            keyword_results = qdrant_client.search(
                collection_name=collection_name,
                query_vector=[0.0] * VECTOR_DIMENSION,
                query_filter=keyword_filter,
                limit=request.top_k,
                with_payload=True,
            )

            # 3. Hợp nhất và Sắp xếp lại (Reciprocal Rank Fusion - RRF)
            fused_scores = {}
            k = 60  # Hằng số RRF, 60 là giá trị tiêu chuẩn

            # Gán điểm cho kết quả vector
            for i, point in enumerate(vector_results):
                rank = i + 1
                score = 1.0 / (k + rank)
                if point.id not in fused_scores:
                    fused_scores[point.id] = {"score": 0.0, "point": point}
                fused_scores[point.id]["score"] += score

            # Gán điểm cho kết quả keyword
            for i, point in enumerate(keyword_results):
                rank = i + 1
                score = 1.0 / (k + rank)
                if point.id not in fused_scores:
                    fused_scores[point.id] = {"score": 0.0, "point": point}
                fused_scores[point.id]["score"] += score

            # Sắp xếp các kết quả đã hợp nhất
            sorted_fused_results = sorted(
                fused_scores.values(), key=lambda x: x["score"], reverse=True
            )

            # 4. Lấy top_k kết quả cuối cùng
            search_results = [
                item["point"] for item in sorted_fused_results[: request.top_k]
            ]

            logging.info(
                f"Kết quả Vector: {len(vector_results)}, Keyword: {len(keyword_results)}, Hợp nhất: {len(search_results)}"
            )

            context = ""
            retrieved_sources_str = set()
            new_doc_ids_found = []

            # Biến cờ để đánh dấu đã tìm thấy nguồn "xịn" (Link/PDF) chưa
            found_priority_source = False

            # Biến dự phòng: lưu lại nguồn docx đầu tiên (để nếu không tìm được link nào thì dùng tạm, hoặc bỏ qua tùy bạn)
            fallback_source = None
            if search_results:
                # top_hit = search_results[0]
                # if top_hit.payload and "source" in top_hit.payload:
                #     retrieved_sources_str.add(top_hit.payload["source"])
                # else:
                #     logging.warning(
                #         f"Kết quả top 1 (ID {top_hit.id}) thiếu payload 'source'."
                #     )

                # for result in search_results:
                #     if result.payload and "content" in result.payload:
                #         context += result.payload["content"] + "\n---\n"
                #         if "doc_id" in result.payload:
                #             new_doc_ids_found.append(result.payload["doc_id"])
                #     else:
                #         logging.warning(
                #             f"Kết quả tìm kiếm ID {result.id} thiếu payload 'content'. Bỏ qua context."
                #         )
                for i, result in enumerate(search_results):
                    # 1. Luôn lấy CONTENT để nạp vào Context cho AI trả lời
                    if result.payload and "content" in result.payload:
                        context += result.payload["content"] + "\n---\n"
                        if "doc_id" in result.payload:
                            new_doc_ids_found.append(result.payload["doc_id"])

                    # 2. Xử lý SOURCE: Logic "Đi tìm Link"
                    if result.payload and "source" in result.payload:
                        raw_source = result.payload["source"]

                        # Kiểm tra nhanh xem nguồn này có phải docx không
                        # (Cách đơn giản: check đuôi file trong chuỗi JSON)
                        is_docx = (
                            ".docx" in raw_source.lower()
                            or ".doc" in raw_source.lower()
                        )
                        is_url = "http://" in raw_source or "https://" in raw_source

                        if not found_priority_source:
                            if is_url or (not is_docx):
                                # A. Nếu gặp Link hoặc PDF -> LẤY NGAY và DỪNG TÌM
                                retrieved_sources_str.add(raw_source)
                                found_priority_source = True
                            else:
                                # B. Nếu là Docx -> Bỏ qua, nhưng lưu làm dự phòng (nếu muốn)
                                if fallback_source is None:
                                    fallback_source = raw_source

                # 3. (Tùy chọn) Xử lý khi duyệt hết mà chỉ toàn là Docx
                # Nếu bạn muốn: "Nếu không có link thì thà không hiện gì cả", hãy xóa đoạn if này.
                # Nếu bạn muốn: "Nếu không có link thì hiện tạm docx đầu tiên", hãy giữ đoạn này.
                if not found_priority_source and fallback_source:
                    # Uncomment dòng dưới nếu muốn hiện docx khi không có link
                    # retrieved_sources_str.add(fallback_source)
                    pass
            else:
                logging.info("Không tìm thấy kết quả NÀO MỚI trong Qdrant (đã lọc).")

            # Phần code RAG, xử lý source, lưu DB...
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
            print(f"Lỗi xử lý RAG: {e}")
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
    retrieved_contexts = []
    if question_category == "NONG_NGHIEP" and "search_results" in locals():
        for result in search_results:
            if result.payload and "content" in result.payload:
                retrieved_contexts.append(result.payload["content"])

    return {
        "answer": final_answer_to_save,
        "sources": parsed_sources,
        "conversation_id": conv_id,
        "retrieved_contexts": retrieved_contexts,
    }


# import os
# import json
# import logging
# from typing import List, Dict, Any
# from fastapi import HTTPException
# from qdrant_client import models

# # Import các thành phần từ app
# from app.core.lifespan import models_cache
# from app.schema.chat_schema import QueryRequest, Source
# from app.models.conversation import Message
# from app.services import conversation_service

# # Import các Prompt Templates
# from app.prompts.chat_prompts import (
#     COMBINED_PROMPT,
#     PROMPT_RAG_TEMPLATE,
#     CHITCHAT_RESPONSE_TEMPLATE,
#     OUT_OF_DOMAIN_RESPONSE_TEMPLATE,
# )

# # Cấu hình log
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# def _format_sources(sources_list: List[List[Source]]) -> str:
#     """
#     Hàm định dạng danh sách nguồn tham khảo để hiển thị đẹp mắt.
#     Loại bỏ các nguồn trùng lặp.
#     """
#     if not sources_list:
#         return ""

#     unique_sources = {}
#     for source_group in sources_list:
#         for source in source_group:
#             if isinstance(source, Source):
#                 # Tạo key để khử trùng lặp (tên + url)
#                 key = (source.name, source.url)
#                 if key in unique_sources:
#                     continue

#                 # Logic lọc nguồn: Ưu tiên link http hoặc file PDF local
#                 if source.url and (
#                     source.url.startswith("http") or source.url == "local_file"
#                 ):
#                     unique_sources[key] = source

#     if not unique_sources:
#         return ""

#     header = "\n\n---\n**Nguồn tham khảo:**\n"
#     source_lines = []
#     for i, source in enumerate(unique_sources.values()):
#         if source.url and source.url != "local_file":
#             source_lines.append(f"{i+1}. [{source.name}]({source.url})")
#         else:
#             source_lines.append(f"{i+1}. {source.name}")

#     return header + "\n".join(source_lines)


# async def process_chat_request(request: QueryRequest) -> Dict[str, Any]:
#     """
#     Hàm xử lý chính cho logic RAG:
#     1. Lấy lịch sử hội thoại.
#     2. Phân loại câu hỏi & Ý định (Intent).
#     3. Nếu là Nông nghiệp:
#        - Tìm kiếm Vector (Top 50).
#        - Re-ranking bằng Cross-Encoder (Lọc lấy Top K).
#        - Sinh câu trả lời với Gemini.
#     4. Lưu lịch sử và trả về kết quả.
#     """

#     # 1. Lấy các model từ Cache (đã load ở lifespan.py)
#     try:
#         embedding_model = models_cache["embedding_model"]
#         qdrant_client = models_cache["qdrant_client"]
#         llm_rag = models_cache["llm_rag"]  # Gemini Pro
#         llm_fast = models_cache["llm_fast"]  # Gemini Flash
#         reranker_model = models_cache.get("reranker_model")  # Model chấm điểm lại
#     except KeyError as e:
#         logger.error(f"Thiếu model trong cache: {e}")
#         raise HTTPException(
#             status_code=500, detail="Hệ thống chưa khởi tạo xong các models AI."
#         )

#     collection_name = os.getenv("QDRANT_COLLECTION_NAME")
#     conv_id = request.conversation_id
#     user_question = request.question

#     # 2. Quản lý Lịch sử hội thoại
#     current_history: List[Dict] = []
#     retrieved_doc_ids: List[str] = []

#     if conv_id:
#         conversation = await conversation_service.get_conversation_by_id(conv_id)
#         if conversation:
#             # Chuyển đổi message object thành dict cho prompt
#             current_history = [
#                 {"role": msg["sender"], "content": msg["content"]}
#                 for msg in conversation.get("messages", [])
#             ]
#             retrieved_doc_ids = conversation.get("retrieved_doc_ids", [])
#     else:
#         # Nếu chưa có conv_id, tạo mới
#         new_conv_data = {"user_id": request.user_id, "messages": []}
#         conv_id = await conversation_service.create_conversation(new_conv_data)

#     # Chỉ lấy 5 tin nhắn gần nhất để làm short-term memory cho LLM
#     current_history_limited = current_history[-5:]
#     chat_history_str = "\n".join(
#         [
#             f"{'Người dùng' if msg['role'] == 'user' else 'Trợ lý'}: {msg['content']}"
#             for msg in current_history_limited
#         ]
#     )

#     # 3. Phân loại câu hỏi & Ý định (Dùng LLM nhanh - Flash)
#     # Bước này giúp xác định xem có cần chạy RAG không
#     combined_prompt = COMBINED_PROMPT.format(
#         chat_history=chat_history_str, question=user_question
#     )

#     # Giá trị mặc định
#     question_category = "NONG_NGHIEP"
#     search_question = user_question
#     user_intent = "NEW_TOPIC"

#     try:
#         response = await llm_fast.generate_content_async(combined_prompt)
#         json_response_str = response.text.strip()
#         # Làm sạch chuỗi JSON nếu model trả về markdown code block
#         if json_response_str.startswith("```json"):
#             json_response_str = json_response_str[7:-3].strip()
#         elif json_response_str.startswith("```"):
#             json_response_str = json_response_str[3:-3].strip()

#         result_json = json.loads(json_response_str)
#         question_category = result_json.get("loai", "NONG_NGHIEP").upper()
#         user_intent = result_json.get("intent", "NEW_TOPIC").upper()
#         search_question = result_json.get("cau_hoi_tim_kiem", user_question)

#         logger.info(
#             f"Phân loại: {question_category} | Intent: {user_intent} | Search Query: {search_question}"
#         )

#     except Exception as e:
#         logger.error(f"Lỗi khi gọi LLM phân loại: {e}. Sử dụng mặc định.")

#     # 4. Xử lý logic theo từng loại câu hỏi
#     final_answer_to_save = ""
#     parsed_sources: List[List[Source]] = []
#     retrieved_contexts_for_eval = (
#         []
#     )  # Biến này dùng để trả về cho script đánh giá (evaluate_rag.py)

#     # --- TRƯỜNG HỢP 1: CÂU HỎI NÔNG NGHIỆP (CHẠY RAG) ---
#     if question_category == "NONG_NGHIEP":
#         try:
#             # A. Vector Search (Retrieval) - Lấy số lượng lớn (Initial Retrieval)
#             # Chúng ta lấy 50 kết quả để đảm bảo không bị sót (High Recall)
#             initial_top_k = 50
#             query_vector = embedding_model.encode(search_question).tolist()

#             # Tạo bộ lọc: Nếu ý định là EXPLORE_NEW (khám phá mới), lọc bỏ các tài liệu đã xem
#             rag_filter = None
#             if user_intent == "EXPLORE_NEW" and retrieved_doc_ids:
#                 logger.info(
#                     f"Intent EXPLORE_NEW: Lọc bỏ {len(retrieved_doc_ids)} tài liệu cũ."
#                 )
#                 rag_filter = models.Filter(
#                     must_not=[
#                         models.FieldCondition(
#                             key="doc_id", match=models.MatchAny(any=retrieved_doc_ids)
#                         )
#                     ]
#                 )

#             # Thực hiện tìm kiếm Vector
#             search_results = qdrant_client.search(
#                 collection_name=collection_name,
#                 query_vector=query_vector,
#                 query_filter=rag_filter,
#                 limit=initial_top_k,
#                 with_payload=True,
#             )

#             logger.info(
#                 f"1. Vector Search: Tìm thấy {len(search_results)} kết quả thô."
#             )

#             # B. Re-ranking (Sắp xếp lại) - Lọc lấy tinh hoa (Precision)
#             final_results = []

#             if search_results:
#                 if reranker_model:
#                     # Chuẩn bị dữ liệu cho Cross-Encoder: List các cặp [Query, Document Content]
#                     passages = []
#                     valid_hits = []

#                     for hit in search_results:
#                         if hit.payload and "content" in hit.payload:
#                             passages.append([search_question, hit.payload["content"]])
#                             valid_hits.append(hit)

#                     if passages:
#                         # Cross-Encoder chấm điểm sự liên quan giữa câu hỏi và đoạn văn
#                         # Scores trả về là số thực (logits), càng cao càng liên quan
#                         scores = reranker_model.predict(passages)

#                         # Gán điểm mới vào kết quả
#                         for i, hit in enumerate(valid_hits):
#                             hit.score = float(scores[i])

#                         # Sắp xếp giảm dần theo điểm Re-ranker
#                         ranked_hits = sorted(
#                             valid_hits, key=lambda x: x.score, reverse=True
#                         )

#                         # Lấy Top-K cuối cùng để đưa vào LLM (ví dụ: top 5 hoặc 10)
#                         final_results = ranked_hits[: request.top_k]
#                         logger.info(
#                             f"2. Re-ranking: Đã lọc lấy {len(final_results)} kết quả tốt nhất."
#                         )
#                 else:
#                     # Fallback nếu không có Re-ranker (dù hiếm khi xảy ra nếu setup đúng)
#                     logger.warning(
#                         "Không tìm thấy model Re-ranker, sử dụng kết quả Vector thuần."
#                     )
#                     final_results = search_results[: request.top_k]
#             else:
#                 logger.info("Không tìm thấy kết quả nào từ Qdrant.")

#             # C. Chuẩn bị Context và Sources
#             context = ""
#             retrieved_sources_str = set()
#             new_doc_ids_found = []

#             for result in final_results:
#                 content = result.payload.get("content", "").strip()
#                 if not content:
#                     continue

#                 # Thêm vào context cho LLM
#                 context += content + "\n---\n"

#                 # Lưu text để phục vụ đánh giá (Evaluation)
#                 retrieved_contexts_for_eval.append(content)

#                 # Lấy thông tin nguồn (Source)
#                 if "source" in result.payload:
#                     retrieved_sources_str.add(result.payload["source"])

#                 # Lấy doc_id để update lịch sử (tránh lặp lại sau này)
#                 if "doc_id" in result.payload:
#                     new_doc_ids_found.append(result.payload["doc_id"])

#             # D. Sinh câu trả lời với Gemini (Generation)
#             final_prompt = PROMPT_RAG_TEMPLATE.format(
#                 chat_history=chat_history_str, context=context, question=user_question
#             )

#             response_from_llm = await llm_rag.generate_content_async(final_prompt)
#             answer_text_only = response_from_llm.text

#             # E. Xử lý danh sách nguồn (Parse JSON string -> Object)
#             for source_json_string in list(retrieved_sources_str):
#                 try:
#                     list_of_source_dicts = json.loads(source_json_string)
#                     if isinstance(list_of_source_dicts, list):
#                         source_objects = [
#                             Source(**data)
#                             for data in list_of_source_dicts
#                             if isinstance(data, dict)
#                         ]
#                         if source_objects:
#                             parsed_sources.append(source_objects)
#                 except Exception as e:
#                     logger.warning(f"Lỗi parse source: {e}")

#             formatted_sources_str = _format_sources(parsed_sources)

#             # Logic kiểm tra câu trả lời từ chối
#             if (
#                 "tôi đang cập nhật thêm thông tin" not in answer_text_only.lower()
#                 and "tôi chưa tìm thấy thông tin" not in answer_text_only.lower()
#             ):
#                 final_answer_to_save = answer_text_only + formatted_sources_str
#                 # Cập nhật doc_id đã xem vào DB
#                 if conv_id and new_doc_ids_found:
#                     await conversation_service.update_retrieved_docs(
#                         conv_id, new_doc_ids_found
#                     )
#             else:
#                 # Nếu không trả lời được, không hiện nguồn
#                 final_answer_to_save = answer_text_only

#         except Exception as e:
#             logger.error(f"Lỗi nghiêm trọng trong luồng RAG: {e}", exc_info=True)
#             final_answer_to_save = "Xin lỗi, hệ thống đang gặp sự cố kỹ thuật khi truy xuất dữ liệu. Vui lòng thử lại sau."

#     # --- TRƯỜNG HỢP 2: CHÀO HỎI XÃ GIAO ---
#     elif question_category == "CHAO_HOI":
#         chitchat_prompt = CHITCHAT_RESPONSE_TEMPLATE.format(question=user_question)
#         try:
#             chitchat_response = await llm_fast.generate_content_async(chitchat_prompt)
#             final_answer_to_save = chitchat_response.text
#         except Exception:
#             final_answer_to_save = "Chào bạn! Tôi là trợ lý ảo chuyên về cây lúa và cây xoài. Tôi có thể giúp gì cho bạn?"

#     # --- TRƯỜNG HỢP 3: CÂU HỎI NGOÀI LỀ ---
#     elif question_category == "NGOAI_LE":
#         ood_prompt = OUT_OF_DOMAIN_RESPONSE_TEMPLATE.format(question=user_question)
#         try:
#             ood_response = await llm_fast.generate_content_async(ood_prompt)
#             final_answer_to_save = ood_response.text
#         except Exception:
#             final_answer_to_save = "Xin lỗi, chuyên môn của tôi chỉ giới hạn ở cây lúa và cây xoài. Bạn vui lòng hỏi các vấn đề liên quan đến nông nghiệp nhé."

#     # Fallback cuối cùng
#     else:
#         final_answer_to_save = "Tôi chưa hiểu rõ câu hỏi. Bạn có thể nói rõ hơn về vấn đề trên cây lúa hoặc xoài không?"

#     # 5. Lưu tin nhắn vào MongoDB
#     if not final_answer_to_save:
#         final_answer_to_save = "Đã có lỗi xảy ra."

#     user_message = Message(sender="user", content=user_question)
#     bot_message = Message(sender="bot", content=final_answer_to_save)

#     if conv_id:
#         try:
#             await conversation_service.add_message(conv_id, user_message.model_dump())
#             await conversation_service.add_message(conv_id, bot_message.model_dump())
#         except Exception as e:
#             logger.error(f"Lỗi khi lưu DB: {e}")
#             # Không raise error ở đây để người dùng vẫn nhận được câu trả lời

#     # 6. Trả về kết quả
#     return {
#         "answer": final_answer_to_save,
#         "sources": parsed_sources,
#         "conversation_id": conv_id,
#         "retrieved_contexts": retrieved_contexts_for_eval,  # Dùng cho đánh giá
#     }
