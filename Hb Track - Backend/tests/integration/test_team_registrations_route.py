"""
Tests for team registration move route.
"""
from datetime import date, datetime, timezone, timedelta
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.core.context import ExecutionContext, get_current_context
from app.core.db import get_async_db
from app.main import app


async def _ensure_role(async_db, code: str, name: str) -> int:
    result = await async_db.execute(
        text("SELECT id FROM roles WHERE code = :code"),
        {"code": code},
    )
    row = result.fetchone()
    if row:
        return int(row[0])

    await async_db.execute(
        text("INSERT INTO roles (code, name) VALUES (:code, :name)"),
        {"code": code, "name": name},
    )
    await async_db.flush()
    result = await async_db.execute(
        text("SELECT id FROM roles WHERE code = :code"),
        {"code": code},
    )
    return int(result.fetchone()[0])


async def _ensure_positions(async_db) -> None:
    await async_db.execute(
        text(
            """
            INSERT INTO defensive_positions (id, name, code) OVERRIDING SYSTEM VALUE
            VALUES (1, 'Def1', 'DEF1')
            ON CONFLICT (id) DO NOTHING
            """
        )
    )
    await async_db.execute(
        text(
            """
            INSERT INTO offensive_positions (id, name, code) OVERRIDING SYSTEM VALUE
            VALUES (1, 'Off1', 'OFF1')
            ON CONFLICT (id) DO NOTHING
            """
        )
    )
    await async_db.flush()


@pytest.mark.asyncio
async def test_move_athlete_route(async_db):
    role_coord = await _ensure_role(async_db, "coordenador", "Coordenador")
    await _ensure_positions(async_db)

    actor_person_id = uuid4()
    actor_user_id = uuid4()
    organization_id = uuid4()
    membership_id = uuid4()
    season_id = uuid4()
    category_id = 1
    team_institutional_id = uuid4()
    team_competitive_id = uuid4()
    athlete_person_id = uuid4()
    athlete_id = uuid4()
    registration_id = uuid4()

    await async_db.execute(
        text("INSERT INTO persons (id, full_name) VALUES (:id, 'Actor Person')"),
        {"id": actor_person_id},
    )
    await async_db.execute(
        text(
            """
            INSERT INTO users (id, email, full_name, person_id, password_hash, status)
            VALUES (:id, :email, 'Actor User', :person_id, 'hash', 'ativo')
            """
        ),
        {
            "id": actor_user_id,
            "email": f"actor_{uuid4().hex[:8]}@example.com",
            "person_id": actor_person_id,
        },
    )
    await async_db.execute(
        text(
            """
            INSERT INTO organizations (id, name, owner_user_id, status)
            VALUES (:id, 'Org Team Reg', :owner_user_id, 'ativo')
            """
        ),
        {"id": organization_id, "owner_user_id": actor_user_id},
    )
    await async_db.execute(
        text(
            """
            INSERT INTO seasons (id, organization_id, created_by_membership_id, year, name, starts_at, ends_at, is_active)
            VALUES (:id, :org_id, :membership_id, 2097, 'Temporada Move', :starts_at, :ends_at, true)
            """
        ),
        {
            "id": season_id,
            "org_id": organization_id,
            "membership_id": membership_id,
            "starts_at": date.today() - timedelta(days=30),
            "ends_at": date.today() + timedelta(days=365),
        },
    )
    await async_db.execute(
        text(
            """
            INSERT INTO membership (id, organization_id, user_id, person_id, role_id, status, season_id)
            VALUES (:id, :org_id, :user_id, :person_id, :role_id, 'ativo', :season_id)
            """
        ),
        {
            "id": membership_id,
            "org_id": organization_id,
            "user_id": actor_user_id,
            "person_id": actor_person_id,
            "role_id": role_coord,
            "season_id": season_id,
        },
    )
    await async_db.execute(
        text(
            """
            INSERT INTO categories (id, code, label, min_age, max_age) OVERRIDING SYSTEM VALUE
            VALUES (:id, 'U99', 'Categoria Teste', 0, 99)
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {"id": category_id},
    )
    await async_db.execute(
        text(
            """
            INSERT INTO teams (id, organization_id, created_by_membership_id, season_id, category_id, name)
            VALUES (:id, :org_id, :membership_id, :season_id, :category_id, :name)
            """
        ),
        {
            "id": team_institutional_id,
            "org_id": organization_id,
            "membership_id": membership_id,
            "season_id": season_id,
            "category_id": category_id,
            "name": "Equipe Institucional",
        },
    )
    await async_db.execute(
        text(
            """
            INSERT INTO teams (id, organization_id, created_by_membership_id, season_id, category_id, name)
            VALUES (:id, :org_id, :membership_id, :season_id, :category_id, :name)
            """
        ),
        {
            "id": team_competitive_id,
            "org_id": organization_id,
            "membership_id": membership_id,
            "season_id": season_id,
            "category_id": category_id,
            "name": "Equipe Competitiva",
        },
    )
    await async_db.execute(
        text("INSERT INTO persons (id, full_name, birth_date) VALUES (:id, 'Athlete Person', :birth)"),
        {"id": athlete_person_id, "birth": date(2012, 1, 1)},
    )
    await async_db.execute(
        text(
            """
            INSERT INTO athletes (
              id, organization_id, created_by_membership_id, person_id, athlete_name, birth_date,
              main_defensive_position_id, main_offensive_position_id, athlete_rg, athlete_cpf, athlete_phone, state
            ) VALUES (
              :id, :org_id, :membership_id, :person_id, 'Athlete Test', :birth,
              1, 1, :rg, :cpf, :phone, 'ativa'
            )
            """
        ),
        {
            "id": athlete_id,
            "org_id": organization_id,
            "membership_id": membership_id,
            "person_id": athlete_person_id,
            "birth": date(2012, 1, 1),
            "rg": f"RG{uuid4().hex[:6]}",
            "cpf": f"CPF{uuid4().hex[:6]}",
            "phone": "11999999999",
        },
    )
    await async_db.execute(
        text(
            """
            INSERT INTO team_registrations (
              id, athlete_id, season_id, category_id, team_id, organization_id,
              created_by_membership_id, start_at
            ) VALUES (
              :id, :athlete_id, :season_id, :category_id, :team_id, :org_id,
              :membership_id, :start_at
            )
            """
        ),
        {
            "id": registration_id,
            "athlete_id": athlete_id,
            "season_id": season_id,
            "category_id": category_id,
            "team_id": team_institutional_id,
            "org_id": organization_id,
            "membership_id": membership_id,
            "start_at": date.today() - timedelta(days=10),
        },
    )
    await async_db.flush()

    ctx = ExecutionContext(
        user_id=actor_user_id,
        person_id=actor_person_id,
        membership_id=membership_id,
        organization_id=organization_id,
        role_code="coordenador",
        is_superadmin=False,
        request_id="team-reg-move",
        timestamp=datetime.now(timezone.utc),
    )

    async def override_get_async_db():
        yield async_db

    async def override_get_current_context():
        return ctx

    app.dependency_overrides[get_async_db] = override_get_async_db
    app.dependency_overrides[get_current_context] = override_get_current_context

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/teams/{team_competitive_id}/registrations",
            json={"athlete_id": str(athlete_id), "start_at": str(date.today())},
        )
        legacy = await client.post(
            f"/api/v1/team-registrations/teams/{team_competitive_id}/registrations",
            json={"athlete_id": str(athlete_id)},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert legacy.status_code == 404

    result = await async_db.execute(
        text("SELECT end_at FROM team_registrations WHERE id = :id"),
        {"id": registration_id},
    )
    old_end = result.fetchone()[0]
    assert old_end == date.today()

    result = await async_db.execute(
        text(
            """
            SELECT team_id, end_at FROM team_registrations
            WHERE athlete_id = :athlete_id AND team_id = :team_id
            ORDER BY created_at DESC LIMIT 1
            """
        ),
        {"athlete_id": athlete_id, "team_id": team_competitive_id},
    )
    row = result.fetchone()
    assert row is not None
    assert row[1] is None
