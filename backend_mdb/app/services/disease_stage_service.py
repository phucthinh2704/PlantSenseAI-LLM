from bson import ObjectId, errors
from datetime import datetime, timezone, date 
from app.core.database import db


def serialize_doc(doc: dict) -> dict:
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


def _convert_dates_to_datetimes(data):
    """
    Hàm helper đệ quy để chuyển đổi datetime.date thành datetime.datetime.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = _convert_dates_to_datetimes(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = _convert_dates_to_datetimes(item)
    elif isinstance(data, date) and not isinstance(data, datetime):
        # Đây là mấu chốt: Chuyển 'date' thành 'datetime' lúc nửa đêm
        return datetime(data.year, data.month, data.day, tzinfo=timezone.utc)
    return data


def add_object_ids_to_steps(stage_data: dict):
    """Tự động thêm _id cho từng prevention/treatment step"""
    from bson import ObjectId

    for field in ["prevention", "treatment"]:
        if field in stage_data and isinstance(stage_data[field], list):
            for step in stage_data[field]:
                if step.get("_id") is None:
                    step["_id"] = str(ObjectId())
    return stage_data


async def create_stage(stage_data: dict) -> str:
    # Xóa _id nếu None
    if stage_data.get("_id") is None:
        stage_data.pop("_id", None)

    # Chuyển đổi date -> datetime trước
    stage_data = _convert_dates_to_datetimes(stage_data)

    stage_data = add_object_ids_to_steps(stage_data)

    now = datetime.now(timezone.utc)
    stage_data["created_at"] = now
    stage_data["updated_at"] = now

    result = await db.disease_stages.insert_one(stage_data)
    return str(result.inserted_id)


async def get_all_stages() -> list:
    docs = await db.disease_stages.find().to_list(length=None)
    return [serialize_doc(d) for d in docs]


async def get_stages_by_disease(disease_id: str) -> list:
    docs = await db.disease_stages.find({"disease_id": disease_id}).to_list(length=None)
    return [serialize_doc(d) for d in docs]


async def get_stage_by_id(stage_id: str) -> dict | None:
    try:
        obj_id = ObjectId(stage_id)
    except errors.InvalidId:
        return None
    doc = await db.disease_stages.find_one({"_id": obj_id})
    return serialize_doc(doc) if doc else None


async def update_stage(stage_id: str, data: dict) -> bool:
    try:
        obj_id = ObjectId(stage_id)
    except errors.InvalidId:
        return False

    # Chuyển đổi date -> datetime trước
    data = _convert_dates_to_datetimes(data)

    if "prevention" in data or "treatment" in data:
        data = add_object_ids_to_steps(data)

    data["updated_at"] = datetime.now(timezone.utc)
    result = await db.disease_stages.update_one({"_id": obj_id}, {"$set": data})
    return result.modified_count > 0


async def delete_stage(stage_id: str) -> bool:
    try:
        obj_id = ObjectId(stage_id)
    except errors.InvalidId:
        return False
    result = await db.disease_stages.delete_one({"_id": obj_id})
    return result.deleted_count > 0
