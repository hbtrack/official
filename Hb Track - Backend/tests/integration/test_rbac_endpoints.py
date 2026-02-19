"""
RBAC smoke tests for critical endpoints.
"""
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
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


def _create_person_user(db, full_name: str, email: str) -> tuple[str, str]:
    person_id = str(uuid4())
    user_id = str(uuid4())
    db.execute(
        text("INSERT INTO persons (id, first_name, last_name, full_name) VALUES (:id, 'John', 'Doe', :name)"),
        {"id": person_id, "name": full_name},
    )
    db.execute(
        text(
            """
            INSERT INTO users (id, email, full_name, person_id, password_hash, status)
            VALUES (:id, :email, :name, :person_id, 'hash', 'ativo')
            """
        ),
        {"id": user_id, "email": email, "name": full_name, "person_id": person_id},
    )
    db.flush()
    return person_id, user_id


def _create_membership(
    db,
    *,
    membership_id: str,
    organization_id: str,
    user_id: str,
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


@contextmanager
def _client_with_context(db, ctx: ExecutionContext):
    def override_get_db():
        yield db

    async def override_get_current_context():
        return ctx

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_context] = override_get_current_context

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def rbac_base(db):
    role_dir = _ensure_role(db, "dirigente", "Dirigente")
    role_coord = _ensure_role(db, "coordenador", "Coordenador")

    actor_person_id, actor_user_id = _create_person_user(
        db,
        "Actor Dirigente",
        f"actor_{uuid4().hex[:8]}@example.com",
    )

    organization_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO organizations (id, name, owner_user_id, status)
            VALUES (:id, 'Org RBAC', :owner_user_id, 'ativo')
            """
        ),
        {"id": organization_id, "owner_user_id": actor_user_id},
    )

    actor_membership_id = str(uuid4())
    active_season_id = str(uuid4())
    planned_season_id = str(uuid4())

    db.execute(
        text(
            """
            INSERT INTO seasons (id, organization_id, created_by_membership_id, year, name, starts_at, ends_at, is_active)
            VALUES (:id, :org_id, :membership_id, 2099, 'Temporada Ativa', :starts_at, :ends_at, true)
            """
        ),
        {
            "id": active_season_id,
            "org_id": organization_id,
            "membership_id": actor_membership_id,
            "starts_at": date.today() - timedelta(days=10),
            "ends_at": date.today() + timedelta(days=100),
        },
    )

    db.execute(
        text(
            """
            INSERT INTO seasons (id, organization_id, created_by_membership_id, year, name, starts_at, ends_at, is_active)
            VALUES (:id, :org_id, :membership_id, 2100, 'Temporada Planejada', :starts_at, :ends_at, false)
            """
        ),
        {
            "id": planned_season_id,
            "org_id": organization_id,
            "membership_id": actor_membership_id,
            "starts_at": date.today() + timedelta(days=30),
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
        season_id=active_season_id,
    )

    db.execute(
        text("INSERT INTO categories (code, label, min_age, max_age) VALUES (:code, :label, 0, 99)"),
        {"code": f"RBAC_{uuid4().hex[:6]}", "label": "Categoria RBAC"},
    )
    db.flush()
    category_id = db.execute(
        text("SELECT id FROM categories WHERE label = 'Categoria RBAC' ORDER BY created_at DESC LIMIT 1")
    ).fetchone()[0]

    team_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO teams (id, organization_id, created_by_membership_id, season_id, category_id, name)
            VALUES (:id, :org_id, :membership_id, :season_id, :category_id, 'Equipe RBAC')
            """
        ),
        {
            "id": team_id,
            "org_id": organization_id,
            "membership_id": actor_membership_id,
            "season_id": active_season_id,
            "category_id": category_id,
        },
    )
    db.flush()

    return {
        "organization_id": organization_id,
        "actor": {
            "user_id": actor_user_id,
            "person_id": actor_person_id,
            "membership_id": actor_membership_id,
        },
        "role_coord": role_coord,
        "active_season_id": active_season_id,
        "planned_season_id": planned_season_id,
        "team_id": team_id,
    }


def _build_context(base, role_code: str) -> ExecutionContext:
    return ExecutionContext(
        user_id=uuid4(),
        person_id=uuid4(),
        membership_id=uuid4(),
        organization_id=base["organization_id"],
        role_code=role_code,
        is_superadmin=False,
        request_id=f"rbac-{uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
    )


@pytest.mark.parametrize(
    "role_code, expected_status",
    [
        ("dirigente", 204),
        ("coordenador", 403),
        ("treinador", 403),
        ("atleta", 403),
    ],
)
def test_delete_user_rbac(db, rbac_base, role_code, expected_status):
    target_person_id, target_user_id = _create_person_user(
        db,
        "User Delete Target",
        f"delete_{uuid4().hex[:8]}@example.com",
    )
    _create_membership(
        db,
        membership_id=str(uuid4()),
        organization_id=rbac_base["organization_id"],
        user_id=target_user_id,
        person_id=target_person_id,
        role_id=rbac_base["role_coord"],
        season_id=rbac_base["active_season_id"],
    )

    ctx = _build_context(rbac_base, role_code)
    with _client_with_context(db, ctx) as client:
        response = client.delete(f"/api/v1/users/{target_user_id}")

    assert response.status_code == expected_status
    if expected_status == 204:
        row = db.execute(
            text("SELECT deleted_at, deleted_reason FROM users WHERE id = :id"),
            {"id": target_user_id},
        ).fetchone()
        assert row.deleted_at is not None
        assert row.deleted_reason is not None


@pytest.mark.parametrize(
    "role_code, expected_status",
    [
        ("dirigente", 200),
        ("coordenador", 200),
        ("treinador", 403),
        ("atleta", 403),
    ],
)
def test_reset_password_rbac(db, rbac_base, role_code, expected_status):
    target_person_id, target_user_id = _create_person_user(
        db,
        "User Reset Target",
        f"reset_{uuid4().hex[:8]}@example.com",
    )
    _create_membership(
        db,
        membership_id=str(uuid4()),
        organization_id=rbac_base["organization_id"],
        user_id=target_user_id,
        person_id=target_person_id,
        role_id=rbac_base["role_coord"],
        season_id=rbac_base["active_season_id"],
    )

    old_hash = db.execute(
        text("SELECT password_hash FROM users WHERE id = :id"),
        {"id": target_user_id},
    ).fetchone()[0]

    ctx = _build_context(rbac_base, role_code)
    with _client_with_context(db, ctx) as client:
        response = client.post(
            f"/api/v1/users/{target_user_id}/reset-password",
            json={"new_password": "NovaSenha123!"},
        )

    assert response.status_code == expected_status
    if expected_status == 200:
        new_hash = db.execute(
            text("SELECT password_hash FROM users WHERE id = :id"),
            {"id": target_user_id},
        ).fetchone()[0]
        assert new_hash != old_hash


@pytest.mark.parametrize(
    "role_code, expected_status",
    [
        ("dirigente", 204),
        ("coordenador", 204),
        ("treinador", 403),
        ("atleta", 403),
    ],
)
def test_delete_team_rbac(db, rbac_base, role_code, expected_status):
    ctx = _build_context(rbac_base, role_code)
    with _client_with_context(db, ctx) as client:
        response = client.delete(
            f"/api/v1/teams/{rbac_base['team_id']}?reason=RBAC"
        )

    assert response.status_code == expected_status
    if expected_status == 204:
        row = db.execute(
            text("SELECT deleted_at, deleted_reason FROM teams WHERE id = :id"),
            {"id": rbac_base["team_id"]},
        ).fetchone()
        assert row.deleted_at is not None
        assert row.deleted_reason == "RBAC"


@pytest.mark.parametrize(
    "role_code, expected_status",
    [
        ("dirigente", 204),
        ("coordenador", 204),
        ("treinador", 403),
        ("atleta", 403),
    ],
)
def test_delete_season_planned_rbac(db, rbac_base, role_code, expected_status):
    ctx = _build_context(rbac_base, role_code)
    with _client_with_context(db, ctx) as client:
        response = client.delete(f"/api/v1/seasons/{rbac_base['planned_season_id']}")

    assert response.status_code == expected_status
    if expected_status == 204:
        row = db.execute(
            text("SELECT canceled_at FROM seasons WHERE id = :id"),
            {"id": rbac_base["planned_season_id"]},
        ).fetchone()
        assert row.canceled_at is not None


def test_delete_season_active_blocked(db, rbac_base):
    ctx = _build_context(rbac_base, "dirigente")
    with _client_with_context(db, ctx) as client:
        response = client.delete(f"/api/v1/seasons/{rbac_base['active_season_id']}")

    assert response.status_code == 409
