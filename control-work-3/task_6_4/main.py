import datetime
import random

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Task 6.4 — JWT Auth")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class LoginRequest(BaseModel):
    username: str
    password: str



def authenticate_user(username: str, password: str) -> bool:
    """
    Упрощённая заглушка: случайно возвращает True или False.
    В реальном приложении — проверка по БД.
    """
    return random.choice([True, False])



def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload["exp"] = expire
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )



@app.post("/login")
def login(request: LoginRequest):
    if not authenticate_user(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token({"sub": request.username})
    return {"access_token": token}


@app.get("/protected_resource")
def protected_resource(username: str = Depends(get_current_user)):
    return {"message": f"Access granted for user '{username}'"}
