
from fastapi import HTTPException, status
from app.model import Role
from app.schema.role_schema import RoleCreate, RoleResponse
from sqlalchemy.orm import Session

def create(data: RoleCreate, db: Session) -> RoleResponse:
    new_role = Role(**data.model_dump())
    db.add(new_role)
    db.commit() 
    db.refresh(new_role)
    return new_role