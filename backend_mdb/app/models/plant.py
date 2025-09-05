from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class Morphology(BaseModel):
    height: str
    stem: str
    leaf: str
    grain: str

class Plant(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    scientific_name: str
    origin: str
    category: str
    growth_duration_days: int
    morphology: Morphology
    description: Optional[str] = None  # mô tả tổng quát
    image_url: Optional[str] = None    # ảnh minh họa

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
