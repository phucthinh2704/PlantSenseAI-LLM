from bson import ObjectId, errors
from datetime import datetime, timezone
from app.core.database import db


def serialize_doc(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


# --- CRUD Conversation ---
async def create_conversation(conv_data: dict) -> str:
    conv_data = {
        **conv_data,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "messages": conv_data.get("messages", []),
    }
    result = await db.conversations.insert_one(conv_data)
    return str(result.inserted_id)


async def get_all_conversations(user_id: str):
    cursor = db.conversations.find({"user_id": user_id})
    docs = await cursor.to_list(length=None)
    return [serialize_doc(d) for d in docs]


async def get_conversation_by_id(conv_id: str):
    try:
        obj_id = ObjectId(conv_id)
    except errors.InvalidId:
        return None
    doc = await db.conversations.find_one({"_id": obj_id})
    return serialize_doc(doc)


async def delete_conversation(conv_id: str) -> bool:
    try:
        obj_id = ObjectId(conv_id)
    except errors.InvalidId:
        return False
    result = await db.conversations.delete_one({"_id": obj_id})
    return result.deleted_count > 0


# --- Messages ---
async def add_message(conv_id: str, message: dict) -> bool:
    try:
        obj_id = ObjectId(conv_id)
    except errors.InvalidId:
        return False

    message["timestamp"] = datetime.now(timezone.utc)
    result = await db.conversations.update_one(
        {"_id": obj_id},
        {
            "$push": {"messages": message},
            "$set": {"updated_at": datetime.now(timezone.utc)},
        },
    )
    return result.modified_count > 0

async def update_conversation_title(conv_id: str, title: str) -> bool:
    try:
        obj_id = ObjectId(conv_id)
    except errors.InvalidId:
        return False

    result = await db.conversations.update_one(
        {"_id": obj_id},
        {"$set": {"title": title, "updated_at": datetime.now(timezone.utc)}},
    )
    return result.modified_count > 0