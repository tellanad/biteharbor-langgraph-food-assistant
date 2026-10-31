from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from biteharbor.backend import OfflineBackend
from biteharbor.graph import build_graph


def configuration(thread_id: str = "test-thread"):
    return {"configurable": {"thread_id": thread_id}}


def test_menu_query_runs_end_to_end():
    graph = build_graph(OfflineBackend(), MemorySaver())
    result = graph.invoke(
        {"user_query": "Show vegan dishes", "customer_id": "demo-priya"},
        configuration(),
    )
    assert "Vegan Pasta Primavera" in result["final_answer"]
    assert "Vegan Buddha Bowl" in result["final_answer"]


def test_order_query_interrupts_and_resumes():
    graph = build_graph(OfflineBackend(), MemorySaver())
    config = configuration("interrupt-test")
    interrupted = graph.invoke(
        {"user_query": "Where is my order?", "customer_id": "demo-priya"}, config
    )
    assert interrupted["__interrupt__"]
    completed = graph.invoke(Command(resume="ORD-201"), config)
    assert "Out for Delivery" in completed["final_answer"]


def test_order_lookup_can_be_cancelled_at_interrupt():
    graph = build_graph(OfflineBackend(), MemorySaver())
    config = configuration("cancel-test")
    graph.invoke({"user_query": "Where is my order?", "customer_id": "demo-priya"}, config)
    completed = graph.invoke(Command(resume="cancel"), config)
    assert completed["final_answer"] == "Order lookup cancelled."


def test_cross_customer_order_access_is_denied():
    graph = build_graph(OfflineBackend(), MemorySaver())
    result = graph.invoke(
        {"user_query": "Track ORD-201", "customer_id": "demo-arjun"},
        configuration("authorization-test"),
    )
    assert "No matching order" in result["final_answer"]
    assert "Butter Chicken" not in result["final_answer"]


def test_mixed_query_runs_both_specialists():
    graph = build_graph(OfflineBackend(), MemorySaver())
    result = graph.invoke(
        {
            "user_query": "Show pizza options and track ORD-201",
            "customer_id": "demo-priya",
        },
        configuration("mixed-test"),
    )
    assert "Margherita Pizza" in result["final_answer"]
    assert "Out for Delivery" in result["final_answer"]


def test_conversation_messages_persist_across_turns():
    graph = build_graph(OfflineBackend(), MemorySaver())
    config = configuration("history-test")
    graph.invoke(
        {
            "user_query": "hello",
            "customer_id": "demo-priya",
            "messages": [HumanMessage(content="hello")],
        },
        config,
    )
    result = graph.invoke(
        {
            "user_query": "show vegan dishes",
            "customer_id": "demo-priya",
            "messages": [HumanMessage(content="show vegan dishes")],
        },
        config,
    )
    assert [message.type for message in result["messages"]] == [
        "human",
        "ai",
        "human",
        "ai",
    ]
