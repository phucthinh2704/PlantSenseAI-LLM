import logging
from fastapi import APIRouter, Depends
from app.schema.response_schema import APIResponse
from app.services import admin_service
from app.core.auth_deps import get_current_admin_user

router = APIRouter()

@router.post("/index/run-incremental", response_model=APIResponse)
async def run_incremental_index(
    admin_user: dict = Depends(get_current_admin_user)
):
    """
    Chạy indexing tăng cường (chỉ index dữ liệu mới/cập nhật).
    """
    result = await admin_service.run_indexing_script(full_reindex=False)
    return APIResponse(success=True, message=result["message"], data=result)


@router.post("/index/run-full-reindex", response_model=APIResponse)
async def run_full_reindex(
    admin_user: dict = Depends(get_current_admin_user)
):
    """
    Chạy full re-index (xóa và chunk lại toàn bộ).
    """
    result = await admin_service.run_indexing_script(full_reindex=True)
    return APIResponse(success=True, message=result["message"], data=result)