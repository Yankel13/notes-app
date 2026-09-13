import os
os.environ["POSTGRES_HOST"] = "localhost"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_app_title():
    assert app.title == "notes-app"
