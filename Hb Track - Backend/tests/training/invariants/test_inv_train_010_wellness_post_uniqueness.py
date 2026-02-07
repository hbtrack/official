"""
INV-TRAIN-010 — Unicidade: 1 wellness_post por athlete×session

Enunciado: Cada atleta só pode ter 1 registro wellness_post por sessão de treino.

Evidência (DB unique index):
  - ux_wellness_post_session_athlete (schema.sql:5180)
  - CREATE UNIQUE INDEX ux_wellness_post_session_athlete ON wellness_post (training_session_id, athlete_id) WHERE (deleted_at IS NULL)

Obrigação A: Analisei o schema.sql. Para criar o payload mínimo, identifico:
  1. FK Obrigatória: organization_id (Âncora: wellness_post.organization_id FK). Usarei fixture inv_org.
  2. FK Obrigatória: training_session_id (Âncora: wellness_post.training_session_id FK). Usarei fixture inv_session.
  3. FK Obrigatória: athlete_id (Âncora: wellness_post.athlete_id FK). Usarei fixture inv_athlete.
  4. FK Obrigatória: created_by_user_id (Âncora: wellness_post.created_by_user_id FK). Usarei fixture inv_user.
  5. NOT NULL: session_rpe (Âncora: wellness_post.session_rpe NOT NULL). Usarei valor válido 5.
  6. NOT NULL: fatigue_after (Âncora: wellness_post.fatigue_after NOT NULL). Usarei valor válido 5.
  7. NOT NULL: mood_after (Âncora: wellness_post.mood_after NOT NULL). Usarei valor válido 5.
  O resto será omitido.

Obrigação B: Invariante alvo: ux_wellness_post_session_athlete (UNIQUE INDEX).
  * SQLSTATE Esperado: 23505 (unique_violation).
  * Constraint Name: ux_wellness_post_session_athlete.
  * Estratégia: pytest.raises validando SQLSTATE e presença do nome da constraint.
"""

from datetime import datetime, timezone, date
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wellness_post import WellnessPost
from app.models.organization import Organization
from app.models.person import Person
from app.models.user import User
from app.models.athlete import Athlete
from app.models.team import Team
from app.models.category import Category
from app.models.training_session import TrainingSession


class TestInvTrain010WellnessPostUniqueness:
    """Testes para INV-TRAIN-010: Unicidade wellness_post por athlete×session."""

    @pytest.mark.asyncio
    async def test_valid_case__different_sessions(self, async_db: AsyncSession):
        """Mesmo atleta pode ter wellness_post em sessões diferentes."""
        
        # Criar fixtures inline para evitar colisão
        category = Category(
            id=99010,
            name="Categoria INV-010",
            max_age=19,
            is_active=True,
        )
        async_db.add(category)

        organization = Organization(
            id=str(uuid4()),
            name="Org INV-010",
        )
        async_db.add(organization)

        person = Person(
            id=str(uuid4()),
            full_name="Atleta INV-010",
            first_name="Atleta",
            last_name="INV-010",
            birth_date=date(1995, 1, 1),
        )
        async_db.add(person)

        user = User(
            id=str(uuid4()),
            person_id=person.id,
            email="inv010@hbtrack.com",
        )
        async_db.add(user)

        team = Team(
            id=uuid4(),
            organization_id=organization.id,
            name="Equipe INV-010",
            category_id=category.id,
            gender="masculino",
            is_our_team=True,
        )
        async_db.add(team)

        await async_db.flush()

        athlete = Athlete(
            id=str(uuid4()),
            person_id=person.id,
            jersey_number=10,
        )
        async_db.add(athlete)

        # Sessão 1
        session1 = TrainingSession(
            id=uuid4(),
            organization_id=organization.id,
            team_id=team.id,
            session_at=datetime.now(timezone.utc),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Sessão 1",
            location="Ginásio",
            status="draft",
            created_by_user_id=user.id,
        )
        async_db.add(session1)

        # Sessão 2
        session2 = TrainingSession(
            id=uuid4(),
            organization_id=organization.id,
            team_id=team.id,
            session_at=datetime.now(timezone.utc),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Sessão 2",
            location="Ginásio",
            status="draft",
            created_by_user_id=user.id,
        )
        async_db.add(session2)

        await async_db.flush()

        # Wellness_post na sessão 1
        wellness_post1 = WellnessPost(
            id=uuid4(),
            organization_id=organization.id,
            training_session_id=session1.id,
            athlete_id=athlete.id,
            created_by_user_id=user.id,
            session_rpe=5,
            fatigue_after=5,
            mood_after=5,
        )
        async_db.add(wellness_post1)

        # Wellness_post na sessão 2 (deve ser aceito)
        wellness_post2 = WellnessPost(
            id=uuid4(),
            organization_id=organization.id,
            training_session_id=session2.id,  # Sessão diferente
            athlete_id=athlete.id,            # Mesmo atleta
            created_by_user_id=user.id,
            session_rpe=6,
            fatigue_after=6,
            mood_after=6,
        )
        async_db.add(wellness_post2)

        await async_db.flush()

        # Se chegou aqui sem exceção, constraint passou
        assert wellness_post1.id is not None
        assert wellness_post2.id is not None

    @pytest.mark.asyncio
    async def test_invalid_case_1__duplicate_athlete_session(self, async_db: AsyncSession):
        """Segundo wellness_post para mesmo atleta na mesma sessão deve ser rejeitado."""
        
        # Criar fixtures inline
        category = Category(
            id=99011,
            name="Categoria INV-010B",
            max_age=19,
            is_active=True,
        )
        async_db.add(category)

        organization = Organization(
            id=str(uuid4()),
            name="Org INV-010B",
        )
        async_db.add(organization)

        person = Person(
            id=str(uuid4()),
            full_name="Atleta INV-010B",
            first_name="Atleta",
            last_name="INV-010B",
            birth_date=date(1995, 1, 1),
        )
        async_db.add(person)

        user = User(
            id=str(uuid4()),
            person_id=person.id,
            email="inv010b@hbtrack.com",
        )
        async_db.add(user)

        team = Team(
            id=uuid4(),
            organization_id=organization.id,
            name="Equipe INV-010B",
            category_id=category.id,
            gender="feminino",
            is_our_team=True,
        )
        async_db.add(team)

        await async_db.flush()

        athlete = Athlete(
            id=str(uuid4()),
            person_id=person.id,
            jersey_number=11,
        )
        async_db.add(athlete)

        session = TrainingSession(
            id=uuid4(),
            organization_id=organization.id,
            team_id=team.id,
            session_at=datetime.now(timezone.utc),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Teste unicidade",
            location="Ginásio",
            status="draft",
            created_by_user_id=user.id,
        )
        async_db.add(session)

        await async_db.flush()

        # Primeiro wellness_post (deve ser aceito)
        wellness_post1 = WellnessPost(
            id=uuid4(),
            organization_id=organization.id,
            training_session_id=session.id,
            athlete_id=athlete.id,
            created_by_user_id=user.id,
            session_rpe=5,
            fatigue_after=5,
            mood_after=5,
        )
        async_db.add(wellness_post1)
        await async_db.flush()

        # Segundo wellness_post para mesmo atleta/sessão (deve ser rejeitado)
        wellness_post2 = WellnessPost(
            id=uuid4(),
            organization_id=organization.id,
            training_session_id=session.id,  # Mesma sessão
            athlete_id=athlete.id,            # Mesmo atleta
            created_by_user_id=user.id,
            session_rpe=6,
            fatigue_after=6,
            mood_after=6,
        )
        async_db.add(wellness_post2)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Assert estável: SQLSTATE (primário)
        orig = exc_info.value.orig
        pgcode = getattr(orig, "pgcode", None)
        assert pgcode == "23505"  # unique_violation

        # Assert estável: constraint_name (secundário, estruturado quando exposto)
        diag = getattr(orig, "diag", None)
        constraint_name = getattr(diag, "constraint_name", None) or getattr(orig, "constraint_name", None)

        if constraint_name is not None:
            assert constraint_name == "ux_wellness_post_session_athlete"

        # Isolamento: restaurar sessão após IntegrityError
        await async_db.rollback()
