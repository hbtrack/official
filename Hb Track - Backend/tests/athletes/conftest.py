"""
Fixtures para testes de Athletes.
"""
import pytest
from datetime import date
from uuid import uuid4
from sqlalchemy import text

from app.models.athlete import Athlete, AthleteState


@pytest.fixture
def person_id(db):
    """Cria uma pessoa no banco e retorna seu ID."""
    pid = str(uuid4())
    db.execute(text("""
        INSERT INTO persons (id, full_name)
        VALUES (:id, 'Test Person Athlete')
    """), {"id": pid})
    db.flush()
    return pid


@pytest.fixture
def user(db, person_id):
    """Cria um usuário no banco."""
    from app.models.user import User
    uid = uuid4()
    email = f"test_{str(uid)[:8]}@example.com"
    db.execute(text("""
        INSERT INTO users (id, email, full_name, person_id, password_hash, status)
        VALUES (:id, :email, 'Test User', :person_id, 'hash', 'ativo')
    """), {"id": str(uid), "email": email, "person_id": person_id})
    db.flush()
    return type('User', (), {'id': uid})()


@pytest.fixture
def organization(db, user):
    """Cria uma organização no banco."""
    from app.models.organization import Organization
    oid = uuid4()
    db.execute(text("""
        INSERT INTO organizations (id, name, owner_user_id, status)
        VALUES (:id, 'Test Org Athletes', :owner_user_id, 'ativo')
    """), {"id": str(oid), "owner_user_id": str(user.id)})
    db.flush()
    return type('Organization', (), {'id': oid})()


@pytest.fixture
def season_ativa(db, organization):
    """Cria uma season ativa."""
    from datetime import timedelta
    sid = uuid4()
    db.execute(text("""
        INSERT INTO seasons (id, organization_id, created_by_membership_id, year, name, starts_at, ends_at)
        VALUES (:id, :org_id, :id, 2025, 'Season 2025', :starts, :ends)
    """), {
        "id": str(sid),
        "org_id": str(organization.id),
        "starts": date.today() - timedelta(days=30),
        "ends": date.today() + timedelta(days=300)
    })
    db.flush()
    return type('Season', (), {'id': sid})()


@pytest.fixture
def membership(db, organization, user, person_id, season_ativa):
    """Cria um membership no banco."""
    mid = uuid4()
    db.execute(text("""
        INSERT INTO membership (id, organization_id, user_id, person_id, role_id, status, season_id)
        VALUES (:id, :org_id, :user_id, :person_id, 3, 'ativo', :season_id)
    """), {
        "id": str(mid),
        "org_id": str(organization.id),
        "user_id": str(user.id),
        "person_id": person_id,
        "season_id": str(season_ativa.id)
    })
    db.flush()
    return type('Membership', (), {'id': mid})()


@pytest.fixture
def athlete_person_id(db):
    """Cria uma pessoa para o atleta."""
    pid = str(uuid4())
    db.execute(text("""
        INSERT INTO persons (id, full_name)
        VALUES (:id, 'Athlete Person')
    """), {"id": pid})
    db.flush()
    return pid


@pytest.fixture
def athlete(db, organization, membership, athlete_person_id):
    """Cria um atleta para testes."""
    a = Athlete(
        organization_id=organization.id,
        created_by_membership_id=membership.id,
        person_id=uuid4(),  # Athlete person_id
        full_name="Atleta Teste Fixture",
        state=AthleteState.ativa.value,
    )
    db.add(a)
    db.flush()
    return a
