from fastapi import HTTPException, status
from app.model import User, UserStatus
from app.schema.auth_schema import AuthLogin, AuthResponse
from sqlalchemy.orm import Session
from app.util import verify_password

def login(login_data: AuthLogin, db: Session) -> AuthResponse:
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email không tồn tại"
        )
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mật khẩu không chính xác"
        )
    if not check_user(user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa được kích hoạt"
        )
    return AuthResponse(
        id=user.id,
        name=user.name
    )

def check_user(user_id: int, db: Session) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại"
        )
    return user.status == UserStatus.active