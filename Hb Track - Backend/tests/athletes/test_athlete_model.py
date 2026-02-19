"""
Testes do modelo Athlete.
Ref: f04026216180, d00cc0ffee0c, d00ec0ffee0e, d012c0ffee12
"""
import pytest
from datetime import date
from uuid import uuid4

from app.models.athlete import Athlete, AthleteState


class TestAthleteModel:
    """Testes de criação e propriedades do modelo Athlete."""

    @pytest.mark.asyncio
    async def test_create_athlete_basic(self, async_db, organization, membership):
        """Criar atleta com campos obrigatórios."""
        athlete = Athlete(
            organization_id=organization.id,
            person_id=uuid4(),
            athlete_name="Maria Silva",
            birth_date=date(2000, 1, 1),
        )
        async_db.add(athlete)
        await async_db.flush()

        assert athlete.id is not None
        assert athlete.athlete_name == "Maria Silva"
        assert athlete.state == AthleteState.ATIVA.value

    @pytest.mark.asyncio
    async def test_create_athlete_all_fields(self, async_db, organization, membership):
        """Criar atleta com todos os campos."""
        athlete = Athlete(
            organization_id=organization.id,
            person_id=uuid4(),
            athlete_name="Ana Santos",
            athlete_nickname="Aninha",
            birth_date=date(2008, 5, 15),
        )
        async_db.add(athlete)
        await async_db.flush()

        assert athlete.athlete_nickname == "Aninha"
        assert athlete.birth_date == date(2008, 5, 15)

    @pytest.mark.asyncio
    async def test_athlete_default_state_ativa(self, async_db, organization, membership):
        """Estado padrão é 'ativa' (R13)."""
        athlete = Athlete(
            organization_id=organization.id,
            person_id=uuid4(),
            athlete_name="Teste Default",
            birth_date=date(2000, 1, 1),
        )
        async_db.add(athlete)
        await async_db.flush()

        assert athlete.state == AthleteState.ATIVA.value

    @pytest.mark.asyncio
    async def test_athlete_is_active_property(self, async_db, organization, membership):
        """Propriedade is_active reflete soft delete."""
        athlete = Athlete(
            organization_id=organization.id,
            person_id=uuid4(),
            athlete_name="Teste Active",
            birth_date=date(2000, 1, 1),
        )
        async_db.add(athlete)
        await async_db.flush()

        assert athlete.is_active is True
        assert athlete.deleted_at is None

    @pytest.mark.asyncio
    async def test_athlete_repr(self, async_db, organization, membership):
        """Representação string do atleta."""
        athlete = Athlete(
            organization_id=organization.id,
            person_id=uuid4(),
            athlete_name="Repr Test",
            birth_date=date(2000, 1, 1),
        )
        async_db.add(athlete)
        await async_db.flush()

        assert "Repr Test" in repr(athlete)
        assert "ativa" in repr(athlete)


class TestAthleteStateEnum:
    """Testes do enum AthleteState."""

    def test_state_values(self):
        """Verificar valores do enum (R13)."""
        assert AthleteState.ATIVA.value == "ativa"
        assert AthleteState.DISPENSADA.value == "dispensada"
        assert AthleteState.ARQUIVADA.value == "arquivada"

    def test_state_from_string(self):
        """Criar enum a partir de string."""
        state = AthleteState("dispensada")
        assert state == AthleteState.DISPENSADA


class TestAthleteSoftDelete:
    """Testes de soft delete (RDB4)."""

    @pytest.mark.asyncio
    async def test_soft_delete_sets_deleted_at(self, async_db, organization, membership):
        """Soft delete define deleted_at."""
        from datetime import datetime, timezone

        athlete = Athlete(
            organization_id=organization.id,
            person_id=uuid4(),
            athlete_name="Soft Delete Test",
            birth_date=date(2000, 1, 1),
        )
        async_db.add(athlete)
        await async_db.flush()

        # Simular soft delete
        athlete.deleted_at = datetime.now(timezone.utc)
        athlete.deleted_reason = "Teste de exclusão"
        await async_db.flush()

        assert athlete.is_active is False
        assert athlete.deleted_reason == "Teste de exclusão"
