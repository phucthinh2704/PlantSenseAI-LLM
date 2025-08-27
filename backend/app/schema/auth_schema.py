from pydantic import BaseModel


class AuthLogin(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class TokenRequest(BaseModel):
    token: str
