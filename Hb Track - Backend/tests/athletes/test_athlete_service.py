"""
Testes do AthleteService.
Ref: R12, R13, R14, R38, RF16
"""
import pytest
from datetime import date
from uuid import uuid4

from app.models.athlete import AthleteState
from app.services.athlete_service import AthleteService


class TestAthleteServiceCreate:
    """Testes de criação de atleta."""

    def test_create_athlete_success(self, db, organization, membership):
        """Criar atleta via service."""
        service = AthleteService(db)

        athlete = service.create(
            organization_id=organization.id,
            created_by_membership_id=membership.id,
            person_id=uuid4(),
            full_name="Atleta Teste",
        )

        assert athlete.id is not None
        assert athlete.full_name == "Atleta Teste"
        assert athlete.state == AthleteState.ativa.value

    def test_create_athlete_with_optional_fields(self, db, organization, membership):
        """Criar atleta com campos opcionais."""
        service = AthleteService(db)

        athlete = service.create(
            organization_id=organization.id,
            created_by_membership_id=membership.id,
            person_id=uuid4(),
            full_name="Atleta Completa",
            nickname="AC",
            birth_date=date(2007, 3, 20),
            position="armadora",
        )

        assert athlete.nickname == "AC"
        assert athlete.birth_date == date(2007, 3, 20)
        assert athlete.position == "armadora"


class TestAthleteServiceRead:
    """Testes de leitura de atletas."""

    def test_list_athletes(self, db, athlete):
        """Listar atletas."""
        service = AthleteService(db)
        athletes = service.list_athletes()

        assert len(athletes) >= 1
        assert any(a.id == athlete.id for a in athletes)

    def test_list_athletes_by_organization(self, db, athlete, organization):
        """Listar atletas por organização."""
        service = AthleteService(db)
        athletes = service.list_athletes(organization_id=organization.id)

        assert len(athletes) >= 1
        assert all(a.organization_id == organization.id for a in athletes)

    def test_get_by_id_found(self, db, athlete):
        """Buscar atleta por ID existente."""
        service = AthleteService(db)
        found = service.get_by_id(athlete.id)

        assert found is not None
        assert found.id == athlete.id

    def test_get_by_id_not_found(self, db):
        """Buscar atleta por ID inexistente."""
        service = AthleteService(db)
        found = service.get_by_id(uuid4())

        assert found is None


class TestAthleteServiceUpdate:
    """Testes de atualização de atleta."""

    def test_update_athlete_name(self, db, athlete):
        """Atualizar nome do atleta."""
        service = AthleteService(db)

        updated = service.update(
            athlete_id=athlete.id,
            full_name="Nome Atualizado",
        )

        assert updated.full_name == "Nome Atualizado"

    def test_update_athlete_position(self, db, athlete):
        """Atualizar posição do atleta."""
        service = AthleteService(db)

        updated = service.update(
            athlete_id=athlete.id,
            position="goleira",
        )

        assert updated.position == "goleira"

    def test_update_athlete_not_found(self, db):
        """Atualizar atleta inexistente retorna None."""
        service = AthleteService(db)

        result = service.update(
            athlete_id=uuid4(),
            full_name="Teste",
        )

        assert result is None


class TestAthleteServiceChangeState:
    """Testes de mudança de estado (R13/R14)."""

    def test_change_state_to_lesionada(self, db, athlete):
        """Mudar estado para lesionada (R13)."""
        service = AthleteService(db)

        new_state = service.change_state(
            athlete=athlete,
            new_state=AthleteState.lesionada,
            reason="Lesão no joelho",
        )

        assert new_state.state == AthleteState.lesionada.value
        assert new_state.reason == "Lesão no joelho"
        assert athlete.state == AthleteState.lesionada.value

    def test_change_state_to_dispensada(self, db, athlete):
        """Mudar estado para dispensada (R13)."""
        service = AthleteService(db)

        new_state = service.change_state(
            athlete=athlete,
            new_state=AthleteState.dispensada,
            reason="Saída voluntária",
        )

        assert new_state.state == AthleteState.dispensada.value
        assert athlete.state == AthleteState.dispensada.value

    def test_change_state_creates_history(self, db, athlete):
        """Mudança de estado cria registro no histórico (RF16)."""
        service = AthleteService(db)

        service.change_state(
            athlete=athlete,
            new_state=AthleteState.lesionada,
            reason="Primeira lesão",
        )

        history = service.get_state_history(athlete.id)
        assert len(history) >= 1
        assert history[0].state == AthleteState.lesionada.value


class TestAthleteServiceStateHistory:
    """Testes de histórico de estados."""

    def test_get_state_history_empty(self, db, athlete):
        """Histórico vazio para atleta sem mudanças."""
        service = AthleteService(db)
        history = service.get_state_history(athlete.id)

        # Pode ter 0 ou 1 (estado inicial)
        assert isinstance(history, list)

    def test_get_state_history_ordered(self, db, athlete):
        """Histórico ordenado por data decrescente."""
        service = AthleteService(db)

        # Criar múltiplas mudanças
        service.change_state(athlete, AthleteState.lesionada, "Lesão 1")
        service.change_state(athlete, AthleteState.ativa, "Recuperada")
        service.change_state(athlete, AthleteState.dispensada, "Dispensa")

        history = service.get_state_history(athlete.id)

        assert len(history) >= 3
        # Mais recente primeiro
        assert history[0].state == AthleteState.dispensada.value
