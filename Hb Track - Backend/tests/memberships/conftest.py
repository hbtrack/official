"""
Fixtures para testes de Memberships.
"""
import pytest
import pytest_asyncio
from datetime import date, timedelta
from uuid import uuid4
from sqlalchemy import text

from app.models.membership import Membership


@pytest_asyncio.fixture
async def person_id(async_db):
    """Cria uma pessoa no banco e retorna seu ID."""
    pid = str(uuid4())
    await async_db.execute(text("""
        INSERT INTO persons (id, first_name, last_name, full_name)
        VALUES (:id, 'Test Person', 'Membership', 'Test Person Membership')
    """), {"id": pid})
    await async_db.flush()
    return pid


@pytest_asyncio.fixture
async def user(async_db, person_id):
    """Cria um usuário no banco."""
    uid = uuid4()
    email = f"test_{str(uid)[:8]}@example.com"
    await async_db.execute(text("""
        INSERT INTO users (id, email, person_id, password_hash, status)
        VALUES (:id, :email, :person_id, 'hash', 'ativo')
    """), {"id": str(uid), "email": email, "person_id": person_id})
    await async_db.flush()
    return type('User', (), {'id': uid})()


@pytest_asyncio.fixture
async def organization(async_db, user):
    """Cria uma organização no banco."""
    oid = uuid4()
    await async_db.execute(text("""
        INSERT INTO organizations (id, name)
        VALUES (:id, 'Test Org Memberships')
    """), {"id": str(oid)})
    await async_db.flush()
    return type('Organization', (), {'id': oid})()


@pytest_asyncio.fixture
async def team(async_db, organization):
    """Cria uma equipe no banco."""
    tid = uuid4()
    await async_db.execute(text("""
        INSERT INTO teams (id, organization_id, name, category_id, gender)
        VALUES (:id, :org_id, 'Test Team Memberships', 1, 'feminino')
    """), {"id": str(tid), "org_id": str(organization.id)})
    await async_db.flush()
    return type('Team', (), {'id': tid})()


@pytest_asyncio.fixture
async def season_ativa(async_db, team):
    """Cria uma season ativa."""
    sid = uuid4()
    await async_db.execute(text("""
        INSERT INTO seasons (id, team_id, year, name, start_date, end_date)
        VALUES (:id, :team_id, 2025, 'Season 2025', :starts, :ends)
    """), {
        "id": str(sid),
        "team_id": str(team.id),
        "starts": date.today() - timedelta(days=30),
        "ends": date.today() + timedelta(days=300)
    })
    await async_db.flush()
    return type('Season', (), {'id': sid})()


@pytest_asyncio.fixture
async def membership(async_db, organization, user, person_id, season_ativa):
    """Cria um membership ativo."""
    m = Membership(
        organization_id=organization.id,
        person_id=person_id,
        role_id=3,  # Treinador
    )
    async_db.add(m)
    await async_db.flush()
    return m


@pytest_asyncio.fixture
async def membership_coach(async_db, organization, user, person_id, season_ativa):
    """Cria um membership de treinador."""
    m = Membership(
        organization_id=organization.id,
        person_id=person_id,
        role_id=3,  # ROLE_COACH
    )
    async_db.add(m)
    await async_db.flush()
    return m
