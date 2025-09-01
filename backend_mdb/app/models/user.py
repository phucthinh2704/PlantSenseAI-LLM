from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone
from enum import Enum
from bson import ObjectId


class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    banned = "banned"


class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")  # MongoDB ObjectId
    name: str  # Tên người dùng
    phone: Optional[str] = None  # Số điện thoại
    avatar: Optional[str] = None  # Ảnh đại diện
    email: EmailStr  # Email để đăng nhập
    password: Optional[str] = None  # Mật khẩu (null nếu đăng nhập bằng Google)

    provider_name: Optional[str] = None  # "local" | "google" | "facebook"
    provider_id: Optional[str] = None  # ID do bên thứ 3 cung cấp
    is_outside: bool = False  # Người dùng đăng ký từ bên ngoài hay nội bộ

    status: UserStatus = UserStatus.inactive  # Trạng thái mặc định
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {ObjectId: str}
