from pydantic import BaseModel
from datetime import date
from typing import Optional


class UserCreate(BaseModel):
    id: int
    name: str
    joined: date


class UserResponse(BaseModel):
    id: int
    name: str
    joined: date
    
    class Config:
        from_attributes = True