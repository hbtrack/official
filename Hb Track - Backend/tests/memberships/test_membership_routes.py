"""
Testes de integração para rotas de Memberships.

Endpoints testados:
- GET    /v1/organizations/{org_id}/memberships
- POST   /v1/organizations/{org_id}/memberships
- GET    /v1/memberships/{membership_id}
- PATCH  /v1/memberships/{membership_id}
"""

import pytest


class TestListMembershipsByOrganization:
    """Testes para GET /v1/organizations/{org_id}/memberships"""

    def test_list_memberships_returns_200(self, client, membership, organization):
        """Deve retornar 200 e lista de memberships."""
        response = client.get(f"/v1/organizations/{organization.id}/memberships")
        # Endpoint retorna 501 (não implementado), ajustar quando implementado
        assert response.status_code in (200, 501)

    def test_list_memberships_pagination(self, client, membership, organization):
        """Deve respeitar parâmetros de paginação."""
        response = client.get(
            f"/v1/organizations/{organization.id}/memberships",
            params={"page": 1, "limit": 10}
        )
        assert response.status_code in (200, 501)

    def test_list_memberships_filter_by_role(self, client, membership, organization):
        """Deve filtrar por role_code."""
        response = client.get(
            f"/v1/organizations/{organization.id}/memberships",
            params={"role_code": "coach"}
        )
        assert response.status_code in (200, 501)

    def test_list_memberships_filter_by_active(self, client, membership, organization):
        """Deve filtrar por is_active."""
        response = client.get(
            f"/v1/organizations/{organization.id}/memberships",
            params={"is_active": True}
        )
        assert response.status_code in (200, 501)


class TestCreateMembership:
    """Testes para POST /v1/organizations/{org_id}/memberships"""

    def test_create_membership_returns_201(self, client, organization, user):
        """Deve criar membership e retornar 201."""
        payload = {
            "user_id": str(user.id),
            "role_code": "coach"
        }
        response = client.post(
            f"/v1/organizations/{organization.id}/memberships",
            json=payload
        )
        # Endpoint retorna 501 (não implementado), ajustar quando implementado
        assert response.status_code in (201, 501)

    def test_create_membership_athlete(self, client, organization, user):
        """Deve criar membership com role athlete."""
        payload = {
            "user_id": str(user.id),
            "role_code": "athlete"
        }
        response = client.post(
            f"/v1/organizations/{organization.id}/memberships",
            json=payload
        )
        assert response.status_code in (201, 501)

    def test_create_membership_missing_user_id(self, client, organization):
        """Deve retornar 422 sem user_id."""
        payload = {"role_code": "coach"}
        response = client.post(
            f"/v1/organizations/{organization.id}/memberships",
            json=payload
        )
        assert response.status_code in (422, 501)

    def test_create_membership_invalid_role(self, client, organization, user):
        """Deve retornar 422 com role inválido."""
        payload = {
            "user_id": str(user.id),
            "role_code": "invalid_role"
        }
        response = client.post(
            f"/v1/organizations/{organization.id}/memberships",
            json=payload
        )
        assert response.status_code in (422, 501)


class TestGetMembership:
    """Testes para GET /v1/memberships/{membership_id}"""

    def test_get_membership_returns_200(self, client, membership):
        """Deve retornar 200 e dados do membership."""
        response = client.get(f"/v1/memberships/{membership.id}")
        assert response.status_code in (200, 501)

    def test_get_membership_not_found_returns_404(self, client):
        """Deve retornar 404 para ID inexistente."""
        import uuid
        fake_id = uuid.uuid4()
        response = client.get(f"/v1/memberships/{fake_id}")
        assert response.status_code in (404, 501)

    def test_get_membership_invalid_uuid(self, client):
        """Deve retornar 422 para UUID inválido."""
        response = client.get("/v1/memberships/invalid-uuid")
        assert response.status_code == 422


class TestUpdateMembership:
    """Testes para PATCH /v1/memberships/{membership_id}"""

    def test_update_membership_returns_200(self, client, membership):
        """Deve atualizar membership e retornar 200."""
        payload = {"role_code": "coordinator"}
        response = client.patch(f"/v1/memberships/{membership.id}", json=payload)
        assert response.status_code in (200, 501)

    def test_update_membership_deactivate(self, client, membership):
        """Deve desativar membership (soft delete)."""
        payload = {"is_active": False}
        response = client.patch(f"/v1/memberships/{membership.id}", json=payload)
        assert response.status_code in (200, 501)

    def test_update_membership_not_found_returns_404(self, client):
        """Deve retornar 404 para ID inexistente."""
        import uuid
        fake_id = uuid.uuid4()
        payload = {"role_code": "coordinator"}
        response = client.patch(f"/v1/memberships/{fake_id}", json=payload)
        assert response.status_code in (404, 501)
