"""Command-line entry point for BiteHarbor."""

import argparse
import logging
import sqlite3
from uuid import uuid4

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from biteharbor.backend import LiveBackend, OfflineBackend
from biteharbor.config import Settings
from biteharbor.graph import build_graph

LOGGER = logging.getLogger("biteharbor")


def main() -> None:
    parser = argparse.ArgumentParser(description="BiteHarbor customer-support assistant")
    parser.add_argument("--demo", action="store_true", help="run locally without model calls")
    parser.add_argument(
        "--customer",
        default="demo-priya",
        help="synthetic customer fixture ID; this is not an authentication mechanism",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        backend = OfflineBackend() if args.demo else LiveBackend(settings)
    except ValueError as error:
        parser.error(str(error))

    with sqlite3.connect(
        settings.data_dir / "checkpoints.sqlite", check_same_thread=False
    ) as connection:
        graph = build_graph(backend, SqliteSaver(connection))
        config = {"configurable": {"thread_id": str(uuid4())}, "recursion_limit": 30}
        mode = "OFFLINE DEMO" if args.demo else "LIVE MODEL"
        print(f"BiteHarbor | synthetic data | {mode}")
        print("Commands: reset, quit. During an order prompt: cancel.")
        while True:
            try:
                query = input("You: ").strip()
                if query.casefold() in {"quit", "exit"}:
                    break
                if query.casefold() == "reset":
                    config["configurable"]["thread_id"] = str(uuid4())
                    print("Started a new conversation.")
                    continue
                if not query:
                    continue
                if len(query) > 4_000:
                    print("Please limit your query to 4,000 characters.")
                    continue
                result = graph.invoke(
                    {
                        "user_query": query,
                        "customer_id": args.customer,
                        "messages": [HumanMessage(content=query)],
                    },
                    config,
                )
                while result.get("__interrupt__"):
                    prompt = result["__interrupt__"][0].value
                    result = graph.invoke(Command(resume=input(f"{prompt} ")[:4_000]), config)
                print(f"BiteHarbor: {result['final_answer']}")
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                break
            except Exception:
                # Provider errors can contain prompts or identifiers, so keep logs metadata-only.
                LOGGER.error("request_failed")
                config["configurable"]["thread_id"] = str(uuid4())
                print("The request failed. Please retry in a new conversation.")


if __name__ == "__main__":
    main()
