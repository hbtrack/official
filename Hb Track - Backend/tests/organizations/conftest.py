"""
Fixtures específicas para testes de Organizations.

Estrutura de dependências:
1. users (owner_user_id necessário)
2. organizations (FK para users.owner_user_id)
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import text

from app.models.organization import Organization


@pytest.fixture
def owner_person_id(db):
    """Cria uma pessoa para ser dona da organização."""
    pid = str(uuid4())
    db.execute(text("""
        INSERT INTO persons (id, full_name)
        VALUES (:id, 'Owner Person')
    """), {"id": pid})
    db.flush()
    return pid


@pytest.fixture
def owner_user_id(db, owner_person_id):
    """Cria um usuário owner para a organização."""
    uid = str(uuid4())
    email = f"owner_{uid[:8]}@example.com"
    db.execute(text("""
        INSERT INTO users (id, email, full_name, person_id, password_hash, status)
        VALUES (:id, :email, 'Owner User', :person_id, 'hash', 'ativo')
    """), {"id": uid, "email": email, "person_id": owner_person_id})
    db.flush()
    return uid


@pytest.fixture
def organization_data():
    """Dados básicos para criar organization."""
    unique_id = uuid4().hex[:8]
    return {
        "name": f"Clube Teste {unique_id}",
    }


@pytest.fixture
def organization(db, owner_user_id, organization_data):
    """Organization para testes."""
    org = Organization(
        name=organization_data["name"],
        owner_user_id=owner_user_id,
        status="ativo",
    )
    db.add(org)
    db.flush()
    return org


@pytest.fixture
def organization_inactive(db, owner_user_id):
    """Organization inativa para testes."""
    unique_id = uuid4().hex[:8]
    org = Organization(
        name=f"Clube Inativo {unique_id}",
        owner_user_id=owner_user_id,
        status="inativo",
    )
    db.add(org)
    db.flush()
    return org


@pytest.fixture
def organization_deleted(db, owner_user_id):
    """Organization soft-deleted para testes."""
    unique_id = uuid4().hex[:8]
    org = Organization(
        name=f"Clube Deletado {unique_id}",
        owner_user_id=owner_user_id,
        status="arquivado",
        deleted_at=datetime.now(timezone.utc),
        deleted_reason="Teste de soft delete",
    )
    db.add(org)
    db.flush()
    return org
