from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_user_returns_created_user() -> None:
    response = client.post("/users", json={"username": "alice", "age": 24})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "username": "alice", "age": 24}


def test_get_existing_user() -> None:
    created = client.post("/users", json={"username": "bob", "age": 31}).json()

    response = client.get(f"/users/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_user_returns_404() -> None:
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_existing_user_returns_204() -> None:
    created = client.post("/users", json={"username": "carol", "age": 28}).json()

    response = client.delete(f"/users/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_user_returns_404() -> None:
    response = client.delete("/users/123")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_user_rejects_invalid_age() -> None:
    response = client.post("/users", json={"username": "teen", "age": -1})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
