"""
Testes de integração do módulo users.
"""
from __future__ import annotations

from datetime import datetime, timezone
import uuid

import pytest

from identity_access.domain.entities import AuthSession
from identity_access.infrastructure.jwt_adapter import JWTAdapter
from users.infrastructure.models import UserProfileModel

ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000301")
ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000302")
COACH_ID = uuid.UUID("00000000-0000-0000-0000-000000000303")
MEMBER_ID = uuid.UUID("00000000-0000-0000-0000-000000000304")
ATHLETE_ID = uuid.UUID("00000000-0000-0000-0000-000000000305")
UNKNOWN_ID = uuid.UUID("00000000-0000-0000-0000-000000000306")
TEAM_ID = uuid.UUID("00000000-0000-0000-0000-000000000307")
SEASON_ID = uuid.UUID("00000000-0000-0000-0000-000000000308")


def _make_jwt(
    user_id: uuid.UUID,
    monkeypatch: pytest.MonkeyPatch,
    role: str,
) -> str:
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET", "users-integration-secret")
    session = AuthSession(
        id=uuid.uuid4(),
        principal_user_id=user_id,
        session_scope_label="full",
        role_labels=[role],
        auth_method_label="password",
        mfa_required=False,
        mfa_satisfied=True,
        issued_at=datetime.now(tz=timezone.utc),
        expires_at=datetime.now(tz=timezone.utc),
        revoked_at=None,
    )
    return JWTAdapter().issue_access_token(session)


def _seed_profile(
    *,
    user_id: uuid.UUID,
    display_name: str,
    role_label: str,
    organization_id: uuid.UUID = ORG_ID,
    first_name: str = "",
    last_name: str = "",
    team_ids: list[uuid.UUID] | None = None,
    season_ids: list[uuid.UUID] | None = None,
    status_label: str = "PENDING_ACTIVATION",
) -> UserProfileModel:
    return UserProfileModel.objects.create(
        id=user_id,
        organization_id=organization_id,
        first_name=first_name,
        last_name=last_name,
        display_name=display_name,
        role_label=role_label,
        status_label=status_label,
        team_ids=[str(team_id) for team_id in (team_ids or [])],
        season_ids=[str(season_id) for season_id in (season_ids or [])],
    )


@pytest.mark.django_db
class TestListUsersEndpoint:
    def test_authenticated_admin_returns_200(self, client, monkeypatch):
        _seed_profile(
            user_id=ADMIN_ID,
            display_name="Admin HB",
            role_label="admin",
            first_name="Ada",
            last_name="Admin",
            team_ids=[TEAM_ID],
        )
        auth = f"Bearer {_make_jwt(ADMIN_ID, monkeypatch, 'admin')}"

        response = client.get("/api/users", HTTP_AUTHORIZATION=auth)

        assert response.status_code == 200
        payload = response.json()
        assert payload["nextPageToken"] is None
        assert len(payload["items"]) == 1
        item = payload["items"][0]
        assert item["id"] == str(ADMIN_ID)
        assert item["displayName"] == "Admin HB"
        assert item["roleLabel"] == "admin"
        assert item["organizationId"] == str(ORG_ID)
        assert item["firstName"] == "Ada"
        assert item["lastName"] == "Admin"
        assert item["statusLabel"] == "PENDING_ACTIVATION"
        assert item["teamIds"] == [str(TEAM_ID)]

    def test_member_returns_403(self, client, monkeypatch):
        auth = f"Bearer {_make_jwt(MEMBER_ID, monkeypatch, 'member')}"

        response = client.get("/api/users", HTTP_AUTHORIZATION=auth)

        assert response.status_code == 403
        payload = response.json()
        assert payload["title"] == "Forbidden"
        assert payload["status"] == 403
        assert "PERM-USR-005" in payload["detail"]

    def test_unauthenticated_returns_401(self, client):
        response = client.get("/api/users")

        assert response.status_code == 401
        payload = response.json()
        assert payload["title"] == "Unauthorized"
        assert payload["status"] == 401
        assert "Token ausente ou inválido." in payload["detail"]


@pytest.mark.django_db
class TestCreateUserEndpoint:
    def test_admin_creates_returns_201(self, client, monkeypatch):
        auth = f"Bearer {_make_jwt(ADMIN_ID, monkeypatch, 'admin')}"

        response = client.post(
            "/api/users",
            data={
                "displayName": "Novo Atleta",
                "roleLabel": "athlete",
                "organizationId": str(ORG_ID),
                "firstName": "Nina",
                "lastName": "Pivot",
                "teamIds": [str(TEAM_ID)],
                "seasonIds": [str(SEASON_ID)],
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=auth,
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["displayName"] == "Novo Atleta"
        assert payload["roleLabel"] == "athlete"
        assert payload["organizationId"] == str(ORG_ID)
        assert payload["firstName"] == "Nina"
        assert payload["lastName"] == "Pivot"
        assert payload["statusLabel"] == "PENDING_ACTIVATION"
        assert payload["teamIds"] == [str(TEAM_ID)]
        assert payload["seasonIds"] == [str(SEASON_ID)]
        created = UserProfileModel.objects.get(id=payload["id"])
        assert created.display_name == "Novo Atleta"
        assert created.role_label == "athlete"

    def test_coach_returns_403(self, client, monkeypatch):
        auth = f"Bearer {_make_jwt(COACH_ID, monkeypatch, 'coach')}"

        response = client.post(
            "/api/users",
            data={"displayName": "Tentativa Coach", "roleLabel": "member"},
            content_type="application/json",
            HTTP_AUTHORIZATION=auth,
        )

        assert response.status_code == 403
        payload = response.json()
        assert payload["title"] == "Forbidden"
        assert payload["status"] == 403
        assert "PERM-USR-002" in payload["detail"]

    def test_invalid_role_label_returns_400(self, client, monkeypatch):
        auth = f"Bearer {_make_jwt(ADMIN_ID, monkeypatch, 'admin')}"

        response = client.post(
            "/api/users",
            data={"displayName": "Role Inválida", "roleLabel": "manager"},
            content_type="application/json",
            HTTP_AUTHORIZATION=auth,
        )

        assert response.status_code == 400
        payload = response.json()
        assert payload["title"] == "Bad Request"
        assert payload["status"] == 400
        assert "roleLabel 'manager' inválido" in payload["detail"]


@pytest.mark.django_db
class TestGetUserEndpoint:
    def test_owner_gets_own_profile(self, client, monkeypatch):
        _seed_profile(
            user_id=ATHLETE_ID,
            display_name="Atleta Dona",
            role_label="athlete",
            first_name="Ana",
            last_name="Armadora",
            team_ids=[TEAM_ID],
        )
        auth = f"Bearer {_make_jwt(ATHLETE_ID, monkeypatch, 'athlete')}"

        response = client.get(f"/api/users/{ATHLETE_ID}", HTTP_AUTHORIZATION=auth)

        assert response.status_code == 200
        payload = response.json()
        assert payload["id"] == str(ATHLETE_ID)
        assert payload["displayName"] == "Atleta Dona"
        assert payload["firstName"] == "Ana"
        assert payload["lastName"] == "Armadora"
        assert payload["teamIds"] == [str(TEAM_ID)]

    def test_unknown_user_returns_404(self, client, monkeypatch):
        auth = f"Bearer {_make_jwt(ADMIN_ID, monkeypatch, 'admin')}"

        response = client.get(f"/api/users/{UNKNOWN_ID}", HTTP_AUTHORIZATION=auth)

        assert response.status_code == 404
        payload = response.json()
        assert payload["title"] == "Not Found"
        assert payload["status"] == 404
        assert str(UNKNOWN_ID) in payload["detail"]


@pytest.mark.django_db
class TestPatchUserEndpoint:
    def test_owner_patches_own_name(self, client, monkeypatch):
        _seed_profile(
            user_id=ATHLETE_ID,
            display_name="Atleta Dona",
            role_label="athlete",
            first_name="Ana",
            last_name="Armadora",
        )
        auth = f"Bearer {_make_jwt(ATHLETE_ID, monkeypatch, 'athlete')}"

        response = client.patch(
            f"/api/users/{ATHLETE_ID}",
            data={"firstName": "Bea", "displayName": "Bea Armadora"},
            content_type="application/json",
            HTTP_AUTHORIZATION=auth,
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["firstName"] == "Bea"
        assert payload["displayName"] == "Bea Armadora"
        updated = UserProfileModel.objects.get(id=ATHLETE_ID)
        assert updated.first_name == "Bea"
        assert updated.display_name == "Bea Armadora"

    def test_athlete_cannot_change_role_label(self, client, monkeypatch):
        _seed_profile(
            user_id=ATHLETE_ID,
            display_name="Atleta Dona",
            role_label="athlete",
        )
        auth = f"Bearer {_make_jwt(ATHLETE_ID, monkeypatch, 'athlete')}"

        response = client.patch(
            f"/api/users/{ATHLETE_ID}",
            data={"roleLabel": "coach"},
            content_type="application/json",
            HTTP_AUTHORIZATION=auth,
        )

        assert response.status_code == 403
        payload = response.json()
        assert payload["title"] == "Forbidden"
        assert payload["status"] == 403
        assert "PERM-USR-004" in payload["detail"]
