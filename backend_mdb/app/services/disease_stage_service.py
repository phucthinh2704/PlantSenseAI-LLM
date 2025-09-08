from bson import ObjectId, errors
from datetime import datetime
from app.core.database import db


def serialize_doc(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


def add_object_ids_to_steps(stage_data: dict):
    """Tự động thêm _id cho từng prevention/treatment step"""
    from bson import ObjectId
    for field in ["prevention", "treatment"]:
        if field in stage_data and isinstance(stage_data[field], list):
            for step in stage_data[field]:
                step["_id"] = str(ObjectId())
    return stage_data


async def create_stage(stage_data: dict) -> str:
    stage_data = add_object_ids_to_steps(stage_data)
    stage_data["created_at"] = datetime.utcnow()
    stage_data["updated_at"] = datetime.utcnow()
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
    if "prevention" in data or "treatment" in data:
        data = add_object_ids_to_steps(data)
    data["updated_at"] = datetime.utcnow()
    result = await db.disease_stages.update_one({"_id": obj_id}, {"$set": data})
    return result.modified_count > 0


async def delete_stage(stage_id: str) -> bool:
    try:
        obj_id = ObjectId(stage_id)
    except errors.InvalidId:
        return False
    result = await db.disease_stages.delete_one({"_id": obj_id})
    return result.deleted_count > 0
