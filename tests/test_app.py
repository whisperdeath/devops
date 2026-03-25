import pytest
from app.app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_home_status_code(client):
    response = client.get("/")
    assert response.status_code == 200


def test_home_content(client):
    response = client.get("/")
    assert b"Hello" in response.data