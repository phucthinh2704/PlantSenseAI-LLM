from pydantic import BaseModel
from typing import List, Optional

class Step(BaseModel):
    step: int
    name: str
    description: str

class DiseaseTreatment(BaseModel):
    step: int
    name: str
    description: str

class Disease(BaseModel):
    name: str
    symptom: str
    prevention: List[DiseaseTreatment]
    treatment: List[DiseaseTreatment]

class Morphology(BaseModel):
    height: str
    stem: str
    leaf: str
    grain: str

class Plant(BaseModel):
    name: str
    scientific_name: str
    origin: str
    category: str
    growth_duration_days: int
    morphology: Morphology
    cultivation_technology: List[Step]
    diseases: Optional[List[Disease]] = []
    class Config:
        from_attributes = True