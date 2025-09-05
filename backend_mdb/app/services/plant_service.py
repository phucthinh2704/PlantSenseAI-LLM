# app/services/plant_service.py
from bson import ObjectId, errors
from datetime import datetime
from app.core.database import db
from app.models.plant import Plant


def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc


async def create_plant(plant_data: dict) -> str:
    """Tạo plant mới"""
    plant_data["created_at"] = datetime.utcnow()
    plant_data["updated_at"] = datetime.utcnow()
    result = await db.plants.insert_one(plant_data)
    return str(result.inserted_id)


async def get_all_plants():
    """Lấy toàn bộ plants"""
    plants_cursor = db.plants.find()
    plants_list = await plants_cursor.to_list(length=None)
    return [serialize_doc(p) for p in plants_list]


async def get_plant_by_id(plant_id: str):
    """Lấy plant theo _id"""
    try:
        obj_id = ObjectId(plant_id)
    except errors.InvalidId:
        return None

    doc = await db.plants.find_one({"_id": obj_id})
    return serialize_doc(doc) if doc else None


async def get_plants_by_category(category: str):
    """Lọc theo category"""
    plants_cursor = db.plants.find(
        {"category": {"$regex": f"^{category}$", "$options": "i"}}
    )
    plants_list = await plants_cursor.to_list(length=None)
    return [serialize_doc(p) for p in plants_list]


async def get_plants_by_name(name: str):
    """Tìm theo tên (regex, không phân biệt hoa thường)"""
    plants_cursor = db.plants.find({"name": {"$regex": name, "$options": "i"}})
    plants_list = await plants_cursor.to_list(length=None)
    return [serialize_doc(p) for p in plants_list]


async def get_plants_by_disease(disease_name: str):
    """Tìm plants có chứa bệnh theo tên"""
    plants_cursor = db.plants.find(
        {"diseases.name": {"$regex": disease_name, "$options": "i"}}
    )
    plants_list = await plants_cursor.to_list(length=None)
    return [serialize_doc(p) for p in plants_list]

async def get_plant_details(plant_id: str):
    # Validate ObjectId
    try:
        obj_id = ObjectId(plant_id)
    except errors.InvalidId:
        return None

    # Plant
    plant = await db.plants.find_one({"_id": obj_id})
    if not plant:
        return None
    plant = serialize_doc(plant)

    # Diseases
    diseases_cursor = db.diseases.find({"plant_ids": plant["_id"]})
    diseases = await diseases_cursor.to_list(length=None)
    diseases = [serialize_doc(d) for d in diseases]

    # Cultivation Techniques
    techniques_cursor = db.cultivation_techniques.find({"plant_id": plant["_id"]})
    techniques = await techniques_cursor.to_list(length=None)
    techniques = [serialize_doc(t) for t in techniques]

    return {
        "plant": plant,
        "diseases": diseases,
        "cultivation_techniques": techniques,
    }

async def update_plant(plant_id: str, update_data: dict):
    """Cập nhật thông tin plant"""
    try:
        obj_id = ObjectId(plant_id)
    except errors.InvalidId:
        return None

    update_data["updated_at"] = datetime.utcnow()
    result = await db.plants.update_one({"_id": obj_id}, {"$set": update_data})
    return result.modified_count > 0


async def delete_plant(plant_id: str):
    """Xóa plant theo id"""
    try:
        obj_id = ObjectId(plant_id)
    except errors.InvalidId:
        return False

    result = await db.plants.delete_one({"_id": obj_id})
    return result.deleted_count > 0
