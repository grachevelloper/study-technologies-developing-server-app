from sqlalchemy import select

from app.database import SessionLocal
from app.models import Product


def seed_products() -> None:
    products = [
        Product(title="Notebook", price=1299.90, count=12, description="Ruled notebook"),
        Product(title="Headphones", price=5490.00, count=5, description="Wireless headphones"),
    ]

    with SessionLocal() as db:
        existing_count = len(db.scalars(select(Product)).all())
        if existing_count:
            print("Products already exist, seed skipped")
            return

        db.add_all(products)
        db.commit()
        print("Added 2 products")


if __name__ == "__main__":
    seed_products()
