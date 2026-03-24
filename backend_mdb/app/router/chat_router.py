import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.schema.chat_schema import QueryResponse
from app.services import chat_service

router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
async def chat_with_rag(
    user_id: str = Form(...),
    question: str = Form(""),
    conversation_id: Optional[str] = Form(None),
    top_k: int = Form(20),
    images: Optional[list[UploadFile]] = File(None),  # Nhận nhiều file ảnh
):
    try:
        # 1. Đọc ảnh đầu tiên (nếu có) thành bytes
        image_bytes = None
        if images:
            first_image = images[0]
            image_bytes = await first_image.read()
            logging.info(f"Nhận file ảnh: {first_image.filename} - Type: {first_image.content_type}")

        # 2. Gọi service xử lý
        result = await chat_service.process_chat_request(
            user_id=user_id,
            conversation_id=conversation_id,
            question=question,
            image_bytes=image_bytes,
            top_k=top_k,
        )

        return QueryResponse(**result)

    except Exception as e:
        logging.error(f"Lỗi API chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi server: {str(e)}"
        )