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
    role: str = "user"  # "user" | "admin"
    provider_name: Optional[str] = None  # "local" | "google" | "facebook"
    provider_id: Optional[str] = None  # ID do bên thứ 3 cung cấp
    is_outside: bool = False  # Người dùng đăng ký từ bên ngoài hay nội bộ
    refresh_token: Optional[str] = None  # Refresh token để cấp mới access token

    status: UserStatus = UserStatus.inactive  # Trạng thái mặc định
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


from app.core.security import hash_password
from app.core.database import user_collection
from app.models.user import UserStatus
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
import os


async def create_admin_user():

    # Lấy từ biến môi trường (nếu có), fallback về giá trị mặc định
    admin_email = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin@password")
    admin_name = os.getenv("ADMIN_NAME", "Admin")

    # Kiểm tra xem admin đã tồn tại chưa
    existing = await user_collection.find_one({"email": admin_email})
    if existing:
        print(f"Admin đã tồn tại ({admin_email})")
        return

    # Tạo mới admin user
    new_user = {
        "name": admin_name,
        "email": admin_email,
        "password": hash_password(admin_password),
        "provider_name": "local",
        "provider_id": None,
        "is_outside": False,
        "status": UserStatus.active.value,
        "role": "admin",
        "avatar": None,
        "phone": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    result = await user_collection.insert_one(new_user)
    print(f"Tạo tài khoản admin mặc định: {str(result.inserted_id)}")
