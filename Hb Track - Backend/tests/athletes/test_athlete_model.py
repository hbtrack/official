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

    def test_create_athlete_basic(self, db, organization, membership):
        """Criar atleta com campos obrigatórios."""
        athlete = Athlete(
            organization_id=organization.id,
            created_by_membership_id=membership.id,
            person_id=uuid4(),
            full_name="Maria Silva",
        )
        db.add(athlete)
        db.flush()

        assert athlete.id is not None
        assert athlete.full_name == "Maria Silva"
        assert athlete.state == AthleteState.ativa.value

    def test_create_athlete_all_fields(self, db, organization, membership):
        """Criar atleta com todos os campos."""
        athlete = Athlete(
            organization_id=organization.id,
            created_by_membership_id=membership.id,
            person_id=uuid4(),
            full_name="Ana Santos",
            nickname="Aninha",
            birth_date=date(2008, 5, 15),
            position="pivô",
        )
        db.add(athlete)
        db.flush()

        assert athlete.nickname == "Aninha"
        assert athlete.birth_date == date(2008, 5, 15)
        assert athlete.position == "pivô"

    def test_athlete_default_state_ativa(self, db, organization, membership):
        """Estado padrão é 'ativa' (R13)."""
        athlete = Athlete(
            organization_id=organization.id,
            created_by_membership_id=membership.id,
            person_id=uuid4(),
            full_name="Teste Default",
        )
        db.add(athlete)
        db.flush()

        assert athlete.state == AthleteState.ativa.value
        assert athlete.current_state == AthleteState.ativa

    def test_athlete_is_active_property(self, db, organization, membership):
        """Propriedade is_active reflete soft delete."""
        athlete = Athlete(
            organization_id=organization.id,
            created_by_membership_id=membership.id,
            person_id=uuid4(),
            full_name="Teste Active",
        )
        db.add(athlete)
        db.flush()

        assert athlete.is_active is True
        assert athlete.deleted_at is None

    def test_athlete_repr(self, db, organization, membership):
        """Representação string do atleta."""
        athlete = Athlete(
            organization_id=organization.id,
            created_by_membership_id=membership.id,
            person_id=uuid4(),
            full_name="Repr Test",
        )
        db.add(athlete)
        db.flush()

        assert "Repr Test" in repr(athlete)
        assert "ativa" in repr(athlete)


class TestAthleteStateEnum:
    """Testes do enum AthleteState."""

    def test_state_values(self):
        """Verificar valores do enum (R13)."""
        assert AthleteState.ativa.value == "ativa"
        assert AthleteState.lesionada.value == "lesionada"
        assert AthleteState.dispensada.value == "dispensada"

    def test_state_from_string(self):
        """Criar enum a partir de string."""
        state = AthleteState("lesionada")
        assert state == AthleteState.lesionada


class TestAthleteSoftDelete:
    """Testes de soft delete (RDB4)."""

    def test_soft_delete_sets_deleted_at(self, db, organization, membership):
        """Soft delete define deleted_at."""
        from datetime import datetime, timezone

        athlete = Athlete(
            organization_id=organization.id,
            created_by_membership_id=membership.id,
            person_id=uuid4(),
            full_name="Soft Delete Test",
        )
        db.add(athlete)
        db.flush()

        # Simular soft delete
        athlete.deleted_at = datetime.now(timezone.utc)
        athlete.deleted_reason = "Teste de exclusão"
        db.flush()

        assert athlete.is_active is False
        assert athlete.deleted_reason == "Teste de exclusão"
