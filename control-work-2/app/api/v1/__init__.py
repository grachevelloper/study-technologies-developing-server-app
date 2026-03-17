from fastapi import APIRouter
from app.api.v1.endpoints import users, products, auth, headers

router = APIRouter(prefix="/api/v1")

router.include_router(users.router)
router.include_router(products.router)
router.include_router(auth.router)
router.include_router(headers.router)