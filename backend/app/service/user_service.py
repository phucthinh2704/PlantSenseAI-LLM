from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.model import User, UserStatus
from app.schema.user_schema import UpdateUserRequest



def get_user_by_id(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại",
        )
    return user


def get_current_user_info(user_id: int, db: Session) -> dict:
    user = get_user_by_id(user_id, db)

    if user.status != UserStatus.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa được kích hoạt",
        )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "avatar": user.avatar,
        "role_id": user.role_id,
        "status": user.status,
    }


def update_profile(user_id: int, update_data: UpdateUserRequest, db: Session) -> dict:
    user = get_user_by_id(user_id, db)

    # data = update_data.dict(exclude_unset=True) 
    data = update_data.model_dump(exclude_unset=True) # chỉ lấy field có truyền vào

    if "name" in data:
        user.name = data["name"]
    if "avatar" in data:
        user.avatar = data["avatar"]
    if "phone" in data:
        user.phone = data["phone"]

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "avatar": user.avatar,
        "phone": user.phone,
    }


def get_all_users(db: Session) -> list:
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "avatar": u.avatar,
            "role_id": u.role_id,
            "status": u.status,
        }
        for u in users
    ]


def delete_user(user_id: int, db: Session):
    user = get_user_by_id(user_id, db)
    db.delete(user)
    db.commit()
