from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Plant(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    origin: str
    category: str
    growth_duration: str          
    morphology: str               
    yields: Optional[str] = None  # VD: "5-7 tấn/ha"
    description: Optional[str] = None
    image_url: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
