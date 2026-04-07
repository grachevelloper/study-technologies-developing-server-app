import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

load_dotenv()

MODE = os.getenv("MODE", "DEV").upper()
DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "admin")

if MODE not in ("DEV", "PROD"):
    raise ValueError(f"Недопустимое значение MODE='{MODE}'. Допустимые: DEV, PROD")

app = FastAPI(
    title="Task 6.3 — Docs Access Control",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db: dict[str, dict] = {}



class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str



def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = fake_users_db.get(credentials.username)
    username_ok = user is not None and secrets.compare_digest(
        credentials.username, user["username"]
    )
    dummy_hash = pwd_context.hash("dummy")
    password_ok = pwd_context.verify(
        credentials.password,
        user["hashed_password"] if user else dummy_hash,
    )
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


def verify_docs_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    user_ok = secrets.compare_digest(credentials.username, DOCS_USER)
    pass_ok = secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )

if MODE == "DEV":
    @app.get("/openapi.json", include_in_schema=False)
    def openapi_schema(_=Depends(verify_docs_credentials)):
        return JSONResponse(
            get_openapi(title=app.title, version=app.version, routes=app.routes)
        )

    @app.get("/docs", include_in_schema=False)
    def swagger_ui(_=Depends(verify_docs_credentials)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title)

else:  # PROD
    @app.get("/docs", include_in_schema=False)
    @app.get("/openapi.json", include_in_schema=False)
    @app.get("/redoc", include_in_schema=False)
    def docs_disabled():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)



@app.post("/register")
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")
    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": pwd_context.hash(user.password),
    }
    return {"message": f"User '{user.username}' registered successfully"}


@app.get("/login")
def login(user=Depends(auth_user)):
    return {"message": f"Welcome, {user['username']}!"}
