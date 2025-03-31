import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.core.agents import BaseAgent, OrchestratorAgent, PlanningAgent
from app.core.tools import BaseTool, WebSearchTool
from app.schemas.chat import Chat, ChatRequest, ChatResponse, Message

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory storage for chats
chats: dict[str, dict[str, Any]] = {}


@router.post("", response_model=ChatResponse)
async def respond(request: ChatRequest) -> Any:
    chat_id = request.chat_id or str(uuid.uuid4())

    if chat_id not in chats:
        agent: OrchestratorAgent = await _initialize_agent_system(chat_id)
        messages: list[Message] = []
        chats[chat_id] = {"agent": agent, "messages": messages}
    else:
        chat = chats[chat_id]
        agent = chat["agent"]
        messages = chat["messages"]

    messages.append(Message(role="user", content=request.message))

    try:
        response = await agent.run({"messages": [request.message]})
        assistant_message = str(response[-1].content)
        messages.append(Message(role="assistant", content=assistant_message))
        return ChatResponse(chat_id=chat_id, response=assistant_message)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        ) from e


@router.get("/{chat_id}", response_model=Chat)
async def get_chat(chat_id: str) -> Any:
    if chat_id not in chats:
        raise HTTPException(status_code=404, detail="chat not found")

    messages = chats[chat_id]["messages"]
    return Chat(id=chat_id, messages=messages)


@router.delete("/{chat_id}")
async def delete_chat(chat_id: str) -> dict[str, str]:
    if chat_id not in chats:
        raise HTTPException(status_code=404, detail="chat not found")

    del chats[chat_id]
    return {"message": f"chat '{chat_id}' deleted successfully"}


async def _initialize_agent_system(chat_id: str) -> OrchestratorAgent:
    """Initialize the agent system based on the requested agent type."""

    model_name = "gpt-4o-mini"
    tools: list[BaseTool] = [WebSearchTool()]
    agents: list[BaseAgent] = [
        PlanningAgent(
            thread_id=chat_id,
            model_name=model_name,
            tools=tools,
        ),
    ]

    return OrchestratorAgent(
        thread_id=chat_id,
        model_name=model_name,
        managed_agents=agents,
    )
