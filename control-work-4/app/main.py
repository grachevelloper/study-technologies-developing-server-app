from __future__ import annotations

from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import store
from app.database import get_db
from app.exceptions import AppException, BusinessRuleViolation, ResourceMissing
from app.models import Product
from app.schemas import (
    ErrorBody,
    ErrorResponse,
    ProductCreate,
    ProductOut,
    UserIn,
    UserOut,
    UserValidationIn,
)

app = FastAPI(title="Control Work 4", version="1.0.0")


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    print(f"{exc.code}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=ErrorBody(code=exc.code, message=exc.message)).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error=ErrorBody(
                code="validation_error",
                message="Request validation failed",
                details=details,
            )
        ).model_dump(),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/exceptions/business-rule", responses={409: {"model": ErrorResponse}})
def business_rule_endpoint(confirmed: bool = False) -> dict[str, str]:
    if not confirmed:
        raise BusinessRuleViolation("Parameter 'confirmed' must be true")
    return {"status": "confirmed"}


@app.get("/exceptions/resources/{resource_id}", responses={404: {"model": ErrorResponse}})
def missing_resource_endpoint(resource_id: int) -> dict[str, int]:
    if resource_id != 1:
        raise ResourceMissing(f"Resource with id={resource_id} was not found")
    return {"id": resource_id}


@app.post("/profiles", status_code=status.HTTP_201_CREATED)
def create_profile(user: UserValidationIn) -> Dict[str, Any]:
    return {
        "username": user.username,
        "age": user.age,
        "email": user.email,
        "phone": user.phone,
    }


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserIn) -> Dict[str, Any]:
    user_id = store.next_user_id()
    store.db[user_id] = user.model_dump()
    return {"id": user_id, **store.db[user_id]}


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int) -> Dict[str, Any]:
    if user_id not in store.db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"id": user_id, **store.db[user_id]}


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int) -> Response:
    if store.db.pop(user_id, None) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
