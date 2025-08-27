from pydantic import BaseModel

class RoleResponse(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class RoleCreate(BaseModel):
    name: str 

class RoleUpdate(BaseModel):
    name: str