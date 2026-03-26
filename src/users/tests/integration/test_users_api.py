"""
Testes de integração — módulo users.
Requerem Django + PostgreSQL (pytest.mark.django_db).
Skeleton: implementar quando banco disponível.
"""
import pytest


@pytest.mark.django_db
class TestListUsersEndpoint:
    def test_authenticated_admin_returns_200(self, client):
        # TODO: configurar JWT mock + criar perfis de teste
        pass

    def test_member_returns_403(self, client):
        pass

    def test_unauthenticated_returns_401(self, client):
        pass


@pytest.mark.django_db
class TestCreateUserEndpoint:
    def test_admin_creates_returns_201(self, client):
        pass

    def test_coach_returns_403(self, client):
        pass

    def test_invalid_role_label_returns_400(self, client):
        pass


@pytest.mark.django_db
class TestGetUserEndpoint:
    def test_owner_gets_own_profile(self, client):
        pass

    def test_unknown_user_returns_404(self, client):
        pass


@pytest.mark.django_db
class TestPatchUserEndpoint:
    def test_owner_patches_own_name(self, client):
        pass

    def test_athlete_cannot_change_role_label(self, client):
        pass
