"""
Tests for the health check endpoint.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """
    Test that the health check endpoint returns the expected response.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    
    # Optionally, test for additional fields if your health check includes them
    # For example, if you add version or uptime information
    # assert "version" in data
    # assert "uptime" in data


def test_health_endpoint_head_request():
    """
    Test that the health check endpoint responds to HEAD requests.
    Often used by load balancers and monitoring systems.
    """
    response = client.head("/api/health")
    assert response.status_code == 200
    # HEAD requests should have no body
    assert not response.content 