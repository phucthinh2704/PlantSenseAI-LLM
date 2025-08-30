from fastapi import HTTPException, status
from app.model import User, UserStatus
from app.schema.auth_schema import AuthLogin, AuthResponse
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
from app.util import verify_password, create_access_token


def login(login_data: AuthLogin, db: Session) -> AuthResponse:
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email không tồn tại"
        )
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Mật khẩu không chính xác"
        )
    if not check_user(user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa được kích hoạt",
        )
    return AuthResponse(
        id=user.id,
        name=user.name,
        access_token=create_access_token(
            data={"sub": str(user.id), "email": user.email, "role_id": user.role_id}
        )
    )


def check_user(user_id: int, db: Session) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại"
        )
    return user.status == UserStatus.active


def login_google(google_token: str, client_id: str, db: Session):
    try:
        # Verify token Google
        id_info = id_token.verify_oauth2_token(
            google_token, requests.Request(), client_id
        )

        # User info từ Google
        user_data = {
            "sub": id_info["sub"],
            "email": id_info.get("email"),
            "name": id_info.get("name"),
            "picture": id_info.get("picture"),
        }

        # Tìm user trong DB
        user = db.query(User).filter(User.email == user_data["email"]).first()

        if not user:
            # Nếu chưa có -> tạo mới
            user = User(
                name=user_data["name"] or "",
                avatar=user_data["picture"] or None,
                email=user_data["email"],
                password=None,
                provider_name="google",
                provider_id=user_data["sub"],
                is_outside=True,
                status=UserStatus.active,
                role_id=2,  # role mặc định
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Tạo JWT app riêng
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role_id": user.role_id}
        )

        return {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "avatar": user.avatar,
            },
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Google không hợp lệ",
        )
