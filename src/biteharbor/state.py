"""Shared graph state."""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class StackState(TypedDict, total=False):
    """Global state flowing through the LangGraph StateGraph."""

    user_query: str
    customer_id: str
    messages: Annotated[list[BaseMessage], add_messages]
    route: list[str]
    menu_response: str
    order_response: str
    final_answer: str
