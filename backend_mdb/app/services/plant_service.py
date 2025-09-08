from bson import ObjectId, errors
from datetime import datetime
from app.core.database import db


def serialize_doc(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def create_plant(plant_data: dict) -> str:
    plant_data["created_at"] = datetime.utcnow()
    plant_data["updated_at"] = datetime.utcnow()
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
    data["updated_at"] = datetime.utcnow()
    result = await db.plants.update_one({"_id": obj_id}, {"$set": data})
    return result.modified_count > 0


async def delete_plant(plant_id: str) -> bool:
    try:
        obj_id = ObjectId(plant_id)
    except errors.InvalidId:
        return False
    result = await db.plants.delete_one({"_id": obj_id})
    return result.deleted_count > 0
