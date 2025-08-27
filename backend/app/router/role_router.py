from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.service import role_service
from app.schema.role_schema import RoleResponse, RoleCreate, RoleUpdate

router = APIRouter(
    prefix="/role",
    tags=['Role']
)

@router.post("/create", response_model=RoleResponse)
async def create(role_data: RoleCreate,
                 db: Session = Depends(get_db)):
    return role_service.create(role_data, db)

@router.post("/update/{role_id}", response_model=RoleResponse)
async def update(role_id: int, role_data: RoleUpdate,
                 db: Session = Depends(get_db)):
    return role_service.update(role_id, role_data, db)

@router.delete("/delete/{role_id}")
async def delete(role_id,
                 db: Session = Depends(get_db)):
    return role_service.delete(role_id, db)

@router.get("/all")
async def delete(db: Session = Depends(get_db)):
    return role_service.get_all(db)