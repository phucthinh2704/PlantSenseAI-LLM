from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Literal, List

from app.schema.response_schema import APIResponse
from app.services import user_service
# Import dependency để bảo vệ route admin
from app.core.auth_deps import get_current_admin_user 
from app.models.user import User, UserStatus # Import model User và Enum

router = APIRouter()

# --- Định nghĩa Pydantic model cho request body ---
class RoleUpdate(BaseModel):
    role: Literal["user", "admin"]

class StatusUpdate(BaseModel):
    status: UserStatus # Dùng enum để xác thực

# --- Định nghĩa Endpoints ---

@router.get("/", response_model=APIResponse)
async def get_all_users(
    admin: User = Depends(get_current_admin_user)
):
    """(Admin) Lấy danh sách tất cả người dùng."""
    users = await user_service.get_all_users_admin()
    
    # Chuyển đổi Pydantic models thành dicts để trả về
    # Loại bỏ các trường nhạy cảm
    users_data = [
        user.model_dump(exclude={"password", "refresh_token"}) 
        for user in users
    ]
    
    return APIResponse(success=True, message="Lấy danh sách người dùng thành công", data=users_data)

@router.put("/{user_id}/role", response_model=APIResponse)
async def update_user_role(
    user_id: str,
    role_update: RoleUpdate,
    admin: User = Depends(get_current_admin_user)
):
    """(Admin) Cập nhật vai trò (role) của người dùng."""
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail="Admin không thể tự thay đổi vai trò của chính mình")
        
    updated = await user_service.update_user_status_or_role(user_id, role_update.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng hoặc không có gì thay đổi")
    return APIResponse(success=True, message="Cập nhật vai trò thành công")

@router.put("/{user_id}/status", response_model=APIResponse)
async def update_user_status(
    user_id: str,
    status_update: StatusUpdate,
    admin: User = Depends(get_current_admin_user)
):
    """(Admin) Cập nhật trạng thái (status) của người dùng."""
    if admin.id == user_id and status_update.status != UserStatus.active:
        raise HTTPException(status_code=400, detail="Admin không thể tự vô hiệu hóa chính mình")

    updated = await user_service.update_user_status_or_role(user_id, status_update.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng hoặc không có gì thay đổi")
    return APIResponse(success=True, message="Cập nhật trạng thái thành công")

@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(
    user_id: str,
    admin: User = Depends(get_current_admin_user)
):
    """(Admin) Xóa một người dùng."""
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail="Admin không thể tự xóa chính mình")
        
    deleted = await user_service.delete_user_admin(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return APIResponse(success=True, message="Đã xóa người dùng")