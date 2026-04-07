import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI(title="Task 6.2 — Hashed Passwords")

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db: dict[str, "UserInDB"] = {}


class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    user = fake_users_db.get(credentials.username)
    username_ok = user is not None and secrets.compare_digest(
        credentials.username, user.username
    )
    dummy_hash = pwd_context.hash("dummy")
    password_ok = pwd_context.verify(
        credentials.password,
        user.hashed_password if user else dummy_hash,
    )
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user  # type: ignore[return-value]



@app.post("/register")
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")
    hashed = pwd_context.hash(user.password)
    fake_users_db[user.username] = UserInDB(
        username=user.username, hashed_password=hashed
    )
    return {"message": f"User '{user.username}' registered successfully"}


@app.get("/login")
def login(user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}
