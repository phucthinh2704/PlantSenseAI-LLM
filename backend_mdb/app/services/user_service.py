from bson import ObjectId, errors
from datetime import datetime, timezone
from app.core.database import db
from app.models.user import User


def serialize_doc(doc: dict) -> dict:
    """
    Chuyển đổi ObjectId sang str mà VẪN GIỮ NGUYÊN KEY '_id'.
    Pydantic sẽ tự động xử lý alias.
    """
    if not doc:
        return None
    # Tạo bản sao để không làm ảnh hưởng doc gốc
    doc_copy = doc.copy()
    if "_id" in doc_copy:
        doc_copy["_id"] = str(doc_copy["_id"])  # <-- Chỉ chuyển đổi giá trị
    return doc_copy


async def create_user(user: User) -> str:
    user_dict = user.model_dump(by_alias=True, exclude_none=True, exclude={"id"})

    # Ghi đè thời gian để đảm bảo múi giờ UTC
    now = datetime.now(timezone.utc)
    user_dict["created_at"] = now
    user_dict["updated_at"] = now

    result = await db.users.insert_one(user_dict)  # Sửa: dùng db.users
    return str(result.inserted_id)


async def get_user_by_email(email: str) -> User | None:
    doc = await db.users.find_one({"email": email})  # Sửa: dùng db.users
    # Sửa: Dùng serialize_doc và Pydantic sẽ tự map _id -> id
    return User(**serialize_doc(doc)) if doc else None


async def get_user_by_id(user_id: str) -> User | None:
    try:
        obj_id = ObjectId(user_id)
    except errors.InvalidId:
        return None

    doc = await db.users.find_one({"_id": obj_id})  # Sửa: dùng db.users
    # Sửa: Dùng serialize_doc
    return User(**serialize_doc(doc)) if doc else None


async def update_user(user_id: str, data: dict):
    data["updated_at"] = datetime.now(timezone.utc)
    await db.users.update_one(
        {"_id": ObjectId(user_id)}, {"$set": data}
    )

