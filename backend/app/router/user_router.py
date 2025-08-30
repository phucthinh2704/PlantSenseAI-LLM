from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.util import get_current_user, get_current_admin
from app.database import get_db
from app.service import user_service
from app.schema.response_schema import APIResponse
from app.schema.user_schema import UpdateUserRequest

router = APIRouter(prefix="/users", tags=["Users"])


# Lấy thông tin user hiện tại
@router.get("/me", response_model=APIResponse)
def get_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_info = user_service.get_current_user_info(current_user["sub"], db)
    return APIResponse(success=True, message="Lấy thông tin user thành công", data=user_info)


# Cập nhật profile
@router.put("/me", response_model=APIResponse)
def update_me(
    update_data: UpdateUserRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated_user = user_service.update_profile(current_user["sub"], update_data, db)
    return APIResponse(success=True, message="Cập nhật thông tin thành công", data=updated_user)


# Chỉ admin mới được xem danh sách user
@router.get("/", response_model=APIResponse)
def get_all_users(
    current_admin: dict = Depends(get_current_admin),  # check role
    db: Session = Depends(get_db),
):
    users = user_service.get_all_users(db)
    return APIResponse(success=True, message="Danh sách user", data=users)


# Chỉ admin mới được xóa user
@router.delete("/{user_id}", response_model=APIResponse)
def delete_user(
    user_id: int,
    current_admin: dict = Depends(get_current_admin),  # check role
    db: Session = Depends(get_db),
):
    user_service.delete_user(user_id, db)
    return APIResponse(success=True, message="Xóa user thành công")
