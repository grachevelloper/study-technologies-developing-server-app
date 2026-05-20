from typing import Optional


def auth_headers(
    user_id: int = 10,
    role: str = "user",
) -> dict[str, str]:
    return {"X-User-Id": str(user_id), "X-User-Role": role}


def create_task(
    client,
    *,
    title: str,
    status: str = "todo",
    priority: int = 3,
    description: Optional[str] = None,
    headers: Optional[dict[str, str]] = None,
):
    payload = {
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
    }
    return client.post("/tasks", json=payload, headers=headers or auth_headers())


def test_create_task_successfully(client) -> None:
    response = create_task(
        client,
        title="Подготовить тесты",
        description="Написать интеграционные тесты",
        priority=4,
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "Подготовить тесты",
        "description": "Написать интеграционные тесты",
        "status": "todo",
        "priority": 4,
        "owner_id": 10,
    }


def test_create_task_rejects_short_title(client) -> None:
    response = create_task(client, title="No")

    assert response.status_code == 422


def test_tasks_require_x_user_id_header(client) -> None:
    response = client.get("/tasks")

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


def test_user_sees_only_own_tasks(client) -> None:
    create_task(client, title="Первая задача", headers=auth_headers(10))
    create_task(client, title="Чужая задача", headers=auth_headers(11))

    response = client.get("/tasks", headers=auth_headers(10))

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Первая задача"]


def test_tasks_can_be_filtered_by_status_and_min_priority(client) -> None:
    create_task(client, title="Todo 1", status="todo", priority=2)
    create_task(client, title="Done 1", status="done", priority=5)
    create_task(client, title="Done 2", status="done", priority=3)

    response = client.get(
        "/tasks",
        params={"status": "done", "min_priority": 4},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Done 1"]


def test_task_status_can_be_updated(client) -> None:
    created = create_task(client, title="Сделать задачу").json()

    response = client.patch(
        f"/tasks/{created['id']}/status",
        json={"status": "done"},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_task_returns_404_for_foreign_or_missing_task(client) -> None:
    created = create_task(client, title="Чужая", headers=auth_headers(12)).json()

    foreign_response = client.get(f"/tasks/{created['id']}", headers=auth_headers(10))
    missing_response = client.get("/tasks/999", headers=auth_headers(10))

    assert foreign_response.status_code == 404
    assert missing_response.status_code == 404


def test_task_can_be_deleted(client) -> None:
    created = create_task(client, title="Удалить задачу").json()

    delete_response = client.delete(f"/tasks/{created['id']}", headers=auth_headers())
    list_response = client.get("/tasks", headers=auth_headers())

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert list_response.json() == []


def test_health_returns_status_and_env(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "env": "local"}
