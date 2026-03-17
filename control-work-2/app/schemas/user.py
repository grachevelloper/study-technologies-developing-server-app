from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    age: Optional[int] = Field(None, ge=1, le=150)
    is_subscribed: Optional[bool] = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Alice",
                "email": "alice@example.com",
                "age": 30,
                "is_subscribed": True
            }
        }

class UserProfile(BaseModel):
    id: str
    username: str
    email: str

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "username",
                "password": "password"
            }
        }