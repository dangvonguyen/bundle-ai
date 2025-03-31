from abc import ABC
from typing import Annotated, Any

from langchain.chat_models.base import BaseChatModel
from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import add_messages, state
from pydantic import BaseModel


class BaseState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]


class BaseAgent(ABC):
    """
    Base interface for all agents in the system.
    """

    name: str
    description: str

    def __init__(self, *, thread_id: str, model_name: str) -> None:
        """
        Initialize the base agent with core attributes.
        """
        self.thread_id = thread_id
        self.model_name = model_name
        self.model = self._load_chat_model()
        self.memory = MemorySaver()
        self._graph: state.CompiledStateGraph | None = None

    def _load_chat_model(self) -> BaseChatModel:
        """
        Get the model instance to use for the agent.
        """
        return ChatOpenAI(model=self.model_name)

    async def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if self._graph is None:
            raise ValueError("Graph not initialized.")

        config: RunnableConfig = {"configurable": {"thread_id": self.thread_id}}
        response: dict[str, Any] = await self._graph.ainvoke(inputs, config)
        return response
