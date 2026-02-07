"""
Fixtures para testes de invariantes de Training.
Adaptado de tests/athletes/conftest.py para uso com async_db.
"""
import pytest_asyncio
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.athlete import Athlete, AthleteState
from app.models.training_session import TrainingSession
from app.models.team import Team


@pytest_asyncio.fixture
async def person_id(async_db: AsyncSession):
    """Cria uma pessoa no banco e retorna seu ID."""
    pid = str(uuid4())
    await async_db.execute(text("""
        INSERT INTO persons (id, full_name, first_name, last_name, birth_date)
        VALUES (:id, 'Test Person Training', 'Test', 'Training', :birth_date)
    """), {"id": pid, "birth_date": date(1995, 1, 1)})
    await async_db.flush()
    return pid


@pytest_asyncio.fixture
async def user(async_db: AsyncSession, person_id: str):
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
async def organization(async_db: AsyncSession):
    """Cria uma organização no banco."""
    oid = uuid4()
    await async_db.execute(text("""
        INSERT INTO organizations (id, name)
        VALUES (:id, 'Test Org Training')
    """), {"id": str(oid)})
    await async_db.flush()
    return type('Organization', (), {'id': oid})()


@pytest_asyncio.fixture
async def team(async_db: AsyncSession, organization, category):
    """Cria um team para testes."""
    tid = uuid4()
    await async_db.execute(text("""
        INSERT INTO teams (id, organization_id, category_id, name, gender, is_our_team)
        VALUES (:id, :org_id, :cat_id, 'Test Team Training', 'masculino', true)
    """), {
        "id": str(tid),
        "org_id": str(organization.id),
        "cat_id": category.id
    })
    await async_db.flush()
    return type('Team', (), {'id': tid})()


@pytest_asyncio.fixture
async def season_ativa(async_db: AsyncSession, team):
    """Cria uma season ativa."""
    sid = uuid4()
    await async_db.execute(text("""
        INSERT INTO seasons (id, team_id, year, name, start_date, end_date)
        VALUES (:id, :team_id, 2025, 'Season 2025', :start_date, :end_date)
    """), {
        "id": str(sid),
        "team_id": str(team.id),
        "start_date": date.today() - timedelta(days=30),
        "end_date": date.today() + timedelta(days=300)
    })
    await async_db.flush()
    return type('Season', (), {'id': sid})()


@pytest_asyncio.fixture
async def membership(async_db: AsyncSession, organization, person_id: str):
    """Cria um org_membership no banco."""
    mid = uuid4()
    await async_db.execute(text("""
        INSERT INTO org_memberships (id, organization_id, person_id, role_id)
        VALUES (:id, :org_id, :person_id, 3)
    """), {
        "id": str(mid),
        "org_id": str(organization.id),
        "person_id": person_id
    })
    await async_db.flush()
    return type('Membership', (), {'id': mid})()


@pytest_asyncio.fixture
async def athlete_person_id(async_db: AsyncSession):
    """Cria uma pessoa para o atleta."""
    pid = str(uuid4())
    await async_db.execute(text("""
        INSERT INTO persons (id, full_name, first_name, last_name)
        VALUES (:id, 'Athlete Person Training', 'Athlete', 'Training')
    """), {"id": pid})
    await async_db.flush()
    return pid


@pytest_asyncio.fixture
async def athlete(async_db: AsyncSession, organization, athlete_person_id: str):
    """Cria um atleta para testes."""
    from datetime import date
    a = Athlete(
        organization_id=organization.id,
        person_id=UUID(athlete_person_id),
        athlete_name="Atleta Teste Training",
        birth_date=date(1995, 1, 1),
        state=AthleteState.ATIVA.value,
    )
    async_db.add(a)
    await async_db.flush()
    return a


@pytest_asyncio.fixture
async def category(async_db: AsyncSession):
    """Cria uma categoria para testes."""
    cid = 9999
    await async_db.execute(text("""
        INSERT INTO categories (id, name, max_age, is_active)
        VALUES (:id, 'Test Category Training', 19, true)
        ON CONFLICT (id) DO NOTHING
    """), {"id": cid})
    await async_db.flush()
    return type('Category', (), {'id': cid})()


@pytest_asyncio.fixture
async def team_membership(async_db: AsyncSession, person_id: str, team):
    """Cria um team_membership para testes (permissão de coach)."""
    tmid = uuid4()
    await async_db.execute(text("""
        INSERT INTO team_memberships (id, person_id, team_id, status)
        VALUES (:id, :person_id, :team_id, 'ativo')
    """), {
        "id": str(tmid),
        "person_id": person_id,
        "team_id": str(team.id)
    })
    await async_db.flush()
    return type('TeamMembership', (), {'id': tmid})()


@pytest_asyncio.fixture
async def training_session(
    async_db: AsyncSession,
    organization,
    team,
    user,
    session_at_offset_hours: int = 3
):
    """
    Cria uma training_session para testes.
    Por padrão, session_at é 3h no futuro (dentro da janela de 2h).
    """
    ts = TrainingSession(
        id=uuid4(),
        organization_id=UUID(str(organization.id)),
        team_id=UUID(str(team.id)),
        session_at=datetime.now(timezone.utc) + timedelta(hours=session_at_offset_hours),
        duration_planned_minutes=90,
        session_type="quadra",
        main_objective="Treino Teste INV",
        location="Ginásio Teste",
        status="draft",
        created_by_user_id=UUID(str(user.id)),
    )
    async_db.add(ts)
    await async_db.flush()
    return ts
