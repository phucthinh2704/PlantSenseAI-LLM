from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel 

T = TypeVar("T")

class APIResponse(GenericModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
