from pydantic import BaseModel

class AuthLogin(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    id: int
    name: str
    
