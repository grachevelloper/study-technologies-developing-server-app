from typing import Optional
from pydantic import BaseModel, EmailStr, Field
import uuid

class UserInDB:
    def __init__(self, username: str, email: str, password: str):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password = password  
        self.is_active = True
        self.created_at = None

users_db = {
    "user123": UserInDB(
        username="user123",
        email="user@example.com",
        password="password123"
    )
}

def get_user_by_username(username: str) -> Optional[UserInDB]:
    return users_db.get(username)

def verify_user_credentials(username: str, password: str) -> bool:
    user = get_user_by_username(username)
    return user is not None and user.password == password