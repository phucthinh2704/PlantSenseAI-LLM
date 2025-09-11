from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timezone
from bson import ObjectId


class Message(BaseModel):
    sender: str  # "user" | "bot"
    content: str
    metadata: Optional[Dict] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Conversation(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    title: Optional[str] = None
    messages: List[Message] = []  # nhúng luôn tin nhắn
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {ObjectId: str}
