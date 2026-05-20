from app.main import app

from tests.test_tasks import auth_headers, create_task


def test_users_me_returns_current_user(client) -> None:
    response = client.get("/users/me", headers=auth_headers(15, "user"))

    assert response.status_code == 200
    assert response.json() == {"id": 15, "role": "user"}


def test_missing_x_user_id_returns_401(client) -> None:
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


def test_non_admin_user_gets_403_for_admin_stats(client) -> None:
    response = client.get("/admin/stats", headers=auth_headers(10, "user"))

    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"


def test_admin_gets_stats_for_all_tasks(client) -> None:
    create_task(client, title="Todo", status="todo", headers=auth_headers(10))
    create_task(client, title="Progress", status="in_progress", headers=auth_headers(11))
    create_task(client, title="Done", status="done", headers=auth_headers(12))

    response = client.get("/admin/stats", headers=auth_headers(1, "admin"))

    assert response.status_code == 200
    assert response.json() == {
        "total_tasks": 3,
        "by_status": {"todo": 1, "in_progress": 1, "done": 1},
    }


def test_regular_user_cannot_delete_foreign_task(client) -> None:
    created = create_task(client, title="Чужая задача", headers=auth_headers(22)).json()

    response = client.delete(f"/tasks/{created['id']}", headers=auth_headers(10))

    assert response.status_code == 404


def test_admin_can_delete_foreign_task(client) -> None:
    created = create_task(client, title="Задача для удаления", headers=auth_headers(22)).json()

    response = client.delete(
        f"/admin/tasks/{created['id']}",
        headers=auth_headers(1, "admin"),
    )

    assert response.status_code == 204
    assert response.content == b""


def test_openapi_groups_routes_by_tags(client) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    openapi = response.json()
    tags = {
        tuple(path_data[method]["tags"])
        for path_data in openapi["paths"].values()
        for method in path_data
    }

    assert ("tasks",) in tags
    assert ("users",) in tags
    assert ("admin",) in tags
