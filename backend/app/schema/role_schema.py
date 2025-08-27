from pydantic import BaseModel

class RoleResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class RoleCreate(BaseModel):
    name: str 

class RoleUpdate(BaseModel):
    name: str