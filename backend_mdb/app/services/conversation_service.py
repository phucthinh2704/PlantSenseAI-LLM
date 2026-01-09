from bson import ObjectId, errors
from datetime import datetime, timezone
from app.core.database import db
from datetime import datetime, timezone
from typing import List


def to_iso_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def to_epoch_ms(dt: datetime) -> int:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def serialize_doc(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    for k in ("created_at", "updated_at"):
        if k in doc and isinstance(doc[k], datetime):
            dt = doc[k]
            doc[k + "_ts"] = to_epoch_ms(dt)  # 1739904123456
            doc[k] = to_iso_z(dt)  # 2025-10-19T03:02:03.456Z

    if "messages" in doc:
        for m in doc["messages"]:
            if isinstance(m.get("timestamp"), datetime):
                m["timestamp_ts"] = to_epoch_ms(m["timestamp"])
                m["timestamp"] = to_iso_z(m["timestamp"])
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


async def update_retrieved_docs(conv_id: str, doc_ids: List[str]) -> bool:
    """Thêm các doc_id mới vào danh sách đã truy xuất của cuộc trò chuyện."""
    try:
        obj_id = ObjectId(conv_id)
    except errors.InvalidId:
        return False

    result = await db.conversations.update_one(
        {"_id": obj_id},
        {
            # $addToSet: Chỉ thêm nếu ID chưa tồn tại, tránh trùng lặp
            "$addToSet": {"retrieved_doc_ids": {"$each": doc_ids}},
            "$set": {"updated_at": datetime.now(timezone.utc)},
        },
    )
    return result.modified_count > 0


async def get_all_conversations_admin():
    """Lấy TẤT CẢ các cuộc hội thoại (chỉ admin)."""
    cursor = db.conversations.find().sort("updated_at", -1)  # Sắp xếp mới nhất
    docs = await cursor.to_list(length=None)
    return [serialize_doc(d) for d in docs]

async def delete_all_conversations_by_user(user_id: str) -> int:
    """Xóa tất cả cuộc hội thoại thuộc về một user_id cụ thể."""
    result = await db.conversations.delete_many({"user_id": user_id})
    return result.deleted_count