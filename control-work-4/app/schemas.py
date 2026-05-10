from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, conint, constr


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Optional[List[Dict[str, Any]]] = None


class ErrorResponse(BaseModel):
    error: ErrorBody


class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    price: float = Field(gt=0)
    count: int = Field(ge=0)
    description: str = Field(min_length=1, max_length=500)


class ProductOut(ProductCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserValidationIn(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = "Unknown"


class UserIn(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=130)


class UserOut(UserIn):
    id: int
