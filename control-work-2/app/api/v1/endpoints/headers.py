from fastapi import APIRouter, Request, Response, HTTPException, status, Header
from typing import Optional
from app.schemas.common import CommonHeaders
from app.core.security import generate_server_time

router = APIRouter(tags=["headers"])

@router.get("/headers-simple")
async def get_headers_simple(
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language")
):
    """Получение заголовков через параметры Header"""
    if not user_agent or not accept_language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required headers: User-Agent and Accept-Language are required"
        )
    
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }

@router.get("/headers")
async def get_headers_with_model(
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language")
):
    """Получение заголовков с валидацией"""
    if not user_agent or not accept_language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required headers"
        )
    
    import re
    pattern = r'^[a-zA-Z-]+(?:;[a-zA-Z]=[0-9.]+)?(?:,[a-zA-Z-]+(?:;[a-zA-Z]=[0-9.]+)?)*$'
    if not re.match(pattern, accept_language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Accept-Language format"
        )
    
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }

@router.get("/info")
async def get_info(
    response: Response,
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language")
):
    """Информационный эндпоинт с заголовками"""
    if not user_agent or not accept_language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required headers"
        )
    
    response.headers["X-Server-Time"] = generate_server_time()
    
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": user_agent,
            "Accept-Language": accept_language
        }
    }