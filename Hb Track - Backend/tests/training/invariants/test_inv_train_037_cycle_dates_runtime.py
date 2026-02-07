"""
INV-TRAIN-037 — Data de início do ciclo deve ser anterior à data de término

RUNTIME DB TEST - Testa constraint real no Postgres via IntegrityError.

Evidência:
- Constraint: `check_cycle_dates CHECK ((start_date < end_date))`
- Schema: `Hb Track - Backend/docs/_generated/schema.sql:2402`
- Model: `app/models/training_cycle.py:110` (CheckConstraint)

Este teste NÃO usa string match. Ele insere registros no DB e verifica
que a constraint é imposta pelo Postgres (SQLSTATE 23514 para CHECK).
"""

from datetime import date, datetime, timezone
from uuid import uuid4, UUID

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.organization import Organization
from app.models.person import Person
from app.models.team import Team
from app.models.user import User
from app.models.training_cycle import TrainingCycle


# ============================================
# FIXTURES LOCAIS (isoladas para este teste)
# ============================================

@pytest_asyncio.fixture
async def inv037_category(async_db: AsyncSession) -> Category:
    """Categoria de teste para INV-TRAIN-037."""
    category = Category(
        id=9937,
        name="Categoria INV-037",
        max_age=19,
        is_active=True,
    )
    async_db.add(category)
    await async_db.flush()
    return category


@pytest_asyncio.fixture
async def inv037_organization(async_db: AsyncSession) -> Organization:
    """Organização de teste para INV-TRAIN-037."""
    org = Organization(
        id=str(uuid4()),
        name="Org INV-TRAIN-037",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv037_person(async_db: AsyncSession) -> Person:
    """Pessoa de teste para INV-TRAIN-037."""
    person = Person(
        id=str(uuid4()),
        full_name="Teste INV-037",
        first_name="Teste",
        last_name="INV-037",
        birth_date=date(1990, 1, 1),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv037_user(async_db: AsyncSession, inv037_person: Person) -> User:
    """Usuário de teste para INV-TRAIN-037."""
    user = User(
        id=str(uuid4()),
        person_id=inv037_person.id,
        email=f"inv037_{uuid4().hex[:8]}@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest_asyncio.fixture
async def inv037_team(
    async_db: AsyncSession,
    inv037_category: Category,
    inv037_organization: Organization,
) -> Team:
    """Equipe de teste para INV-TRAIN-037."""
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv037_organization.id),
        name="Equipe INV-037",
        category_id=inv037_category.id,
        gender="feminino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


# ============================================
# TESTES RUNTIME
# ============================================

class TestInvTrain037CycleDatesRuntime:
    """
    Testes RUNTIME para INV-TRAIN-037: check_cycle_dates.

    Prova que o Postgres impõe start_date < end_date.
    """

    @pytest.mark.asyncio
    async def test_valid_cycle_dates_accepted(
        self,
        async_db: AsyncSession,
        inv037_organization: Organization,
        inv037_team: Team,
        inv037_user: User,
    ):
        """
        CASO POSITIVO: start_date < end_date deve ser aceito.

        Evidência: schema.sql:2402 - CHECK ((start_date < end_date))
        """
        cycle = TrainingCycle(
            id=uuid4(),
            organization_id=UUID(inv037_organization.id),
            team_id=inv037_team.id,
            type="macro",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),  # 6 meses depois
            status="active",
            created_by_user_id=UUID(inv037_user.id),
        )
        async_db.add(cycle)
        await async_db.flush()

        # Se chegou aqui sem exceção, constraint passou
        assert cycle.id is not None

    @pytest.mark.asyncio
    async def test_equal_dates_rejected(
        self,
        async_db: AsyncSession,
        inv037_organization: Organization,
        inv037_team: Team,
        inv037_user: User,
    ):
        """
        CASO NEGATIVO: start_date = end_date deve ser rejeitado.

        Evidência: schema.sql:2402 - CHECK ((start_date < end_date))
        A constraint exige estritamente < (não <=).
        """
        cycle = TrainingCycle(
            id=uuid4(),
            organization_id=UUID(inv037_organization.id),
            team_id=inv037_team.id,
            type="macro",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 1),  # IGUAL - deve falhar
            status="active",
            created_by_user_id=UUID(inv037_user.id),
        )
        async_db.add(cycle)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Verifica se é a constraint correta
        assert "check_cycle_dates" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_start_after_end_rejected(
        self,
        async_db: AsyncSession,
        inv037_organization: Organization,
        inv037_team: Team,
        inv037_user: User,
    ):
        """
        CASO NEGATIVO: start_date > end_date deve ser rejeitado.

        Evidência: schema.sql:2402 - CHECK ((start_date < end_date))
        """
        cycle = TrainingCycle(
            id=uuid4(),
            organization_id=UUID(inv037_organization.id),
            team_id=inv037_team.id,
            type="meso",
            start_date=date(2026, 6, 30),
            end_date=date(2026, 1, 1),  # ANTES - deve falhar
            status="active",
            created_by_user_id=UUID(inv037_user.id),
        )
        async_db.add(cycle)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Verifica se é a constraint correta
        assert "check_cycle_dates" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_boundary_one_day_apart_accepted(
        self,
        async_db: AsyncSession,
        inv037_organization: Organization,
        inv037_team: Team,
        inv037_user: User,
    ):
        """
        CASO LIMITE: start_date um dia antes de end_date deve ser aceito.

        Evidência: schema.sql:2402 - CHECK ((start_date < end_date))
        """
        cycle = TrainingCycle(
            id=uuid4(),
            organization_id=UUID(inv037_organization.id),
            team_id=inv037_team.id,
            type="meso",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 2),  # 1 dia depois - deve passar
            status="active",
            created_by_user_id=UUID(inv037_user.id),
        )
        async_db.add(cycle)
        await async_db.flush()

        assert cycle.id is not None
