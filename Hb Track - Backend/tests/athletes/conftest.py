"""
Fixtures para testes de Athletes.
"""
import pytest
import pytest_asyncio
from datetime import date
from uuid import uuid4
from sqlalchemy import text

from app.models.athlete import Athlete, AthleteState


@pytest_asyncio.fixture
async def person_id(async_db):
    """Cria uma pessoa no banco e retorna seu ID."""
    pid = str(uuid4())
    await async_db.execute(text("""
        INSERT INTO persons (id, first_name, last_name, full_name)
        VALUES (:id, 'Test Person', 'Athlete', 'Test Person Athlete')
    """), {"id": pid})
    await async_db.flush()
    return pid


@pytest_asyncio.fixture
async def user(async_db, person_id):
    """Cria um usuário no banco."""
    from app.models.user import User
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
    from app.models.organization import Organization
    oid = uuid4()
    await async_db.execute(text("""
        INSERT INTO organizations (id, name)
        VALUES (:id, 'Test Org Athletes')
    """), {"id": str(oid)})
    await async_db.flush()
    return type('Organization', (), {'id': oid})()


@pytest_asyncio.fixture
async def team(async_db, organization):
    """Cria uma equipe no banco."""
    tid = uuid4()
    await async_db.execute(text("""
        INSERT INTO teams (id, organization_id, name, category_id, gender)
        VALUES (:id, :org_id, 'Test Team Athletes', 1, 'feminino')
    """), {"id": str(tid), "org_id": str(organization.id)})
    await async_db.flush()
    return type('Team', (), {'id': tid})()


@pytest_asyncio.fixture
async def season_ativa(async_db, team):
    """Cria uma season ativa."""
    from datetime import timedelta
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
    """Cria um membership no banco."""
    mid = uuid4()
    await async_db.execute(text("""
        INSERT INTO org_memberships (id, organization_id, person_id, role_id, start_at)
        VALUES (:id, :org_id, :person_id, 3, NOW())
    """), {
        "id": str(mid),
        "org_id": str(organization.id),
        "person_id": person_id
    })
    await async_db.flush()
    return type('Membership', (), {'id': mid})()


@pytest_asyncio.fixture
async def athlete_person_id(async_db):
    """Cria uma pessoa para o atleta."""
    pid = str(uuid4())
    await async_db.execute(text("""
        INSERT INTO persons (id, first_name, last_name, full_name, birth_date)
        VALUES (:id, 'Athlete', 'Person', 'Athlete Person', '2010-01-01')
    """), {"id": pid})
    await async_db.flush()
    return pid


@pytest_asyncio.fixture
async def athlete(async_db, organization, membership, athlete_person_id):
    """Cria um atleta para testes."""
    a = Athlete(
        person_id=athlete_person_id,
        athlete_name="Atleta Teste Fixture",
        birth_date=date(2010, 1, 1),
        state=AthleteState.ATIVA.value,
    )
    async_db.add(a)
    await async_db.flush()
    return a
