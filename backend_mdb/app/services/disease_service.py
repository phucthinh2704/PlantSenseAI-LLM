from bson import ObjectId, errors
from datetime import datetime
from app.core.database import db


def serialize_doc(doc: dict) -> dict:
    """Chuyển _id của Mongo sang str để trả về JSON."""
    doc["_id"] = str(doc["_id"])
    return doc


async def create_disease(disease_data: dict) -> str:
    disease_data["created_at"] = datetime.utcnow()
    disease_data["updated_at"] = datetime.utcnow()
    result = await db.diseases.insert_one(disease_data)
    return str(result.inserted_id)


async def get_all_diseases() -> list:
    cursor = db.diseases.find()
    docs = await cursor.to_list(length=None)
    return [serialize_doc(d) for d in docs]


async def get_disease_by_id(disease_id: str) -> dict | None:
    try:
        obj_id = ObjectId(disease_id)
    except errors.InvalidId:
        return None
    doc = await db.diseases.find_one({"_id": obj_id})
    return serialize_doc(doc) if doc else None


async def get_diseases_by_plant(plant_id: str) -> list:
    cursor = db.diseases.find({"plant_ids": plant_id})
    docs = await cursor.to_list(length=None)
    return [serialize_doc(d) for d in docs]


async def get_diseases_by_plant_and_stage(plant_id: str, stage: str) -> list:
    """Lọc theo plant_id và stage của treatment/prevention."""
    cursor = db.diseases.find({
        "plant_ids": plant_id,
        "$or": [
            {"treatment.stage": stage},
            {"prevention.stage": stage}
        ]
    })
    docs = await cursor.to_list(length=None)
    return [serialize_doc(d) for d in docs]


async def update_disease(disease_id: str, data: dict) -> bool:
    try:
        obj_id = ObjectId(disease_id)
    except errors.InvalidId:
        return False
    data["updated_at"] = datetime.utcnow()
    result = await db.diseases.update_one({"_id": obj_id}, {"$set": data})
    return result.modified_count > 0


async def delete_disease(disease_id: str) -> bool:
    try:
        obj_id = ObjectId(disease_id)
    except errors.InvalidId:
        return False
    result = await db.diseases.delete_one({"_id": obj_id})
    return result.deleted_count > 0
