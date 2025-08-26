from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.service import role_service
from app.schema.role_schema import RoleResponse, RoleCreate

router = APIRouter(
    prefix="/role",
    tags=['Role']
)

@router.post("/create", response_model=RoleResponse)
async def create(task_data: RoleCreate,
                 db: Session = Depends(get_db)):
    return role_service.create(task_data, db)