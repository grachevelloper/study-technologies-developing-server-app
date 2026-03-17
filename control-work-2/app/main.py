from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_v1_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    Контрольная работа №2 по FastAPI
    """,
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)

@app.get("/")
async def root():
    """Корневой маршрут с информацией о API"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else "Not available in production",
        "endpoints": {
            "users": {
                "create_user": "POST /api/v1/users/create"
            },
            "products": {
                "search": "GET /api/v1/products/search?keyword=&category=&limit=",
                "get_by_id": "GET /api/v1/products/{product_id}"
            },
            "auth": {
                "login": "POST /login",
                "profile": "GET /profile",
                "check_session": "GET /check-session",
                "logout": "POST /logout"
            },
            "headers": {
                "simple": "GET /headers-simple",
                "with_model": "GET /headers",
                "info": "GET /info"
            }
        }
    }
