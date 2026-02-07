"""
INV-TRAIN-043 — Data de início do microciclo deve ser anterior à data de término

RUNTIME DB TEST - Testa constraint real no Postgres via IntegrityError.

Obrigação A:
- Tabela: training_microcycles
- Colunas: training_microcycles.week_start (DATE, NOT NULL), training_microcycles.week_end (DATE, NOT NULL)
- Constraint: check_microcycle_dates CHECK ((week_start < week_end))
- Schema: schema.sql:2462

Obrigação B:
- SQLSTATE: 23514 (CHECK violation)
- constraint_name: check_microcycle_dates

Este teste NÃO usa string match. Ele insere registros no DB e verifica
que a constraint é imposta pelo Postgres.
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


# ============================================
# FIXTURES LOCAIS (isoladas para este teste)
# ============================================

@pytest_asyncio.fixture
async def inv043_category(async_db: AsyncSession) -> Category:
    """Categoria de teste para INV-TRAIN-043."""
    category = Category(
        id=9943,
        name="Categoria INV-043",
        max_age=19,
        is_active=True,
    )
    async_db.add(category)
    await async_db.flush()
    return category


@pytest_asyncio.fixture
async def inv043_organization(async_db: AsyncSession) -> Organization:
    """Organização de teste para INV-TRAIN-043."""
    org = Organization(
        id=str(uuid4()),
        name="Org INV-TRAIN-043",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv043_person(async_db: AsyncSession) -> Person:
    """Pessoa de teste para INV-TRAIN-043."""
    person = Person(
        id=str(uuid4()),
        full_name="Teste INV-043",
        first_name="Teste",
        last_name="INV-043",
        birth_date=date(1990, 1, 1),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv043_user(async_db: AsyncSession, inv043_person: Person) -> User:
    """Usuário de teste para INV-TRAIN-043."""
    user = User(
        id=str(uuid4()),
        person_id=inv043_person.id,
        email=f"inv043_{uuid4().hex[:8]}@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest_asyncio.fixture
async def inv043_team(
    async_db: AsyncSession,
    inv043_category: Category,
    inv043_organization: Organization,
) -> Team:
    """Equipe de teste para INV-TRAIN-043."""
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv043_organization.id),
        name="Equipe INV-043",
        category_id=inv043_category.id,
        gender="feminino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


# ============================================
# TESTES RUNTIME
# ============================================

class TestInvTrain043MicrocycleDatesCheck:
    """
    Testes RUNTIME para INV-TRAIN-043: check_microcycle_dates.

    Prova que o Postgres impõe week_start < week_end em training_microcycles.

    Obrigação A:
    - Tabela: training_microcycles
    - Colunas: training_microcycles.week_start (DATE, NOT NULL), training_microcycles.week_end (DATE, NOT NULL)
    - Constraint: check_microcycle_dates CHECK ((week_start < week_end))
    - Schema: schema.sql:2462

    Obrigação B:
    - SQLSTATE: 23514 (CHECK violation)
    - constraint_name: check_microcycle_dates
    """

    @pytest.mark.asyncio
    async def test_valid_case__week_start_before_week_end(
        self,
        async_db: AsyncSession,
        inv043_organization: Organization,
        inv043_team: Team,
        inv043_user: User,
    ):
        """
        CASO POSITIVO: week_start < week_end deve ser aceito.

        Evidência: schema.sql:2462 - CHECK ((week_start < week_end))
        """
        microcycle = TrainingMicrocycle(
            id=uuid4(),
            organization_id=UUID(inv043_organization.id),
            team_id=inv043_team.id,
            week_start=date(2026, 1, 6),   # Segunda-feira
            week_end=date(2026, 1, 12),    # Domingo
            created_by_user_id=UUID(inv043_user.id),
        )
        async_db.add(microcycle)
        await async_db.flush()

        # Se chegou aqui sem exceção, constraint passou
        assert microcycle.id is not None

    @pytest.mark.asyncio
    async def test_invalid_case_1__week_start_equals_week_end(
        self,
        async_db: AsyncSession,
        inv043_organization: Organization,
        inv043_team: Team,
        inv043_user: User,
    ):
        """
        CASO NEGATIVO 1: week_start = week_end deve ser rejeitado.

        Evidência: schema.sql:2462 - CHECK ((week_start < week_end))
        A constraint exige estritamente < (não <=).
        """
        microcycle = TrainingMicrocycle(
            id=uuid4(),
            organization_id=UUID(inv043_organization.id),
            team_id=inv043_team.id,
            week_start=date(2026, 1, 6),
            week_end=date(2026, 1, 6),  # IGUAL - deve falhar
            created_by_user_id=UUID(inv043_user.id),
        )
        async_db.add(microcycle)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Verifica SQLSTATE e constraint via helper canônico
        assert_pg_constraint_violation(
            exc_info,
            "23514",
            "check_microcycle_dates"
        )

        # Rollback após IntegrityError para limpar sessão
        await async_db.rollback()

    @pytest.mark.asyncio
    async def test_invalid_case_2__week_start_after_week_end(
        self,
        async_db: AsyncSession,
        inv043_organization: Organization,
        inv043_team: Team,
        inv043_user: User,
    ):
        """
        CASO NEGATIVO 2: week_start > week_end deve ser rejeitado.

        Evidência: schema.sql:2462 - CHECK ((week_start < week_end))
        """
        microcycle = TrainingMicrocycle(
            id=uuid4(),
            organization_id=UUID(inv043_organization.id),
            team_id=inv043_team.id,
            week_start=date(2026, 1, 12),  # Domingo
            week_end=date(2026, 1, 6),     # Segunda anterior - deve falhar
            created_by_user_id=UUID(inv043_user.id),
        )
        async_db.add(microcycle)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Verifica SQLSTATE e constraint via helper canônico
        assert_pg_constraint_violation(
            exc_info,
            "23514",
            "check_microcycle_dates"
        )

        # Rollback após IntegrityError para limpar sessão
        await async_db.rollback()
