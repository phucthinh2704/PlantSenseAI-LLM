from app.schema.response_schema import APIResponse
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.service import auth_service
from app.schema.auth_schema import AuthResponse, AuthLogin, TokenRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=APIResponse)
async def login(login_data: AuthLogin, db: Session = Depends(get_db)):
    result = auth_service.login(login_data, db)
    return APIResponse(success=True, message="Đăng nhập thành công", data=result)


@router.post("/google")
async def auth_google(req: TokenRequest):
    return {
        "access_token": req.token,
        "email": "thinh@example.com",
        "name": "Phuc Thinh",
    }
