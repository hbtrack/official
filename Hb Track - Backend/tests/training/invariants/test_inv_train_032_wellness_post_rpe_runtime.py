"""
INV-TRAIN-032 — RPE da sessão deve estar entre 0 e 10

RUNTIME DB TEST - Testa constraint real no Postgres via IntegrityError.

Evidência:
- Constraint: `ck_wellness_post_rpe CHECK (((session_rpe >= 0) AND (session_rpe <= 10)))`
- Schema: `Hb Track - Backend/docs/ssot/schema.sql:2836`
- Model: `app/models/wellness_post.py:57` (session_rpe SmallInteger)

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
from app.models.athlete import Athlete
from app.models.training_session import TrainingSession
from app.models.wellness_post import WellnessPost


# ============================================
# FIXTURES LOCAIS (isoladas para este teste)
# ============================================

@pytest_asyncio.fixture
async def inv032_category(async_db: AsyncSession) -> Category:
    """Categoria de teste para INV-TRAIN-032."""
    category = Category(
        id=9932,
        name="Categoria INV-032",
        max_age=19,
        is_active=True,
    )
    async_db.add(category)
    await async_db.flush()
    return category


@pytest_asyncio.fixture
async def inv032_organization(async_db: AsyncSession) -> Organization:
    """Organização de teste para INV-TRAIN-032."""
    org = Organization(
        id=str(uuid4()),
        name="Org INV-TRAIN-032",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv032_person(async_db: AsyncSession) -> Person:
    """Pessoa de teste para INV-TRAIN-032."""
    person = Person(
        id=str(uuid4()),
        full_name="Teste INV-032",
        first_name="Teste",
        last_name="INV-032",
        birth_date=date(1990, 1, 1),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv032_athlete_person(async_db: AsyncSession) -> Person:
    """Pessoa (atleta) de teste para INV-TRAIN-032."""
    person = Person(
        id=str(uuid4()),
        full_name="Atleta INV-032",
        first_name="Atleta",
        last_name="INV-032",
        birth_date=date(2005, 6, 15),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv032_user(async_db: AsyncSession, inv032_person: Person) -> User:
    """Usuário de teste para INV-TRAIN-032."""
    user = User(
        id=str(uuid4()),
        person_id=inv032_person.id,
        email=f"inv032_{uuid4().hex[:8]}@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest_asyncio.fixture
async def inv032_team(
    async_db: AsyncSession,
    inv032_category: Category,
    inv032_organization: Organization,
) -> Team:
    """Equipe de teste para INV-TRAIN-032."""
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv032_organization.id),
        name="Equipe INV-032",
        category_id=inv032_category.id,
        gender="feminino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


@pytest_asyncio.fixture
async def inv032_athlete(
    async_db: AsyncSession,
    inv032_athlete_person: Person,
    inv032_organization: Organization,
) -> Athlete:
    """Atleta de teste para INV-TRAIN-032."""
    athlete = Athlete(
        id=uuid4(),
        person_id=UUID(inv032_athlete_person.id),
        organization_id=UUID(inv032_organization.id),
        athlete_name="Atleta INV-032",
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
async def inv032_training_session(
    async_db: AsyncSession,
    inv032_organization: Organization,
    inv032_team: Team,
    inv032_user: User,
) -> TrainingSession:
    """Sessão de treino de teste para INV-TRAIN-032."""
    session = TrainingSession(
        id=uuid4(),
        organization_id=UUID(inv032_organization.id),
        team_id=inv032_team.id,
        created_by_user_id=UUID(inv032_user.id),
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

class TestInvTrain032WellnessPostRpeRuntime:
    """
    Testes RUNTIME para INV-TRAIN-032: ck_wellness_post_rpe.

    Prova que o Postgres impõe session_rpe BETWEEN 0 AND 10.
    """

    @pytest.mark.asyncio
    async def test_valid_rpe_zero_accepted(
        self,
        async_db: AsyncSession,
        inv032_organization: Organization,
        inv032_training_session: TrainingSession,
        inv032_athlete: Athlete,
        inv032_user: User,
    ):
        """
        CASO POSITIVO: session_rpe = 0 deve ser aceito.

        Evidência: schema.sql:2836 - CHECK ((session_rpe >= 0) AND (session_rpe <= 10))
        """
        wellness = WellnessPost(
            id=uuid4(),
            organization_id=UUID(inv032_organization.id),
            training_session_id=inv032_training_session.id,
            athlete_id=inv032_athlete.id,
            created_by_user_id=UUID(inv032_user.id),
            session_rpe=0,  # Mínimo válido
            fatigue_after=5,
            mood_after=5,
        )
        async_db.add(wellness)
        await async_db.flush()

        assert wellness.id is not None

    @pytest.mark.asyncio
    async def test_valid_rpe_ten_accepted(
        self,
        async_db: AsyncSession,
        inv032_organization: Organization,
        inv032_training_session: TrainingSession,
        inv032_athlete: Athlete,
        inv032_user: User,
    ):
        """
        CASO POSITIVO: session_rpe = 10 deve ser aceito.

        Evidência: schema.sql:2836 - CHECK ((session_rpe >= 0) AND (session_rpe <= 10))
        """
        wellness = WellnessPost(
            id=uuid4(),
            organization_id=UUID(inv032_organization.id),
            training_session_id=inv032_training_session.id,
            athlete_id=inv032_athlete.id,
            created_by_user_id=UUID(inv032_user.id),
            session_rpe=10,  # Máximo válido
            fatigue_after=5,
            mood_after=5,
        )
        async_db.add(wellness)
        await async_db.flush()

        assert wellness.id is not None

    @pytest.mark.asyncio
    async def test_valid_rpe_middle_accepted(
        self,
        async_db: AsyncSession,
        inv032_organization: Organization,
        inv032_training_session: TrainingSession,
        inv032_athlete: Athlete,
        inv032_user: User,
    ):
        """
        CASO POSITIVO: session_rpe = 5 (meio do range) deve ser aceito.

        Evidência: schema.sql:2836 - CHECK ((session_rpe >= 0) AND (session_rpe <= 10))
        """
        wellness = WellnessPost(
            id=uuid4(),
            organization_id=UUID(inv032_organization.id),
            training_session_id=inv032_training_session.id,
            athlete_id=inv032_athlete.id,
            created_by_user_id=UUID(inv032_user.id),
            session_rpe=5,  # Valor intermediário
            fatigue_after=5,
            mood_after=5,
        )
        async_db.add(wellness)
        await async_db.flush()

        assert wellness.id is not None

    @pytest.mark.asyncio
    async def test_rpe_negative_rejected(
        self,
        async_db: AsyncSession,
        inv032_organization: Organization,
        inv032_training_session: TrainingSession,
        inv032_athlete: Athlete,
        inv032_user: User,
    ):
        """
        CASO NEGATIVO: session_rpe = -1 deve ser rejeitado.

        Evidência: schema.sql:2836 - CHECK ((session_rpe >= 0) AND (session_rpe <= 10))
        """
        wellness = WellnessPost(
            id=uuid4(),
            organization_id=UUID(inv032_organization.id),
            training_session_id=inv032_training_session.id,
            athlete_id=inv032_athlete.id,
            created_by_user_id=UUID(inv032_user.id),
            session_rpe=-1,  # NEGATIVO - deve falhar
            fatigue_after=5,
            mood_after=5,
        )
        async_db.add(wellness)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        assert "ck_wellness_post_rpe" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_rpe_above_ten_rejected(
        self,
        async_db: AsyncSession,
        inv032_organization: Organization,
        inv032_training_session: TrainingSession,
        inv032_athlete: Athlete,
        inv032_user: User,
    ):
        """
        CASO NEGATIVO: session_rpe = 11 deve ser rejeitado.

        Evidência: schema.sql:2836 - CHECK ((session_rpe >= 0) AND (session_rpe <= 10))
        """
        wellness = WellnessPost(
            id=uuid4(),
            organization_id=UUID(inv032_organization.id),
            training_session_id=inv032_training_session.id,
            athlete_id=inv032_athlete.id,
            created_by_user_id=UUID(inv032_user.id),
            session_rpe=11,  # ACIMA DE 10 - deve falhar
            fatigue_after=5,
            mood_after=5,
        )
        async_db.add(wellness)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        assert "ck_wellness_post_rpe" in str(exc_info.value).lower()
