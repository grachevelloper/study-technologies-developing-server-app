from __future__ import annotations

from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from app.schemas import UserContext
from app.storage import AppStorage, storage


def get_current_user(
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
    x_user_role: str = Header(default="user", alias="X-User-Role"),
) -> UserContext:
    if x_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        user_id = int(x_user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized") from exc

    role = "admin" if x_user_role == "admin" else "user"
    return UserContext(id=user_id, role=role)


def require_admin(current_user: UserContext = Depends(get_current_user)) -> UserContext:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return current_user


def get_storage() -> AppStorage:
    return storage
