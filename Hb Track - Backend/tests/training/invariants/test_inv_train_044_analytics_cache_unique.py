"""
INV-TRAIN-044 — Unicidade de cache lookup (team + microcycle + month + granularity)

RUNTIME DB TEST - Testa constraint UNIQUE real no Postgres via IntegrityError.

Obrigação A:
- Tabela: training_analytics_cache
- Colunas: training_analytics_cache.team_id (UUID, NOT NULL), training_analytics_cache.microcycle_id (UUID, nullable),
           training_analytics_cache.month (DATE, nullable), training_analytics_cache.granularity (VARCHAR, NOT NULL)
- Constraint: uq_training_analytics_cache_lookup UNIQUE (team_id, microcycle_id, month, granularity)
- Schema: schema.sql:3661

Obrigação B:
- SQLSTATE: 23505 (unique_violation)
- constraint_name: uq_training_analytics_cache_lookup

Este teste NÃO usa string match. Ele insere registros no DB e verifica
que a constraint é imposta pelo Postgres.

Nota: PostgreSQL trata NULLs como distintos em UNIQUE constraints padrão.
Para testar duplicatas, usamos campos com valores reais (não-NULL).
"""

from datetime import date
from uuid import uuid4, UUID

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tests._helpers.pg_error import assert_pg_constraint_violation
from app.models.category import Category
from app.models.organization import Organization
from app.models.person import Person
from app.models.team import Team
from app.models.user import User
from app.models.training_microcycle import TrainingMicrocycle
from app.models.training_analytics_cache import TrainingAnalyticsCache


# ============================================
# FIXTURES LOCAIS (isoladas para este teste)
# ============================================

@pytest_asyncio.fixture
async def inv044_category(async_db: AsyncSession) -> Category:
    """Categoria de teste para INV-TRAIN-044."""
    category = Category(
        id=9944,
        name="Categoria INV-044",
        max_age=19,
        is_active=True,
    )
    async_db.add(category)
    await async_db.flush()
    return category


@pytest_asyncio.fixture
async def inv044_organization(async_db: AsyncSession) -> Organization:
    """Organização de teste para INV-TRAIN-044."""
    org = Organization(
        id=str(uuid4()),
        name="Org INV-TRAIN-044",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv044_person(async_db: AsyncSession) -> Person:
    """Pessoa de teste para INV-TRAIN-044."""
    person = Person(
        id=str(uuid4()),
        full_name="Teste INV-044",
        first_name="Teste",
        last_name="INV-044",
        birth_date=date(1990, 1, 1),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv044_user(async_db: AsyncSession, inv044_person: Person) -> User:
    """Usuário de teste para INV-TRAIN-044."""
    user = User(
        id=str(uuid4()),
        person_id=inv044_person.id,
        email=f"inv044_{uuid4().hex[:8]}@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest_asyncio.fixture
async def inv044_team(
    async_db: AsyncSession,
    inv044_category: Category,
    inv044_organization: Organization,
) -> Team:
    """Equipe de teste para INV-TRAIN-044."""
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv044_organization.id),
        name="Equipe INV-044",
        category_id=inv044_category.id,
        gender="feminino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


@pytest_asyncio.fixture
async def inv044_microcycle(
    async_db: AsyncSession,
    inv044_organization: Organization,
    inv044_team: Team,
    inv044_user: User,
) -> TrainingMicrocycle:
    """Microciclo de teste para INV-TRAIN-044."""
    microcycle = TrainingMicrocycle(
        id=uuid4(),
        organization_id=UUID(inv044_organization.id),
        team_id=inv044_team.id,
        week_start=date(2026, 1, 6),
        week_end=date(2026, 1, 12),
        created_by_user_id=UUID(inv044_user.id),
    )
    async_db.add(microcycle)
    await async_db.flush()
    return microcycle


# ============================================
# TESTES RUNTIME
# ============================================

class TestInvTrain044AnalyticsCacheUnique:
    """
    Testes RUNTIME para INV-TRAIN-044: uq_training_analytics_cache_lookup.

    Prova que o Postgres impõe unicidade (team_id, microcycle_id, month, granularity).

    Obrigação A:
    - Tabela: training_analytics_cache
    - Colunas: training_analytics_cache.team_id, training_analytics_cache.microcycle_id,
               training_analytics_cache.month, training_analytics_cache.granularity
    - Constraint: uq_training_analytics_cache_lookup UNIQUE (team_id, microcycle_id, month, granularity)
    - Schema: schema.sql:3661

    Obrigação B:
    - SQLSTATE: 23505 (unique_violation)
    - constraint_name: uq_training_analytics_cache_lookup
    """

    @pytest.mark.asyncio
    async def test_valid_case__unique_combination_accepted(
        self,
        async_db: AsyncSession,
        inv044_team: Team,
        inv044_microcycle: TrainingMicrocycle,
    ):
        """
        CASO POSITIVO: Combinações únicas devem ser aceitas.

        Evidência: schema.sql:3661 - UNIQUE (team_id, microcycle_id, month, granularity)
        """
        # Cache 1: weekly para microciclo específico
        cache1 = TrainingAnalyticsCache(
            id=uuid4(),
            team_id=inv044_team.id,
            microcycle_id=inv044_microcycle.id,
            month=date(2026, 1, 1),
            granularity="weekly",
        )
        async_db.add(cache1)
        await async_db.flush()

        # Cache 2: monthly para mesmo time/microcycle/month (granularity diferente - OK)
        cache2 = TrainingAnalyticsCache(
            id=uuid4(),
            team_id=inv044_team.id,
            microcycle_id=inv044_microcycle.id,
            month=date(2026, 1, 1),
            granularity="monthly",  # diferente
        )
        async_db.add(cache2)
        await async_db.flush()

        assert cache1.id is not None
        assert cache2.id is not None

    @pytest.mark.asyncio
    async def test_invalid_case_1__duplicate_weekly_cache(
        self,
        async_db: AsyncSession,
        inv044_team: Team,
        inv044_microcycle: TrainingMicrocycle,
    ):
        """
        CASO NEGATIVO 1: Duplicata de cache weekly deve ser rejeitada.

        Evidência: schema.sql:3661 - UNIQUE (team_id, microcycle_id, month, granularity)
        """
        month_ref = date(2026, 2, 1)

        # Cache original
        cache1 = TrainingAnalyticsCache(
            id=uuid4(),
            team_id=inv044_team.id,
            microcycle_id=inv044_microcycle.id,
            month=month_ref,
            granularity="weekly",
        )
        async_db.add(cache1)
        await async_db.flush()

        # Duplicata (mesma combinação completa)
        cache_dup = TrainingAnalyticsCache(
            id=uuid4(),
            team_id=inv044_team.id,  # mesmo
            microcycle_id=inv044_microcycle.id,  # mesmo
            month=month_ref,  # mesmo
            granularity="weekly",  # mesmo
        )
        async_db.add(cache_dup)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Verifica SQLSTATE e constraint via helper canônico
        assert_pg_constraint_violation(
            exc_info,
            "23505",
            "uq_training_analytics_cache_lookup"
        )

        await async_db.rollback()

    @pytest.mark.asyncio
    async def test_invalid_case_2__duplicate_monthly_cache(
        self,
        async_db: AsyncSession,
        inv044_team: Team,
        inv044_microcycle: TrainingMicrocycle,
    ):
        """
        CASO NEGATIVO 2: Duplicata de cache monthly deve ser rejeitada.

        Evidência: schema.sql:3661 - UNIQUE (team_id, microcycle_id, month, granularity)
        """
        month_ref = date(2026, 3, 1)

        # Cache original
        cache1 = TrainingAnalyticsCache(
            id=uuid4(),
            team_id=inv044_team.id,
            microcycle_id=inv044_microcycle.id,
            month=month_ref,
            granularity="monthly",
        )
        async_db.add(cache1)
        await async_db.flush()

        # Duplicata (mesma combinação completa)
        cache_dup = TrainingAnalyticsCache(
            id=uuid4(),
            team_id=inv044_team.id,  # mesmo
            microcycle_id=inv044_microcycle.id,  # mesmo
            month=month_ref,  # mesmo
            granularity="monthly",  # mesmo
        )
        async_db.add(cache_dup)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Verifica SQLSTATE e constraint via helper canônico
        assert_pg_constraint_violation(
            exc_info,
            "23505",
            "uq_training_analytics_cache_lookup"
        )

        await async_db.rollback()
