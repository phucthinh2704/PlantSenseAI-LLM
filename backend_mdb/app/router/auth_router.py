from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

import os
from app.models.user import User, UserStatus
from app.services import user_service, auth_service
from app.schema.response_schema import APIResponse
from app.core.security import (
    create_access_token,
    verify_password,
    hash_password,
    oauth2_scheme,
    decode_access_token,
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


# Login (local)
@router.post("/login", response_model=APIResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_service.get_user_by_email(form_data.username)
    if (
        not user
        or not user.password
        or not verify_password(form_data.password, user.password)
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return APIResponse(
        success=True,
        message="Login successful",
        data={"access_token": token, "token_type": "bearer"},
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
