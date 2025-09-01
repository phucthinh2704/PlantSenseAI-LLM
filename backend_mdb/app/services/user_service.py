from app.models.user import User
from app.core.database import user_collection
from app.core.security import hash_password, verify_password
from datetime import datetime
from bson import ObjectId, errors


async def create_user(user: User) -> str:
    user_dict = user.model_dump(by_alias=True, exclude_none=True)
    result = await user_collection.insert_one(user_dict)
    return str(result.inserted_id)


async def get_user_by_email(email: str) -> User | None:
    doc = await user_collection.find_one({"email": email})
    return User(**doc) if doc else None


async def get_user_by_id(user_id: str) -> User | None:
    try:
        obj_id = ObjectId(user_id)
    except errors.InvalidId:
        return None

    doc = await user_collection.find_one({"_id": obj_id})
    if doc:
        # chuyển ObjectId sang str
        doc["id"] = str(doc["_id"])  # hoặc doc["_id"] = str(doc["_id"])
        doc.pop("_id", None)
        return User(**doc)
    return None


async def update_user(user_id: str, data: dict):
    data["updated_at"] = datetime.utcnow()
    await user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
