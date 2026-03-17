from pydantic import BaseModel, Field
from typing import Optional

class ProductResponse(BaseModel):
    product_id: int
    name: str
    category: str
    price: float

class ProductSearchParams(BaseModel):
    keyword: str = Field(..., description="Ключевое слово для поиска")
    category: Optional[str] = Field(None, description="Категория для фильтрации")
    limit: int = Field(10, ge=1, le=100, description="Максимальное количество")