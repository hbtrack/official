"""
Admin endpoints (dev-only) for Neon checks and minimal seed.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.cache import get_cache_stats, clear_all_caches
from app.services.provisioning_service import _name_matches, _normalized_hints

router = APIRouter(prefix="/admin", tags=["admin"])


def _ensure_dev_only() -> None:
    if not settings.is_local:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")


def _audit_seed(
    db: Session,
    *,
    entity: str,
    entity_id: str | None,
    action: str,
    context: dict[str, Any],
) -> None:
    db.execute(
        text(
            """
            INSERT INTO audit_logs (entity, entity_id, action, justification, context, actor_user_id)
            VALUES (:entity, :entity_id, :action, :justification, :context::jsonb, NULL)
            """
        ),
        {
            "entity": entity,
            "entity_id": entity_id,
            "action": action,
            "justification": "neon_check_and_seed",
            "context": context,
        },
    )


def _table_exists(db: Session, table_name: str) -> bool:
    result = db.execute(
        text(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = :table_name
            """
        ),
        {"table_name": table_name},
    ).fetchone()
    return result is not None


@router.get("/neon/check-and-seed", status_code=status.HTTP_200_OK)
def neon_check_and_seed(db: Session = Depends(get_db)) -> dict[str, Any]:
    _ensure_dev_only()

    report: dict[str, Any] = {
        "checks": {},
        "seeds": [],
        "warnings": [],
    }

    # Connectivity
    db.execute(text("SELECT 1"))
    report["checks"]["connectivity"] = True

    # Tables
    required_tables = [
        "roles",
        "alembic_version",
        "organizations",
        "seasons",
        "teams",
        "categories",
        "defensive_positions",
        "offensive_positions",
        "schooling_levels",
        "membership",
        "team_registrations",
        "audit_logs",
    ]
    table_checks = {name: _table_exists(db, name) for name in required_tables}
    report["checks"]["tables"] = table_checks

    # roles.code and seed roles
    role_codes = [
        ("superadmin", "Super Administrador"),
        ("dirigente", "Dirigente"),
        ("coordenador", "Coordenador"),
        ("treinador", "Treinador"),
        ("atleta", "Atleta"),
    ]
    inserted_roles: list[str] = []
    for code, name in role_codes:
        exists = db.execute(
            text("SELECT 1 FROM roles WHERE lower(code) = lower(:code)"),
            {"code": code},
        ).fetchone()
        if not exists:
            db.execute(
                text("INSERT INTO roles (code, name) VALUES (:code, :name)"),
                {"code": code, "name": name},
            )
            _audit_seed(
                db,
                entity="roles",
                entity_id=None,
                action="seed_insert",
                context={"code": code, "name": name},
            )
            report["seeds"].append(f"roles:{code}")
            inserted_roles.append(code)
    report["checks"]["roles_seeded"] = inserted_roles
    report["checks"]["roles_code_present"] = (
        db.execute(
            text(
                """
                SELECT COUNT(*) FROM roles
                WHERE lower(code) IN ('superadmin','dirigente','coordenador','treinador','atleta')
                """
            )
        ).scalar()
        == 5
    )

    # alembic_version checks
    alembic_col = db.execute(
        text(
            """
            SELECT data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'alembic_version' AND column_name = 'version_num'
            """
        )
    ).fetchone()
    report["checks"]["alembic_version_column"] = {
        "data_type": alembic_col[0] if alembic_col else None,
        "character_maximum_length": alembic_col[1] if alembic_col else None,
    }
    alembic_version = db.execute(
        text("SELECT version_num FROM alembic_version LIMIT 1")
    ).fetchone()
    report["checks"]["alembic_version"] = alembic_version[0] if alembic_version else None
    report["checks"]["alembic_has_e6"] = bool(
        alembic_version and "e6_add_roles_code" in alembic_version[0]
    )

    # Superadmin user
    superadmin_row = db.execute(
        text("SELECT id, person_id FROM users WHERE is_superadmin = true LIMIT 1")
    ).fetchone()
    if not superadmin_row:
        person_id = str(uuid4())
        user_id = str(uuid4())
        db.execute(
            text(
                """
                INSERT INTO persons (id, full_name, email)
                VALUES (:id, :full_name, :email)
                """
            ),
            {
                "id": person_id,
                "full_name": "Super Administrador",
                "email": "admin@hbtracking.com",
            },
        )
        db.execute(
            text(
                """
                INSERT INTO users (id, email, full_name, person_id, password_hash, status, is_superadmin)
                VALUES (:id, :email, :full_name, :person_id, :password_hash, 'ativo', true)
                """
            ),
            {
                "id": user_id,
                "email": "admin@hbtracking.com",
                "full_name": "Super Administrador",
                "person_id": person_id,
                "password_hash": "seeded",
            },
        )
        _audit_seed(
            db,
            entity="users",
            entity_id=user_id,
            action="seed_insert",
            context={"email": "admin@hbtracking.com", "is_superadmin": True},
        )
        report["seeds"].append("users:superadmin")
        superadmin_row = (user_id, person_id)
    report["checks"]["superadmin_exists"] = True

    # Organization (single)
    org_row = db.execute(
        text(
            """
            SELECT id FROM organizations
            WHERE deleted_at IS NULL
            ORDER BY created_at ASC
            LIMIT 1
            """
        )
    ).fetchone()
    if not org_row:
        org_id = str(uuid4())
        owner_user_id = superadmin_row[0]
        db.execute(
            text(
                """
                INSERT INTO organizations (id, name, owner_user_id, status)
                VALUES (:id, :name, :owner_user_id, 'ativo')
                """
            ),
            {
                "id": org_id,
                "name": "Clube HB Tracking",
                "owner_user_id": owner_user_id,
            },
        )
        _audit_seed(
            db,
            entity="organizations",
            entity_id=org_id,
            action="seed_insert",
            context={"name": "Clube HB Tracking"},
        )
        report["seeds"].append("organizations:clube_hb_tracking")
        org_row = (org_id,)
    report["checks"]["organization_exists"] = True

    organization_id = str(org_row[0])

    # Role IDs
    role_dir = db.execute(
        text("SELECT id FROM roles WHERE lower(code) = 'dirigente' LIMIT 1")
    ).fetchone()
    role_dir_id = int(role_dir[0]) if role_dir else None
    if role_dir_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="role_dirigente_missing",
        )

    # Active season
    today = datetime.now(timezone.utc).date()
    active_season = db.execute(
        text(
            """
            SELECT id FROM seasons
            WHERE organization_id = :org_id
              AND deleted_at IS NULL
              AND canceled_at IS NULL
              AND interrupted_at IS NULL
              AND starts_at IS NOT NULL
              AND ends_at IS NOT NULL
              AND :today BETWEEN starts_at AND ends_at
            ORDER BY starts_at DESC
            LIMIT 1
            """
        ),
        {"org_id": organization_id, "today": today},
    ).fetchone()

    membership_id = None
    if not active_season:
        season_id = str(uuid4())
        membership_id = str(uuid4())
        year = today.year
        db.execute(
            text(
                """
                INSERT INTO seasons (
                    id, organization_id, created_by_membership_id, year, name,
                    starts_at, ends_at, is_active
                )
                VALUES (
                    :id, :org_id, :membership_id, :year, :name,
                    :starts_at, :ends_at, true
                )
                """
            ),
            {
                "id": season_id,
                "org_id": organization_id,
                "membership_id": membership_id,
                "year": year,
                "name": f"Temporada {year}",
                "starts_at": date(year, 1, 1),
                "ends_at": date(year, 12, 31),
            },
        )
        db.execute(
            text(
                """
                INSERT INTO membership (
                    id, organization_id, user_id, person_id, role_id, status, season_id
                )
                VALUES (
                    :id, :org_id, :user_id, :person_id, :role_id, 'ativo', :season_id
                )
                """
            ),
            {
                "id": membership_id,
                "org_id": organization_id,
                "user_id": superadmin_row[0],
                "person_id": superadmin_row[1],
                "role_id": role_dir_id,
                "season_id": season_id,
            },
        )
        _audit_seed(
            db,
            entity="seasons",
            entity_id=season_id,
            action="seed_insert",
            context={"year": year, "name": f"Temporada {year}"},
        )
        _audit_seed(
            db,
            entity="membership",
            entity_id=membership_id,
            action="seed_insert",
            context={"role": "dirigente", "season_id": season_id},
        )
        report["seeds"].append("seasons:active")
        active_season = (season_id,)

    if not membership_id:
        membership_row = db.execute(
            text(
                """
                SELECT id FROM membership
                WHERE organization_id = :org_id
                ORDER BY created_at ASC
                LIMIT 1
                """
            ),
            {"org_id": organization_id},
        ).fetchone()
        if membership_row:
            membership_id = str(membership_row[0])
        else:
            membership_id = str(uuid4())
            db.execute(
                text(
                    """
                    INSERT INTO membership (
                        id, organization_id, user_id, person_id, role_id, status, season_id
                    )
                    VALUES (
                        :id, :org_id, :user_id, :person_id, :role_id, 'ativo', :season_id
                    )
                    """
                ),
                {
                    "id": membership_id,
                    "org_id": organization_id,
                    "user_id": superadmin_row[0],
                    "person_id": superadmin_row[1],
                    "role_id": role_dir_id,
                    "season_id": active_season[0],
                },
            )
            _audit_seed(
                db,
                entity="membership",
                entity_id=membership_id,
                action="seed_insert",
                context={"role": "dirigente", "season_id": active_season[0]},
            )
            report["seeds"].append("membership:dirigente")

    # Planned season
    planned_season = db.execute(
        text(
            """
            SELECT id FROM seasons
            WHERE organization_id = :org_id
              AND deleted_at IS NULL
              AND canceled_at IS NULL
              AND starts_at IS NOT NULL
              AND starts_at > :today
            ORDER BY starts_at ASC
            LIMIT 1
            """
        ),
        {"org_id": organization_id, "today": today},
    ).fetchone()
    if not planned_season:
        next_year = today.year + 1
        season_id = str(uuid4())
        db.execute(
            text(
                """
                INSERT INTO seasons (
                    id, organization_id, created_by_membership_id, year, name,
                    starts_at, ends_at, is_active
                )
                VALUES (
                    :id, :org_id, :membership_id, :year, :name,
                    :starts_at, :ends_at, false
                )
                """
            ),
            {
                "id": season_id,
                "org_id": organization_id,
                "membership_id": membership_id,
                "year": next_year,
                "name": f"Temporada {next_year}",
                "starts_at": date(next_year, 1, 1),
                "ends_at": date(next_year, 12, 31),
            },
        )
        _audit_seed(
            db,
            entity="seasons",
            entity_id=season_id,
            action="seed_insert",
            context={"year": next_year, "name": f"Temporada {next_year}"},
        )
        report["seeds"].append("seasons:planned")

    # Categories
    categories_count = db.execute(text("SELECT COUNT(*) FROM categories")).scalar()
    if categories_count == 0:
        categories = [
            (1, "U12", "Infantil", 10, 12),
            (2, "U14", "Cadete", 13, 14),
            (3, "U16", "Juvenil", 15, 16),
            (4, "U18", "Junior", 17, 18),
            (5, "ADULTO", "Adulto", 19, 39),
            (6, "MASTER", "Master", 40, 60),
        ]
        for cid, code, label, min_age, max_age in categories:
            db.execute(
                text(
                    """
                    INSERT INTO categories (id, code, label, min_age, max_age)
                    VALUES (:id, :code, :label, :min_age, :max_age)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {
                    "id": cid,
                    "code": code,
                    "label": label,
                    "min_age": min_age,
                    "max_age": max_age,
                },
            )
        _audit_seed(
            db,
            entity="categories",
            entity_id=None,
            action="seed_insert",
            context={"count": len(categories)},
        )
        report["seeds"].append("categories")

    # Defensive positions
    def_count = db.execute(text("SELECT COUNT(*) FROM defensive_positions")).scalar()
    if def_count == 0:
        defensive_positions = [
            (1, "1a Defensora", "DEF1"),
            (2, "2a Defensora", "DEF2"),
            (3, "Defensora Base", "DEF_BASE"),
            (4, "Defensora Avancada", "DEF_AV"),
            (5, "Goleira", "GOLEIRA"),
        ]
        for pid, name, code in defensive_positions:
            db.execute(
                text(
                    """
                    INSERT INTO defensive_positions (id, name, code)
                    VALUES (:id, :name, :code)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {"id": pid, "name": name, "code": code},
            )
        _audit_seed(
            db,
            entity="defensive_positions",
            entity_id=None,
            action="seed_insert",
            context={"count": len(defensive_positions)},
        )
        report["seeds"].append("defensive_positions")

    # Offensive positions
    off_count = db.execute(text("SELECT COUNT(*) FROM offensive_positions")).scalar()
    if off_count == 0:
        offensive_positions = [
            (1, "Ponta Esquerda", "PE"),
            (2, "Ponta Direita", "PD"),
            (3, "Pivo", "PIVO"),
            (4, "Lateral Esquerda", "LE"),
            (5, "Lateral Direita", "LD"),
            (6, "Armadora Central", "ARM"),
        ]
        for pid, name, code in offensive_positions:
            db.execute(
                text(
                    """
                    INSERT INTO offensive_positions (id, name, code)
                    VALUES (:id, :name, :code)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {"id": pid, "name": name, "code": code},
            )
        _audit_seed(
            db,
            entity="offensive_positions",
            entity_id=None,
            action="seed_insert",
            context={"count": len(offensive_positions)},
        )
        report["seeds"].append("offensive_positions")

    # Schooling levels
    school_count = db.execute(text("SELECT COUNT(*) FROM schooling_levels")).scalar()
    if school_count == 0:
        schooling_levels = [
            (1, "7o ano Ensino Fundamental", "7EF", 7),
            (2, "8o ano Ensino Fundamental", "8EF", 8),
            (3, "9o ano Ensino Fundamental", "9EF", 9),
            (4, "1o ano Ensino Medio", "1EM", 10),
            (5, "2o ano Ensino Medio", "2EM", 11),
            (6, "3o ano Ensino Medio", "3EM", 12),
        ]
        for sid, name, code, level_order in schooling_levels:
            db.execute(
                text(
                    """
                    INSERT INTO schooling_levels (id, name, code, level_order)
                    VALUES (:id, :name, :code, :level_order)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {
                    "id": sid,
                    "name": name,
                    "code": code,
                    "level_order": level_order,
                },
            )
        _audit_seed(
            db,
            entity="schooling_levels",
            entity_id=None,
            action="seed_insert",
            context={"count": len(schooling_levels)},
        )
        report["seeds"].append("schooling_levels")

    # Institutional team
    team_exists = db.execute(
        text(
            """
            SELECT id, name FROM teams
            WHERE organization_id = :org_id
              AND season_id = :season_id
              AND deleted_at IS NULL
            """
        ),
        {"org_id": organization_id, "season_id": active_season[0]},
    ).fetchall()

    if team_exists:
        hints = _normalized_hints()
        report["checks"]["institutional_team_found"] = any(
            _name_matches(row[1], hints) for row in team_exists
        )
    else:
        report["checks"]["institutional_team_found"] = False

    if not report["checks"]["institutional_team_found"]:
        category_row = db.execute(
            text("SELECT id FROM categories ORDER BY id ASC LIMIT 1")
        ).fetchone()
        if category_row:
            team_id = str(uuid4())
            db.execute(
                text(
                    """
                    INSERT INTO teams (
                        id, organization_id, created_by_membership_id, season_id, category_id, name
                    )
                    VALUES (
                        :id, :org_id, :membership_id, :season_id, :category_id, :name
                    )
                    ON CONFLICT (season_id, category_id, name) DO NOTHING
                    """
                ),
                {
                    "id": team_id,
                    "org_id": organization_id,
                    "membership_id": membership_id,
                    "season_id": active_season[0],
                    "category_id": int(category_row[0]),
                    "name": "Equipe Institucional",
                },
            )
            _audit_seed(
                db,
                entity="teams",
                entity_id=team_id,
                action="seed_insert",
                context={
                    "season_id": str(active_season[0]),
                    "name": "Equipe Institucional",
                },
            )
            report["seeds"].append("teams:institucional")
            report["checks"]["institutional_team_found"] = True
        else:
            report["warnings"].append("no_categories_for_institutional_team")

    return {"status": "ok", "report": report}


@router.get("/health/utc-season", status_code=status.HTTP_200_OK)
def health_utc_season(db: Session = Depends(get_db)) -> dict[str, Any]:
    _ensure_dev_only()

    now_utc = datetime.now(timezone.utc)
    today = now_utc.date()

    season_row = db.execute(
        text(
            """
            SELECT id, starts_at, ends_at, canceled_at, interrupted_at
            FROM seasons
            WHERE deleted_at IS NULL
            ORDER BY starts_at DESC NULLS LAST, created_at DESC
            LIMIT 1
            """
        )
    ).fetchone()

    status_name = None
    season_id = None
    if season_row:
        season_id = str(season_row[0])
        starts_at = season_row[1]
        ends_at = season_row[2]
        canceled_at = season_row[3]
        interrupted_at = season_row[4]

        if canceled_at is not None:
            status_name = "cancelada"
        elif interrupted_at is not None:
            status_name = "interrompida"
        elif starts_at and ends_at and today > ends_at:
            status_name = "encerrada"
        elif starts_at and ends_at and starts_at <= today <= ends_at:
            status_name = "ativa"
        else:
            status_name = "planejada"

    has_institutional_team = False
    if season_id:
        teams = db.execute(
            text(
                """
                SELECT name FROM teams
                WHERE season_id = :season_id AND deleted_at IS NULL
                """
            ),
            {"season_id": season_id},
        ).fetchall()
        hints = _normalized_hints()
        has_institutional_team = any(_name_matches(row[0], hints) for row in teams)

    return {
        "now_utc": now_utc.isoformat(),
        "season_status": status_name,
        "has_institutional_team": has_institutional_team,
    }


@router.get("/cache/stats")
def get_cache_statistics() -> dict[str, Any]:
    """
    Retorna estatísticas dos caches server-side (dev-only).

    Mostra:
    - Tamanho atual de cada cache
    - Capacidade máxima
    - TTL configurado
    """
    _ensure_dev_only()
    return get_cache_stats()


@router.post("/cache/clear")
def clear_cache() -> dict[str, str]:
    """
    Limpa todos os caches server-side (dev-only).

    Útil para:
    - Testes
    - Forçar refresh de dados
    - Debug
    """
    _ensure_dev_only()
    clear_all_caches()
    return {"status": "success", "message": "Todos os caches foram limpos"}
