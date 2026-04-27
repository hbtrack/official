"""
Testes de integração do módulo teams.
"""
from __future__ import annotations

from datetime import datetime, timezone
import uuid

import pytest

from identity_access.domain.entities import AuthSession
from identity_access.infrastructure.jwt_adapter import JWTAdapter
from teams.infrastructure.models import TeamModel

ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000101")
ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000102")
TEAM_ID = uuid.UUID("00000000-0000-0000-0000-000000000103")


def _make_jwt(
    user_id: uuid.UUID,
    monkeypatch: pytest.MonkeyPatch,
    role: str = "admin",
) -> str:
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET", "teams-integration-secret")
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


@pytest.mark.django_db
def test_list_teams_requires_authenticated_actor(client):
    response = client.get("/api/teams")

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthenticated"


@pytest.mark.django_db
def test_list_teams_returns_seeded_team_for_authenticated_actor(client, monkeypatch):
    TeamModel.objects.create(
        id=TEAM_ID,
        organization_id=ORG_ID,
        name="Adulto Masculino A",
        short_name="HB A",
        category_label="adulto_masculino",
        status_label="ACTIVE",
        athlete_ids=[],
        staff_user_ids=[str(ADMIN_ID)],
    )
    auth = f"Bearer {_make_jwt(ADMIN_ID, monkeypatch)}"

    response = client.get("/api/teams", HTTP_AUTHORIZATION=auth)

    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 1
    assert payload["page_size"] == 20
    assert payload["total"] == 1
    team = payload["data"][0]
    assert team["id"] == str(TEAM_ID)
    assert team["organization_id"] == str(ORG_ID)
    assert team["name"] == "Adulto Masculino A"
    assert team["category_label"] == "adulto_masculino"
    assert team["status_label"] == "ACTIVE"
    assert team["season_id"] is None
    assert team["short_name"] == "HB A"
    assert team["athlete_ids"] == []
    assert team["staff_user_ids"] == [str(ADMIN_ID)]
    assert team["roster_notes"] is None
    assert team["created_at"]
    assert team["updated_at"]
