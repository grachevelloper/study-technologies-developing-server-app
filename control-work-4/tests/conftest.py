import pytest
from faker import Faker

from app.store import reset_user_store


@pytest.fixture(autouse=True)
def clean_user_store() -> None:
    reset_user_store()


@pytest.fixture
def faker() -> Faker:
    return Faker("ru_RU")
