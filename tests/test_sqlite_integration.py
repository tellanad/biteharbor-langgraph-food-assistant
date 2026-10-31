import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver

from biteharbor.backend import OfflineBackend
from biteharbor.graph import build_graph


def test_graph_runs_with_production_sqlite_checkpointer(tmp_path):
    database = tmp_path / "checkpoints.sqlite"
    with sqlite3.connect(database, check_same_thread=False) as connection:
        graph = build_graph(OfflineBackend(), SqliteSaver(connection))
        result = graph.invoke(
            {"user_query": "hello", "customer_id": "demo-priya"},
            {"configurable": {"thread_id": "sqlite-test"}},
        )
    assert "Welcome to BiteHarbor" in result["final_answer"]
