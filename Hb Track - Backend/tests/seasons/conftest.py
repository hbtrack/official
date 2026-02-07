"""
Fixtures específicas para testes de Seasons.

Estas fixtures são automaticamente descobertas pelo pytest
e ficam disponíveis para todos os testes neste diretório.

Estrutura de dependências:
1. persons (sem FK)
2. users (FK para persons)
3. organizations (FK para users)
4. roles (seed data - já existem)
5. seasons (FK para organizations, membership deferred)
6. membership (FK para organizations, users, persons, roles, seasons deferred)
"""

import pytest
from datetime import date, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.models.season import Season


@pytest.fixture
def person_id(db):
    """Cria uma pessoa no banco e retorna seu ID."""
    pid = str(uuid4())
    db.execute(text("""
        INSERT INTO persons (id, full_name)
        VALUES (:id, 'Test Person')
    """), {"id": pid})
    db.flush()
    return pid


@pytest.fixture
def user_id(db, person_id):
    """Cria um usuário no banco e retorna seu ID."""
    uid = str(uuid4())
    email = f"test_{uid[:8]}@example.com"
    db.execute(text("""
        INSERT INTO users (id, email, full_name, person_id, password_hash, status)
        VALUES (:id, :email, 'Test User', :person_id, 'hash', 'ativo')
    """), {"id": uid, "email": email, "person_id": person_id})
    db.flush()
    return uid


@pytest.fixture
def organization_id(db, user_id):
    """Cria uma organização no banco e retorna seu ID."""
    oid = str(uuid4())
    db.execute(text("""
        INSERT INTO organizations (id, name, owner_user_id, status)
        VALUES (:id, 'Test Org', :owner_user_id, 'ativo')
    """), {"id": oid, "owner_user_id": user_id})
    db.flush()
    return oid


@pytest.fixture
def membership_id(db, organization_id, user_id, person_id, season_base_id):
    """Cria um membership no banco e retorna seu ID."""
    mid = str(uuid4())
    db.execute(text("""
        INSERT INTO membership (id, organization_id, user_id, person_id, role_id, status, season_id)
        VALUES (:id, :org_id, :user_id, :person_id, 2, 'ativo', :season_id)
    """), {
        "id": mid,
        "org_id": organization_id,
        "user_id": user_id,
        "person_id": person_id,
        "season_id": season_base_id
    })
    db.flush()
    return mid


@pytest.fixture
def season_base_id(db, organization_id):
    """Cria uma season base sem membership (usando DEFERRED constraint) e retorna seu ID."""
    sid = str(uuid4())
    # Cria uma season temporária com membership_id nulo (será atualizada depois)
    # Como a FK é DEFERRABLE INITIALLY DEFERRED, isso funciona dentro da mesma transação
    db.execute(text("""
        INSERT INTO seasons (id, organization_id, created_by_membership_id, year, name, starts_at, ends_at)
        VALUES (:id, :org_id, :id, 2020, 'Base Season', :starts, :ends)
    """), {
        "id": sid,
        "org_id": organization_id,
        "starts": date.today() + timedelta(days=30),
        "ends": date.today() + timedelta(days=365)
    })
    db.flush()
    return sid


@pytest.fixture
def season_data():
    """Dados básicos para criar season."""
    return {
        "year": 2025,
        "name": "Temporada 2025",
        "starts_at": date.today() + timedelta(days=30),
        "ends_at": date.today() + timedelta(days=365),
    }


@pytest.fixture
def season_planejada(db, organization_id, membership_id, season_data):
    """Season no status planejada (future starts_at)."""
    season = Season(
        organization_id=organization_id,
        created_by_membership_id=membership_id,
        **season_data
    )
    db.add(season)
    db.flush()
    return season


@pytest.fixture
def season_ativa(db, organization_id, membership_id):
    """Season no status ativa (started, not ended)."""
    season = Season(
        organization_id=organization_id,
        created_by_membership_id=membership_id,
        year=2024,
        name="Temporada Ativa",
        starts_at=date.today() - timedelta(days=30),
        ends_at=date.today() + timedelta(days=300),
    )
    db.add(season)
    db.flush()
    return season


@pytest.fixture
def season_encerrada(db, organization_id, membership_id):
    """Season no status encerrada (ends_at passed)."""
    season = Season(
        organization_id=organization_id,
        created_by_membership_id=membership_id,
        year=2023,
        name="Temporada Encerrada",
        starts_at=date.today() - timedelta(days=365),
        ends_at=date.today() - timedelta(days=30),
    )
    db.add(season)
    db.flush()
    return season


@pytest.fixture
def season_interrompida(db, organization_id, membership_id):
    """Season no status interrompida (interrupted_at set)."""
    from datetime import datetime, timezone
    
    season = Season(
        organization_id=organization_id,
        created_by_membership_id=membership_id,
        year=2022,
        name="Temporada Interrompida",
        starts_at=date.today() - timedelta(days=60),
        ends_at=date.today() + timedelta(days=200),
        interrupted_at=datetime.now(timezone.utc),
    )
    db.add(season)
    db.flush()
    return season


@pytest.fixture
def season_cancelada(db, organization_id, membership_id):
    """Season no status cancelada (canceled_at set, before start)."""
    from datetime import datetime, timezone
    
    season = Season(
        organization_id=organization_id,
        created_by_membership_id=membership_id,
        year=2021,
        name="Temporada Cancelada",
        starts_at=date.today() + timedelta(days=60),
        ends_at=date.today() + timedelta(days=400),
        canceled_at=datetime.now(timezone.utc),
    )
    db.add(season)
    db.flush()
    return season


@pytest.fixture
def client(db, organization_id, membership_id, user_id, person_id):
    """
    TestClient com override de get_db E get_current_user.
    
    Esta fixture sobrescreve a fixture global do conftest.py
    para injetar o current_user com os IDs reais das fixtures.
    """
    from app.main import app
    from app.core.db import get_db
    from app.core.auth import get_current_user, MockUser

    def override_get_db():
        try:
            yield db
        finally:
            pass

    async def override_get_current_user():
        """Retorna MockUser com IDs reais das fixtures."""
        return MockUser(
            user_id=user_id,
            person_id=person_id,
            membership_id=membership_id,
            organization_id=organization_id,
            role="coordenador",
            permissions=["*"],
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
