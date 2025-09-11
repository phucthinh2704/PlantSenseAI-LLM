from fastapi import APIRouter, Depends, HTTPException
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
    oauth2_scheme,
    decode_access_token,
    decode_refresh_token
)

router = APIRouter()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


# Register (local)
@router.post("/register", response_model=APIResponse)
async def register(user: User):
    existing = await user_service.get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    if user.password:
        user.password = hash_password(user.password)
    user.status = UserStatus.active
    inserted_id = await user_service.create_user(user)
    return APIResponse(
        success=True,
        message="User registered successfully",
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
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Tạo token
    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Lưu refresh_token vào DB (nếu bạn muốn revoke sau này)
    user.refresh_token = refresh_token
    await user_service.update_user(user.id, {"refresh_token": refresh_token})

    return APIResponse(
        success=True,
        message="Login success",
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
        raise HTTPException(status_code=401, detail="Invalid Google token")
    return APIResponse(
        success=True,
        message="Đăng nhập thành công",
        data=result,
    )


# Me (get current user from JWT)
@router.get("/me", response_model=APIResponse)
async def get_me(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return APIResponse(
        success=True,
        message="User retrieved successfully",
        data=user.dict(),
    )

class LogoutRequest(BaseModel):
    refreshToken: str

@router.post("/logout", response_model=APIResponse)
async def logout(request: LogoutRequest):
    refresh_token = request.refreshToken
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Missing refresh token")

    try:
        # Giải mã refresh token
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get("sub")
        user = await user_service.get_user_by_id(user_id)

        if not user or user.refresh_token != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Xoá refresh token trong DB
        await user_service.update_user(user.id, {"refresh_token": None})

        return APIResponse(
            success=True,
            message="Logged out successfully",
            data=None,
        )
    except Exception as e:
        raise HTTPException(status_code=403, detail="Refresh token expired")