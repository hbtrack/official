"""
Tests for TeamService.restore soft delete behavior.
"""
from datetime import datetime, timezone, date, timedelta
from uuid import uuid4

from sqlalchemy import text

from app.services.team_service import TeamService


def _ensure_role_id(db, code: str, name: str) -> int:
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


def test_team_restore_clears_soft_delete(db):
    person_id = str(uuid4())
    user_id = str(uuid4())
    organization_id = str(uuid4())
    membership_id = str(uuid4())
    season_id = str(uuid4())
    team_id = str(uuid4())
    role_id = _ensure_role_id(db, "coordenador", "Coordenador")

    db.execute(
        text("INSERT INTO persons (id, full_name) VALUES (:id, 'Restore Person')"),
        {"id": person_id},
    )
    db.execute(
        text(
            """
            INSERT INTO users (id, email, full_name, person_id, password_hash, status)
            VALUES (:id, :email, 'Restore User', :person_id, 'hash', 'ativo')
            """
        ),
        {"id": user_id, "email": f"restore_{uuid4().hex[:8]}@example.com", "person_id": person_id},
    )
    db.execute(
        text(
            """
            INSERT INTO organizations (id, name, owner_user_id, status)
            VALUES (:id, 'Org Restore', :owner_user_id, 'ativo')
            """
        ),
        {"id": organization_id, "owner_user_id": user_id},
    )
    db.execute(
        text(
            """
            INSERT INTO seasons (id, organization_id, created_by_membership_id, year, name, starts_at, ends_at, is_active)
            VALUES (:id, :org_id, :membership_id, 2096, 'Temporada Restore', :starts_at, :ends_at, true)
            """
        ),
        {
            "id": season_id,
            "org_id": organization_id,
            "membership_id": membership_id,
            "starts_at": date.today() - timedelta(days=1),
            "ends_at": date.today() + timedelta(days=365),
        },
    )
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
    db.execute(
        text(
            """
            INSERT INTO categories (code, label, min_age, max_age)
            VALUES (:code, 'Categoria Restore', 0, 99)
            """
        ),
        {"code": f"REST_{uuid4().hex[:6]}"},
    )
    db.flush()
    category_id = db.execute(
        text("SELECT id FROM categories WHERE label = 'Categoria Restore' ORDER BY created_at DESC LIMIT 1")
    ).fetchone()[0]

    db.execute(
        text(
            """
            INSERT INTO teams (id, organization_id, created_by_membership_id, season_id, category_id, name, deleted_at, deleted_reason)
            VALUES (:id, :org_id, :membership_id, :season_id, :category_id, 'Equipe Restore', :deleted_at, :deleted_reason)
            """
        ),
        {
            "id": team_id,
            "org_id": organization_id,
            "membership_id": membership_id,
            "season_id": season_id,
            "category_id": category_id,
            "deleted_at": datetime.now(timezone.utc),
            "deleted_reason": "Teste",
        },
    )
    db.flush()

    service = TeamService(db)
    team = service.get_by_id(team_id)
    restored = service.restore(team)

    assert restored.deleted_at is None
    assert restored.deleted_reason is None
