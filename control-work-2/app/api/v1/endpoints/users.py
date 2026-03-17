from fastapi import APIRouter, HTTPException, status
from app.schemas.user import UserCreate

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/create",
    response_model=UserCreate,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
    description="Создает нового пользователя (Задание 3.1)"
)
async def create_user(user: UserCreate):
    """
    Создает нового пользователя:
    
    - **name**: имя пользователя (обязательно)
    - **email**: email (обязательно, валидация формата)
    - **age**: возраст (опционально, должно быть положительным)
    - **is_subscribed**: подписка на рассылку (опционально)
    """
    # Здесь обычно сохраняли бы в БД
    return user