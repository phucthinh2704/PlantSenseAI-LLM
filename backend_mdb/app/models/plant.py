from pydantic import BaseModel, Field
from typing import Optional, List
from .source import Source
from datetime import datetime, timezone

class Plant(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    category: str # Ngũ cốc, Cây ăn quả...
    plant_type: str # Lúa, Xoài...
    
    # Đổi các trường này thành Optional vì Excel gom chung vào "Thông tin giống"
    origin: Optional[str] = None
    growth_duration: Optional[str] = None
    morphology: Optional[str] = None
    yields: Optional[str] = None  
    
    description: Optional[str] = None # Lưu toàn bộ "Chú thích" và "Thông tin giống"
    image_url: Optional[str] = None
    sources: List[Source] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))