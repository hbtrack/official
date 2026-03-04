"""Testa status padrão de sessão criada via microcycle_id no endpoint."""

from datetime import date, datetime, timezone
from uuid import uuid4, UUID

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.context import ExecutionContext, get_current_context
from app.core.db import get_async_db
from app.core.permissions_map import get_permissions_for_role
from app.models.category import Category
from app.models.organization import Organization
from app.models.person import Person
from app.models.team import Team
from app.models.training_microcycle import TrainingMicrocycle
from app.models.user import User


@pytest.mark.asyncio
async def test_create_training_session_with_microcycle_sets_expected_status(async_db):
    category = Category(
        id=999,
        name="Categoria Teste",
        max_age=19,
        is_active=True,
    )
    async_db.add(category)

    organization = Organization(
        id=str(uuid4()),
        name="Org Teste Microciclo",
    )
    async_db.add(organization)

    person = Person(
        id=str(uuid4()),
        full_name="Treinador Microciclo",
        first_name="Treinador",
        last_name="Microciclo",
        birth_date=date(1990, 1, 1),
    )
    async_db.add(person)

    user = User(
        id=str(uuid4()),
        email="treinador.microciclo@hbtrack.com",
        person_id=person.id,
    )
    async_db.add(user)

    await async_db.flush()

    team = Team(
        id=uuid4(),
        organization_id=UUID(organization.id),
        name="Equipe Microciclo",
        category_id=category.id,
        gender="masculino",
        is_our_team=True,
    )
    async_db.add(team)

    await async_db.flush()

    microcycle = TrainingMicrocycle(
        organization_id=UUID(organization.id),
        team_id=team.id,
        week_start=date(2026, 1, 19),
        week_end=date(2026, 1, 26),
        created_by_user_id=UUID(user.id),
    )
    async_db.add(microcycle)

    await async_db.flush()

    ctx = ExecutionContext(
        user_id=UUID(user.id),
        email=user.email,
        role_code="treinador",
        request_id=str(uuid4()),
        person_id=None,
        is_superadmin=False,
        organization_id=UUID(organization.id),
        membership_id=uuid4(),
        team_ids=[team.id],
        permissions=get_permissions_for_role("treinador"),
    )

    async def override_get_async_db():
        yield async_db

    async def override_get_current_context():
        return ctx

    app.dependency_overrides[get_async_db] = override_get_async_db
    app.dependency_overrides[get_current_context] = override_get_current_context

    base_payload = {
        "organization_id": organization.id,
        "team_id": str(team.id),
        "session_at": datetime(2026, 1, 20, 10, 0, tzinfo=timezone.utc).isoformat(),
        "session_type": "quadra",
        "microcycle_id": str(microcycle.id),
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response_complete = await client.post(
            "/api/v1/training-sessions",
            json={
                **base_payload,
                "duration_planned_minutes": 90,
                "location": "Campo A",
                "main_objective": "Treino completo",
            },
        )
        response_incomplete = await client.post(
            "/api/v1/training-sessions",
            json=base_payload,
        )

    app.dependency_overrides.clear()

    assert response_complete.status_code == 201
    assert response_complete.json()["status"] == "scheduled"

    assert response_incomplete.status_code == 201
    assert response_incomplete.json()["status"] == "draft"
