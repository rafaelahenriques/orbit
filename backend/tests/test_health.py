from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_are_available_outside_production(client: TestClient) -> None:
    assert client.get("/api/docs").status_code == 200


def test_docs_are_hidden_in_production() -> None:
    client = TestClient(create_app(Settings(environment="production")))

    assert client.get("/api/docs").status_code == 404
    assert client.get("/api/openapi.json").status_code == 404
