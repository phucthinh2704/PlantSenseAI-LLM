from typing import List
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.service import role_service
from app.schema.role_schema import RoleResponse, RoleCreate, RoleUpdate
from app.schema.response_schema import APIResponse


router = APIRouter(
    prefix="/role",
    tags=['Role']
)

@router.post("/create", response_model=APIResponse[RoleResponse])
async def create(role_data: RoleCreate,
                 db: Session = Depends(get_db)):
    result = role_service.create(role_data, db)
    return APIResponse(
        success=True,
        message="Tạo vai trò thành công",
        data=result
    )

@router.get("/all", response_model=APIResponse[List[RoleResponse]])
async def get_all(db: Session = Depends(get_db)):
    result = role_service.get_all(db)
    return APIResponse(
        success=True,
        message="Lấy danh sách vai trò thành công",
        data=result
    )

@router.get("/{role_id}", response_model=APIResponse[RoleResponse])
async def detail(role_id: int, db: Session = Depends(get_db)):
    result = role_service.detail(role_id, db)
    return APIResponse(
        success=True,
        message="Lấy chi tiết vai trò thành công",
        data=result
    )

@router.put("/update/{role_id}", response_model=APIResponse[RoleResponse])
async def update(role_id: int, role_data: RoleUpdate,
                 db: Session = Depends(get_db)):
    result = role_service.update(role_id, role_data, db)
    return APIResponse(
        success=True,
        message="Cập nhật vai trò thành công",
        data=result
    )

@router.delete("/delete/{role_id}", response_model=APIResponse)
async def delete(role_id,
                 db: Session = Depends(get_db)):
    role_service.delete(role_id, db)
    return APIResponse(
        success=True,
        message="Xóa vai trò thành công",
    )

