# Контрольная работа №4 — FastAPI, Alembic, ошибки и тесты

Решение покрывает задания 9.1, 10.1, 10.2, 11.1 и 11.2.

## Установка

```bash
cd control-work-4
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Если нужно изменить путь к базе данных, скопируйте пример окружения:

```bash
cp .env.example .env
```

Файл `.env` добавлен в `.gitignore`.

## Миграции Alembic

Используется SQLite. В проекте уже есть две ревизии:

- `20260510_0001_create_products.py` — создаёт таблицу `products` с полями `id`, `title`, `price`, `count`.
- `20260510_0002_add_product_description.py` — добавляет поле `description NOT NULL`.

Применить миграции:

```bash
alembic upgrade head
```

Добавить две тестовые записи в таблицу `products`:

```bash
python3 seed_products.py
```

Проверить состояние миграций:

```bash
alembic current
alembic history
```

## Запуск приложения

```bash
uvicorn app.main:app --reload
```

Swagger UI будет доступен по адресу:

```text
http://127.0.0.1:8000/docs
```

## Основные эндпоинты

### Задание 10.1 — пользовательские исключения

```bash
curl "http://127.0.0.1:8000/exceptions/business-rule"
curl "http://127.0.0.1:8000/exceptions/business-rule?confirmed=true"
curl "http://127.0.0.1:8000/exceptions/resources/42"
```

### Задание 10.2 — валидация JSON

```bash
curl -X POST "http://127.0.0.1:8000/profiles" \
  -H "Content-Type: application/json" \
  -d '{"username":"student","age":21,"email":"student@example.com","password":"strong123"}'
```

Пример невалидного запроса:

```bash
curl -X POST "http://127.0.0.1:8000/profiles" \
  -H "Content-Type: application/json" \
  -d '{"username":"student","age":18,"email":"bad-email","password":"short"}'
```

### Задания 11.1 и 11.2 — CRUD пользователей в памяти

```bash
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","age":24}'

curl "http://127.0.0.1:8000/users/1"

curl -X DELETE "http://127.0.0.1:8000/users/1"
```

## Тестирование

Запуск всех тестов:

```bash
pytest
```

Что проверяется:

- кастомные exception classes и handlers;
- пользовательский handler ошибок валидации;
- синхронные тесты через `fastapi.testclient.TestClient`;
- асинхронные тесты через `pytest-asyncio`, `httpx.AsyncClient` и `ASGITransport`;
- генерация тестовых данных через `Faker`;
- очистка in-memory хранилища между тестами.
