from pydantic import BaseModel, Field


class AgentInfo(BaseModel):
    name: str = Field(description="Name of the agent")
    description: str = Field(description="Description of the agent")


class AgentListResponse(BaseModel):
    agents: list[AgentInfo] = Field(description="list of available agents")
