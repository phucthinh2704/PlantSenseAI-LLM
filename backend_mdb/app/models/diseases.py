from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class TreatmentStep(BaseModel):
    step: int
    name: str
    description: str
    chemical: Optional[str] = None  # thuốc, hoạt chất
    dosage: Optional[str] = None  # liều lượng
    note: Optional[str] = None


class Disease(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    cause: Optional[str] = None
    symptom: str
    prevention: List[TreatmentStep]
    treatment: List[TreatmentStep]
    image_url: Optional[str] = None

    plant_ids: List[str]  # danh sách _id các plant bị bệnh này
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
