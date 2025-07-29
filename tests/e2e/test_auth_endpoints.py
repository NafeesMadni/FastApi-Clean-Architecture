from fastapi.testclient import TestClient
from src.auth.models import RegisterUserRequest

def test_register_and_login_flow(client: TestClient):
    # Test registration
    register_data = RegisterUserRequest(
        email="test.user@example.com",
        password="testpassword123",
        first_name="Test",
        last_name="User"
    )
    
    response = client.post("/auth/", json=register_data.model_dump())
    assert response.status_code == 201

    # Test successful login
    login_response = client.post(
        "/auth/token",
        data={
            "username": register_data.email,
            "password": register_data.password,
            "grant_type": "password"
        }
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

def test_login_failures(client: TestClient):
    # Test login with non-existent user
    response = client.post(
        "/auth/token",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword",
            "grant_type": "password"
        }
    )
    assert response.status_code == 401

    # Test login with wrong password
    response = client.post(
        "/auth/token",
        data={
            "username": "test.user@example.com",
            "password": "wrongpassword",
            "grant_type": "password"
        }
    )
    assert response.status_code == 401

def test_rate_limiting(client: TestClient):
    # Test rate limiting on registration
    for _ in range(6):  # Attempt 6 registrations (limit is 5/hour)
        response = client.post(
            "/auth/",
            json={
                "email": f"test{_}@example.com",
                "password": "testpassword123",
                "first_name": "Test",
                "last_name": "User"
            }
        )
    assert response.status_code == 429  # Too Many Requests 