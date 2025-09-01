from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
