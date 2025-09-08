from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Disease(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    cause: Optional[str] = None
    image_url: Optional[str] = None
    plant_ids: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
