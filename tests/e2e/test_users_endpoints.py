from fastapi.testclient import TestClient

def test_get_current_user(client: TestClient, auth_headers):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    user_data = response.json()
    assert "email" in user_data
    assert "first_name" in user_data
    assert "last_name" in user_data
    assert "password_hash" not in user_data

def test_change_password(client: TestClient, auth_headers):
    # Change password
    response = client.put(
        "/users/change-password",
        headers=auth_headers,
        json={
            "current_password": "testpassword123",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123"
        }
    )
    assert response.status_code == 200

    # Try logging in with new password
    login_response = client.post(
        "/auth/token",
        data={
            "username": "test.user@example.com",
            "password": "newpassword123",
            "grant_type": "password"
        }
    )
    assert login_response.status_code == 200

def test_password_change_validation(client: TestClient, auth_headers):
    # Test wrong current password
    response = client.put(
        "/users/change-password",
        headers=auth_headers,
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123"
        }
    )
    assert response.status_code == 401

    # Test password mismatch
    response = client.put(
        "/users/change-password",
        headers=auth_headers,
        json={
            "current_password": "testpassword123",
            "new_password": "newpassword123",
            "new_password_confirm": "differentpassword123"
        }
    )
    assert response.status_code == 400

def test_user_endpoints_authorization(client: TestClient):
    # Try accessing user endpoints without auth
    response = client.get("/users/me")
    assert response.status_code == 401

    response = client.put(
        "/users/change-password",
        json={
            "current_password": "testpassword123",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123"
        }
    )
    assert response.status_code == 401 