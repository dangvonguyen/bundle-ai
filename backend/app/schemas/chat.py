from typing import Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(description="The role of the message sender (user or assistant)")
    content: str = Field(description="The content of the message")


class Conversation(BaseModel):
    id: str = Field(description="Unique conversation identifier")
    messages: list[Message] = Field(
        default_factory=list, description="List of messages in the conversation"
    )


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    message: str = Field(description="User message")


class ChatResponse(BaseModel):
    conversation_id: str = Field(description="Conversation ID")
    response: str = Field(description="Assistant response")
