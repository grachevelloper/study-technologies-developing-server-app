from fastapi import FastAPI, HTTPException
from app.config import load_config
from app.logger import logger
from app.models import User, Message, UserCreate, UserResponse, Product

config = load_config()

app = FastAPI(
    title="My FastAPI Project",
    description="Пример проекта на FastAPI",
    version="1.0.0"
)

app.debug = True
logger.info("Приложение запущено в режиме отладки")

fake_users_db = [
    {"username": "vasya", "user_info": "любит колбасу"},
    {"username": "katya", "user_info": "любит петь"},
    {"username": "john_doe", "user_info": "любит программировать"},
    {"username": "jane_smith", "user_info": "любит рисовать"},
]

fake_users_dict = {
    1: {"username": "john_doe", "email": "john@example.com"},
    2: {"username": "jane_smith", "email": "jane@example.com"},
    3: {"username": "alice_jones", "email": "alice@example.com"},
    4: {"username": "bob_white", "email": "bob@example.com"},
}

fake_products = [
    Product(id=1, name="Ноутбук", price=75000.50, in_stock=True),
    Product(id=2, name="Мышь", price=1500.00, in_stock=True),
    Product(id=3, name="Клавиатура", price=3500.00, in_stock=False),
    Product(id=4, name="Монитор", price=25000.00, in_stock=True),
]


@app.get("/")
async def root():
    logger.info("Обработка запроса к корневому эндпоинту")
    return {"message": "Hello MIREA!"}


@app.get("/custom")
async def read_custom_message():
    logger.info("Обработка запроса к /custom")
    return {"message": "This is a custom message!"}


@app.get("/users")
async def get_all_users():
    logger.info("Получение списка всех пользователей")
    return fake_users_db


@app.get("/users/{user_id}")
async def get_user_by_id(user_id: int):
    logger.info(f"Поиск пользователя с ID: {user_id}")
    if user_id in fake_users_dict:
        return fake_users_dict[user_id]
    return {"error": "User not found"}


@app.get("/users/by-username/{username}")
async def get_user_by_username(username: str):
    logger.info(f"Поиск пользователя с username: {username}")
    for user in fake_users_db:
        if user["username"] == username:
            return user
    return {"error": "User not found"}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    logger.info(f"Удаление пользователя с ID: {user_id}")
    if user_id in fake_users_dict:
        del fake_users_dict[user_id]
        return {"message": f"Пользователь с ID {user_id} был удален"}
    return {"error": "User not found"}


@app.get("/users/")
async def read_users_with_limit(limit: int = 10):
    logger.info(f"Получение списка пользователей с лимитом: {limit}")
    limited_users = dict(list(fake_users_dict.items())[:limit])
    return limited_users


@app.get("/users/filter/")
async def filter_users(username: str = None, email: str = None, limit: int = 10):
    logger.info(f"Фильтрация пользователей: username={username}, email={email}, limit={limit}")
    filtered_users = fake_users_dict.copy()
    
    if username:
        filtered_users = {key: user for key, user in filtered_users.items() 
                         if username.lower() in user["username"].lower()}
    
    if email:
        filtered_users = {key: user for key, user in filtered_users.items() 
                         if email.lower() in user["email"].lower()}
    
    return dict(list(filtered_users.items())[:limit])


@app.post("/add_user")
async def add_user(username: str, user_info: str):
    logger.info(f"Добавление пользователя: {username}")
    new_user = {"username": username, "user_info": user_info}
    fake_users_db.append(new_user)
    return {"message": "Юзер успешно добавлен в базу данных"}


@app.post("/add_user_json", response_model=UserResponse)
async def add_user_json(user: UserCreate):
    logger.info(f"Добавление пользователя через JSON: {user.username}")
    new_user = {"username": user.username, "user_info": user.user_info}
    fake_users_db.append(new_user)
    return new_user


@app.post("/")
async def create_message(user: User):
    logger.info(f"Получено сообщение от пользователя: {user.username}")
    logger.info(f"Текст сообщения: {user.message}")
    return user


@app.get("/products")
async def get_all_products():
    logger.info("Получение списка всех продуктов")
    return fake_products


@app.get("/products/{product_id}")
async def get_product_by_id(product_id: int):
    logger.info(f"Поиск продукта с ID: {product_id}")
    for product in fake_products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/products/")
async def get_products_by_price(max_price: float = None, in_stock_only: bool = False):
    logger.info(f"Фильтрация продуктов: max_price={max_price}, in_stock_only={in_stock_only}")
    filtered_products = fake_products.copy()
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p.price <= max_price]
    
    if in_stock_only:
        filtered_products = [p for p in filtered_products if p.in_stock]
    
    return filtered_products


@app.post("/products")
async def create_product(product: Product):
    logger.info(f"Создание нового продукта: {product.name}")
    fake_products.append(product)
    return product


@app.put("/products/{product_id}")
async def update_product(product_id: int, product: Product):
    logger.info(f"Обновление продукта с ID: {product_id}")
    for i, p in enumerate(fake_products):
        if p.id == product_id:
            fake_products[i] = product
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.patch("/products/{product_id}")
async def partial_update_product(product_id: int, price: float = None, in_stock: bool = None):
    logger.info(f"Частичное обновление продукта с ID: {product_id}")
    for i, p in enumerate(fake_products):
        if p.id == product_id:
            if price is not None:
                fake_products[i].price = price
            if in_stock is not None:
                fake_products[i].in_stock = in_stock
            return fake_products[i]
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/info")
async def get_info():
    return {
        "app_name": "My FastAPI Project",
        "debug_mode": config.debug,
        "database_configured": bool(config.db.database_url),
        "total_users": len(fake_users_db),
        "total_products": len(fake_products)
    }


@app.get("/pydantic-example")
async def pydantic_example():
    from datetime import datetime
    
    user = User(
        id=123,
        signup_ts="2024-01-01 12:00",
        friends=[1, "2", 3]
    )
    
    return {
        "user_id": user.id,
        "user_name": user.name,
        "signup_ts": user.signup_ts,
        "friends": user.friends
    }