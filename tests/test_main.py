from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_running_message() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI CI/CD project is running"}


def test_health_check_returns_healthy() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_greet_uses_name() -> None:
    response = client.get("/greet", params={"name": "Bro"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Bro!"}


def test_echo_returns_payload() -> None:
    response = client.post("/echo", json={"message": "pipeline ready"})

    assert response.status_code == 200
    assert response.json() == {"message": "pipeline ready"}
