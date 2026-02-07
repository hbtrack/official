import pytest
from uuid import uuid4
from sqlalchemy import text
from app.models.user import User


@pytest.fixture
def person_id(db):
    """Cria uma pessoa para associar aos users."""
    pid = str(uuid4())
    db.execute(
        text("""
            INSERT INTO persons (id, full_name, birth_date, created_at, updated_at)
            VALUES (:id, 'Pessoa Teste User', '1990-01-01', NOW(), NOW())
        """),
        {"id": pid}
    )
    db.flush()
    return pid


@pytest.fixture
def user_data(person_id):
    """Dados básicos para criar user."""
    return {
        "person_id": person_id,
        "email": f"test-{uuid4().hex[:8]}@example.com",
        "full_name": "Usuário Teste",
        "password_hash": "hashed_password",
        "status": "ativo",
    }


@pytest.fixture
def user(db, user_data):
    """User para testes."""
    u = User(**user_data)
    db.add(u)
    db.flush()
    return u
