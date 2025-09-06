from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TreatmentStep(BaseModel):
    step: int
    name: str
    description: str
    stage: Optional[str] = None  # giai đoạn cây (VD: "Mạ", "Đẻ nhánh", "Trổ đồng")
    chemical: Optional[str] = None
    dosage: Optional[str] = None
    note: Optional[str] = None


class Disease(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    cause: Optional[str] = None
    symptom: str
    prevention: List[TreatmentStep]
    treatment: List[TreatmentStep]
    image_url: Optional[str] = None

    plant_ids: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
