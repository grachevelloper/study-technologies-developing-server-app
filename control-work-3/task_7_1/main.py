import datetime
import secrets
from enum import Enum
from typing import Callable

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Task 7.1 — RBAC")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

fake_users_db: dict[str, dict] = {}



class Role(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"


ROLE_PERMISSIONS: dict[Role, list[str]] = {
    Role.admin: ["create", "read", "update", "delete"],
    Role.user: ["read", "update"],
    Role.guest: ["read"],
}



class UserRegister(BaseModel):
    username: str
    password: str
    role: Role = Role.guest


class LoginRequest(BaseModel):
    username: str
    password: str


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username, "role": role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_roles(allowed_roles: list[Role]) -> Callable:
    def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return dependency



@app.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
def register(request: Request, user: UserRegister):
    for existing in list(fake_users_db.keys()):
        if secrets.compare_digest(existing, user.username):
            raise HTTPException(status_code=409, detail="User already exists")
    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": pwd_context.hash(user.password),
        "role": user.role.value,
    }
    return {"message": "New user created", "role": user.role.value}


@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, data: LoginRequest):
    found_user = None
    for username, user in fake_users_db.items():
        if secrets.compare_digest(username, data.username):
            found_user = user
            break
    if found_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(data.password, found_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Authorization failed")
    token = create_access_token({"sub": data.username, "role": found_user["role"]})
    return {"access_token": token, "token_type": "bearer"}



@app.get("/protected_resource")
def protected_resource(
    current_user: dict = Depends(require_roles([Role.admin, Role.user]))
):
    perms = ROLE_PERMISSIONS[Role(current_user["role"])]
    return {
        "message": "Access granted",
        "user": current_user["username"],
        "role": current_user["role"],
        "permissions": perms,
    }


@app.post("/admin/resource")
def admin_create_resource(
    current_user: dict = Depends(require_roles([Role.admin]))
):
    return {
        "message": "Resource created by admin",
        "created_by": current_user["username"],
    }


@app.put("/user/resource/{resource_id}")
def user_update_resource(
    resource_id: int,
    current_user: dict = Depends(require_roles([Role.admin, Role.user])),
):
    return {
        "message": f"Resource {resource_id} updated",
        "updated_by": current_user["username"],
        "role": current_user["role"],
    }


@app.get("/guest/resource")
def guest_read_resource(
    current_user: dict = Depends(require_roles([Role.admin, Role.user, Role.guest]))
):
    return {
        "message": "Public resource (read-only)",
        "accessed_by": current_user["username"],
        "role": current_user["role"],
    }
