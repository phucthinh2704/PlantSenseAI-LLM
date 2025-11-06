from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone


class Disease(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    cause: Optional[str] = None
    image_url: Optional[str] = None
    plant_ids: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
