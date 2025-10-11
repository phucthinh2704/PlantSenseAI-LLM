from pydantic import BaseModel, Field
from typing import Optional, List
from .source import Source
from datetime import datetime


class TreatmentStep(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    step: int
    name: str
    description: str
    chemical: Optional[str] = None
    dosage: Optional[str] = None
    note: Optional[str] = None


class DiseaseStage(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    disease_id: str
    stage: str
    symptom: str
    prevention: List[TreatmentStep]
    treatment: List[TreatmentStep]
    
    sources: List[Source] = Field(
        default_factory=list, 
        description="Danh sách các nguồn tham khảo cho giai đoạn bệnh này"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
