"""
INV-TRAIN-034 — Qualidade do sono deve estar entre 1 e 5

RUNTIME DB TEST - Testa constraint real no Postgres via IntegrityError.

Evidência:
- Constraint: `ck_wellness_pre_sleep_quality CHECK (((sleep_quality >= 1) AND (sleep_quality <= 5)))`
- Schema: `Hb Track - Backend/docs/_generated/schema.sql:2895`
- Model: `app/models/wellness_pre.py:59` (sleep_quality SmallInteger)

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
async def inv034_category(async_db: AsyncSession) -> Category:
    """Categoria de teste para INV-TRAIN-034."""
    category = Category(
        id=9934,
        name="Categoria INV-034",
        max_age=19,
        is_active=True,
    )
    async_db.add(category)
    await async_db.flush()
    return category


@pytest_asyncio.fixture
async def inv034_organization(async_db: AsyncSession) -> Organization:
    """Organização de teste para INV-TRAIN-034."""
    org = Organization(
        id=str(uuid4()),
        name="Org INV-TRAIN-034",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv034_person(async_db: AsyncSession) -> Person:
    """Pessoa de teste para INV-TRAIN-034."""
    person = Person(
        id=str(uuid4()),
        full_name="Teste INV-034",
        first_name="Teste",
        last_name="INV-034",
        birth_date=date(1990, 1, 1),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv034_athlete_person(async_db: AsyncSession) -> Person:
    """Pessoa (atleta) de teste para INV-TRAIN-034."""
    person = Person(
        id=str(uuid4()),
        full_name="Atleta INV-034",
        first_name="Atleta",
        last_name="INV-034",
        birth_date=date(2005, 6, 15),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv034_user(async_db: AsyncSession, inv034_person: Person) -> User:
    """Usuário de teste para INV-TRAIN-034."""
    user = User(
        id=str(uuid4()),
        person_id=inv034_person.id,
        email=f"inv034_{uuid4().hex[:8]}@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest_asyncio.fixture
async def inv034_team(
    async_db: AsyncSession,
    inv034_category: Category,
    inv034_organization: Organization,
) -> Team:
    """Equipe de teste para INV-TRAIN-034."""
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv034_organization.id),
        name="Equipe INV-034",
        category_id=inv034_category.id,
        gender="feminino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


@pytest_asyncio.fixture
async def inv034_athlete(
    async_db: AsyncSession,
    inv034_athlete_person: Person,
    inv034_organization: Organization,
) -> Athlete:
    """Atleta de teste para INV-TRAIN-034."""
    athlete = Athlete(
        id=uuid4(),
        person_id=UUID(inv034_athlete_person.id),
        organization_id=UUID(inv034_organization.id),
        athlete_name="Atleta INV-034",
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
async def inv034_training_session(
    async_db: AsyncSession,
    inv034_organization: Organization,
    inv034_team: Team,
    inv034_user: User,
) -> TrainingSession:
    """Sessão de treino de teste para INV-TRAIN-034."""
    session = TrainingSession(
        id=uuid4(),
        organization_id=UUID(inv034_organization.id),
        team_id=inv034_team.id,
        created_by_user_id=UUID(inv034_user.id),
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

class TestInvTrain034WellnessPreSleepQualityRuntime:
    """
    Testes RUNTIME para INV-TRAIN-034: ck_wellness_pre_sleep_quality.

    Prova que o Postgres impõe sleep_quality BETWEEN 1 AND 5.
    """

    @pytest.mark.asyncio
    async def test_valid_sleep_quality_one_accepted(
        self,
        async_db: AsyncSession,
        inv034_organization: Organization,
        inv034_training_session: TrainingSession,
        inv034_athlete: Athlete,
        inv034_user: User,
    ):
        """
        CASO POSITIVO: sleep_quality = 1 deve ser aceito.

        Evidência: schema.sql:2895 - CHECK ((sleep_quality >= 1) AND (sleep_quality <= 5))
        """
        wellness = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv034_organization.id),
            training_session_id=inv034_training_session.id,
            athlete_id=inv034_athlete.id,
            created_by_user_id=UUID(inv034_user.id),
            sleep_hours=Decimal("7"),
            sleep_quality=1,  # Mínimo válido
            fatigue_pre=5,
            stress_level=5,
            muscle_soreness=5,
        )
        async_db.add(wellness)
        await async_db.flush()

        assert wellness.id is not None

    @pytest.mark.asyncio
    async def test_valid_sleep_quality_five_accepted(
        self,
        async_db: AsyncSession,
        inv034_organization: Organization,
        inv034_training_session: TrainingSession,
        inv034_athlete: Athlete,
        inv034_user: User,
    ):
        """
        CASO POSITIVO: sleep_quality = 5 deve ser aceito.

        Evidência: schema.sql:2895 - CHECK ((sleep_quality >= 1) AND (sleep_quality <= 5))
        """
        wellness = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv034_organization.id),
            training_session_id=inv034_training_session.id,
            athlete_id=inv034_athlete.id,
            created_by_user_id=UUID(inv034_user.id),
            sleep_hours=Decimal("7"),
            sleep_quality=5,  # Máximo válido
            fatigue_pre=5,
            stress_level=5,
            muscle_soreness=5,
        )
        async_db.add(wellness)
        await async_db.flush()

        assert wellness.id is not None

    @pytest.mark.asyncio
    async def test_valid_sleep_quality_middle_accepted(
        self,
        async_db: AsyncSession,
        inv034_organization: Organization,
        inv034_training_session: TrainingSession,
        inv034_athlete: Athlete,
        inv034_user: User,
    ):
        """
        CASO POSITIVO: sleep_quality = 3 (meio do range) deve ser aceito.

        Evidência: schema.sql:2895 - CHECK ((sleep_quality >= 1) AND (sleep_quality <= 5))
        """
        wellness = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv034_organization.id),
            training_session_id=inv034_training_session.id,
            athlete_id=inv034_athlete.id,
            created_by_user_id=UUID(inv034_user.id),
            sleep_hours=Decimal("7"),
            sleep_quality=3,  # Valor intermediário
            fatigue_pre=5,
            stress_level=5,
            muscle_soreness=5,
        )
        async_db.add(wellness)
        await async_db.flush()

        assert wellness.id is not None

    @pytest.mark.asyncio
    async def test_sleep_quality_zero_rejected(
        self,
        async_db: AsyncSession,
        inv034_organization: Organization,
        inv034_training_session: TrainingSession,
        inv034_athlete: Athlete,
        inv034_user: User,
    ):
        """
        CASO NEGATIVO: sleep_quality = 0 deve ser rejeitado.

        Evidência: schema.sql:2895 - CHECK ((sleep_quality >= 1) AND (sleep_quality <= 5))
        Note: sleep_quality começa em 1, não em 0.
        """
        wellness = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv034_organization.id),
            training_session_id=inv034_training_session.id,
            athlete_id=inv034_athlete.id,
            created_by_user_id=UUID(inv034_user.id),
            sleep_hours=Decimal("7"),
            sleep_quality=0,  # ABAIXO DE 1 - deve falhar
            fatigue_pre=5,
            stress_level=5,
            muscle_soreness=5,
        )
        async_db.add(wellness)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        assert "ck_wellness_pre_sleep_quality" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_sleep_quality_six_rejected(
        self,
        async_db: AsyncSession,
        inv034_organization: Organization,
        inv034_training_session: TrainingSession,
        inv034_athlete: Athlete,
        inv034_user: User,
    ):
        """
        CASO NEGATIVO: sleep_quality = 6 deve ser rejeitado.

        Evidência: schema.sql:2895 - CHECK ((sleep_quality >= 1) AND (sleep_quality <= 5))
        """
        wellness = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv034_organization.id),
            training_session_id=inv034_training_session.id,
            athlete_id=inv034_athlete.id,
            created_by_user_id=UUID(inv034_user.id),
            sleep_hours=Decimal("7"),
            sleep_quality=6,  # ACIMA DE 5 - deve falhar
            fatigue_pre=5,
            stress_level=5,
            muscle_soreness=5,
        )
        async_db.add(wellness)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        assert "ck_wellness_pre_sleep_quality" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_sleep_quality_negative_rejected(
        self,
        async_db: AsyncSession,
        inv034_organization: Organization,
        inv034_training_session: TrainingSession,
        inv034_athlete: Athlete,
        inv034_user: User,
    ):
        """
        CASO NEGATIVO: sleep_quality = -1 deve ser rejeitado.

        Evidência: schema.sql:2895 - CHECK ((sleep_quality >= 1) AND (sleep_quality <= 5))
        """
        wellness = WellnessPre(
            id=uuid4(),
            organization_id=UUID(inv034_organization.id),
            training_session_id=inv034_training_session.id,
            athlete_id=inv034_athlete.id,
            created_by_user_id=UUID(inv034_user.id),
            sleep_hours=Decimal("7"),
            sleep_quality=-1,  # NEGATIVO - deve falhar
            fatigue_pre=5,
            stress_level=5,
            muscle_soreness=5,
        )
        async_db.add(wellness)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        assert "ck_wellness_pre_sleep_quality" in str(exc_info.value).lower()
