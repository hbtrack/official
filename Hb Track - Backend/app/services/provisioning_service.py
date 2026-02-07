"""
Helpers for provisioning users and athletes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID
import unicodedata
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.organization import Organization
from app.models.role import Role
from app.models.season import Season
from app.models.team import Team
from app.models.category import Category


ZERO_UUID = "00000000-0000-0000-0000-000000000000"


@dataclass(frozen=True)
class SeasonSelection:
    season: Season
    is_future: bool


async def resolve_organization_id(db: AsyncSession, preferred_id: Optional[str]) -> str:
    if preferred_id and str(preferred_id) != ZERO_UUID:
        return str(preferred_id)

    result = await db.execute(
        select(Organization)
        .where(Organization.deleted_at.is_(None))
        .order_by(Organization.created_at.asc())
    )
    orgs = result.scalars().all()

    if not orgs:
        raise ValueError("organization_not_found")
    if len(orgs) > 1:
        raise ValueError("multiple_organizations")

    return str(orgs[0].id)


async def resolve_role_id(db: AsyncSession, role_code: str) -> int:
    result = await db.execute(
        select(Role).where(Role.code == role_code)
    )
    role = result.scalar_one_or_none()
    if not role:
        raise ValueError("role_not_found")
    return int(role.id)


async def select_current_or_next_season(db: AsyncSession, organization_id: str) -> SeasonSelection:
    today = date.today()
    org_id = UUID(str(organization_id))
    base = (
        select(Season)
        .join(Team, Season.team_id == Team.id)
        .where(Team.organization_id == org_id)
        .where(Season.deleted_at.is_(None))
        .where(Season.canceled_at.is_(None))
        .where(Season.interrupted_at.is_(None))
    )

    result = await db.execute(
        base.where(Season.start_date <= today)
        .where(Season.end_date >= today)
        .order_by(Season.start_date.desc())
        .limit(1)
    )
    active = result.scalar_one_or_none()
    if active:
        return SeasonSelection(active, False)

    result = await db.execute(
        base.where(Season.start_date > today)
        .order_by(Season.start_date.asc())
        .limit(1)
    )
    planned = result.scalar_one_or_none()
    if planned:
        return SeasonSelection(planned, True)

    raise ValueError("season_not_found")


async def calculate_category_id(db: AsyncSession, *, birth_date: date, season_start: date) -> int:
    age = season_start.year - birth_date.year
    if (season_start.month, season_start.day) < (birth_date.month, birth_date.day):
        age -= 1

    result = await db.execute(
        select(Category)
        .where((Category.min_age.is_(None)) | (Category.min_age <= age))
        .where((Category.max_age.is_(None)) | (Category.max_age >= age))
        .order_by(Category.min_age.desc())
        .limit(1)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise ValueError("category_not_found")
    return int(category.id)


async def find_institutional_team(
    db: AsyncSession,
    *,
    organization_id: str,
    season_id: str,
    category_id: Optional[int],
) -> Team:
    if settings.INSTITUTIONAL_TEAM_ID:
        team = await db.get(Team, settings.INSTITUTIONAL_TEAM_ID)
        if not team or team.deleted_at is not None:
            raise ValueError("institutional_team_missing")
        if str(team.organization_id) != str(organization_id):
            raise ValueError("institutional_team_mismatch")
        if str(team.season_id) != str(season_id):
            raise ValueError("institutional_team_mismatch")
        return team

    stmt = (
        select(Team)
        .where(Team.organization_id == str(organization_id))
        .where(Team.season_id == str(season_id))
        .where(Team.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    teams = list(result.scalars().all())

    if category_id is not None:
        category_teams = [team for team in teams if team.category_id == category_id]
        if category_teams:
            teams = category_teams

    hints = _normalized_hints()
    matches = [
        team for team in teams
        if _name_matches(team.name, hints)
    ]
    if not matches:
        raise ValueError("institutional_team_missing")

    matches.sort(key=lambda team: (_name_score(team.name, hints), team.created_at))
    return matches[0]


def _normalized_hints() -> list[str]:
    raw = settings.INSTITUTIONAL_TEAM_ALIASES or ""
    parts = [part.strip() for part in raw.split(",") if part.strip()]
    if not parts:
        parts = ["equipe institucional", "grupo de avaliacao", "institucional", "avaliacao"]
    return [_normalize_name(part) for part in parts]


def _name_matches(name: str, hints: Iterable[str]) -> bool:
    normalized = _normalize_name(name)
    return any(hint in normalized for hint in hints)


def _name_score(name: str, hints: Iterable[str]) -> int:
    normalized = _normalize_name(name)
    if "institucional" in normalized:
        return 0
    if "avaliacao" in normalized:
        return 1
    for hint in hints:
        if hint in normalized:
            return 2
    return 3


def _normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_accents = "".join(
        char for char in normalized
        if not unicodedata.combining(char)
    )
    return without_accents.lower().strip()
