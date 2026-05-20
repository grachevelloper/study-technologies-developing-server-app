from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.storage import reset_state


@pytest.fixture(autouse=True)
def clean_state() -> None:
    reset_state()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
