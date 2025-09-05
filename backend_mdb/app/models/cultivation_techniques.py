from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class Step(BaseModel):
    step: int
    name: str
    description: str
    image_url: Optional[str] = None


class CultivationTechnique(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    plant_id: str  # liên kết với _id của plant
    season: Optional[str] = None  # vụ gieo trồng
    steps: List[Step]

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
