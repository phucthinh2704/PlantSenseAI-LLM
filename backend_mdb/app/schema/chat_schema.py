import uuid
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field

class Source(BaseModel):
    name: str
    url: str
    retrieved_at: date = Field(default_factory=date.today)

class QueryRequest(BaseModel):
    question: str
    user_id: str  # Xác định người dùng
    conversation_id: Optional[str] = None # Tùy chọn, null cho tin nhắn đầu
    top_k: int = 12

class QueryResponse(BaseModel):
    answer: str
    sources: List[List[Source]]
    conversation_id: str # Luôn trả về để frontend có thể lưu lại