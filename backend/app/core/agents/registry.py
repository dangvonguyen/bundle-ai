from typing import Any

from app.core.agents import BaseAgent

# Agent registry to store agent implementations
_AGENT_REGISTRY: dict[str, type[BaseAgent]] = {}


def register_agent(name: str, agent_cls: type[BaseAgent]) -> None:
    """
    Register an agent implementation in the registry.
    """
    _AGENT_REGISTRY[name] = agent_cls


def get_agent_class(name: str) -> type[BaseAgent]:
    """
    Get an agent class by name from the registry.
    """
    if name not in _AGENT_REGISTRY:
        raise ValueError(
            f"No agent registered with the name '{name}'. "
            f"Available agents: {list(_AGENT_REGISTRY.keys())}"
        )
    return _AGENT_REGISTRY[name]


def create_agent(name: str, **kwargs: Any) -> BaseAgent:
    """
    Create an agent instance by name.
    """
    agent_cls = get_agent_class(name)
    return agent_cls(**kwargs)


def list_available_agents() -> dict[str, str]:
    """
    List all available agent types with their description.
    """
    return {name: agent_cls.description for name, agent_cls in _AGENT_REGISTRY.items()}
