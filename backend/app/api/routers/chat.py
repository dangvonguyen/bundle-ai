import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.core.agents import BaseAgent, OrchestratorAgent, PlanningAgent
from app.core.tools import BaseTool, WebSearchTool
from app.schemas.chat import ChatRequest, ChatResponse, Conversation, Message

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory storage for conversations
conversations: dict[str, dict[str, Any]] = {}


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> Any:
    conversation_id = request.conversation_id or str(uuid.uuid4())

    if conversation_id not in conversations:
        agent: OrchestratorAgent = await _initialize_agent_system(conversation_id)
        messages: list[Message] = []
        conversations[conversation_id] = {"agent": agent, "messages": messages}
    else:
        conversation = conversations[conversation_id]
        agent = conversation["agent"]
        messages = conversation["messages"]

    messages.append(Message(role="user", content=request.message))

    try:
        response = await agent.run({"messages": [request.message]})
        assistant_message = str(response[-1].content)
        messages.append(Message(role="assistant", content=assistant_message))
        return ChatResponse(conversation_id=conversation_id, response=assistant_message)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        ) from e


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str) -> Any:
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = conversations[conversation_id]["messages"]
    return Conversation(id=conversation_id, messages=messages)


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str) -> dict[str, str]:
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    del conversations[conversation_id]
    return {"message": f"Conversation '{conversation_id}' deleted successfully"}


async def _initialize_agent_system(conversation_id: str) -> OrchestratorAgent:
    """Initialize the agent system based on the requested agent type."""

    model_name = "gpt-4o-mini"
    tools: list[BaseTool] = [WebSearchTool()]
    agents: list[BaseAgent] = [
        PlanningAgent(
            thread_id=conversation_id,
            model_name=model_name,
            tools=tools,
        ),
    ]

    return OrchestratorAgent(
        thread_id=conversation_id,
        model_name=model_name,
        managed_agents=agents,
    )
