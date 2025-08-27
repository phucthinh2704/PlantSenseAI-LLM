from sqlalchemy import TIMESTAMP, Boolean, Column, String, text, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.util import get_password_hash
from app.database import Base, SessionLocal
import enum

class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    banned = "banned"

class BaseModel:
    id = Column(Integer, primary_key=True, index=True, nullable=False)

class Role(Base, BaseModel):
    __tablename__= "role"

    name = Column(String, nullable = False)

    users = relationship("User", back_populates="role")
    
# BẢNG USER (NGƯỜI DÙNG)
class User(Base, BaseModel):
    __tablename__= "user"
    
    name = Column(String, nullable=False) # Tên người dùng
    phone = Column(String) # Số điện thoại
    avatar = Column(String) # Ảnh đại diện
    email = Column(String, nullable=False) # Email để đăng nhập
    password = Column(String) # Mật khẩu (có thể null do có dùng đăng nhập với google/facebook)
    provider_name = Column(String) # Phân biệt user đăng nhập bằng google/facebook
    provider_id = Column(String) # ID do bên thứ 3 cung cấp
    is_outside = Column(Boolean, nullable=False, default=False) # Người dùng đăng ký từ bên trong hay bên ngoài
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.inactive)
    create_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')) # Thời gian tạo người dùng
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)

    role = relationship("Role", back_populates="users")
    refresh_token = relationship("RefreshToken", uselist=False, back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base, BaseModel):
    __tablename__= "refresh_token"

    token = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True)

    user = relationship("User", back_populates="refresh_token")




def init_data():
    session = SessionLocal()

    existing_roles = session.query(Role).filter(Role.name.in_(["admin", "user"])).all()
    existing_role_names = {role.name for role in existing_roles}

    roles_to_create = []
    if "admin" not in existing_role_names:
        roles_to_create.append(Role(name="admin"))
    if "user" not in existing_role_names:
        roles_to_create.append(Role(name="user"))
    
    if roles_to_create:
        session.add_all(roles_to_create)
        session.commit()

    admin_role = session.query(Role).filter(Role.name == "admin").first()

    admin_email = "admin@gmail.com"
    existing_admin = session.query(User).filter(User.email == admin_email).first()

    if not existing_admin:
        admin_user = User(
            name="Admin",
            email=admin_email,
            password=get_password_hash("123"),  
            status=UserStatus.active,
            role_id=admin_role.id,
            is_outside=False,
        )
        session.add(admin_user)
        session.commit()

    session.close()


