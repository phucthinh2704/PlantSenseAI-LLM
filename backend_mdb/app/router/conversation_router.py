from fastapi import APIRouter, HTTPException
from app.models.conversation import Conversation, Message
from app.schema.response_schema import APIResponse
from app.services import conversation_service
from pydantic import BaseModel

router = APIRouter()


@router.post("/", response_model=APIResponse)
async def create_conversation(conv: Conversation):
    inserted_id = await conversation_service.create_conversation(
        conv.model_dump(by_alias=True, exclude={"id"})
    )
    return APIResponse(
        success=True, message="Conversation created", data={"inserted_id": inserted_id}
    )


@router.get("/user/{user_id}", response_model=APIResponse)
async def get_user_conversations(user_id: str):
    conversations = await conversation_service.get_all_conversations(user_id)
    return APIResponse(
        success=True, message="Conversations retrieved", data=conversations
    )


@router.get("/{conv_id}", response_model=APIResponse)
async def get_conversation(conv_id: str):
    conv = await conversation_service.get_conversation_by_id(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return APIResponse(success=True, message="Conversation retrieved", data=conv)


@router.delete("/{conv_id}", response_model=APIResponse)
async def delete_conversation(conv_id: str):
    deleted = await conversation_service.delete_conversation(conv_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return APIResponse(success=True, message="Conversation deleted")


@router.post("/{conv_id}/messages", response_model=APIResponse)
async def add_message(conv_id: str, message: Message):
    updated = await conversation_service.add_message(conv_id, message.model_dump())
    if not updated:
        raise HTTPException(
            status_code=404, detail="Conversation not found or not updated"
        )
    return APIResponse(success=True, message="Message added")


class UpdateConversationTitle(BaseModel):
    title: str


@router.put("/{conv_id}/title", response_model=APIResponse)
async def update_conversation_title(conv_id: str, title: UpdateConversationTitle):
    updated = await conversation_service.update_conversation_title(conv_id, title.title)
    if not updated:
        raise HTTPException(
            status_code=404, detail="Conversation not found or not updated"
        )
    return APIResponse(success=True, message="Conversation title updated")
