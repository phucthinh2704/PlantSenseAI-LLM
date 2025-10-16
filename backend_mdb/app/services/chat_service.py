import os
import logging
import json
from typing import List

from app.core.lifespan import models_cache, conversation_histories
from app.schema.chat_schema import QueryRequest, Source
from app.prompts.chat_prompts import QUERY_REWRITE_TEMPLATE, PROMPT_RAG_TEMPLATE

async def process_chat_request(request: QueryRequest) -> dict:
    embedding_model = models_cache["embedding_model"]
    qdrant_client = models_cache["qdrant_client"]
    llm_rag = models_cache["llm_rag"]
    llm_fast = models_cache["llm_fast"]
    collection_name = os.getenv("QDRANT_COLLECTION_NAME")

    session_id = request.session_id
    current_history = conversation_histories.get(session_id, [])

    chat_history_str = "\n".join(
        [f"Người dùng: {msg['content']}" if msg['role'] == 'user' else f"Trợ lý: {msg['content']}" for msg in current_history]
    )
    
    logging.info(f"Session ID: {session_id} | Lịch sử hiện tại: {current_history}")

    # 1. Viết lại câu hỏi để tìm kiếm nếu có lịch sử trò chuyện
    search_question = request.question
    if current_history:
        logging.info(f"Câu hỏi gốc: {request.question}")
        rewrite_prompt = QUERY_REWRITE_TEMPLATE.format(
            chat_history=chat_history_str, question=request.question
        )
        response = await llm_fast.generate_content_async(rewrite_prompt)
        search_question = response.text.strip()
        logging.info(f"Câu hỏi được viết lại để tìm kiếm: {search_question}")
    
    # 2. Vector hóa và tìm kiếm trong Qdrant
    text_to_search = "query: " + search_question
    query_vector = embedding_model.encode(text_to_search).tolist()

    search_results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=request.top_k,
    )

    # 3. Xây dựng ngữ cảnh và nguồn
    context = ""
    retrieved_sources_str = set()
    for result in search_results:
        context += result.payload["content"] + "\n---\n"
        retrieved_sources_str.add(result.payload["source"])

    # 4. Tạo prompt cuối cùng và gọi LLM để sinh câu trả lời
    final_prompt = PROMPT_RAG_TEMPLATE.format(
        chat_history=chat_history_str, context=context, question=request.question
    )

    response_from_llm = await llm_rag.generate_content_async(final_prompt)
    answer = response_from_llm.text

    # 5. Cập nhật lịch sử trò chuyện
    current_history.append({"role": "user", "content": request.question})
    current_history.append({"role": "model", "content": answer})
    conversation_histories[session_id] = current_history

    # 6. Xử lý và trả về nguồn
    parsed_sources: List[List[Source]] = []
    for source_json_string in list(retrieved_sources_str):
        try:
            list_of_source_dicts = json.loads(source_json_string)
            source_objects = [Source(**data) for data in list_of_source_dicts]
            parsed_sources.append(source_objects)
        except (json.JSONDecodeError, TypeError) as e:
            logging.warning(f"Bỏ qua source không hợp lệ: {source_json_string}. Lỗi: {e}")
            continue
    
    return {
        "answer": answer,
        "sources": parsed_sources,
        "session_id": session_id
    }