"""Stateless HTTP adapter for the BiteHarbor portfolio demo."""

import logging
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

from biteharbor.backend import OfflineBackend
from biteharbor.graph import build_graph

LOGGER = logging.getLogger("biteharbor.web")
INDEX_HTML = (Path(__file__).parents[2] / "web" / "index.html").read_text(encoding="utf-8")

CustomerId = Literal["demo-priya", "demo-arjun", "demo-sneha", "demo-rahul", "demo-kavya"]


class ChatRequest(BaseModel):
    """Validated public demo request."""

    message: str = Field(min_length=1, max_length=4_000)
    customer_id: CustomerId = "demo-priya"
    identifier: str | None = Field(default=None, max_length=254)


class ChatResponse(BaseModel):
    """Stable response contract for the web client."""

    status: Literal["completed", "needs_identifier"]
    answer: str | None = None
    prompt: str | None = None
    request_id: str


app = FastAPI(
    title="BiteHarbor API",
    description="Grounded menu discovery and customer-scoped order support.",
    version="0.2.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Add browser protections and prevent caching customer-support responses."""
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; img-src 'self' data:; "
        "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home() -> str:
    """Serve the portfolio demo client."""
    return INDEX_HTML


@app.get("/api/health")
async def health() -> dict[str, str]:
    """Expose a dependency-free deployment health check."""
    return {"status": "ok", "service": "biteharbor", "mode": "synthetic-demo"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    """Run one stateless turn through the LangGraph workflow."""
    request_id = str(uuid4())
    query = payload.message.strip()
    if payload.identifier and payload.identifier.strip():
        query = f"{query}\nOrder identifier: {payload.identifier.strip()}"

    try:
        graph = build_graph(OfflineBackend(), MemorySaver())
        result = graph.invoke(
            {
                "user_query": query,
                "customer_id": payload.customer_id,
                "messages": [HumanMessage(content=query)],
            },
            {"configurable": {"thread_id": request_id}, "recursion_limit": 30},
        )
        if result.get("__interrupt__"):
            return ChatResponse(
                status="needs_identifier",
                prompt=str(result["__interrupt__"][0].value),
                request_id=request_id,
            )
        return ChatResponse(
            status="completed", answer=result["final_answer"], request_id=request_id
        )
    except Exception:
        LOGGER.exception("web_request_failed", extra={"request_id": request_id})
        raise
