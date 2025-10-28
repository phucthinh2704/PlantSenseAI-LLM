import logging
from fastapi import APIRouter, HTTPException
from app.schema.chat_schema import QueryRequest, QueryResponse 
from app.services import chat_service

router = APIRouter()

@router.post("/ask", response_model=QueryResponse) 
async def chat_with_rag(request: QueryRequest):
    try:
        result = await chat_service.process_chat_request(request)
        return QueryResponse(**result)
    except Exception as e:
        logging.error(f"Đã xảy ra lỗi trong API chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Đã có lỗi xảy ra ở server: {str(e)}"
        )