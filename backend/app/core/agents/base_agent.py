from abc import ABC, abstractmethod
from typing import Annotated, Any

from langchain.chat_models.base import BaseChatModel
from langchain_core.messages import AnyMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import add_messages
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

    def _load_chat_model(self) -> BaseChatModel:
        """
        Get the model instance to use for the agent.
        """
        return ChatOpenAI(model=self.model_name)

    @abstractmethod
    async def run(self, inputs: dict[str, Any]) -> list[BaseMessage]:
        """
        Execute the agent with the given input.
        """
        raise NotImplementedError()
