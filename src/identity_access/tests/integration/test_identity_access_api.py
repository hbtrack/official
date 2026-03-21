"""
Testes de integração do módulo identity_access.
Requerem Django configurado (DJANGO_SETTINGS_MODULE) + PostgreSQL.
Marcados com pytest.mark.django_db — executados somente no CI/CD com banco.
"""
import pytest


@pytest.mark.django_db
class TestAuthLoginEndpoint:
    def test_login_valid_returns_200(self, client):
        """POST /auth/login com credenciais válidas retorna 200 + tokens."""
        pass  # implementar com factory_boy + Django test client

    def test_login_invalid_returns_401(self, client):
        """POST /auth/login com credenciais inválidas retorna 401."""
        pass

    def test_login_malformed_returns_400(self, client):
        """POST /auth/login sem email retorna 400."""
        pass


@pytest.mark.django_db
class TestAuthLogoutEndpoint:
    def test_logout_valid_session_returns_204(self, client):
        """POST /auth/logout com Bearer válido retorna 204."""
        pass

    def test_logout_no_token_returns_401(self, client):
        """POST /auth/logout sem token retorna 401."""
        pass


@pytest.mark.django_db
class TestAuthRefreshEndpoint:
    def test_refresh_valid_token_returns_200(self, client):
        """POST /auth/refresh com refresh token válido retorna novo par."""
        pass

    def test_refresh_used_token_returns_401(self, client):
        """POST /auth/refresh com token já usado retorna 401 (rotação OWASP API2:2023)."""
        pass


@pytest.mark.django_db
class TestAuthMeEndpoint:
    def test_me_authenticated_returns_200(self, client):
        """GET /auth/me com Bearer válido retorna sessão do caller."""
        pass

    def test_me_no_token_returns_401(self, client):
        """GET /auth/me sem token retorna 401."""
        pass


@pytest.mark.django_db
class TestListActiveSessionsEndpoint:
    def test_admin_can_list_sessions(self, client):
        """GET /auth/sessions como admin retorna 200."""
        pass

    def test_non_admin_returns_403(self, client):
        """GET /auth/sessions como coach retorna 403 (BFLA)."""
        pass


@pytest.mark.django_db
class TestRoleManagementEndpoints:
    def test_assign_role_admin_returns_200(self, client):
        """POST /auth/users/{userId}/roles como admin retorna 200."""
        pass

    def test_assign_role_non_admin_returns_403(self, client):
        """POST /auth/users/{userId}/roles como coach retorna 403."""
        pass

    def test_revoke_last_admin_returns_409(self, client):
        """DELETE /auth/users/{userId}/roles/admin com único admin retorna 409."""
        pass
