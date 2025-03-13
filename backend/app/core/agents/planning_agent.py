from typing import Any, Literal, Optional, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, state
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from app.core.agents import BaseAgent, BaseState
from app.core.agents.registry import register_agent
from app.core.tools import BaseTool

PLANNER_AGENT_SYSTEM_PROMPT = """
You are a highly capable planning agent whose primary responsibility is to develop well-structured, step-by-step plan to solve complex tasks.
In your response, express all thoughts and steps in the first person, as if you are personally taking the actions described.

GUIDELINES:
1. **Clarify the objective:** Identify key goals, constraints, and assumptions.
2. **Break Down the Task:** Decompose the complex task into smaller, manageable \
sub-tasks, and don't make it too rambling.
"""  # noqa: E501


class PlanState(BaseState):
    """
    State object for the Planning Agent workflow.
    """

    plan: list[str] = Field(default_factory=list)
    current_step: int = 0


class PlanningAgent(BaseAgent):
    """
    Planning Agent that breaks down complex tasks into structured steps.

    This agent specializes in creating comprehensive, step-by-step plans
    and then executing those plans to solve complex problems.
    """

    name: str = "planning"
    description: str = (
        "Creates and executes comprehensive, step-by-step plans to solve complex tasks"
    )
    system_prompt: str = PLANNER_AGENT_SYSTEM_PROMPT

    def __init__(
        self,
        *,
        model_name: str,
        thread_id: str,
        tools: Optional[list[BaseTool]] = None,
    ) -> None:
        super().__init__(
            thread_id=thread_id,
            model_name=model_name,
        )
        self.tools = tools or []
        self.model_with_tools = self.model.bind_tools(self.tools)
        self._graph = self._create_graph()

    async def run(self, inputs: dict[str, Any]) -> list[BaseMessage]:
        """
        Execute the agent with the given input.
        """
        config: RunnableConfig = {"configurable": {"thread_id": self.thread_id}}
        response = await self._graph.ainvoke(inputs, config)
        return response["messages"]  # type: ignore

    def _create_graph(self) -> state.CompiledStateGraph:
        async def create_plan(state: PlanState) -> dict[str, Any]:
            class Plan(BaseModel):
                """
                Schema for structured output from the planning phase.
                """

                steps: list[str]

            structured_model = self.model.with_structured_output(Plan)
            messages = [SystemMessage(content=self.system_prompt)] + state.messages
            response = cast(Plan, await structured_model.ainvoke(messages))

            # Format plan as a message
            plan_steps = "\n".join([f"- {step}" for step in response.steps])
            plan_message = AIMessage(content=f"Here is my plan:\n{plan_steps}")

            return {
                "messages": [plan_message],
                "plan": response.steps,
                "current_step": 0,
            }

        async def execute_step(state: PlanState) -> dict[str, Any]:
            current_step = state.current_step
            current_objective = state.plan[current_step]

            execution_prompt = (
                f"Now fulfil this objective: {current_objective}\n"
                "Focus on finding the solution, don't reply to anything unrelated"
            )
            messages = [*state.messages, HumanMessage(content=execution_prompt)]
            response = cast(AIMessage, await self.model_with_tools.ainvoke(messages))

            # Only advance to next step if no tool calls were made
            next_step = current_step + (0 if response.tool_calls else 1)
            return {"messages": [response], "current_step": next_step}

        async def process_tools(state: PlanState) -> dict[str, Any]:
            response = cast(AIMessage, await self.model.ainvoke(state.messages))
            return {"messages": [response], "current_step": state.current_step + 1}

        def route_from_execute_step(
            state: PlanState,
        ) -> Literal["execute_step", "tools", "respond"]:
            last_message = state.messages[-1]

            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                return "tools"

            if state.current_step >= len(state.plan):
                return "respond"

            return "execute_step"

        def route_from_process_tools(
            state: PlanState,
        ) -> Literal["execute_step", "respond"]:
            if state.current_step >= len(state.plan):
                return "respond"
            else:
                return "execute_step"

        async def respond(state: PlanState) -> dict[str, Any]:
            prompt = (
                "Now answer my original question from the information you gathered "
                "through the planning you did"
            )
            messages = [*state.messages, HumanMessage(content=prompt)]
            response = cast(AIMessage, await self.model.ainvoke(messages))
            return {"messages": [response]}

        # Build workflow graph
        workflow = StateGraph(PlanState)

        workflow.add_node(create_plan)
        workflow.add_node(execute_step)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.add_node(process_tools)
        workflow.add_node(respond)

        workflow.add_edge("__start__", "create_plan")
        workflow.add_edge("create_plan", "execute_step")
        workflow.add_edge("tools", "process_tools")
        workflow.add_conditional_edges("execute_step", route_from_execute_step)
        workflow.add_conditional_edges("process_tools", route_from_process_tools)
        workflow.add_edge("respond", "__end__")

        graph = workflow.compile(self.memory)
        graph.name = "Planning Agent"

        return graph


# Register the agent in the registry
register_agent(PlanningAgent.name, PlanningAgent)
