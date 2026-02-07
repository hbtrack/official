"""
INV-TRAIN-034 — Qualidade do sono deve estar entre 1 e 5

Enunciado: Qualidade do sono deve estar entre 1 e 5.

Evidência (DB constraint):
  - ck_wellness_pre_sleep_quality CHECK ((sleep_quality >= 1) AND (sleep_quality <= 5)) (schema.sql:2895)

Obrigação A: Analisei o schema.sql. Para criar o payload mínimo, identifico:
  1. FK Obrigatória: organization_id (Âncora: wellness_pre.organization_id FK). Usarei fixture inv_org.
  2. FK Obrigatória: training_session_id (Âncora: wellness_pre.training_session_id FK). Usarei fixture inv_session.
  3. FK Obrigatória: athlete_id (Âncora: wellness_pre.athlete_id FK). Usarei fixture inv_athlete.
  4. FK Obrigatória: created_by_user_id (Âncora: wellness_pre.created_by_user_id FK). Usarei fixture inv_user.
  5. NOT NULL: sleep_hours (Âncora: wellness_pre.sleep_hours NOT NULL). Usarei valor válido 8.0.
  6. NOT NULL: sleep_quality (Âncora: wellness_pre.sleep_quality NOT NULL). Campo alvo do teste.
  7. NOT NULL: fatigue_pre (Âncora: wellness_pre.fatigue_pre NOT NULL). Usarei valor válido 3.
  8. NOT NULL: stress_level (Âncora: wellness_pre.stress_level NOT NULL). Usarei valor válido 3.
  9. NOT NULL: muscle_soreness (Âncora: wellness_pre.muscle_soreness NOT NULL). Usarei valor válido 3.
  O resto será omitido.

Obrigação B: Invariante alvo: ck_wellness_pre_sleep_quality (CHECK).
  * SQLSTATE Esperado: 23514 (check_violation).
  * Constraint Name: ck_wellness_pre_sleep_quality.
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


class TestInvTrain034WellnessPreSleepQuality:
    """Testes para INV-TRAIN-034: Qualidade do sono deve estar entre 1 e 5."""

    @pytest.mark.asyncio
    async def test_valid_case__quality_3(self, async_db: AsyncSession):
        """sleep_quality = 3 deve ser aceito (valor válido no range)."""
        
        # Criar fixtures inline para evitar colisão
        category = Category(
            id=99036,
            name="Categoria INV-034",
            max_age=19,
            is_active=True,
        )
        async_db.add(category)

        organization = Organization(
            id=str(uuid4()),
            name="Org INV-034",
        )
        async_db.add(organization)

        person = Person(
            id=str(uuid4()),
            full_name="Atleta INV-034",
            first_name="Atleta",
            last_name="INV-034",
            birth_date=date(1995, 1, 1),
        )
        async_db.add(person)

        user = User(
            id=str(uuid4()),
            person_id=person.id,
            email="inv034@hbtrack.com",
        )
        async_db.add(user)

        team = Team(
            id=uuid4(),
            organization_id=organization.id,
            name="Equipe INV-034",
            category_id=category.id,
            gender="masculino",
            is_our_team=True,
        )
        async_db.add(team)

        await async_db.flush()

        athlete = Athlete(
            id=str(uuid4()),
            person_id=person.id,
            jersey_number=36,
        )
        async_db.add(athlete)

        session = TrainingSession(
            id=uuid4(),
            organization_id=organization.id,
            team_id=team.id,
            session_at=datetime.now(timezone.utc),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Teste sleep quality válido",
            location="Ginásio",
            status="draft",
            created_by_user_id=user.id,
        )
        async_db.add(session)

        await async_db.flush()

        # Payload mínimo com sleep_quality válido
        wellness_pre = WellnessPre(
            id=uuid4(),
            organization_id=organization.id,
            training_session_id=session.id,
            athlete_id=athlete.id,
            created_by_user_id=user.id,
            sleep_hours=Decimal("8.0"),
            sleep_quality=3,  # Valor válido
            fatigue_pre=3,
            stress_level=3,
            muscle_soreness=3,
        )
        async_db.add(wellness_pre)
        await async_db.flush()

        # Se chegou aqui sem exceção, constraint passou
        assert wellness_pre.id is not None

    @pytest.mark.asyncio
    async def test_invalid_case_1__quality_exceeds_5(self, async_db: AsyncSession):
        """sleep_quality = 6 deve ser rejeitado pela constraint DB (excede limite superior)."""
        
        # Criar fixtures inline
        category = Category(
            id=99037,
            name="Categoria INV-034B",
            max_age=19,
            is_active=True,
        )
        async_db.add(category)

        organization = Organization(
            id=str(uuid4()),
            name="Org INV-034B",
        )
        async_db.add(organization)

        person = Person(
            id=str(uuid4()),
            full_name="Atleta INV-034B",
            first_name="Atleta",
            last_name="INV-034B",
            birth_date=date(1995, 1, 1),
        )
        async_db.add(person)

        user = User(
            id=str(uuid4()),
            person_id=person.id,
            email="inv034b@hbtrack.com",
        )
        async_db.add(user)

        team = Team(
            id=uuid4(),
            organization_id=organization.id,
            name="Equipe INV-034B",
            category_id=category.id,
            gender="feminino",
            is_our_team=True,
        )
        async_db.add(team)

        await async_db.flush()

        athlete = Athlete(
            id=str(uuid4()),
            person_id=person.id,
            jersey_number=37,
        )
        async_db.add(athlete)

        session = TrainingSession(
            id=uuid4(),
            organization_id=organization.id,
            team_id=team.id,
            session_at=datetime.now(timezone.utc),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Teste sleep quality inválido",
            location="Ginásio",
            status="draft",
            created_by_user_id=user.id,
        )
        async_db.add(session)

        await async_db.flush()

        # Payload com sleep_quality inválido (excede 5)
        wellness_pre = WellnessPre(
            id=uuid4(),
            organization_id=organization.id,
            training_session_id=session.id,
            athlete_id=athlete.id,
            created_by_user_id=user.id,
            sleep_hours=Decimal("8.0"),
            sleep_quality=6,  # Excede o limite
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
            assert constraint_name == "ck_wellness_pre_sleep_quality"

        # Isolamento: restaurar sessão após IntegrityError
        await async_db.rollback()

    @pytest.mark.asyncio
    async def test_invalid_case_2__quality_zero(self, async_db: AsyncSession):
        """sleep_quality = 0 deve ser rejeitado pela constraint DB (abaixo do limite inferior)."""
        
        # Criar fixtures inline
        category = Category(
            id=99038,
            name="Categoria INV-034C",
            max_age=19,
            is_active=True,
        )
        async_db.add(category)

        organization = Organization(
            id=str(uuid4()),
            name="Org INV-034C",
        )
        async_db.add(organization)

        person = Person(
            id=str(uuid4()),
            full_name="Atleta INV-034C",
            first_name="Atleta",
            last_name="INV-034C",
            birth_date=date(1995, 1, 1),
        )
        async_db.add(person)

        user = User(
            id=str(uuid4()),
            person_id=person.id,
            email="inv034c@hbtrack.com",
        )
        async_db.add(user)

        team = Team(
            id=uuid4(),
            organization_id=organization.id,
            name="Equipe INV-034C",
            category_id=category.id,
            gender="masculino",
            is_our_team=True,
        )
        async_db.add(team)

        await async_db.flush()

        athlete = Athlete(
            id=str(uuid4()),
            person_id=person.id,
            jersey_number=38,
        )
        async_db.add(athlete)

        session = TrainingSession(
            id=uuid4(),
            organization_id=organization.id,
            team_id=team.id,
            session_at=datetime.now(timezone.utc),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Teste sleep quality zero",
            location="Ginásio",
            status="draft",
            created_by_user_id=user.id,
        )
        async_db.add(session)

        await async_db.flush()

        # Payload com sleep_quality inválido (zero)
        wellness_pre = WellnessPre(
            id=uuid4(),
            organization_id=organization.id,
            training_session_id=session.id,
            athlete_id=athlete.id,
            created_by_user_id=user.id,
            sleep_hours=Decimal("8.0"),
            sleep_quality=0,  # Abaixo do limite
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
            assert constraint_name == "ck_wellness_pre_sleep_quality"

        # Isolamento: restaurar sessão após IntegrityError
        await async_db.rollback()

    def test_constraint_checks_sleep_quality(self):
        """Verifica que a constraint verifica o campo sleep_quality."""
        content = self._get_schema_content()
        lines = content.split("\n")

        constraint_line = None
        for line in lines:
            if self.CONSTRAINT_NAME in line:
                constraint_line = line
                break

        assert constraint_line, f"Constraint {self.CONSTRAINT_NAME} não encontrada"
        assert "sleep_quality" in constraint_line, (
            "Constraint deve verificar o campo sleep_quality"
        )

    def test_constraint_min_value_one(self):
        """Verifica que a constraint exige valor mínimo 1."""
        content = self._get_schema_content()
        lines = content.split("\n")

        constraint_line = None
        for line in lines:
            if self.CONSTRAINT_NAME in line:
                constraint_line = line
                break

        assert constraint_line, f"Constraint {self.CONSTRAINT_NAME} não encontrada"
        assert ">= 1" in constraint_line or ">=1" in constraint_line, (
            "Constraint deve exigir sleep_quality >= 1"
        )

    def test_constraint_max_value_five(self):
        """Verifica que a constraint exige valor máximo 5."""
        content = self._get_schema_content()
        lines = content.split("\n")

        constraint_line = None
        for line in lines:
            if self.CONSTRAINT_NAME in line:
                constraint_line = line
                break

        assert constraint_line, f"Constraint {self.CONSTRAINT_NAME} não encontrada"
        assert "<= 5" in constraint_line or "<=5" in constraint_line, (
            "Constraint deve exigir sleep_quality <= 5"
        )

    def test_constraint_uses_and_logic(self):
        """Verifica que a constraint usa AND para combinar min e max."""
        content = self._get_schema_content()
        lines = content.split("\n")

        constraint_line = None
        for line in lines:
            if self.CONSTRAINT_NAME in line:
                constraint_line = line
                break

        assert constraint_line, f"Constraint {self.CONSTRAINT_NAME} não encontrada"
        assert "AND" in constraint_line, (
            "Constraint deve usar AND para combinar >= 1 e <= 5"
        )
