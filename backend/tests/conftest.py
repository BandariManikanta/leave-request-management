import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    """A test client backed by a fresh copy of the seed data in a temp directory."""
    with TestClient(create_app(tmp_path)) as test_client:
        yield test_client
