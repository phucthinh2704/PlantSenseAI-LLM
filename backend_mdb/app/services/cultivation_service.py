from bson import ObjectId, errors
from app.core.database import db
from datetime import datetime

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

async def create_cultivation(cultivation_data: dict):
    cultivation_data["created_at"] = datetime.utcnow()
    cultivation_data["updated_at"] = datetime.utcnow()
    result = await db.cultivation_techniques.insert_one(cultivation_data)
    return str(result.inserted_id)

async def get_all_cultivations():
    cursor = db.cultivation_techniques.find()
    docs = await cursor.to_list(length=None)
    return [serialize_doc(d) for d in docs]

async def get_cultivation_by_id(cultivation_id: str):
    try:
        obj_id = ObjectId(cultivation_id)
    except errors.InvalidId:
        return None
    doc = await db.cultivation_techniques.find_one({"_id": obj_id})
    return serialize_doc(doc) if doc else None

async def get_cultivations_by_plant(plant_id: str):
    cursor = db.cultivation_techniques.find({"plant_id": plant_id})
    docs = await cursor.to_list(length=None)
    return [serialize_doc(d) for d in docs]

async def update_cultivation(cultivation_id: str, data: dict):
    try:
        obj_id = ObjectId(cultivation_id)
    except errors.InvalidId:
        return None
    data["updated_at"] = datetime.utcnow()
    result = await db.cultivation_techniques.update_one({"_id": obj_id}, {"$set": data})
    return result.modified_count > 0

async def delete_cultivation(cultivation_id: str):
    try:
        obj_id = ObjectId(cultivation_id)
    except errors.InvalidId:
        return False
    result = await db.cultivation_techniques.delete_one({"_id": obj_id})
    return result.deleted_count > 0
