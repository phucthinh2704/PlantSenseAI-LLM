from pydantic import BaseModel, EmailStr
from typing import Optional
from app.model import UserStatus


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    # email không cho user tự sửa
    # password update sẽ có schema riêng (ChangePasswordRequest)
    
    class Config:
        orm_mode = True

