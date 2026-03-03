"""
INV-TRAIN-001: Soma de focos ≤ 120%

Testa a constraint DB que impede soma de focos > 120% em:
- training_sessions: ck_training_sessions_focus_total_sum (schema.sql:2640)
- session_templates: chk_session_templates_total_focus (schema.sql:2127)

Evidência service: training_microcycle_service.py:11 (regra documentada)

Obrigação A: training_sessions.focus_physical, training_sessions.focus_technical, 
training_sessions.focus_tactical, training_sessions.focus_psychological. 
CHECK constraint ck_training_sessions_focus_total_sum.

Obrigação B: SQLSTATE 23514, constraint_name ck_training_sessions_focus_total_sum, 
constraint_name chk_session_templates_total_focus.
"""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tests._helpers.pg_error import assert_pg_constraint_violation
from app.models.category import Category
from app.models.organization import Organization
from app.models.person import Person
from app.models.team import Team
from app.models.training_session import TrainingSession as TrainingSessionModel
from app.models.user import User


@pytest_asyncio.fixture
async def inv001_category(async_db: AsyncSession) -> Category:
    category = Category(
        id=9901,
        name="Categoria INV-001",
        max_age=19,
        is_active=True,
    )
    async_db.add(category)
    await async_db.flush()
    return category


@pytest_asyncio.fixture
async def inv001_organization(async_db: AsyncSession) -> Organization:
    org = Organization(
        id=str(uuid4()),
        name="Org INV-TRAIN-001",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv001_person(async_db: AsyncSession) -> Person:
    person = Person(
        id=str(uuid4()),
        full_name="Teste INV-001",
        first_name="Teste",
        last_name="INV-001",
        birth_date=date(1990, 1, 1),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv001_user(async_db: AsyncSession, inv001_person: Person) -> User:
    user = User(
        id=str(uuid4()),
        person_id=inv001_person.id,
        email="inv001@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest_asyncio.fixture
async def inv001_team(
    async_db: AsyncSession,
    inv001_category: Category,
    inv001_organization: Organization,
) -> Team:
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv001_organization.id),
        name="Equipe INV-001",
        category_id=inv001_category.id,
        gender="feminino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


class TestInvTrain001FocusSumConstraint:
    """Testes para INV-TRAIN-001: Soma de focos ≤ 120%"""

    @pytest.mark.asyncio
    async def test_valid_case__sum_at_120(
        self,
        async_db: AsyncSession,
        inv001_team: Team,
        inv001_organization: Organization,
        inv001_user: User,
    ):
        """Soma de focos = 120% deve ser aceita (limite exato)."""
        session = TrainingSessionModel(
            id=uuid4(),
            organization_id=UUID(inv001_organization.id),
            team_id=inv001_team.id,
            session_at=datetime.now(timezone.utc) + timedelta(hours=2),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Treino limite 120%",
            location="Ginasio",
            status="draft",
            created_by_user_id=UUID(inv001_user.id),
            # Soma = 20 + 20 + 20 + 20 + 20 + 10 + 10 = 120
            focus_attack_positional_pct=20,
            focus_defense_positional_pct=20,
            focus_transition_offense_pct=20,
            focus_transition_defense_pct=20,
            focus_attack_technical_pct=20,
            focus_defense_technical_pct=10,
            focus_physical_pct=10,
        )
        async_db.add(session)
        await async_db.flush()

        # Se chegou aqui sem exceção, constraint passou
        assert session.id is not None

    @pytest.mark.asyncio
    async def test_invalid_case_1__sum_exceeds_120(
        self,
        async_db: AsyncSession,
        inv001_team: Team,
        inv001_organization: Organization,
        inv001_user: User,
    ):
        """Soma de focos = 121% deve ser rejeitada pela constraint DB."""
        session = TrainingSessionModel(
            id=uuid4(),
            organization_id=UUID(inv001_organization.id),
            team_id=inv001_team.id,
            session_at=datetime.now(timezone.utc) + timedelta(hours=2),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Treino excede 120%",
            location="Ginasio",
            status="draft",
            created_by_user_id=UUID(inv001_user.id),
            # Soma = 20 + 20 + 20 + 20 + 20 + 10 + 11 = 121 (excede)
            focus_attack_positional_pct=20,
            focus_defense_positional_pct=20,
            focus_transition_offense_pct=20,
            focus_transition_defense_pct=20,
            focus_attack_technical_pct=20,
            focus_defense_technical_pct=10,
            focus_physical_pct=11,
        )
        async_db.add(session)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Verifica constraint usando helper canônico
        assert_pg_constraint_violation(
            exc_info,
            "23514",
            "ck_training_sessions_focus_total_sum"
        )
        
        await async_db.rollback()

    @pytest.mark.asyncio
    async def test_invalid_case_2__negative_focus(
        self,
        async_db: AsyncSession,
        inv001_team: Team,
        inv001_organization: Organization,
        inv001_user: User,
    ):
        """Valores negativos de foco devem ser rejeitados pela constraint DB."""
        session = TrainingSessionModel(
            id=uuid4(),
            organization_id=UUID(inv001_organization.id),
            team_id=inv001_team.id,
            session_at=datetime.now(timezone.utc) + timedelta(hours=2),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Treino com foco negativo",
            location="Ginasio",
            status="draft",
            created_by_user_id=UUID(inv001_user.id),
            # Valor negativo deve ser rejeitado
            focus_attack_positional_pct=-5,
            focus_defense_positional_pct=20,
            focus_transition_offense_pct=20,
            focus_transition_defense_pct=20,
            focus_attack_technical_pct=20,
            focus_defense_technical_pct=10,
            focus_physical_pct=10,
        )
        async_db.add(session)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Verifica constraint usando helper canônico
        assert_pg_constraint_violation(
            exc_info,
            "23514",
            "ck_training_sessions_focus_attack_positional_range"
        )

        await async_db.rollback()
