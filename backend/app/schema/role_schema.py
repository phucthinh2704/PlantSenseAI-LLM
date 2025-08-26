from pydantic import BaseModel

class RoleResponse(BaseModel):
    id: int
    name: str
    class config:
        from_attributes: True

class RoleCreate(BaseModel):
    name: str
    class config:
        from_attributes: True