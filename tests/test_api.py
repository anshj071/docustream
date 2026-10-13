import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "DocuStream" in response.json()["message"]


def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "/api/v1/auth/register" in data["paths"]
    assert "/api/v1/documents/upload" in data["paths"]
    assert "/api/v1/documents/{document_id}/ask" in data["paths"]


def test_unauthorized_access():
    response = client.get("/api/v1/documents/")
    assert response.status_code == 401
