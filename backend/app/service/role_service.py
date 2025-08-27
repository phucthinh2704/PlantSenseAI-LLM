
from fastapi import HTTPException, status
from app.model import Role
from app.schema.role_schema import RoleCreate, RoleResponse, RoleUpdate
from sqlalchemy.orm import Session
from typing import List

def create(data: RoleCreate, db: Session) -> RoleResponse:
    new_role = Role(**data.model_dump())
    db.add(new_role)
    db.commit() 
    db.refresh(new_role)
    return new_role

def detail(role_id: int, db: Session) -> RoleResponse:
    role_query = db.query(Role).filter(Role.id == role_id)
    if not role_query.first():
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Role not found"
    )
    return role_query.first()

def update(role_id: int, role_data: RoleUpdate, db: Session) -> RoleResponse:
    role_query = db.query(Role).filter(Role.id == role_id)
    if not role_query.first():
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Role not found"
    )
    role_query.update(role_data.model_dump(), synchronize_session=False)
    db.commit()
    return role_query.first()


def delete(role_id: int, db: Session) -> None:
    role_query = db.query(Role).filter(Role.id == role_id)
    if not role_query.first():
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Role not found"
    )   
    role_query.delete(synchronize_session=False)
    db.commit()

def get_all(db: Session) -> List[RoleResponse]:
    return db.query(Role).all()