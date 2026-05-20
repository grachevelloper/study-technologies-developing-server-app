from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas import UserContext

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserContext)
def get_me(current_user: UserContext = Depends(get_current_user)) -> UserContext:
    return current_user


@router.get("/{user_id}", response_model=UserContext)
def get_user(user_id: int) -> UserContext:
    return UserContext(id=user_id, role="user")
