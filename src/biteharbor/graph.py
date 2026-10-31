"""LangGraph assembly with bounded human-in-the-loop order identification."""

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from biteharbor.domain import extract_identifier
from biteharbor.state import StackState


def build_graph(backend, checkpointer):
    """Compile the application graph against an injected backend and checkpointer."""

    def orchestrator_node(state: StackState):
        history = state.get("messages", [])[:-1]
        return {
            "route": backend.route(state["user_query"], history),
            "menu_response": "",
            "order_response": "",
            "final_answer": "",
        }

    def menu_node(state: StackState):
        history = state.get("messages", [])[:-1]
        return {"menu_response": backend.answer_menu(state["user_query"], history)}

    def order_node(state: StackState):
        identifier = extract_identifier(state["user_query"])
        attempts = 0
        while not identifier and attempts < 3:
            answer = interrupt("Provide your order ID, tracking ID, or email (or type cancel).")
            if str(answer).strip().casefold() == "cancel":
                return {"order_response": "Order lookup cancelled."}
            identifier = extract_identifier(str(answer))
            attempts += 1
        if not identifier:
            return {"order_response": "No valid identifier received. Start a new lookup."}
        history = state.get("messages", [])[:-1]
        return {
            "order_response": backend.answer_order(
                state["user_query"], identifier, state["customer_id"], history
            )
        }

    def synthesis_node(state: StackState):
        parts = [state.get("menu_response", ""), state.get("order_response", "")]
        final_answer = "\n\n".join(part for part in parts if part)
        return {"final_answer": final_answer, "messages": [AIMessage(content=final_answer)]}

    graph = StateGraph(StackState)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("menu_agent", menu_node)
    graph.add_node("order_agent", order_node)
    graph.add_node("synthesizer", synthesis_node)
    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges(
        "orchestrator",
        lambda state: "menu_agent" if "menu_agent" in state["route"] else "order_agent",
        {"menu_agent": "menu_agent", "order_agent": "order_agent"},
    )
    graph.add_conditional_edges(
        "menu_agent",
        lambda state: "order_agent" if "order_agent" in state["route"] else "synthesizer",
        {"order_agent": "order_agent", "synthesizer": "synthesizer"},
    )
    graph.add_edge("order_agent", "synthesizer")
    graph.add_edge("synthesizer", END)
    return graph.compile(checkpointer=checkpointer)
