"""Tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_models():
    """Test models listing endpoint"""
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    assert "models" in response.json()
    assert len(response.json()["models"]) > 0


# Note: Chat endpoint test requires AWS credentials and mocking
# Add more comprehensive tests with mocked Bedrock client as needed
