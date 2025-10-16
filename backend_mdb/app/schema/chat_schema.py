import uuid
from datetime import date
from typing import List
from pydantic import BaseModel, Field

class Source(BaseModel):
    name: str
    url: str
    retrieved_at: date = Field(default_factory=date.today)

class QueryRequest(BaseModel):
    question: str
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    top_k: int = 10

class QueryResponse(BaseModel):
    answer: str
    sources: List[List[Source]]
    session_id: str