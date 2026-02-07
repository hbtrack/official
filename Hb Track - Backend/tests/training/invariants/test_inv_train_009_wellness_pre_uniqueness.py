"""
INV-TRAIN-009 — Unicidade: 1 wellness_pre por athlete×session (apenas ativos)

Classe: A (DB Constraint - UNIQUE INDEX parcial)
Evidência: schema.sql:5187 (ux_wellness_pre_session_athlete)
Predicate: WHERE deleted_at IS NULL

Obrigação A (Requisitos de Inserção - payload mínimo p/ wellness_pre):
- FKs obrigatórias:
  1) organization_id  (wellness_pre.organization_id FK -> organizations)
  2) training_session_id (wellness_pre.training_session_id FK -> training_sessions)
  3) athlete_id (wellness_pre.athlete_id FK -> athletes)
  4) created_by_user_id (wellness_pre.created_by_user_id FK -> users)
- NOT NULL (sem depender de defaults do ORM):
  sleep_hours, sleep_quality, fatigue_pre, stress_level, muscle_soreness
  (timestamps têm default no DB, mas setamos explicitamente para evitar falsos positivos)

Obrigação B (Critério de Falha):
- Invariante alvo: ux_wellness_pre_session_athlete (UNIQUE INDEX)
- SQLSTATE esperado: 23505 (unique_violation)
- Constraint/index name (quando exposto): ux_wellness_pre_session_athlete
- Estratégia: pytest.raises(IntegrityError) + assert pgcode + constraint_name (se disponível)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from uuid import UUID, uuid4

import re

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.organization import Organization
from app.models.person import Person
from app.models.team import Team
from app.models.user import User
from app.models.athlete import Athlete
from app.models.training_session import TrainingSession
from app.models.wellness_pre import WellnessPre


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _pgcode_from_orig(orig) -> str | None:
    """Extract SQLSTATE from driver-specific exception object."""
    # psycopg2/psycopg3: pgcode; asyncpg: sqlstate
    return getattr(orig, "pgcode", None) or getattr(orig, "sqlstate", None)


def _constraint_name_from_orig(orig) -> str | None:
    """
    Extract constraint/index name deterministically.

    Priority:
      1) psycopg diag.constraint_name (structured, when available)
      2) driver attribute constraint_name (some drivers expose it)
      3) regex on exception message (Postgres always includes it in text)
    """
    # Try structured access first
    diag = getattr(orig, "diag", None)
    name = getattr(diag, "constraint_name", None)
    if name:
        return name

    name = getattr(orig, "constraint_name", None)
    if name:
        return name

    # Fallback: parse from Postgres error message
    # Common formats:
    #   ... violates unique constraint "NAME"
    #   ... violates unique index "NAME"
    msg = str(orig) if orig else ""
    m = re.search(r'violates unique (?:constraint|index) "([^"]+)"', msg)
    if m:
        return m.group(1)
    return None


# -----------------------
# FIXTURES (mínimas)
# -----------------------

@pytest_asyncio.fixture
async def inv009_category(async_db: AsyncSession) -> Category:
    # anti-colisão: nada fixo
    cat_id = int(uuid4().int % 1_000_000)
    cat = Category(
        id=cat_id,
        name=f"Cat INV-009 {uuid4().hex[:6]}",
        max_age=20,
        is_active=True,
    )
    async_db.add(cat)
    await async_db.flush()
    return cat


@pytest_asyncio.fixture
async def inv009_org(async_db: AsyncSession) -> Organization:
    org = Organization(
        id=str(uuid4()),
        name=f"Org INV-009 {uuid4().hex[:6]}",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv009_person(async_db: AsyncSession) -> Person:
    person = Person(
        id=str(uuid4()),
        full_name="Atleta INV-009",
        first_name="Atleta",
        last_name="INV-009",
        birth_date=date(1995, 1, 1),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv009_user(async_db: AsyncSession, inv009_person: Person) -> User:
    user = User(
        id=str(uuid4()),
        person_id=inv009_person.id,
        email=f"inv009_{uuid4().hex[:8]}@test.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest_asyncio.fixture
async def inv009_team(
    async_db: AsyncSession,
    inv009_category: Category,
    inv009_org: Organization,
) -> Team:
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv009_org.id),
        name=f"Team INV-009 {uuid4().hex[:6]}",
        category_id=inv009_category.id,
        gender="masculino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


@pytest_asyncio.fixture
async def inv009_athlete(
    async_db: AsyncSession,
    inv009_person: Person,
    inv009_org: Organization,
) -> Athlete:
    # IMPORTANT: wellness_pre.athlete_id FK -> athletes.id (NOT person.id!)
    # Athlete model requires: athlete_name (NOT NULL), birth_date (NOT NULL)
    athlete = Athlete(
        id=uuid4(),
        organization_id=UUID(inv009_org.id),
        person_id=inv009_person.id,
        athlete_name=inv009_person.full_name or "Atleta INV-009",
        birth_date=inv009_person.birth_date or date(1995, 1, 1),
    )
    async_db.add(athlete)
    await async_db.flush()
    return athlete


@pytest_asyncio.fixture
async def inv009_session_1(
    async_db: AsyncSession,
    inv009_org: Organization,
    inv009_team: Team,
    inv009_user: User,
) -> TrainingSession:
    sess = TrainingSession(
        id=uuid4(),
        organization_id=UUID(inv009_org.id),
        team_id=inv009_team.id,
        session_at=_now() + timedelta(hours=2),
        duration_planned_minutes=90,
        session_type="quadra",
        main_objective="INV-009 session 1",
        location="Ginasio",
        status="draft",
        created_by_user_id=UUID(inv009_user.id),
    )
    async_db.add(sess)
    await async_db.flush()
    return sess


@pytest_asyncio.fixture
async def inv009_session_2(
    async_db: AsyncSession,
    inv009_org: Organization,
    inv009_team: Team,
    inv009_user: User,
) -> TrainingSession:
    sess = TrainingSession(
        id=uuid4(),
        organization_id=UUID(inv009_org.id),
        team_id=inv009_team.id,
        session_at=_now() + timedelta(hours=4),
        duration_planned_minutes=90,
        session_type="quadra",
        main_objective="INV-009 session 2",
        location="Ginasio",
        status="draft",
        created_by_user_id=UUID(inv009_user.id),
    )
    async_db.add(sess)
    await async_db.flush()
    return sess


# -----------------------
# TESTES (1 válido + 2 bordas)
# -----------------------

class TestInvTrain009WellnessPreUniqueness:
    """
    INV-TRAIN-009: UNIQUE INDEX parcial (training_session_id, athlete_id) WHERE deleted_at IS NULL
    Prova: Runtime Integration via async_db.
    SQLSTATE: 23505 (unique_violation)
    """

    @pytest.mark.asyncio
    async def test_valid__same_athlete_different_sessions_accepted(
        self,
        async_db: AsyncSession,
        inv009_org: Organization,
        inv009_user: User,
        inv009_athlete: Athlete,
        inv009_session_1: TrainingSession,
        inv009_session_2: TrainingSession,
    ):
        # mesmo athlete em sessões diferentes -> permitido
        w1 = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv009_org.id),
            training_session_id=inv009_session_1.id,
            athlete_id=inv009_athlete.id,
            sleep_hours=8.0,
            sleep_quality=3,
            fatigue_pre=2,
            stress_level=2,
            muscle_soreness=1,
            created_by_user_id=UUID(inv009_user.id),
            filled_at=_now(),
            created_at=_now(),
            updated_at=_now(),
            deleted_at=None,
            deleted_reason=None,
        )
        w2 = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv009_org.id),
            training_session_id=inv009_session_2.id,
            athlete_id=inv009_athlete.id,
            sleep_hours=7.5,
            sleep_quality=4,
            fatigue_pre=3,
            stress_level=1,
            muscle_soreness=2,
            created_by_user_id=UUID(inv009_user.id),
            filled_at=_now(),
            created_at=_now(),
            updated_at=_now(),
            deleted_at=None,
            deleted_reason=None,
        )
        async_db.add_all([w1, w2])
        await async_db.flush()

        assert w1.id is not None
        assert w2.id is not None

    @pytest.mark.asyncio
    async def test_invalid__duplicate_same_session_rejected(
        self,
        async_db: AsyncSession,
        inv009_org: Organization,
        inv009_user: User,
        inv009_athlete: Athlete,
        inv009_session_1: TrainingSession,
    ):
        # 1º registro (ativo)
        w1 = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv009_org.id),
            training_session_id=inv009_session_1.id,
            athlete_id=inv009_athlete.id,
            sleep_hours=8.0,
            sleep_quality=3,
            fatigue_pre=2,
            stress_level=2,
            muscle_soreness=1,
            created_by_user_id=UUID(inv009_user.id),
            filled_at=_now(),
            created_at=_now(),
            updated_at=_now(),
            deleted_at=None,
            deleted_reason=None,
        )
        async_db.add(w1)
        await async_db.flush()

        # 2º registro com mesma dupla athlete×session (ativo) -> viola UNIQUE parcial
        w2 = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv009_org.id),
            training_session_id=inv009_session_1.id,
            athlete_id=inv009_athlete.id,
            sleep_hours=7.0,
            sleep_quality=4,
            fatigue_pre=3,
            stress_level=1,
            muscle_soreness=2,
            created_by_user_id=UUID(inv009_user.id),
            filled_at=_now(),
            created_at=_now(),
            updated_at=_now(),
            deleted_at=None,
            deleted_reason=None,
        )
        async_db.add(w2)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        orig = exc_info.value.orig
        assert _pgcode_from_orig(orig) == "23505"

        cname = _constraint_name_from_orig(orig)
        assert cname == "ux_wellness_pre_session_athlete", (
            f"Expected constraint ux_wellness_pre_session_athlete, got {cname!r}. "
            f"orig={type(orig).__name__} msg={str(orig)!r}"
        )

        await async_db.rollback()

    @pytest.mark.asyncio
    async def test_invalid__duplicate_same_session_different_data_rejected(
        self,
        async_db: AsyncSession,
        inv009_org: Organization,
        inv009_user: User,
        inv009_athlete: Athlete,
        inv009_session_1: TrainingSession,
    ):
        """
        Segundo caso de borda: mesma dupla athlete×session, mas com dados
        completamente diferentes (valores extremos). Prova que a constraint
        é baseada em (session_id, athlete_id), não nos valores dos campos.
        """
        # 1º registro com valores mínimos
        w1 = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv009_org.id),
            training_session_id=inv009_session_1.id,
            athlete_id=inv009_athlete.id,
            sleep_hours=4.0,
            sleep_quality=1,
            fatigue_pre=0,
            stress_level=0,
            muscle_soreness=0,
            created_by_user_id=UUID(inv009_user.id),
            filled_at=_now(),
            created_at=_now(),
            updated_at=_now(),
            deleted_at=None,
            deleted_reason=None,
        )
        async_db.add(w1)
        await async_db.flush()

        # 2º registro com valores máximos (dados totalmente diferentes)
        w2 = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv009_org.id),
            training_session_id=inv009_session_1.id,
            athlete_id=inv009_athlete.id,
            sleep_hours=12.0,
            sleep_quality=5,
            fatigue_pre=10,
            stress_level=10,
            muscle_soreness=10,
            created_by_user_id=UUID(inv009_user.id),
            filled_at=_now(),
            created_at=_now(),
            updated_at=_now(),
            deleted_at=None,
            deleted_reason=None,
        )
        async_db.add(w2)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        orig = exc_info.value.orig
        assert _pgcode_from_orig(orig) == "23505"

        cname = _constraint_name_from_orig(orig)
        assert cname == "ux_wellness_pre_session_athlete", (
            f"Expected constraint ux_wellness_pre_session_athlete, got {cname!r}. "
            f"orig={type(orig).__name__} msg={str(orig)!r}"
        )

        await async_db.rollback()

    @pytest.mark.asyncio
    async def test_valid__soft_deleted_row_does_not_block_new_active_row(
        self,
        async_db: AsyncSession,
        inv009_org: Organization,
        inv009_user: User,
        inv009_athlete: Athlete,
        inv009_session_1: TrainingSession,
    ):
        # prova do predicado WHERE deleted_at IS NULL:
        # se o registro anterior está soft-deletado (deleted_at NOT NULL),
        # um novo ativo com mesma dupla deve ser ACEITO.

        w_deleted = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv009_org.id),
            training_session_id=inv009_session_1.id,
            athlete_id=inv009_athlete.id,
            sleep_hours=8.0,
            sleep_quality=3,
            fatigue_pre=2,
            stress_level=2,
            muscle_soreness=1,
            created_by_user_id=UUID(inv009_user.id),
            filled_at=_now(),
            created_at=_now(),
            updated_at=_now(),
            deleted_at=_now(),
            deleted_reason="cleanup test INV-009",
        )
        async_db.add(w_deleted)
        await async_db.flush()

        w_active = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv009_org.id),
            training_session_id=inv009_session_1.id,
            athlete_id=inv009_athlete.id,
            sleep_hours=7.0,
            sleep_quality=4,
            fatigue_pre=3,
            stress_level=1,
            muscle_soreness=2,
            created_by_user_id=UUID(inv009_user.id),
            filled_at=_now(),
            created_at=_now(),
            updated_at=_now(),
            deleted_at=None,
            deleted_reason=None,
        )
        async_db.add(w_active)
        await async_db.flush()

        assert w_active.id is not None
