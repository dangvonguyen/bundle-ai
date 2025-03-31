from typing import Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(description="The role of the message sender (user or assistant)")
    content: str = Field(description="The content of the message")


class Chat(BaseModel):
    id: str = Field(description="Unique chat identifier")
    messages: list[Message] = Field(
        default_factory=list, description="List of messages in the chat"
    )


class ChatRequest(BaseModel):
    chat_id: Optional[str] = Field(None, description="Existing chat ID")
    message: str = Field(description="User message")


class ChatResponse(BaseModel):
    chat_id: str = Field(description="Chat ID")
    response: str = Field(description="Assistant response")
