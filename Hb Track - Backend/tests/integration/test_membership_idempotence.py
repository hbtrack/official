"""
Tests for membership idempotence on user creation.
"""
from datetime import date, timedelta, datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.context import ExecutionContext, get_current_context
from app.core.db import get_db
from app.main import app


def _ensure_role(db, code: str, name: str) -> int:
    row = db.execute(
        text("SELECT id FROM roles WHERE code = :code"),
        {"code": code},
    ).fetchone()
    if row:
        return int(row[0])

    db.execute(
        text("INSERT INTO roles (code, name) VALUES (:code, :name)"),
        {"code": code, "name": name},
    )
    db.flush()
    return int(
        db.execute(
            text("SELECT id FROM roles WHERE code = :code"),
            {"code": code},
        ).fetchone()[0]
    )


def _create_person(db, name: str) -> str:
    person_id = str(uuid4())
    db.execute(
        text("INSERT INTO persons (id, first_name, last_name, full_name) VALUES (:id, 'John', 'Doe', :name)"),
        {"id": person_id, "name": name},
    )
    db.flush()
    return person_id


def _create_user(db, person_id: str, email: str, full_name: str) -> str:
    user_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO users (id, email, full_name, person_id, password_hash, status)
            VALUES (:id, :email, :full_name, :person_id, 'hash', 'ativo')
            """
        ),
        {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "person_id": person_id,
        },
    )
    db.flush()
    return user_id


def _create_membership(
    db,
    *,
    membership_id: str,
    organization_id: str,
    user_id: str | None,
    person_id: str,
    role_id: int,
    season_id: str,
) -> None:
    db.execute(
        text(
            """
            INSERT INTO membership (id, organization_id, user_id, person_id, role_id, status, season_id)
            VALUES (:id, :org_id, :user_id, :person_id, :role_id, 'ativo', :season_id)
            """
        ),
        {
            "id": membership_id,
            "org_id": organization_id,
            "user_id": user_id,
            "person_id": person_id,
            "role_id": role_id,
            "season_id": season_id,
        },
    )
    db.flush()


def _override_client(db, ctx: ExecutionContext) -> TestClient:
    def override_get_db():
        yield db

    async def override_get_current_context():
        return ctx

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_context] = override_get_current_context
    return TestClient(app)


def test_membership_idempotent_on_user_create(db):
    role_dir = _ensure_role(db, "dirigente", "Dirigente")
    role_coord = _ensure_role(db, "coordenador", "Coordenador")

    actor_person_id = _create_person(db, "Actor Dirigente")
    actor_user_id = _create_user(
        db,
        actor_person_id,
        f"actor_{uuid4().hex[:8]}@example.com",
        "Actor Dirigente",
    )

    organization_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO organizations (id, name, owner_user_id, status)
            VALUES (:id, 'Org Membership', :owner_user_id, 'ativo')
            """
        ),
        {"id": organization_id, "owner_user_id": actor_user_id},
    )

    actor_membership_id = str(uuid4())
    season_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO seasons (id, organization_id, created_by_membership_id, year, name, starts_at, ends_at, is_active)
            VALUES (:id, :org_id, :membership_id, 2098, 'Temporada Membership', :starts_at, :ends_at, true)
            """
        ),
        {
            "id": season_id,
            "org_id": organization_id,
            "membership_id": actor_membership_id,
            "starts_at": date.today() - timedelta(days=1),
            "ends_at": date.today() + timedelta(days=365),
        },
    )

    _create_membership(
        db,
        membership_id=actor_membership_id,
        organization_id=organization_id,
        user_id=actor_user_id,
        person_id=actor_person_id,
        role_id=role_dir,
        season_id=season_id,
    )

    target_person_id = _create_person(db, "Pessoa Coordenador")
    existing_membership_id = str(uuid4())
    _create_membership(
        db,
        membership_id=existing_membership_id,
        organization_id=organization_id,
        user_id=None,
        person_id=target_person_id,
        role_id=role_coord,
        season_id=season_id,
    )

    ctx = ExecutionContext(
        user_id=uuid4(),
        person_id=uuid4(),
        membership_id=uuid4(),
        organization_id=organization_id,
        role_code="dirigente",
        is_superadmin=False,
        request_id=f"membership-{uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
    )

    client = _override_client(db, ctx)
    try:
        payload = {
            "email": f"novo_{uuid4().hex[:8]}@example.com",
            "full_name": "Novo Coordenador",
            "password": "Senha12345!",
            "person_id": target_person_id,
            "role": "coordenador",
        }
        response = client.post("/api/v1/users", json=payload)
    finally:
        app.dependency_overrides.clear()
        client.close()

    assert response.status_code == 201
    user_id = response.json()["id"]

    count = db.execute(
        text(
            """
            SELECT COUNT(*) FROM membership
            WHERE organization_id = :org_id AND person_id = :person_id AND season_id = :season_id
            """
        ),
        {"org_id": organization_id, "person_id": target_person_id, "season_id": season_id},
    ).fetchone()[0]
    assert count == 1

    membership_user = db.execute(
        text(
            "SELECT user_id FROM membership WHERE id = :id"
        ),
        {"id": existing_membership_id},
    ).fetchone()[0]
    assert str(membership_user) == user_id
