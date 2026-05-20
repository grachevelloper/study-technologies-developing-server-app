# Контрольная работа №5 — FastAPI, Docker, WebSocket и зависимости

Проект реализует:

- REST API для задач пользователя;
- маршрут `/health`;
- WebSocket-комнаты `/ws/rooms/{room_id}`;
- маршруты `/users` и `/admin` с зависимостями и проверкой роли;
- интеграционные тесты на `pytest` и `TestClient`.

## Структура

```text
app/
  main.py
  dependencies.py
  schemas.py
  storage.py
  routers/
    tasks.py
    users.py
    admin.py
tests/
  conftest.py
  test_tasks.py
  test_websocket.py
  test_dependencies_and_routing.py
```

## Установка и локальный запуск

```bash
cd control-work-5
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Тесты

```bash
pytest
```

## Docker

```bash
docker compose up --build
```

После запуска можно проверить:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/tasks -H "X-User-Id: 10"
```

Для пустого хранилища `/tasks` вернёт:

```json
[]
```

Если контейнер запущен через `docker compose`, маршрут `/health` вернёт:

```json
{
  "status": "ok",
  "env": "docker"
}
```
