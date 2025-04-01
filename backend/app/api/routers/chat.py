import uuid
from typing import Annotated, Any, cast

from fastapi import APIRouter, File, HTTPException, UploadFile
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.agents import BaseAgent, OrchestratorAgent, PlanningAgent, RetrievalAgent
from app.core.tools import BaseTool, WebSearchTool
from app.core.utils import generate_uuid
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
        assistant_message = str(response["messages"][-1].content)
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


@router.post("/{chat_id}/upload")
async def upload_files(
    chat_id: str, files: Annotated[list[UploadFile], File()]
) -> dict[str, str]:
    orchestrator: OrchestratorAgent = chats[chat_id]["agent"]
    retrieval = cast(RetrievalAgent, orchestrator.managed_agents.get("retrieval"))

    documents = []
    for file in files:
        filename = file.filename or "unknown"
        file_extension = filename.rsplit(".", 1)[-1]
        if file_extension != "txt":
            raise HTTPException(status_code=400, detail="Unsupported file type")

        content: bytes = await file.read()
        content_str = content.decode("utf-8")
        metadata = {
            "source": filename,
            "uuid": generate_uuid("hash", value=content_str),
        }
        documents.append(Document(page_content=content_str, metadata=metadata))

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    await retrieval.add_documents(chunks)
    return {"message": "Documents added successfully"}


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
        RetrievalAgent(
            thread_id=chat_id,
            model_name=model_name,
        ),
    ]

    return OrchestratorAgent(
        thread_id=chat_id,
        model_name=model_name,
        managed_agents=agents,
    )
