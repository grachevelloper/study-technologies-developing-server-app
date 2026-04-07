# Контрольная работа №3 — FastAPI Security & Database

## Установка зависимостей

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск заданий

Каждое задание — отдельное приложение в своей папке.

```bash
# Задание 6.1
uvicorn task_6_1.main:app --reload --port 8001

# Задание 6.2
uvicorn task_6_2.main:app --reload --port 8002

# Задание 6.3 (скопируйте .env.example → .env и настройте)
cp .env.example task_6_3/.env
uvicorn task_6_3.main:app --reload --port 8003

# Задание 6.4
uvicorn task_6_4.main:app --reload --port 8004

# Задание 6.5
uvicorn task_6_5.main:app --reload --port 8005

# Задание 7.1
uvicorn task_7_1.main:app --reload --port 8006

# Задание 8.1
cd task_8_1 && uvicorn main:app --reload --port 8007

# Задание 8.2
cd task_8_2 && uvicorn main:app --reload --port 8008
```

---

## Тестирование эндпоинтов

### Задание 6.1 — Basic Auth

```bash
# Неверные данные (401)
curl -u wrong:wrong http://localhost:8001/login

# Верные данные (200)
curl -u admin:secret http://localhost:8001/login
```

### Задание 6.2 — Хеширование паролей

```bash
# Регистрация
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"correctpass"}' \
  http://localhost:8002/register

# Успешный логин
curl -u user1:correctpass http://localhost:8002/login

# Неверный пароль (401)
curl -u user1:wrongpass http://localhost:8002/login
```

### Задание 6.3 — Документация DEV/PROD

```bash
# DEV: открыть /docs с паролем
curl -u admin:admin http://localhost:8003/docs

# PROD (MODE=PROD в .env): получить 404
curl http://localhost:8003/docs
```

### Задание 6.4 — JWT

```bash
# Логин (результат зависит от random, повторите при 401)
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"securepassword123"}' \
  http://localhost:8004/login

# Доступ к защищённому ресурсу
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8004/protected_resource
```

### Задание 6.5 — JWT + Register + Rate Limiting

```bash
# Регистрация
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8005/register

# Логин
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8005/login

# Защищённый ресурс
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8005/protected_resource
```

### Задание 7.1 — RBAC

```bash
# Регистрация admin
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"boss","password":"pass","role":"admin"}' \
  http://localhost:8006/register

# Регистрация guest
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"visitor","password":"pass","role":"guest"}' \
  http://localhost:8006/register

# Логин
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"boss","password":"pass"}' \
  http://localhost:8006/login

# Только для admin
curl -X POST -H "Authorization: Bearer <TOKEN>" http://localhost:8006/admin/resource

# Доступен всем ролям
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8006/guest/resource
```

### Задание 8.1 — SQLite Users

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"12345"}' \
  http://localhost:8007/register
```

### Задание 8.2 — Todo CRUD

```bash
# Создать
curl -X POST -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread"}' \
  http://localhost:8008/todos

# Получить
curl http://localhost:8008/todos/1

# Обновить
curl -X PUT -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Done","completed":true}' \
  http://localhost:8008/todos/1

# Удалить
curl -X DELETE http://localhost:8008/todos/1
```

## Переменные окружения (задание 6.3)

Скопируйте `.env.example` в `.env` внутри папки `task_6_3/`:

```
MODE=DEV          # DEV или PROD
DOCS_USER=admin
DOCS_PASSWORD=admin
```
