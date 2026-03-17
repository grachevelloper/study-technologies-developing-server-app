from pydantic import BaseModel, Field, field_validator
from fastapi import Header
import re

class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="User-Agent")
    accept_language: str = Field(..., alias="Accept-Language")
    
    @field_validator('accept_language')
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        pattern = r'^[a-zA-Z-]+(?:;[a-zA-Z]=[0-9.]+)?(?:,[a-zA-Z-]+(?:;[a-zA-Z]=[0-9.]+)?)*$'
        if not re.match(pattern, v):
            raise ValueError('Invalid Accept-Language format')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept-Language": "en-US,en;q=0.9,es;q=0.8"
            }
        }

class MessageResponse(BaseModel):
    """Схема для простых сообщений"""
    message: str