import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI(title="Task 6.1 — Basic Auth")

security = HTTPBasic()

CORRECT_USERNAME = "admin"
CORRECT_PASSWORD = "secret"


def authenticate(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    correct_username = secrets.compare_digest(credentials.username, CORRECT_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, CORRECT_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/login")
def login(username: str = Depends(authenticate)):
    return {"message": "You got my secret, welcome"}
