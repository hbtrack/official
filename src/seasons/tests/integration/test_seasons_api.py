"""
Testes de integração do módulo seasons.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import uuid

import pytest

from identity_access.domain.entities import AuthSession
from identity_access.infrastructure.jwt_adapter import JWTAdapter
from seasons.infrastructure.models import SeasonModel

ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000201")
COACH_ID = uuid.UUID("00000000-0000-0000-0000-000000000202")
TEAM_ID = uuid.UUID("00000000-0000-0000-0000-000000000203")
SEASON_ID = uuid.UUID("00000000-0000-0000-0000-000000000204")


def _make_jwt(
    user_id: uuid.UUID,
    monkeypatch: pytest.MonkeyPatch,
    role: str = "coach",
) -> str:
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET", "seasons-integration-secret")
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
def test_list_seasons_requires_authenticated_actor(client):
    response = client.get("/api/seasons")

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthenticated"


@pytest.mark.django_db
def test_list_seasons_returns_seeded_season_for_authenticated_actor(client, monkeypatch):
    SeasonModel.objects.create(
        id=SEASON_ID,
        organization_id=ORG_ID,
        name="Temporada 2026",
        sport_cycle_label="handebol",
        status_label="ACTIVE",
        start_date=date(2026, 1, 10),
        end_date=date(2026, 12, 20),
        phase_labels=["preparacao", "competicao"],
        team_ids=[str(TEAM_ID)],
        competition_ids=[],
    )
    auth = f"Bearer {_make_jwt(COACH_ID, monkeypatch)}"

    response = client.get("/api/seasons", HTTP_AUTHORIZATION=auth)

    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 1
    assert payload["page_size"] == 20
    assert payload["total"] == 1
    season = payload["data"][0]
    assert season["id"] == str(SEASON_ID)
    assert season["name"] == "Temporada 2026"
    assert season["start_date"] == "2026-01-10"
    assert season["end_date"] == "2026-12-20"
    assert season["status_label"] == "ACTIVE"
    assert season["phase_labels"] == ["preparacao", "competicao"]
    assert season["team_ids"] == [str(TEAM_ID)]
    assert season["competition_ids"] == []
    assert season["organization_id"] == str(ORG_ID)
    assert season["sport_cycle_label"] == "handebol"
    assert season["created_at"]
    assert season["updated_at"]
