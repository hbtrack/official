"""
INV-TRAIN-033 — Horas de sono deve estar entre 0 e 24

Enunciado: Horas de sono deve estar entre 0 e 24.

Evidência (DB constraint):
  - ck_wellness_pre_sleep_hours CHECK ((sleep_hours >= 0) AND (sleep_hours <= 24)) (schema.sql:2894)

Obrigação A: Analisei o schema.sql. Para criar o payload mínimo, identifico:
  1. FK Obrigatória: organization_id (Âncora: wellness_pre.organization_id FK). Usarei fixture inv_org.
  2. FK Obrigatória: training_session_id (Âncora: wellness_pre.training_session_id FK). Usarei fixture inv_session.
  3. FK Obrigatória: athlete_id (Âncora: wellness_pre.athlete_id FK). Usarei fixture inv_athlete.
  4. FK Obrigatória: created_by_user_id (Âncora: wellness_pre.created_by_user_id FK). Usarei fixture inv_user.
  5. NOT NULL: sleep_hours (Âncora: wellness_pre.sleep_hours NOT NULL). Campo alvo do teste.
  6. NOT NULL: sleep_quality (Âncora: wellness_pre.sleep_quality NOT NULL). Usarei valor válido 3.
  7. NOT NULL: fatigue_pre (Âncora: wellness_pre.fatigue_pre NOT NULL). Usarei valor válido 3.
  8. NOT NULL: stress_level (Âncora: wellness_pre.stress_level NOT NULL). Usarei valor válido 3.
  9. NOT NULL: muscle_soreness (Âncora: wellness_pre.muscle_soreness NOT NULL). Usarei valor válido 3.
  O resto será omitido.

Obrigação B: Invariante alvo: ck_wellness_pre_sleep_hours (CHECK).
  * SQLSTATE Esperado: 23514 (check_violation).
  * Constraint Name: ck_wellness_pre_sleep_hours.
  * Estratégia: pytest.raises validando SQLSTATE e presença do nome da constraint.
"""

from datetime import datetime, timezone, date
from uuid import uuid4
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wellness_pre import WellnessPre
from app.models.organization import Organization
from app.models.person import Person
from app.models.user import User
from app.models.athlete import Athlete
from app.models.team import Team
from app.models.category import Category
from app.models.training_session import TrainingSession


class TestInvTrain033WellnessPreSleepHours:
    """Testes para INV-TRAIN-033: Horas de sono deve estar entre 0 e 24."""

    @pytest.mark.asyncio
    async def test_valid_case__sleep_12_hours(self, async_db: AsyncSession):
        """sleep_hours = 12.0 deve ser aceito (valor válido no range)."""
        
        # Criar fixtures inline para evitar colisão
        category = Category(
            id=99033,
            name="Categoria INV-033",
            max_age=19,
            is_active=True,
        )
        async_db.add(category)

        organization = Organization(
            id=str(uuid4()),
            name="Org INV-033",
        )
        async_db.add(organization)

        person = Person(
            id=str(uuid4()),
            full_name="Atleta INV-033",
            first_name="Atleta",
            last_name="INV-033",
            birth_date=date(1995, 1, 1),
        )
        async_db.add(person)

        user = User(
            id=str(uuid4()),
            person_id=person.id,
            email="inv033@hbtrack.com",
        )
        async_db.add(user)

        team = Team(
            id=uuid4(),
            organization_id=organization.id,
            name="Equipe INV-033",
            category_id=category.id,
            gender="masculino",
            is_our_team=True,
        )
        async_db.add(team)

        await async_db.flush()

        athlete = Athlete(
            id=str(uuid4()),
            person_id=person.id,
            athlete_name="Atleta 033",
            birth_date=date(1995, 1, 1),
        )
        async_db.add(athlete)

        session = TrainingSession(
            id=uuid4(),
            organization_id=organization.id,
            team_id=team.id,
            session_at=datetime.now(timezone.utc),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Teste sleep hours válido",
            location="Ginásio",
            status="draft",
            created_by_user_id=user.id,
        )
        async_db.add(session)

        await async_db.flush()

        # Payload mínimo com sleep_hours válido
        wellness_pre = WellnessPre(
            id=uuid4(),
            organization_id=organization.id,
            training_session_id=session.id,
            athlete_id=athlete.id,
            created_by_user_id=user.id,
            sleep_hours=Decimal("12.0"),  # Valor válido
            sleep_quality=3,
            fatigue_pre=3,
            stress_level=3,
            muscle_soreness=3,
        )
        async_db.add(wellness_pre)
        await async_db.flush()

        # Se chegou aqui sem exceção, constraint passou
        assert wellness_pre.id is not None

    @pytest.mark.asyncio
    async def test_invalid_case_1__sleep_exceeds_24(self, async_db: AsyncSession):
        """sleep_hours = 25.0 deve ser rejeitado pela constraint DB (excede limite superior)."""
        
        # Criar fixtures inline
        category = Category(
            id=99034,
            name="Categoria INV-033B",
            max_age=19,
            is_active=True,
        )
        async_db.add(category)

        organization = Organization(
            id=str(uuid4()),
            name="Org INV-033B",
        )
        async_db.add(organization)

        person = Person(
            id=str(uuid4()),
            full_name="Atleta INV-033B",
            first_name="Atleta",
            last_name="INV-033B",
            birth_date=date(1995, 1, 1),
        )
        async_db.add(person)

        user = User(
            id=str(uuid4()),
            person_id=person.id,
            email="inv033b@hbtrack.com",
        )
        async_db.add(user)

        team = Team(
            id=uuid4(),
            organization_id=organization.id,
            name="Equipe INV-033B",
            category_id=category.id,
            gender="feminino",
            is_our_team=True,
        )
        async_db.add(team)

        await async_db.flush()

        athlete = Athlete(
            id=str(uuid4()),
            person_id=person.id,
            athlete_name="Atleta 033B",
            birth_date=date(1995, 1, 1),
        )
        async_db.add(athlete)

        session = TrainingSession(
            id=uuid4(),
            organization_id=organization.id,
            team_id=team.id,
            session_at=datetime.now(timezone.utc),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Teste sleep hours inválido",
            location="Ginásio",
            status="draft",
            created_by_user_id=user.id,
        )
        async_db.add(session)

        await async_db.flush()

        # Payload com sleep_hours inválido (excede 24)
        wellness_pre = WellnessPre(
            id=uuid4(),
            organization_id=organization.id,
            training_session_id=session.id,
            athlete_id=athlete.id,
            created_by_user_id=user.id,
            sleep_hours=Decimal("25.0"),  # Excede o limite
            sleep_quality=3,
            fatigue_pre=3,
            stress_level=3,
            muscle_soreness=3,
        )
        async_db.add(wellness_pre)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Assert estável: SQLSTATE (primário)
        orig = exc_info.value.orig
        pgcode = getattr(orig, "pgcode", None)
        assert pgcode == "23514"  # CHECK violation

        # Assert estável: constraint_name (secundário, estruturado quando exposto)
        diag = getattr(orig, "diag", None)
        constraint_name = getattr(diag, "constraint_name", None) or getattr(orig, "constraint_name", None)

        if constraint_name is not None:
            assert constraint_name == "ck_wellness_pre_sleep_hours"

        # Isolamento: restaurar sessão após IntegrityError
        await async_db.rollback()

    @pytest.mark.asyncio
    async def test_invalid_case_2__sleep_negative(self, async_db: AsyncSession):
        """sleep_hours = -1.0 deve ser rejeitado pela constraint DB (abaixo do limite inferior)."""
        
        # Criar fixtures inline
        category = Category(
            id=99035,
            name="Categoria INV-033C",
            max_age=19,
            is_active=True,
        )
        async_db.add(category)

        organization = Organization(
            id=str(uuid4()),
            name="Org INV-033C",
        )
        async_db.add(organization)

        person = Person(
            id=str(uuid4()),
            full_name="Atleta INV-033C",
            first_name="Atleta",
            last_name="INV-033C",
            birth_date=date(1995, 1, 1),
        )
        async_db.add(person)

        user = User(
            id=str(uuid4()),
            person_id=person.id,
            email="inv033c@hbtrack.com",
        )
        async_db.add(user)

        team = Team(
            id=uuid4(),
            organization_id=organization.id,
            name="Equipe INV-033C",
            category_id=category.id,
            gender="masculino",
            is_our_team=True,
        )
        async_db.add(team)

        await async_db.flush()

        athlete = Athlete(
            id=str(uuid4()),
            person_id=person.id,
            athlete_name="Atleta 033C",
            birth_date=date(1995, 1, 1),
        )
        async_db.add(athlete)

        session = TrainingSession(
            id=uuid4(),
            organization_id=organization.id,
            team_id=team.id,
            session_at=datetime.now(timezone.utc),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Teste sleep hours negativo",
            location="Ginásio",
            status="draft",
            created_by_user_id=user.id,
        )
        async_db.add(session)

        await async_db.flush()

        # Payload com sleep_hours inválido (negativo)
        wellness_pre = WellnessPre(
            id=uuid4(),
            organization_id=organization.id,
            training_session_id=session.id,
            athlete_id=athlete.id,
            created_by_user_id=user.id,
            sleep_hours=Decimal("-1.0"),  # Abaixo do limite
            sleep_quality=3,
            fatigue_pre=3,
            stress_level=3,
            muscle_soreness=3,
        )
        async_db.add(wellness_pre)

        with pytest.raises(IntegrityError) as exc_info:
            await async_db.flush()

        # Assert estável: SQLSTATE (primário)
        orig = exc_info.value.orig
        pgcode = getattr(orig, "pgcode", None)
        assert pgcode == "23514"  # CHECK violation

        # Assert estável: constraint_name (secundário, estruturado quando exposto)
        diag = getattr(orig, "diag", None)
        constraint_name = getattr(diag, "constraint_name", None) or getattr(orig, "constraint_name", None)

        if constraint_name is not None:
            assert constraint_name == "ck_wellness_pre_sleep_hours"

        # Isolamento: restaurar sessão após IntegrityError
        await async_db.rollback()
