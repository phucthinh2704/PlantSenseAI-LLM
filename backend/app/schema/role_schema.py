from pydantic import Field, BaseModel
from typing import Annotated
from fastapi import Query

class RoleResponse(BaseModel):
    id: int
    name: str

class RoleCreate(BaseModel):
    name: str 

class RoleUpdate(BaseModel):
    name: str