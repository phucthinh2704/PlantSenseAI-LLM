from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.services.auth_service import get_current_active_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency để kiểm tra xem người dùng có phải là admin không.
    """
    if current_user.role != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập",
        )
    return current_user
