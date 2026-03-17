from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from app.models.product import get_product_by_id, search_products
from app.schemas.product import ProductResponse, ProductSearchParams

router = APIRouter(prefix="/products", tags=["products"])

@router.get(
    "/search",
    response_model=List[ProductResponse],
    summary="Поиск продуктов",
    description="Поиск продуктов по ключевому слову и категории (Задание 3.2)"
)
async def search_products_endpoint(
    keyword: str = Query(..., description="Ключевое слово для поиска"),
    category: Optional[str] = Query(None, description="Категория для фильтрации"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество")
):
    """
    Поиск продуктов:
    
    - **keyword**: обязательное ключевое слово
    - **category**: опциональная категория
    - **limit**: максимальное количество результатов (по умолчанию 10)
    """
    results = search_products(keyword, category)
    return results[:limit]

@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Получить продукт по ID",
    description="Возвращает информацию о продукте по его ID (Задание 3.2)"
)
async def get_product(product_id: int):
    """
    Получение продукта по ID:
    
    - **product_id**: идентификатор продукта
    """
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product