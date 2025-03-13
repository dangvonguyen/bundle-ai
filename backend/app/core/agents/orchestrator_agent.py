from typing import Any, Literal, cast

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, state
from pydantic import BaseModel, Field

from app.core.agents import BaseAgent, BaseState
from app.core.agents.registry import register_agent

ORCHESTRATOR_SYSTEM_PROMPT = """
You are an intelligent Orchestrator Agent that serves as the central coordinator for a multi-agent system.

Modes of Operation:
1. Direct Response: For simple queries, greetings, or straightforward tasks, you can respond directly.
2. Delegation: For complex tasks, you can delegate to specialized agents.

IMPORTANT GUIDELINES:
- Be helpful, concise, and accurate in your responses
- Maintain a consistent, friendly tone throughout the conversation
"""  # noqa: E501


class OrchestratorState(BaseState):
    """
    State object for Orchestrator Agent workflow.
    """

    active_agent: str = ""
    specialized_agents: list[str] = Field(default_factory=list)


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent that coordinates multiple specialized agents.

    Serves as the central intelligence that analyzes user requests,
    determines whether to handle them directly or delegate to specialized
    agents, and manages the overall conversation flow.
    """

    name: str = "orchestrator"
    description: str = (
        "Central coordinator that manages specialized agents to handle tasks"
    )
    system_prompt: str = ORCHESTRATOR_SYSTEM_PROMPT

    def __init__(
        self, *, thread_id: str, model_name: str, managed_agents: list[BaseAgent]
    ) -> None:
        super().__init__(
            thread_id=thread_id,
            model_name=model_name,
        )
        self.managed_agents = {agent.name: agent for agent in managed_agents}
        self._graph = self._create_graph()

    async def run(self, inputs: dict[str, Any]) -> list[BaseMessage]:
        """
        Execute the agent with the given input.
        """
        config: RunnableConfig = {"configurable": {"thread_id": self.thread_id}}
        response = await self._graph.ainvoke(inputs, config)
        return response["messages"]  # type: ignore

    def _create_graph(self) -> state.CompiledStateGraph:
        async def analyze_request(
            state: OrchestratorState,
        ) -> dict[str, Any]:
            class Analyze(BaseModel):
                """
                Schema for structured output from the analysis.
                """

                reason: str = Field(description="Reasoning for the agent choice")
                chosen_agent: str = Field(
                    description="Name of the chosen agent to take the task."
                )

            structured_model = self.model.with_structured_output(Analyze)

            # Create prompt with available agents
            agent_descriptions = "\n".join(
                [
                    f"- '{agent_name}': {agent.description}"
                    for agent_name, agent in self.managed_agents.items()
                ]
            )

            analyze_prompt = (
                f"{self.system_prompt}\n\n"
                f"Available agents and their descriptions: {agent_descriptions}\n\n"
                "If you want to respond to the user query directly, the chosen agent "
                "should be 'None'."
            )

            messages = [SystemMessage(content=analyze_prompt)] + state.messages
            response = cast(Analyze, await structured_model.ainvoke(messages))
            return {
                "active_agent": response.chosen_agent,
                "specialized_agents": list(self.managed_agents),
            }

        def route_from_analyze(
            state: OrchestratorState,
        ) -> Literal["respond", "delegate"]:
            if state.active_agent == "None":
                return "respond"
            else:
                return "delegate"

        async def respond_user(state: OrchestratorState) -> dict[str, list[AIMessage]]:
            messages = [SystemMessage(content=self.system_prompt)] + state.messages
            response = cast(AIMessage, await self.model.ainvoke(messages))
            return {"messages": [response]}

        async def delegate_to_specialized_agent(
            state: OrchestratorState,
        ) -> dict[str, list[BaseMessage]]:
            message_length = len(state.messages)
            agent_name = state.active_agent

            # Handle missing agent
            if agent_name not in self.managed_agents:
                error_msg = (
                    f"Agent '{agent_name}' not found. "
                    f"Available agents: {list(self.managed_agents)}"
                )
                return {"messages": [AIMessage(content=error_msg)]}

            # Execute specialized agent
            agent = self.managed_agents[agent_name]
            inputs = {"messages": [state.messages[-1].content]}
            responses = await agent.run(inputs)

            return {"messages": responses[message_length:]}

        # Build the workflow graph
        workflow = StateGraph(OrchestratorState)

        workflow.add_node("analyze", analyze_request)
        workflow.add_node("respond", respond_user)
        workflow.add_node("delegate", delegate_to_specialized_agent)

        workflow.add_edge("__start__", "analyze")
        workflow.add_conditional_edges("analyze", route_from_analyze)
        workflow.add_edge("respond", "__end__")
        workflow.add_edge("delegate", "__end__")

        graph = workflow.compile(self.memory)
        graph.name = "Orchestrator Agent"

        return graph


# Register the agent in the registry
register_agent(OrchestratorAgent.name, OrchestratorAgent)
