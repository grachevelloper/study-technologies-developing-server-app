from __future__ import annotations

import pytest
from faker import Faker
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def async_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


def user_payload(faker: Faker, age: int | None = None) -> dict[str, int | str]:
    return {
        "username": faker.user_name(),
        "age": age if age is not None else faker.random_int(min=19, max=80),
    }


@pytest.mark.asyncio
async def test_async_create_user(async_client: AsyncClient, faker: Faker) -> None:
    payload = user_payload(faker)

    response = await async_client.post("/users", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == payload["username"]
    assert data["age"] == payload["age"]


@pytest.mark.asyncio
async def test_async_get_existing_user(async_client: AsyncClient, faker: Faker) -> None:
    created = (await async_client.post("/users", json=user_payload(faker))).json()

    response = await async_client.get(f"/users/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


@pytest.mark.asyncio
async def test_async_get_missing_user(async_client: AsyncClient) -> None:
    response = await async_client.get("/users/1000")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_async_delete_existing_user(async_client: AsyncClient, faker: Faker) -> None:
    created = (await async_client.post("/users", json=user_payload(faker))).json()

    response = await async_client.delete(f"/users/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.asyncio
async def test_async_delete_same_user_twice(async_client: AsyncClient, faker: Faker) -> None:
    created = (await async_client.post("/users", json=user_payload(faker))).json()

    first_response = await async_client.delete(f"/users/{created['id']}")
    second_response = await async_client.delete(f"/users/{created['id']}")

    assert first_response.status_code == 204
    assert second_response.status_code == 404
    assert second_response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_async_create_user_accepts_boundary_age(async_client: AsyncClient, faker: Faker) -> None:
    response = await async_client.post("/users", json=user_payload(faker, age=0))

    assert response.status_code == 201
    assert response.json()["age"] == 0
