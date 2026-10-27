"""Shared state definitions and Pydantic routing schemas"""

from typing import Annotated, Literal

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class RouterDecision(BaseModel):
    """Structured output schema for the orchestrator."""

    agents: list[Literal["menu_agent", "order_agent"]] = Field(
        description="Specialist agents to route to. Use both if query spans menu and order.",
        min_length=1,
        max_length=2,
    )
    reasoning: str = Field(description="Brief explanation of why these agents were selected.")


class StackState(TypedDict, total=False):
    """Global state flowing through the LangGraph StateGraph."""

    # Multi-turn conversation messages with automatic merging
    messages: Annotated[list[BaseMessage], add_messages]
    # Current turn inputs
    user_query: str
    customer_id: str
    # Orchestrator routing output
    route: list[str]
    # Specialist output buffers (isolated scratchpads)
    menu_response: str
    order_response: str
    # Final merged output presented to the user
    final_answer: str
