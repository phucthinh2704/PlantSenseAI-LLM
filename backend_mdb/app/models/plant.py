from pydantic import BaseModel, Field
from typing import Optional, List
from .source import Source
from datetime import datetime, timezone


class Plant(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    origin: str
    plant_type: str
    category: str
    growth_duration: str
    morphology: str
    yields: Optional[str] = None  # VD: "5-7 tấn/ha"
    description: Optional[str] = None
    image_url: Optional[str] = None
    sources: List[Source] = Field(
        default_factory=list,
        description="Danh sách các nguồn tham khảo cho thông tin về giống cây này",
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
