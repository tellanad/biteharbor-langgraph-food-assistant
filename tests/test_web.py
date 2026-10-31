from fastapi.testclient import TestClient

from biteharbor.web import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "biteharbor",
        "mode": "synthetic-demo",
    }
    assert response.headers["cache-control"] == "no-store"


def test_menu_chat_endpoint():
    response = client.post(
        "/api/chat",
        json={"message": "Show vegan dishes", "customer_id": "demo-priya"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert "Vegan Buddha Bowl" in payload["answer"]


def test_order_chat_collects_then_accepts_identifier():
    first = client.post(
        "/api/chat",
        json={"message": "Where is my order?", "customer_id": "demo-priya"},
    )
    assert first.json()["status"] == "needs_identifier"

    second = client.post(
        "/api/chat",
        json={
            "message": "Where is my order?",
            "identifier": "ORD-201",
            "customer_id": "demo-priya",
        },
    )
    assert second.json()["status"] == "completed"
    assert "Out for Delivery" in second.json()["answer"]


def test_order_chat_does_not_cross_customer_boundary():
    response = client.post(
        "/api/chat",
        json={
            "message": "Track my order",
            "identifier": "ORD-201",
            "customer_id": "demo-arjun",
        },
    )
    assert "No matching order" in response.json()["answer"]


def test_chat_rejects_unknown_customer():
    response = client.post(
        "/api/chat",
        json={"message": "hello", "customer_id": "unknown"},
    )
    assert response.status_code == 422
