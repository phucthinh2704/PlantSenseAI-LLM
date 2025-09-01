from bson import ObjectId
from app.core.database import db

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def create_plant(plant_data: dict):
    result = db.plants.insert_one(plant_data)
    return str(result.inserted_id)

def get_all_plants():
    return [serialize_doc(p) for p in db.plants.find()]

def get_plant_by_id(plant_id: str):
    plant = db.plants.find_one({"_id": ObjectId(plant_id)})
    return serialize_doc(plant) if plant else None

def get_plants_by_category(category: str):
    return [serialize_doc(p) for p in db.plants.find({"category": category})]

def get_plants_by_name(name: str):
    return [serialize_doc(p) for p in db.plants.find({"name": {"$regex": name, "$options": "i"}})]

def get_plants_by_disease(disease_name: str):
    return [serialize_doc(p) for p in db.plants.find({"diseases.name": {"$regex": disease_name, "$options": "i"}})]
