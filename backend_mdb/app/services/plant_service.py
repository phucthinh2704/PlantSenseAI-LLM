from bson import ObjectId, errors
from datetime import datetime
from app.core.database import db


def serialize_doc(doc):
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


async def create_plant(plant_data: dict) -> str:
    plant_data["created_at"] = datetime.utcnow()
    plant_data["updated_at"] = datetime.utcnow()
    result = await db.plants.insert_one(plant_data)
    return str(result.inserted_id)


async def get_all_plants():
    plants_cursor = db.plants.find()
    plants_list = await plants_cursor.to_list(length=None)
    return [serialize_doc(p) for p in plants_list]


async def get_plant_by_id(plant_id: str):
    try:
        obj_id = ObjectId(plant_id)
    except errors.InvalidId:
        return None

    doc = await db.plants.find_one({"_id": obj_id})
    return serialize_doc(doc)


async def get_plants_by_category(category: str):
    plants_cursor = db.plants.find(
        {"category": {"$regex": f"^{category}$", "$options": "i"}}
    )
    plants_list = await plants_cursor.to_list(length=None)
    return [serialize_doc(p) for p in plants_list]


async def get_plants_by_name(name: str):
    plants_cursor = db.plants.find({"name": {"$regex": name, "$options": "i"}})
    plants_list = await plants_cursor.to_list(length=None)
    return [serialize_doc(p) for p in plants_list]


async def get_plant_details(plant_id: str):
    try:
        obj_id = ObjectId(plant_id)
    except errors.InvalidId:
        return None

    plant = await db.plants.find_one({"_id": obj_id})
    if not plant:
        return None
    plant = serialize_doc(plant)

    diseases_cursor = db.diseases.find({"plant_ids": plant["_id"]})
    diseases = [serialize_doc(d) for d in await diseases_cursor.to_list(length=None)]

    techniques_cursor = db.cultivation_techniques.find({"plant_id": plant["_id"]})
    techniques = [
        serialize_doc(t) for t in await techniques_cursor.to_list(length=None)
    ]

    return {"plant": plant, "diseases": diseases, "cultivation_techniques": techniques}


async def update_plant(plant_id: str, update_data: dict):
    try:
        obj_id = ObjectId(plant_id)
    except errors.InvalidId:
        return None

    update_data["updated_at"] = datetime.utcnow()
    result = await db.plants.update_one({"_id": obj_id}, {"$set": update_data})
    return result.modified_count > 0


async def delete_plant(plant_id: str):
    try:
        obj_id = ObjectId(plant_id)
    except errors.InvalidId:
        return False

    result = await db.plants.delete_one({"_id": obj_id})
    return result.deleted_count > 0
