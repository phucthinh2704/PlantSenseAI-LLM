from bson import ObjectId, errors
from datetime import datetime, date, timezone
from app.core.database import db


def serialize_doc(doc):
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
        # Chuyển date thành datetime lúc nửa đêm (00:00:00)
        return datetime(data.year, data.month, data.day, tzinfo=timezone.utc)
    return data


async def create_plant(plant_data: dict) -> str:

    # Xóa trường _id nếu nó là None, để MongoDB tự tạo ObjectId
    if plant_data.get("_id") is None:
        plant_data.pop("_id", None)

    # Chuyển đổi mọi đối tượng `date` thành `datetime` trước khi chèn
    plant_data = _convert_dates_to_datetimes(plant_data)

    # Sử dụng datetime.now(timezone.utc) thay vì datetime.utcnow()
    now = datetime.now(timezone.utc)
    plant_data["created_at"] = now
    plant_data["updated_at"] = now

    result = await db.plants.insert_one(plant_data)
    return str(result.inserted_id)


async def get_all_plants():
    cursor = db.plants.find()
    docs = await cursor.to_list(length=None)
    return [serialize_doc(d) for d in docs]


async def get_plant_by_id(plant_id: str):
    try:
        obj_id = ObjectId(plant_id)
    except errors.InvalidId:
        return None
    doc = await db.plants.find_one({"_id": obj_id})
    return serialize_doc(doc)


async def get_plant_details(plant_id: str):
    plant = await get_plant_by_id(plant_id)
    if not plant:
        return None

    # lấy bệnh & kỹ thuật canh tác liên quan
    diseases = [
        serialize_doc(d) async for d in db.diseases.find({"plant_ids": plant["_id"]})
    ]
    cultivations = [
        serialize_doc(c)
        async for c in db.cultivation_techniques.find({"plant_id": plant["_id"]})
    ]

    return {
        "plant": plant,
        "diseases": diseases,
        "cultivation_techniques": cultivations,
    }


async def update_plant(plant_id: str, data: dict) -> bool:
    try:
        obj_id = ObjectId(plant_id)
    except errors.InvalidId:
        return False

    # Cũng áp dụng chuyển đổi cho hàm update
    data = _convert_dates_to_datetimes(data)

    data["updated_at"] = datetime.now(timezone.utc)  # Dùng timezone-aware
    result = await db.plants.update_one({"_id": obj_id}, {"$set": data})
    return result.modified_count > 0


async def delete_plant(plant_id: str) -> bool:
    try:
        obj_id = ObjectId(plant_id)
    except errors.InvalidId:
        return False
    result = await db.plants.delete_one({"_id": obj_id})
    return result.deleted_count > 0
