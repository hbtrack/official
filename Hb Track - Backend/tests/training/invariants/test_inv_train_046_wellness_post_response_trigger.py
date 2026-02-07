"""
INV-TRAIN-046 — Trigger atualiza responded_at em wellness_reminders ao inserir wellness_post

RUNTIME DB TEST - Testa trigger real no Postgres.

Obrigação A:
- Tabela: wellness_post
- Trigger: tr_update_wellness_post_response
- Function: fn_update_wellness_response_timestamp
- Schema trigger: schema.sql:5222
- Schema function: schema.sql:287

Obrigação B:
- Efeito: UPDATE wellness_reminders SET responded_at = NOW()
         WHERE training_session_id = NEW.training_session_id
         AND athlete_id = NEW.athlete_id
         AND responded_at IS NULL

Este teste prova que o trigger atualiza responded_at automaticamente.
"""

from datetime import date, datetime, timedelta, timezone
from uuid import uuid4, UUID

import pytest
import pytest_asyncio
from sqlalchemy import text
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
async def inv046_category(async_db: AsyncSession) -> Category:
    """Categoria de teste para INV-TRAIN-046."""
    category = Category(
        id=9946,
        name="Categoria INV-046",
        max_age=19,
        is_active=True,
    )
    async_db.add(category)
    await async_db.flush()
    return category


@pytest_asyncio.fixture
async def inv046_organization(async_db: AsyncSession) -> Organization:
    """Organização de teste para INV-TRAIN-046."""
    org = Organization(
        id=str(uuid4()),
        name="Org INV-TRAIN-046",
    )
    async_db.add(org)
    await async_db.flush()
    return org


@pytest_asyncio.fixture
async def inv046_person(async_db: AsyncSession) -> Person:
    """Pessoa de teste para INV-TRAIN-046."""
    person = Person(
        id=str(uuid4()),
        full_name="Teste INV-046",
        first_name="Teste",
        last_name="INV-046",
        birth_date=date(1990, 1, 1),
    )
    async_db.add(person)
    await async_db.flush()
    return person


@pytest_asyncio.fixture
async def inv046_user(async_db: AsyncSession, inv046_person: Person) -> User:
    """Usuário de teste para INV-TRAIN-046."""
    user = User(
        id=str(uuid4()),
        person_id=inv046_person.id,
        email=f"inv046_{uuid4().hex[:8]}@hbtrack.com",
    )
    async_db.add(user)
    await async_db.flush()
    return user


@pytest_asyncio.fixture
async def inv046_team(
    async_db: AsyncSession,
    inv046_category: Category,
    inv046_organization: Organization,
) -> Team:
    """Equipe de teste para INV-TRAIN-046."""
    team = Team(
        id=uuid4(),
        organization_id=UUID(inv046_organization.id),
        name="Equipe INV-046",
        category_id=inv046_category.id,
        gender="feminino",
        is_our_team=True,
    )
    async_db.add(team)
    await async_db.flush()
    return team


@pytest_asyncio.fixture
async def inv046_athlete(
    async_db: AsyncSession,
    inv046_person: Person,
    inv046_organization: Organization,
) -> Athlete:
    """Atleta de teste para INV-TRAIN-046."""
    athlete = Athlete(
        id=uuid4(),
        person_id=UUID(inv046_person.id),
        organization_id=UUID(inv046_organization.id),
        athlete_name="Atleta INV-046",
        birth_date=date(2000, 1, 1),
    )
    async_db.add(athlete)
    await async_db.flush()
    return athlete


@pytest_asyncio.fixture
async def inv046_training_session(
    async_db: AsyncSession,
    inv046_organization: Organization,
    inv046_team: Team,
    inv046_user: User,
) -> TrainingSession:
    """Sessão de treino de teste para INV-TRAIN-046."""
    session = TrainingSession(
        id=uuid4(),
        organization_id=UUID(inv046_organization.id),
        team_id=inv046_team.id,
        created_by_user_id=UUID(inv046_user.id),
        session_at=datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc),
        session_type="quadra",
        status="scheduled",
    )
    async_db.add(session)
    await async_db.flush()
    return session


# ============================================
# TESTES RUNTIME
# ============================================

class TestInvTrain046WellnessPostResponseTrigger:
    """
    Testes RUNTIME para INV-TRAIN-046: tr_update_wellness_post_response.

    Prova que o trigger atualiza responded_at em wellness_reminders
    quando um wellness_post é inserido para o mesmo atleta/sessão.

    Obrigação A:
    - Tabela: wellness_post
    - Trigger: tr_update_wellness_post_response
    - Function: fn_update_wellness_response_timestamp
    - Schema trigger: schema.sql:5222
    - Schema function: schema.sql:287

    Obrigação B:
    - Efeito: UPDATE wellness_reminders SET responded_at = NOW()
             WHERE training_session_id = NEW.training_session_id
             AND athlete_id = NEW.athlete_id
             AND responded_at IS NULL
    """

    @pytest.mark.asyncio
    async def test_valid_case__trigger_updates_responded_at(
        self,
        async_db: AsyncSession,
        inv046_organization: Organization,
        inv046_team: Team,
        inv046_user: User,
        inv046_athlete: Athlete,
        inv046_training_session: TrainingSession,
    ):
        """
        CASO POSITIVO: Inserir wellness_post atualiza responded_at no reminder.

        Evidência: schema.sql:5222 - trigger tr_update_wellness_post_response
        Evidência: schema.sql:287 - function fn_update_wellness_response_timestamp
        """
        # Arrange: criar wellness_reminder via raw SQL (sem ORM model)
        reminder_id = uuid4()
        sent_at = datetime.now(timezone.utc) - timedelta(hours=2)

        await async_db.execute(
            text("""
                INSERT INTO wellness_reminders
                (id, training_session_id, athlete_id, sent_at, responded_at, reminder_count)
                VALUES (:id, :session_id, :athlete_id, :sent_at, NULL, 1)
            """),
            {
                "id": reminder_id,
                "session_id": inv046_training_session.id,
                "athlete_id": inv046_athlete.id,
                "sent_at": sent_at,
            }
        )
        await async_db.flush()

        # Verificar que responded_at é NULL antes do wellness_post
        result_before = await async_db.execute(
            text("SELECT responded_at FROM wellness_reminders WHERE id = :id"),
            {"id": reminder_id}
        )
        row_before = result_before.fetchone()
        assert row_before[0] is None, "responded_at deve ser NULL antes do wellness_post"

        # Act: inserir wellness_post (deve disparar o trigger)
        wellness_post = WellnessPost(
            id=uuid4(),
            organization_id=UUID(inv046_organization.id),
            training_session_id=inv046_training_session.id,
            athlete_id=inv046_athlete.id,
            created_by_user_id=UUID(inv046_user.id),
            session_rpe=7,
            fatigue_after=6,
            mood_after=7,
        )
        async_db.add(wellness_post)
        await async_db.flush()

        # Assert: verificar que responded_at foi atualizado pelo trigger
        result_after = await async_db.execute(
            text("SELECT responded_at FROM wellness_reminders WHERE id = :id"),
            {"id": reminder_id}
        )
        row_after = result_after.fetchone()

        assert row_after[0] is not None, (
            "responded_at deve ser atualizado pelo trigger tr_update_wellness_post_response "
            "após inserir wellness_post"
        )

    @pytest.mark.asyncio
    async def test_trigger_does_not_update_already_responded(
        self,
        async_db: AsyncSession,
        inv046_organization: Organization,
        inv046_team: Team,
        inv046_user: User,
        inv046_athlete: Athlete,
        inv046_training_session: TrainingSession,
    ):
        """
        CASO CONTROLE: Trigger não atualiza reminder já respondido.

        O trigger só atualiza WHERE responded_at IS NULL.
        Se já tem responded_at, não deve ser modificado.

        Evidência: schema.sql:287 - WHERE responded_at IS NULL
        """
        # Arrange: criar wellness_reminder já respondido
        reminder_id = uuid4()
        sent_at = datetime.now(timezone.utc) - timedelta(hours=2)
        original_responded_at = datetime.now(timezone.utc) - timedelta(hours=1)

        await async_db.execute(
            text("""
                INSERT INTO wellness_reminders
                (id, training_session_id, athlete_id, sent_at, responded_at, reminder_count)
                VALUES (:id, :session_id, :athlete_id, :sent_at, :responded_at, 1)
            """),
            {
                "id": reminder_id,
                "session_id": inv046_training_session.id,
                "athlete_id": inv046_athlete.id,
                "sent_at": sent_at,
                "responded_at": original_responded_at,
            }
        )
        await async_db.flush()

        # Act: inserir wellness_post
        wellness_post = WellnessPost(
            id=uuid4(),
            organization_id=UUID(inv046_organization.id),
            training_session_id=inv046_training_session.id,
            athlete_id=inv046_athlete.id,
            created_by_user_id=UUID(inv046_user.id),
            session_rpe=7,
            fatigue_after=6,
            mood_after=7,
        )
        async_db.add(wellness_post)
        await async_db.flush()

        # Assert: responded_at não deve ter sido alterado
        result = await async_db.execute(
            text("SELECT responded_at FROM wellness_reminders WHERE id = :id"),
            {"id": reminder_id}
        )
        row = result.fetchone()

        # O timestamp original deve ser preservado (com tolerância de microssegundos)
        assert row[0] is not None
        # Comparar ignorando microssegundos que podem variar
        assert abs((row[0] - original_responded_at).total_seconds()) < 1, (
            "responded_at não deve ser alterado se já estava preenchido"
        )

    @pytest.mark.asyncio
    async def test_trigger_only_updates_matching_athlete_session(
        self,
        async_db: AsyncSession,
        inv046_organization: Organization,
        inv046_team: Team,
        inv046_user: User,
        inv046_athlete: Athlete,
        inv046_training_session: TrainingSession,
        inv046_person: Person,
    ):
        """
        CASO CONTROLE: Trigger só atualiza reminder do mesmo atleta/sessão.

        Reminder de outro atleta ou outra sessão não deve ser afetado.

        Evidência: schema.sql:287 - WHERE training_session_id = NEW.training_session_id
                                   AND athlete_id = NEW.athlete_id
        """
        # Arrange: criar outro atleta
        other_athlete = Athlete(
            id=uuid4(),
            person_id=UUID(inv046_person.id),
            organization_id=UUID(inv046_organization.id),
            athlete_name="Outro Atleta INV-046",
            birth_date=date(2001, 2, 2),
        )
        async_db.add(other_athlete)
        await async_db.flush()

        # Criar reminder para OUTRO atleta na mesma sessão
        other_reminder_id = uuid4()
        sent_at = datetime.now(timezone.utc) - timedelta(hours=2)

        await async_db.execute(
            text("""
                INSERT INTO wellness_reminders
                (id, training_session_id, athlete_id, sent_at, responded_at, reminder_count)
                VALUES (:id, :session_id, :athlete_id, :sent_at, NULL, 1)
            """),
            {
                "id": other_reminder_id,
                "session_id": inv046_training_session.id,
                "athlete_id": other_athlete.id,  # OUTRO atleta
                "sent_at": sent_at,
            }
        )
        await async_db.flush()

        # Act: inserir wellness_post para inv046_athlete (não other_athlete)
        wellness_post = WellnessPost(
            id=uuid4(),
            organization_id=UUID(inv046_organization.id),
            training_session_id=inv046_training_session.id,
            athlete_id=inv046_athlete.id,  # atleta original
            created_by_user_id=UUID(inv046_user.id),
            session_rpe=7,
            fatigue_after=6,
            mood_after=7,
        )
        async_db.add(wellness_post)
        await async_db.flush()

        # Assert: reminder do OUTRO atleta não foi afetado
        result = await async_db.execute(
            text("SELECT responded_at FROM wellness_reminders WHERE id = :id"),
            {"id": other_reminder_id}
        )
        row = result.fetchone()

        assert row[0] is None, (
            "responded_at de outro atleta não deve ser afetado pelo trigger"
        )
