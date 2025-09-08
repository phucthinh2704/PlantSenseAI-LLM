from bson import ObjectId, errors
from datetime import datetime
from app.core.database import db


def serialize_doc(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


async def create_disease(disease_data: dict) -> str:
    disease_data["created_at"] = datetime.utcnow()
    disease_data["updated_at"] = datetime.utcnow()
    result = await db.diseases.insert_one(disease_data)
    return str(result.inserted_id)


async def get_all_diseases() -> list:
    docs = await db.diseases.find().to_list(length=None)
    return [serialize_doc(d) for d in docs]


async def get_disease_by_id(disease_id: str) -> dict | None:
    try:
        obj_id = ObjectId(disease_id)
    except errors.InvalidId:
        return None
    doc = await db.diseases.find_one({"_id": obj_id})
    return serialize_doc(doc) if doc else None


async def get_diseases_by_plant(plant_id: str) -> list:
    docs = await db.diseases.find({"plant_ids": plant_id}).to_list(length=None)
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
