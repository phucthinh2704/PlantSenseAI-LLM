import uuid
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field

class Source(BaseModel):
    name: str
    url: str
    retrieved_at: date = Field(default_factory=date.today)

class QueryResponse(BaseModel):
    answer: str
    sources: List[List[Source]]
    conversation_id: str  # Luôn trả về để frontend có thể lưu lại
    disease_info: Optional[dict] = None  # Thông tin bệnh từ CNN (nếu có ảnh)