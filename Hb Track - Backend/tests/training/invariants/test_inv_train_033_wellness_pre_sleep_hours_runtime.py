"""
INV-TRAIN-033 — Horas de sono deve estar entre 0 e 24

RUNTIME DB TEST - Testa constraint real no Postgres via IntegrityError.

Evidência:
- Constraint: `ck_wellness_pre_sleep_hours CHECK (((sleep_hours >= (0)::numeric) AND (sleep_hours <= (24)::numeric)))`
- Schema: `Hb Track - Backend/docs/_generated/schema.sql:2895`
- Model: `app/models/wellness_pre.py:58` (sleep_hours Numeric(4,1))

Este teste NÃO usa string match. Ele insere registros no DB e verifica
que a constraint é imposta pelo Postgres (SQLSTATE 23514 para CHECK).
"""

from datetime import date, datetime, timezone
from decimal import Decimal
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
from app.models.athlete import Athlete
from app.models.training_session import TrainingSession
from app.models.wellness_pre import WellnessPre


# ============================================
# FIXTURES LOCAIS (isoladas para este teste)
# ============================================

@pytest_asyncio.fixture
async def inv033_category(async_db: AsyncSession) -> Category:
    """Categoria de teste para INV-TRAIN-033."""
    category = Category(
        id=9933,
        name="Categoria INV-033",
        max_age=19,
        is_active=True,
    )
    async_db.add(category)
    await async_db.flush()
    return category


@pytest_asyncio.fixture
async def inv033_organization(async_db: AsyncSession) -> Organization:
    """Organização de teste para INV-TRAIN-033."""
    org = Organization(
        id=str(uuid4()),
        name="Org INV-TRAIN-033",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv033_person(async_db: AsyncSession) -> Person:
    """Pessoa de teste para INV-TRAIN-033."""
    person = Person(
        id=str(uuid4()),
        full_name="Teste INV-033",
        first_name="Teste",
        last_name="INV-033",
        birth_date=date(1990, 1, 1),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv033_athlete_person(async_db: AsyncSession) -> Person:
    """Pessoa (atleta) de teste para INV-TRAIN-033."""
    person = Person(
        id=str(uuid4()),
        full_name="Atleta INV-033",
        first_name="Atleta",
        last_name="INV-033",
        birth_date=date(2005, 6, 15),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv033_user(async_db: AsyncSession, inv033_person: Person) -> User:
    """Usuário de teste para INV-TRAIN-033."""
    user = User(
        id=str(uuid4()),
        person_id=inv033_person.id,
        email=f"inv033_{uuid4().hex[:8]}@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest_asyncio.fixture
async def inv033_team(
    async_db: AsyncSession,
    inv033_category: Category,
    inv033_organization: Organization,
) -> Team:
    """Equipe de teste para INV-TRAIN-033."""
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv033_organization.id),
        name="Equipe INV-033",
        category_id=inv033_category.id,
        gender="feminino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


@pytest_asyncio.fixture
async def inv033_athlete(
    async_db: AsyncSession,
    inv033_athlete_person: Person,
    inv033_organization: Organization,
) -> Athlete:
    """Atleta de teste para INV-TRAIN-033."""
    athlete = Athlete(
        id=uuid4(),
        person_id=UUID(inv033_athlete_person.id),
        organization_id=UUID(inv033_organization.id),
        athlete_name="Atleta INV-033",
        birth_date=date(2005, 6, 15),
        state="ativa",
        injured=False,
        medical_restriction=False,
        load_restricted=False,
    )
    async_db.add(athlete)
    await async_db.flush()
    return athlete


@pytest_asyncio.fixture
async def inv033_training_session(
    async_db: AsyncSession,
    inv033_organization: Organization,
    inv033_team: Team,
    inv033_user: User,
) -> TrainingSession:
    """Sessão de treino de teste para INV-TRAIN-033."""
    session = TrainingSession(
        id=uuid4(),
        organization_id=UUID(inv033_organization.id),
        team_id=inv033_team.id,
        created_by_user_id=UUID(inv033_user.id),
        session_at=datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        session_type="quadra",
        status="draft",
    )
    async_db.add(session)
    await async_db.flush()
    return session


# ============================================
# TESTES RUNTIME
# ============================================

class TestInvTrain033WellnessPreSleepHoursRuntime:
    """
    Testes RUNTIME para INV-TRAIN-033: ck_wellness_pre_sleep_hours.

    Prova que o Postgres impõe sleep_hours BETWEEN 0 AND 24.
    """

    @pytest.mark.asyncio
    async def test_valid_sleep_hours_zero_accepted(
        self,
        async_db: AsyncSession,
        inv033_organization: Organization,
        inv033_training_session: TrainingSession,
        inv033_athlete: Athlete,
        inv033_user: User,
    ):
        """
        CASO POSITIVO: sleep_hours = 0 deve ser aceito.

        Evidência: schema.sql:2895 - CHECK ((sleep_hours >= 0) AND (sleep_hours <= 24))
        """
        wellness = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv033_organization.id),
            training_session_id=inv033_training_session.id,
            athlete_id=inv033_athlete.id,
            created_by_user_id=UUID(inv033_user.id),
            sleep_hours=Decimal("0"),  # Mínimo válido
            sleep_quality=3,
            fatigue_pre=5,
            stress_level=5,
            muscle_soreness=5,
        )
        async_db.add(wellness)
        await async_db.flush()

        assert wellness.id is not None

    @pytest.mark.asyncio
    async def test_valid_sleep_hours_24_accepted(
        self,
        async_db: AsyncSession,
        inv033_organization: Organization,
        inv033_training_session: TrainingSession,
        inv033_athlete: Athlete,
        inv033_user: User,
    ):
        """
        CASO POSITIVO: sleep_hours = 24 deve ser aceito.

        Evidência: schema.sql:2895 - CHECK ((sleep_hours >= 0) AND (sleep_hours <= 24))
        """
        wellness = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv033_organization.id),
            training_session_id=inv033_training_session.id,
            athlete_id=inv033_athlete.id,
            created_by_user_id=UUID(inv033_user.id),
            sleep_hours=Decimal("24"),  # Máximo válido
            sleep_quality=3,
            fatigue_pre=5,
            stress_level=5,
            muscle_soreness=5,
        )
        async_db.add(wellness)
        await async_db.flush()

        assert wellness.id is not None

    @pytest.mark.asyncio
    async def test_valid_sleep_hours_decimal_accepted(
        self,
        async_db: AsyncSession,
        inv033_organization: Organization,
        inv033_training_session: TrainingSession,
        inv033_athlete: Athlete,
        inv033_user: User,
    ):
        """
        CASO POSITIVO: sleep_hours = 7.5 (valor decimal típico) deve ser aceito.

        Evidência: schema.sql:2895 - CHECK ((sleep_hours >= 0) AND (sleep_hours <= 24))
        """
        wellness = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv033_organization.id),
            training_session_id=inv033_training_session.id,
            athlete_id=inv033_athlete.id,
            created_by_user_id=UUID(inv033_user.id),
            sleep_hours=Decimal("7.5"),  # Valor típico com decimal
            sleep_quality=3,
            fatigue_pre=5,
            stress_level=5,
            muscle_soreness=5,
        )
        async_db.add(wellness)
        await async_db.flush()

        assert wellness.id is not None

    @pytest.mark.asyncio
    async def test_sleep_hours_negative_rejected(
        self,
        async_db: AsyncSession,
        inv033_organization: Organization,
        inv033_training_session: TrainingSession,
        inv033_athlete: Athlete,
        inv033_user: User,
    ):
        """
        CASO NEGATIVO: sleep_hours = -1 deve ser rejeitado.

        Evidência: schema.sql:2895 - CHECK ((sleep_hours >= 0) AND (sleep_hours <= 24))
        """
        wellness = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv033_organization.id),
            training_session_id=inv033_training_session.id,
            athlete_id=inv033_athlete.id,
            created_by_user_id=UUID(inv033_user.id),
            sleep_hours=Decimal("-1"),  # NEGATIVO - deve falhar
            sleep_quality=3,
            fatigue_pre=5,
            stress_level=5,
            muscle_soreness=5,
        )
        async_db.add(wellness)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        assert "ck_wellness_pre_sleep_hours" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_sleep_hours_above_24_rejected(
        self,
        async_db: AsyncSession,
        inv033_organization: Organization,
        inv033_training_session: TrainingSession,
        inv033_athlete: Athlete,
        inv033_user: User,
    ):
        """
        CASO NEGATIVO: sleep_hours = 25 deve ser rejeitado.

        Evidência: schema.sql:2895 - CHECK ((sleep_hours >= 0) AND (sleep_hours <= 24))
        """
        wellness = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv033_organization.id),
            training_session_id=inv033_training_session.id,
            athlete_id=inv033_athlete.id,
            created_by_user_id=UUID(inv033_user.id),
            sleep_hours=Decimal("25"),  # ACIMA DE 24 - deve falhar
            sleep_quality=3,
            fatigue_pre=5,
            stress_level=5,
            muscle_soreness=5,
        )
        async_db.add(wellness)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        assert "ck_wellness_pre_sleep_hours" in str(exc_info.value).lower()
