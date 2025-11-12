from fastapi import APIRouter, Depends, HTTPException, status # <-- Thêm status
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

import os
from app.models.user import User, UserStatus
from app.services import user_service, auth_service
from app.schema.response_schema import APIResponse
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_password,
    decode_access_token,
    decode_refresh_token
)
# --- THAY ĐỔI: Import dependency ---
from app.services.auth_service import get_current_active_user

router = APIRouter()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


# Register (local)
@router.post("/register", response_model=APIResponse)
async def register(user: User):
    existing = await user_service.get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
    
    # Đảm bảo password tồn tại trước khi hash
    if not user.password:
        raise HTTPException(status_code=400, detail="Mật khẩu là bắt buộc")
        
    user.password = hash_password(user.password)
    user.status = UserStatus.active
    
    # --- SỬA: model_dump() để loại bỏ 'id' None ---
    inserted_id = await user_service.create_user(user)
    
    return APIResponse(
        success=True,
        message="Đăng ký tài khoản thành công",
        data={"inserted_id": inserted_id},
    )


class LoginRequest(BaseModel):
    email: str
    password: str


# Login (local)
@router.post("/login", response_model=APIResponse)
async def login(form_data: LoginRequest):
    user = await user_service.get_user_by_email(form_data.email)
    if (
        not user
        or not user.password
        or not verify_password(form_data.password, user.password)
    ):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác")

    # Tạo token
    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Lưu refresh_token vào DB
    await user_service.update_user(user.id, {"refresh_token": refresh_token})

    return APIResponse(
        success=True,
        message="Đăng nhập thành công",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "status": user.status,
                "avatar": user.avatar,
            },
        },
    )


class TokenRequest(BaseModel):
    token: str


# Login (Google OAuth2)
@router.post("/google", response_model=APIResponse)
async def login_google(req: TokenRequest):
    result = await auth_service.google_login(req.token, GOOGLE_CLIENT_ID)
    if not result:
        raise HTTPException(status_code=401, detail="Token Google không hợp lệ")
    return APIResponse(
        success=True,
        message="Đăng nhập thành công",
        data=result,
    )


# Me (get current user from JWT)
@router.get("/me", response_model=APIResponse)
# --- THAY ĐỔI: Dùng dependency ---
async def get_me(current_user: User = Depends(get_current_active_user)):
    # Không cần decode token, hàm dependency đã làm việc đó
    # Trả về Pydantic model đã được serialize
    return APIResponse(
        success=True,
        message="Lấy thông tin người dùng thành công",
        data=current_user.model_dump(by_alias=True)
    )

class LogoutRequest(BaseModel):
    refreshToken: str

@router.post("/logout", response_model=APIResponse)
async def logout(request: LogoutRequest):
    # (Code logout của bạn đã ổn, giữ nguyên)
    refresh_token = request.refreshToken
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Thiếu refresh token")

    try:
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get("sub")
        user = await user_service.get_user_by_id(user_id)

        if not user or user.refresh_token != refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token không hợp lệ")

        await user_service.update_user(user.id, {"refresh_token": None})

        return APIResponse(
            success=True,
            message="Đăng xuất thành công",
            data=None,
        )
    except Exception as e:
        raise HTTPException(status_code=403, detail="Refresh token không hợp lệ hoặc hết hạn")