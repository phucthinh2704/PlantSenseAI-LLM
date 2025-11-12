from fastapi import HTTPException, status, Depends
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.database import db  # <-- Sửa: dùng db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    oauth2_scheme,
    decode_access_token,
)
from app.models.user import User, UserStatus
from app.services import user_service  # <-- THÊM
from jose import JWTError  # <-- THÊM
from datetime import datetime, timezone  # <-- THÊM


async def google_login(google_token: str, client_id: str):
    try:
        id_info = id_token.verify_oauth2_token(
            google_token, google_requests.Request(), client_id
        )

        user_data = {
            "sub": id_info["sub"],
            "email": id_info.get("email"),
            "name": id_info.get("name"),
            "picture": id_info.get("picture"),
        }

        # Sửa: Dùng user_service
        user = await user_service.get_user_by_email(user_data["email"])

        if not user:
            # Sửa: Khớp Pydantic model User
            new_user_data = {
                "name": user_data.get("name") or "",
                "avatar": user_data.get("picture") or None,
                "email": user_data.get("email"),
                "password": None,
                "provider_name": "google",
                "provider_id": user_data["sub"],
                "is_outside": True,
                "status": UserStatus.active,  # Dùng enum
                "role": "user",
            }
            # Sửa: Dùng create_user từ service
            new_user_id = await user_service.create_user(User(**new_user_data))
            user = await user_service.get_user_by_id(new_user_id)

        # Tạo JWT
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Sửa: Dùng user_service
        await user_service.update_user(user.id, {"refresh_token": refresh_token})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "avatar": user.avatar,
                "role": user.role,
                "status": user.status,
            },
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Google không hợp lệ",
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency: Giải mã token, lấy user_id, và truy vấn DB để lấy user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = await user_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency: Lấy user hiện tại và kiểm tra xem họ có "active" không.
    (Đây là hàm mà `auth_deps.py` cần)
    """
    if current_user.status != UserStatus.active:
        raise HTTPException(status_code=400, detail="Tài khoản không hoạt động")
    return current_user
