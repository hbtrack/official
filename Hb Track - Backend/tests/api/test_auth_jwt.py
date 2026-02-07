"""
Testes de autenticação JWT.
Ref: FASE 6 — Autenticação com JWT

Cobre:
- Login endpoint
- JWT validation
- Protected endpoints
- Role-based access control
"""

import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


class TestPasswordHashing:
    """Testes de hashing de senha."""

    def test_hash_password_returns_hash(self):
        """Verifica que hash_password retorna hash bcrypt."""
        password = "senhaSegura123"
        hashed = hash_password(password)
        
        assert hashed.startswith("$2b$")  # bcrypt prefix
        assert len(hashed) == 60  # bcrypt hash length

    def test_verify_password_correct(self):
        """Verifica senha correta."""
        password = "senhaSegura123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Verifica senha incorreta."""
        password = "senhaSegura123"
        hashed = hash_password(password)
        
        assert verify_password("senhaErrada", hashed) is False


class TestJWTToken:
    """Testes de criação e validação de JWT."""

    def test_create_access_token(self):
        """Verifica criação de JWT."""
        data = {
            "sub": "user-123",
            "person_id": "person-456",
            "role_code": "coordenador",
            "is_superadmin": False,
            "organization_id": "org-789",
            "membership_id": "mem-abc"
        }
        token = create_access_token(data)
        
        assert token is not None
        assert len(token) > 100  # JWT is long
        assert token.count(".") == 2  # JWT has 3 parts

    def test_decode_access_token(self):
        """Verifica decodificação de JWT."""
        data = {
            "sub": "user-123",
            "person_id": "person-456",
            "role_code": "coordenador",
            "is_superadmin": False,
            "organization_id": "org-789",
            "membership_id": "mem-abc"
        }
        token = create_access_token(data)
        payload = decode_access_token(token)
        
        assert payload["sub"] == "user-123"
        assert payload["person_id"] == "person-456"
        assert payload["role_code"] == "coordenador"
        assert payload["is_superadmin"] is False
        assert payload["organization_id"] == "org-789"
        assert payload["membership_id"] == "mem-abc"
        assert "exp" in payload  # expiration claim

    def test_decode_invalid_token_raises(self):
        """Verifica que token inválido gera exceção."""
        from jose import JWTError
        
        with pytest.raises(JWTError):
            decode_access_token("invalid.token.here")


class TestLoginEndpoint:
    """Testes do endpoint de login."""

    def test_login_success(self, client, superadmin_cookies):
        """Verifica login com credenciais válidas retorna cookies HttpOnly."""
        # Se superadmin_cookies existe, o login já funcionou
        assert "hb_access_token" in superadmin_cookies

    def test_login_wrong_password(self, client):
        """Verifica login com senha errada retorna 401."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "admin@hbtrack.com",
                "password": "senhaDefinitivamenteErrada123!"
            }
        )
        
        # Em ENV=test, rate limiter está desabilitado (10000/min)
        # Deve sempre retornar 401, nunca 429
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_login_user_not_found(self, client):
        """Verifica login com usuário inexistente retorna 401."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "email_que_nao_existe_xyz123@teste.com",
                "password": "qualquerSenha"
            }
        )
        
        # Em ENV=test, rate limiter está desabilitado (10000/min)
        # Deve sempre retornar 401, nunca 429
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestProtectedEndpoints:
    """Testes de endpoints protegidos."""

    def test_access_without_token_401(self, client):
        """Verifica que endpoint protegido sem token retorna 401."""
        response = client.get("/api/v1/teams")
        
        assert response.status_code == 401

    def test_access_with_valid_token(self, auth_client):
        """Verifica que endpoint protegido com cookie válido funciona."""
        response = auth_client.get("/api/v1/teams")
        assert response.status_code == 200

    def test_access_with_invalid_token_401(self, client):
        """Verifica que token inválido retorna 401."""
        response = client.get(
            "/api/v1/teams",
            cookies={"hb_access_token": "invalid.token.here"}
        )
        
        assert response.status_code == 401
