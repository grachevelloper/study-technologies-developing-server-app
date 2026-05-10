from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_business_rule_exception_returns_custom_error() -> None:
    response = client.get("/exceptions/business-rule")

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "business_rule_violation",
            "message": "Parameter 'confirmed' must be true",
            "details": None,
        }
    }


def test_missing_resource_exception_returns_custom_error() -> None:
    response = client.get("/exceptions/resources/42")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "resource_missing"
    assert response.json()["error"]["message"] == "Resource with id=42 was not found"


def test_valid_profile_payload_returns_created_profile() -> None:
    response = client.post(
        "/profiles",
        json={
            "username": "student",
            "age": 21,
            "email": "student@example.com",
            "password": "strong123",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "username": "student",
        "age": 21,
        "email": "student@example.com",
        "phone": "Unknown",
    }


def test_invalid_profile_payload_returns_custom_validation_error() -> None:
    response = client.post(
        "/profiles",
        json={
            "username": "student",
            "age": 18,
            "email": "not-email",
            "password": "short",
        },
    )

    body = response.json()
    fields = {detail["field"] for detail in body["error"]["details"]}

    assert response.status_code == 422
    assert body["error"]["code"] == "validation_error"
    assert "body.age" in fields
    assert "body.email" in fields
    assert "body.password" in fields
