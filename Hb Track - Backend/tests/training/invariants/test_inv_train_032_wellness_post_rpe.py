"""
INV-TRAIN-032: RPE da sessão deve estar entre 0 e 10

Enunciado: O campo session_rpe em wellness_post deve estar no intervalo [0, 10].

Evidência (DB constraint):
  - ck_wellness_post_rpe CHECK ((session_rpe >= 0) AND (session_rpe <= 10)) (schema.sql:2833)

Obrigação A: Analisei o schema.sql. Para criar o payload mínimo, identifico:
  1. FK Obrigatória: organization_id (Âncora: wellness_post.organization_id FK). Usarei fixture inv_org.
  2. FK Obrigatória: training_session_id (Âncora: wellness_post.training_session_id FK). Usarei fixture inv_session.
  3. FK Obrigatória: athlete_id (Âncora: wellness_post.athlete_id FK). Usarei fixture inv_athlete.
  4. FK Obrigatória: created_by_user_id (Âncora: wellness_post.created_by_user_id FK). Usarei fixture inv_user.
  5. NOT NULL: overall_feeling (Âncora: wellness_post.overall_feeling NOT NULL). Usarei valor válido 5.
  6. NOT NULL: session_rpe (Âncora: wellness_post.session_rpe NOT NULL). Campo alvo do teste.
  O resto será omitido.

Obrigação B: Invariante alvo: ck_wellness_post_rpe (CHECK).
  * SQLSTATE Esperado: 23514 (check_violation).
  * Constraint Name: ck_wellness_post_rpe.
  * Estratégia: pytest.raises validando SQLSTATE e presença do nome da constraint.
"""

from datetime import datetime, timezone, timedelta
from uuid import uuid4
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tests._helpers.pg_error import assert_pg_constraint_violation
from app.models.category import Category
from app.models.organization import Organization
from app.models.person import Person
from app.models.team import Team
from app.models.training_session import TrainingSession
from app.models.user import User
from app.models.wellness_post import WellnessPost


@pytest.fixture
async def inv032_category(async_db: AsyncSession) -> Category:
    """Fixture para Category do INV-032"""
    category = Category(
        id=9932,
        name="Categoria INV-032",
        max_age=18,
        is_active=True,
    )
    async_db.add(category)
    await async_db.flush()
    return category


@pytest.fixture
async def inv032_organization(async_db: AsyncSession) -> Organization:
    """Fixture para Organization do INV-032"""
    org = Organization(
        id=str(uuid4()),
        name="Org INV-032",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest.fixture
async def inv032_person(async_db: AsyncSession) -> Person:
    """Fixture para Person do INV-032"""
    person = Person(
        id=str(uuid4()),
        full_name="Atleta INV-032",
        first_name="Atleta",
        last_name="INV-032",
        birth_date="1995-01-01",
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest.fixture
async def inv032_user(async_db: AsyncSession, inv032_person: Person) -> User:
    """Fixture para User do INV-032"""
    user = User(
        id=str(uuid4()),
        person_id=inv032_person.id,
        email="inv032@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest.fixture
async def inv032_team(async_db: AsyncSession, inv032_category: Category, inv032_organization: Organization) -> Team:
    """Fixture para Team do INV-032"""
    team = Team(
        id=uuid4(),
        organization_id=inv032_organization.id,
        name="Team INV-032",
        category_id=inv032_category.id,
        gender="masculino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


@pytest.fixture
async def inv032_session(
    async_db: AsyncSession, 
    inv032_organization: Organization, 
    inv032_team: Team, 
    inv032_user: User
) -> TrainingSession:
    """Fixture para TrainingSession do INV-032"""
    session = TrainingSession(
        id=uuid4(),
        organization_id=inv032_organization.id,
        team_id=inv032_team.id,
        session_at=datetime.now(timezone.utc) + timedelta(hours=2),
        duration_planned_minutes=90,
        session_type="quadra",
        main_objective="Teste INV-032",
        location="Ginasio",
        status="draft",
        created_by_user_id=inv032_user.id,
    )
    async_db.add(session)
    await async_db.flush()
    return session


class TestInvTrain032WellnessPostRpe:
    """Classe A: DB Constraint CHECK ck_wellness_post_rpe"""

    @pytest.mark.asyncio
    async def test_valid_case__rpe_at_boundaries(
        self, 
        async_db: AsyncSession, 
        inv032_organization: Organization,
        inv032_session: TrainingSession,
        inv032_person: Person,
        inv032_user: User
    ):
        """RPE nos limites 0 e 10 deve ser aceito"""
        # Teste com RPE = 0 (limite inferior)
        wellness_min = WellnessPost(
            id=uuid4(),
            organization_id=inv032_organization.id,
            training_session_id=inv032_session.id,
            athlete_id=inv032_person.id,
            overall_feeling=5,
            session_rpe=0,  # Limite mínimo
            created_by_user_id=inv032_user.id
        )
        async_db.add(wellness_min)
        await async_db.flush()

        # Teste com RPE = 10 (limite superior)
        wellness_max = WellnessPost(
            id=uuid4(),
            organization_id=inv032_organization.id,
            training_session_id=inv032_session.id,
            athlete_id=inv032_person.id,
            overall_feeling=3,
            session_rpe=10,  # Limite máximo
            created_by_user_id=inv032_user.id
        )
        async_db.add(wellness_max)
        await async_db.flush()

        # Se chegou aqui sem exceção, constraint passou
        assert wellness_min.id is not None
        assert wellness_max.id is not None

    @pytest.mark.asyncio
    async def test_invalid_case_1__rpe_below_minimum(
        self, 
        async_db: AsyncSession, 
        inv032_organization: Organization,
        inv032_session: TrainingSession,
        inv032_person: Person,
        inv032_user: User
    ):
        """RPE abaixo do mínimo (< 0) deve ser rejeitado pela constraint DB"""
        wellness = WellnessPost(
            id=uuid4(),
            organization_id=inv032_organization.id,
            training_session_id=inv032_session.id,
            athlete_id=inv032_person.id,
            overall_feeling=5,
            session_rpe=-1,  # Viola constraint (< 0)
            created_by_user_id=inv032_user.id
        )
        async_db.add(wellness)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Verifica constraint usando helper canônico (driver-agnostic)
        assert_pg_constraint_violation(
            exc_info, "23514", "ck_wellness_post_rpe"
        )
        
        await async_db.rollback()

    @pytest.mark.asyncio
    async def test_invalid_case_2__rpe_above_maximum(
        self, 
        async_db: AsyncSession, 
        inv032_organization: Organization,
        inv032_session: TrainingSession,
        inv032_person: Person,
        inv032_user: User
    ):
        """RPE acima do máximo (> 10) deve ser rejeitado pela constraint DB"""
        wellness = WellnessPost(
            id=uuid4(),
            organization_id=inv032_organization.id,
            training_session_id=inv032_session.id,
            athlete_id=inv032_person.id,
            overall_feeling=4,
            session_rpe=11,  # Viola constraint (> 10)
            created_by_user_id=inv032_user.id
        )
        async_db.add(wellness)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Verifica constraint usando helper canônico (driver-agnostic)
        assert_pg_constraint_violation(
            exc_info, "23514", "ck_wellness_post_rpe"
        )
        
        await async_db.rollback()
