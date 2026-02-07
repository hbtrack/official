"""
Fixtures para testes de Memberships.
"""
import pytest
from datetime import date, timedelta
from uuid import uuid4
from sqlalchemy import text

from app.models.membership import Membership


@pytest.fixture
def person_id(db):
    """Cria uma pessoa no banco e retorna seu ID."""
    pid = str(uuid4())
    db.execute(text("""
        INSERT INTO persons (id, full_name)
        VALUES (:id, 'Test Person Membership')
    """), {"id": pid})
    db.flush()
    return pid


@pytest.fixture
def user(db, person_id):
    """Cria um usuário no banco."""
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
    oid = uuid4()
    db.execute(text("""
        INSERT INTO organizations (id, name, owner_user_id, status)
        VALUES (:id, 'Test Org Memberships', :owner_user_id, 'ativo')
    """), {"id": str(oid), "owner_user_id": str(user.id)})
    db.flush()
    return type('Organization', (), {'id': oid})()


@pytest.fixture
def season_ativa(db, organization):
    """Cria uma season ativa."""
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
    """Cria um membership ativo."""
    m = Membership(
        organization_id=organization.id,
        user_id=user.id,
        role_id=3,  # Treinador
    )
    db.add(m)
    db.flush()
    return m


@pytest.fixture
def membership_coach(db, organization, user, person_id, season_ativa):
    """Cria um membership de treinador."""
    m = Membership(
        organization_id=organization.id,
        user_id=user.id,
        role_id=3,  # ROLE_COACH
    )
    db.add(m)
    db.flush()
    return m
