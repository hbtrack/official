"""
Testes de integração do módulo identity_access.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

import pytest
from django.contrib.auth import get_user_model

from identity_access.domain.entities import AuthSession
from identity_access.infrastructure.jwt_adapter import JWTAdapter
from identity_access.infrastructure.models import AuthSessionModel, UserRoleBindingModel

ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000401")
COACH_ID = uuid.UUID("00000000-0000-0000-0000-000000000402")
MEMBER_ID = uuid.UUID("00000000-0000-0000-0000-000000000403")
TARGET_ID = uuid.UUID("00000000-0000-0000-0000-000000000404")
UNKNOWN_ID = uuid.UUID("00000000-0000-0000-0000-000000000405")
PASSWORD = "HBTrack@Test2026"


def _configure_hs256(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET", "identity-access-integration-secret")


def _create_user(user_id: uuid.UUID, email: str, password: str = PASSWORD):
    user_model = get_user_model()
    return user_model.objects.create_user(
        id=user_id,
        username=email,
        email=email,
        password=password,
    )


def _bind_role(user_id: uuid.UUID, role_label: str) -> None:
    UserRoleBindingModel.objects.create(user_id=user_id, role_label=role_label)


def _create_session(
    *,
    session_id: uuid.UUID,
    principal_user_id: uuid.UUID,
    role_labels: list[str],
    expires_at: datetime | None = None,
    revoked_at: datetime | None = None,
) -> AuthSession:
    issued_at = datetime.now(tz=timezone.utc)
    return AuthSession(
        id=session_id,
        principal_user_id=principal_user_id,
        session_scope_label="web",
        role_labels=role_labels,
        auth_method_label="password",
        mfa_required=False,
        mfa_satisfied=True,
        issued_at=issued_at,
        expires_at=expires_at or (issued_at + timedelta(hours=12)),
        revoked_at=revoked_at,
    )


def _persist_session(session: AuthSession) -> None:
    AuthSessionModel.objects.create(
        id=session.id,
        principal_user_id=session.principal_user_id,
        session_scope_label=session.session_scope_label,
        role_labels=session.role_labels,
        auth_method_label=session.auth_method_label or "",
        mfa_required=session.mfa_required or False,
        mfa_satisfied=session.mfa_satisfied or False,
        issued_at=session.issued_at,
        expires_at=session.expires_at,
        revoked_at=session.revoked_at,
    )


def _make_bearer(session: AuthSession, monkeypatch: pytest.MonkeyPatch) -> str:
    _configure_hs256(monkeypatch)
    token = JWTAdapter().issue_access_token(session)
    return f"Bearer {token}"


@pytest.mark.django_db
class TestAuthLoginEndpoint:
    def test_login_valid_returns_200(self, client, monkeypatch):
        _configure_hs256(monkeypatch)
        _create_user(ADMIN_ID, "admin@hbtrack.test")
        _bind_role(ADMIN_ID, "admin")

        response = client.post(
            "/api/auth/login",
            data={"email": "admin@hbtrack.test", "password": PASSWORD},
            content_type="application/json",
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["accessToken"]
        assert payload["refreshToken"]
        assert payload["session"]["principalUserId"] == str(ADMIN_ID)
        assert payload["session"]["roleLabels"] == ["admin"]
        assert AuthSessionModel.objects.count() == 1

    def test_login_invalid_returns_401(self, client):
        _create_user(ADMIN_ID, "admin@hbtrack.test")
        _bind_role(ADMIN_ID, "admin")

        response = client.post(
            "/api/auth/login",
            data={"email": "admin@hbtrack.test", "password": "senha-errada"},
            content_type="application/json",
        )

        assert response.status_code == 401
        payload = response.json()
        assert payload["title"] == "Unauthorized"
        assert payload["status"] == 401
        assert "Credenciais inválidas." in payload["detail"]

    def test_login_malformed_returns_400(self, client):
        response = client.post(
            "/api/auth/login",
            data={"email": "", "password": PASSWORD},
            content_type="application/json",
        )

        assert response.status_code == 400
        payload = response.json()
        assert payload["title"] == "Bad Request"
        assert payload["status"] == 400
        assert "email e password são obrigatórios." in payload["detail"]


@pytest.mark.django_db
class TestAuthLogoutEndpoint:
    def test_logout_valid_session_returns_204(self, client, monkeypatch):
        session = _create_session(
            session_id=uuid.uuid4(),
            principal_user_id=ADMIN_ID,
            role_labels=["admin"],
        )
        _persist_session(session)
        auth = _make_bearer(session, monkeypatch)

        response = client.post("/api/auth/logout", HTTP_AUTHORIZATION=auth)

        assert response.status_code == 204
        model = AuthSessionModel.objects.get(id=session.id)
        assert model.revoked_at is not None
        assert model.refresh_token_used is True
        assert model.refresh_token_hash == ""

    def test_logout_no_token_returns_401(self, client):
        response = client.post("/api/auth/logout")

        assert response.status_code == 401
        payload = response.json()
        assert payload["title"] == "Unauthorized"
        assert payload["status"] == 401
        assert "Token ausente ou inválido." in payload["detail"]


@pytest.mark.django_db
class TestAuthRefreshEndpoint:
    def test_refresh_valid_token_returns_200(self, client, monkeypatch):
        _configure_hs256(monkeypatch)
        _create_user(ADMIN_ID, "admin@hbtrack.test")
        _bind_role(ADMIN_ID, "admin")

        login_response = client.post(
            "/api/auth/login",
            data={"email": "admin@hbtrack.test", "password": PASSWORD},
            content_type="application/json",
        )
        refresh_token = login_response.json()["refreshToken"]

        response = client.post(
            "/api/auth/refresh",
            data={"refreshToken": refresh_token},
            content_type="application/json",
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["accessToken"]
        assert payload["refreshToken"]
        assert payload["refreshToken"] != refresh_token

    def test_refresh_used_token_returns_401(self, client, monkeypatch):
        _configure_hs256(monkeypatch)
        _create_user(ADMIN_ID, "admin@hbtrack.test")
        _bind_role(ADMIN_ID, "admin")

        login_response = client.post(
            "/api/auth/login",
            data={"email": "admin@hbtrack.test", "password": PASSWORD},
            content_type="application/json",
        )
        refresh_token = login_response.json()["refreshToken"]

        first_refresh = client.post(
            "/api/auth/refresh",
            data={"refreshToken": refresh_token},
            content_type="application/json",
        )
        assert first_refresh.status_code == 200

        response = client.post(
            "/api/auth/refresh",
            data={"refreshToken": refresh_token},
            content_type="application/json",
        )

        assert response.status_code == 401
        payload = response.json()
        assert payload["title"] == "Unauthorized"
        assert payload["status"] == 401
        assert "Refresh token inválido, expirado ou já utilizado." in payload["detail"]


@pytest.mark.django_db
class TestAuthMeEndpoint:
    def test_me_authenticated_returns_200(self, client, monkeypatch):
        session = _create_session(
            session_id=uuid.uuid4(),
            principal_user_id=ADMIN_ID,
            role_labels=["admin"],
        )
        _persist_session(session)
        auth = _make_bearer(session, monkeypatch)

        response = client.get("/api/auth/me", HTTP_AUTHORIZATION=auth)

        assert response.status_code == 200
        payload = response.json()
        assert payload["id"] == str(session.id)
        assert payload["principalUserId"] == str(ADMIN_ID)
        assert payload["roleLabels"] == ["admin"]
        assert payload["sessionScopeLabel"] == "web"

    def test_me_no_token_returns_401(self, client):
        response = client.get("/api/auth/me")

        assert response.status_code == 401
        payload = response.json()
        assert payload["title"] == "Unauthorized"
        assert payload["status"] == 401
        assert "Token ausente ou inválido." in payload["detail"]


@pytest.mark.django_db
class TestListActiveSessionsEndpoint:
    def test_admin_can_list_sessions(self, client, monkeypatch):
        admin_session = _create_session(
            session_id=uuid.uuid4(),
            principal_user_id=ADMIN_ID,
            role_labels=["admin"],
        )
        member_session = _create_session(
            session_id=uuid.uuid4(),
            principal_user_id=MEMBER_ID,
            role_labels=["member"],
        )
        _persist_session(admin_session)
        _persist_session(member_session)
        auth = _make_bearer(admin_session, monkeypatch)

        response = client.get("/api/auth/sessions", HTTP_AUTHORIZATION=auth)

        assert response.status_code == 200
        payload = response.json()
        assert payload["nextPageToken"] is None
        assert len(payload["items"]) == 2
        principal_ids = {item["principalUserId"] for item in payload["items"]}
        assert principal_ids == {str(ADMIN_ID), str(MEMBER_ID)}

    def test_non_admin_returns_403(self, client, monkeypatch):
        coach_session = _create_session(
            session_id=uuid.uuid4(),
            principal_user_id=COACH_ID,
            role_labels=["coach"],
        )
        auth = _make_bearer(coach_session, monkeypatch)

        response = client.get("/api/auth/sessions", HTTP_AUTHORIZATION=auth)

        assert response.status_code == 403
        payload = response.json()
        assert payload["title"] == "Forbidden"
        assert payload["status"] == 403
        assert "listActiveSessions requer role admin" in payload["detail"]


@pytest.mark.django_db
class TestRoleManagementEndpoints:
    def test_assign_role_admin_returns_200(self, client, monkeypatch):
        _create_user(ADMIN_ID, "admin@hbtrack.test")
        _create_user(TARGET_ID, "target@hbtrack.test")
        _bind_role(ADMIN_ID, "admin")
        admin_session = _create_session(
            session_id=uuid.uuid4(),
            principal_user_id=ADMIN_ID,
            role_labels=["admin"],
        )
        auth = _make_bearer(admin_session, monkeypatch)

        response = client.post(
            f"/api/auth/users/{TARGET_ID}/roles",
            data={"roleLabel": "coach"},
            content_type="application/json",
            HTTP_AUTHORIZATION=auth,
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["userId"] == str(TARGET_ID)
        assert payload["roles"] == ["coach"]
        assert UserRoleBindingModel.objects.filter(user_id=TARGET_ID, role_label="coach").exists()

    def test_assign_role_non_admin_returns_403(self, client, monkeypatch):
        _create_user(COACH_ID, "coach@hbtrack.test")
        _create_user(TARGET_ID, "target@hbtrack.test")
        _bind_role(COACH_ID, "coach")
        coach_session = _create_session(
            session_id=uuid.uuid4(),
            principal_user_id=COACH_ID,
            role_labels=["coach"],
        )
        auth = _make_bearer(coach_session, monkeypatch)

        response = client.post(
            f"/api/auth/users/{TARGET_ID}/roles",
            data={"roleLabel": "member"},
            content_type="application/json",
            HTTP_AUTHORIZATION=auth,
        )

        assert response.status_code == 403
        payload = response.json()
        assert payload["title"] == "Forbidden"
        assert payload["status"] == 403
        assert "apenas admin pode atribuir ou revogar roles" in payload["detail"]

    def test_revoke_last_admin_returns_409(self, client, monkeypatch):
        _create_user(ADMIN_ID, "admin@hbtrack.test")
        _bind_role(ADMIN_ID, "admin")
        admin_session = _create_session(
            session_id=uuid.uuid4(),
            principal_user_id=ADMIN_ID,
            role_labels=["admin"],
        )
        auth = _make_bearer(admin_session, monkeypatch)

        response = client.delete(
            f"/api/auth/users/{ADMIN_ID}/roles/admin",
            HTTP_AUTHORIZATION=auth,
        )

        assert response.status_code == 409
        payload = response.json()
        assert payload["title"] == "Conflict"
        assert payload["status"] == 409
        assert "último role 'admin'" in payload["detail"]
        assert UserRoleBindingModel.objects.filter(user_id=ADMIN_ID, role_label="admin").exists()
