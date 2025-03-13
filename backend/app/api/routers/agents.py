from typing import Any

from fastapi import APIRouter, HTTPException

from app.core.agents.registry import list_available_agents
from app.schemas.agent import AgentInfo, AgentListResponse

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=AgentListResponse)
async def get_available_agents() -> Any:
    agents_dict = list_available_agents()
    agents = [
        AgentInfo(name=name, description=description)
        for name, description in agents_dict.items()
    ]
    return AgentListResponse(agents=agents)


@router.get("/{agent_name}", response_model=AgentInfo)
async def get_agent_info(agent_name: str) -> Any:
    agents_dict = list_available_agents()
    if agent_name not in agents_dict:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Agent '{agent_name}' not found. Available agents: {list(agents_dict)}"
            ),
        )
    return AgentInfo(name=agent_name, description=agents_dict[agent_name])
