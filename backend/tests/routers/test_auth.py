import pytest
from fastapi import status

def test_register_user(test_client, fake_user_data):
    response = test_client.post("/api/auth/register", json=fake_user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.json()
    assert response.json()["email"] == fake_user_data["email"]

def test_login_user(test_client, fake_user_data):
    # First register the user
    test_client.post("/api/auth/register", json=fake_user_data)
    
    # Then try to login
    login_data = {
        "email": fake_user_data["email"],
        "password": fake_user_data["password"]
    }
    response = test_client.post("/api/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_invalid_login(test_client):
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = test_client.post("/api/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(test_client, fake_user_data):
    # Register and login
    test_client.post("/api/auth/register", json=fake_user_data)
    login_response = test_client.post("/api/auth/login", json={
        "email": fake_user_data["email"],
        "password": fake_user_data["password"]
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    response = test_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == fake_user_data["email"] 