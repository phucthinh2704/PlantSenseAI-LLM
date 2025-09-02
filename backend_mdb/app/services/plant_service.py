from bson import ObjectId, errors
from app.core.database import db

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def create_plant(plant_data: dict):
    result = db.plants.insert_one(plant_data)
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
    if doc:
        return serialize_doc(doc)
    return None

async def get_plants_by_category(category: str):
    plants_cursor = db.plants.find({"category": category})
    plants_list = await plants_cursor.to_list(length=None)
    return [serialize_doc(p) for p in plants_list]

async def get_plants_by_name(name: str):
    plants_cursor = db.plants.find({"name": {"$regex": name, "$options": "i"}})
    plants_list = await plants_cursor.to_list(length=None)
    return [serialize_doc(p) for p in plants_list]

async def get_plants_by_disease(disease_name: str):
    plants_cursor = db.plants.find({"diseases.name": {"$regex": disease_name, "$options": "i"}})
    plants_list = await plants_cursor.to_list(length=None)
    return [serialize_doc(p) for p in plants_list]
