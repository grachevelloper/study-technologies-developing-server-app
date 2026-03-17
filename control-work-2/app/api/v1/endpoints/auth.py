from fastapi import APIRouter, HTTPException, Response, Request, Cookie, status
from typing import Optional
from app.schemas.user import LoginRequest, UserProfile
from app.schemas.common import MessageResponse
from app.models.user import verify_user_credentials, get_user_by_username
from app.core.security import (
    create_session_token,
    verify_session_token,
    check_session_validity,
    generate_uuid
)

router = APIRouter(tags=["authentication"])

@router.post(
    "/login",
    response_model=UserProfile,
    summary="Вход в систему",
    description="Аутентификация с установкой cookie (Задания 5.1, 5.2, 5.3)"
)
async def login(response: Response, login_data: LoginRequest):
    """
    Вход в систему:
    
    - **username**: имя пользователя
    - **password**: пароль
    
    При успешном входе устанавливается httpOnly cookie session_token
    """
    if not verify_user_credentials(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user = get_user_by_username(login_data.username)
    
    from datetime import datetime
    session_token = create_session_token(user.id, datetime.utcnow().timestamp())
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=300,  
        secure=True, 
        samesite="lax",
        path="/"
    )
    
    return UserProfile(
        id=user.id,
        username=user.username,
        email=user.email
    )

@router.get(
    "/profile",
    response_model=UserProfile,
    responses={
        401: {"description": "Unauthorized", "model": MessageResponse}
    },
    summary="Профиль пользователя",
    description="Защищенный маршрут, требующий валидной сессии"
)
async def get_profile(
    request: Request,
    response: Response,
    session_token: Optional[str] = Cookie(None, alias="session_token")
):
    """
    Получение профиля пользователя.
    Требуется валидная session_token cookie.
    """
    if not session_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MessageResponse(message="Unauthorized")
    
    is_valid, user_id, timestamp = verify_session_token(session_token)
    
    if not is_valid or not user_id:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MessageResponse(message="Invalid session")
    
    is_valid_time, status_session = check_session_validity(timestamp)
    
    if not is_valid_time:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MessageResponse(message="Session expired")
    
    if status_session == 'renew':
        from datetime import datetime
        new_token = create_session_token(user_id, datetime.utcnow().timestamp())
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            max_age=300,
            secure=False,
            samesite="lax",
            path="/"
        )
    
    return UserProfile(
        id=user_id,
        username="user123",
        email="user@example.com"
    )

@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    """Выход из системы - удаляет cookie сессии"""
    response.delete_cookie(key="session_token", path="/")
    return MessageResponse(message="Logout successful")

@router.get("/check-session")
async def check_session(
    response: Response,
    session_token: Optional[str] = Cookie(None, alias="session_token")
):
    """Вспомогательный маршрут для проверки состояния сессии"""
    if not session_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "No session"}
    
    is_valid, user_id, timestamp = verify_session_token(session_token)
    
    if not is_valid:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Invalid session"}
    
    from datetime import datetime
    now = datetime.utcnow().timestamp()
    time_diff = now - timestamp
    
    return {
        "user_id": user_id,
        "last_activity": datetime.fromtimestamp(timestamp).isoformat(),
        "current_time": datetime.fromtimestamp(now).isoformat(),
        "seconds_since_activity": time_diff,
        "session_valid": time_diff <= 300,
        "needs_renew": 180 <= time_diff < 300
    }