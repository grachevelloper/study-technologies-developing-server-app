from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class User(BaseModel):
    id: int
    name: str = "John Doe"
    signup_ts: Optional[datetime] = None
    friends: List[int] = []


class Message(BaseModel):
    username: str
    message: str


class UserCreate(BaseModel):
    username: str
    user_info: str


class UserResponse(BaseModel):
    username: str
    user_info: str


class Product(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool = True