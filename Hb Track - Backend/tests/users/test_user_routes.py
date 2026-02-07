"""
Tests for user routes.
"""
import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(db, user):
    """Test client with authentication override using an existing user."""
    from app.main import app
    from app.core.db import get_db
    from app.core.auth import get_current_user
    from app.models import User
    
    def override_get_db():
        yield db
    
    def override_get_current_user():
        return user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


class TestListUsers:
    """Tests for GET /v1/users."""

    def test_list_users_returns_200(self, client, user):
        """Test list users endpoint returns 200."""
        response = client.get("/v1/users")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


class TestCreateUser:
    """Tests for POST /v1/users."""

    def test_create_user_returns_201(self, client, person_id):
        """Test create user endpoint returns 201."""
        payload = {
            "email": f"route_test_{uuid.uuid4().hex[:8]}@example.com",
            "full_name": "Usuário Route Test",
            "password": "SenhaSegura123!",
            "person_id": str(person_id),
        }
        response = client.post("/v1/users", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["full_name"] == payload["full_name"]
        assert "password" not in data
        assert "password_hash" not in data


class TestGetUser:
    """Tests for GET /v1/users/{user_id}."""

    def test_get_user_returns_200(self, client, user):
        """Test get user endpoint returns 200."""
        response = client.get(f"/v1/users/{user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(user.id)
        assert data["email"] == user.email

    def test_get_user_not_found_returns_404(self, client):
        """Test get user returns 404 for non-existent user."""
        fake_id = uuid.uuid4()
        response = client.get(f"/v1/users/{fake_id}")
        
        assert response.status_code == 404


class TestUpdateUser:
    """Tests for PATCH /v1/users/{user_id}."""

    def test_update_user_returns_200(self, client, user):
        """Test update user endpoint returns 200."""
        payload = {"full_name": "Nome Atualizado Route"}
        response = client.patch(f"/v1/users/{user.id}", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Nome Atualizado Route"
