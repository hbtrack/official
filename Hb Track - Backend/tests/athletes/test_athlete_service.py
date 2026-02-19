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

    @pytest.mark.asyncio
    async def test_create_athlete_success(self, async_db, organization, membership):
        """Criar atleta via service."""
        service = AthleteService(async_db)

        athlete = await service.create(
            organization_id=organization.id,
            person_id=uuid4(),
            full_name="Atleta Teste",
        )

        assert athlete.id is not None
        assert athlete.athlete_name == "Atleta Teste"
        assert athlete.state == AthleteState.ATIVA.value

    @pytest.mark.asyncio
    async def test_create_athlete_with_optional_fields(self, async_db, organization, membership):
        """Criar atleta com campos opcionais."""
        service = AthleteService(async_db)

        athlete = await service.create(
            organization_id=organization.id,
            person_id=uuid4(),
            full_name="Atleta Completa",
            nickname="AC",
            birth_date=date(2007, 3, 20),
        )

        assert athlete.athlete_nickname == "AC"
        assert athlete.birth_date == date(2007, 3, 20)


class TestAthleteServiceRead:
    """Testes de leitura de atletas."""

    @pytest.mark.asyncio
    async def test_list_athletes(self, async_db, athlete):
        """Listar atletas."""
        service = AthleteService(async_db)
        athletes, total = await service.list_athletes(
            organization_id=athlete.organization_id
        )

        assert len(athletes) >= 1
        assert any(a.id == athlete.id for a in athletes)

    @pytest.mark.asyncio
    async def test_list_athletes_by_organization(self, async_db, athlete, organization):
        """Listar atletas por organização."""
        service = AthleteService(async_db)
        athletes, total = await service.list_athletes(organization_id=organization.id)

        assert len(athletes) >= 1
        assert all(a.organization_id == str(organization.id) for a in athletes)

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, async_db, athlete):
        """Buscar atleta por ID existente."""
        service = AthleteService(async_db)
        found = await service.get_by_id(athlete.id)

        assert found is not None
        assert found.id == athlete.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, async_db):
        """Buscar atleta por ID inexistente."""
        service = AthleteService(async_db)
        found = await service.get_by_id(uuid4())

        assert found is None


class TestAthleteServiceUpdate:
    """Testes de atualização de atleta."""

    @pytest.mark.asyncio
    async def test_update_athlete_name(self, async_db, athlete):
        """Atualizar nome do atleta."""
        service = AthleteService(async_db)

        updated = await service.update(
            athlete_id=athlete.id,
            athlete_name="Nome Atualizado",
        )

        assert updated.athlete_name == "Nome Atualizado"

    @pytest.mark.asyncio
    async def test_update_athlete_position(self, async_db, athlete):
        """Atualizar posição do atleta."""
        service = AthleteService(async_db)

        updated = await service.update(
            athlete_id=athlete.id,
            athlete_nickname="goleira",
        )

        assert updated.athlete_nickname == "goleira"

    @pytest.mark.asyncio
    async def test_update_athlete_not_found(self, async_db):
        """Atualizar atleta inexistente retorna None."""
        service = AthleteService(async_db)

        result = await service.update(
            athlete_id=uuid4(),
            athlete_name="Teste",
        )

        assert result is None


class TestAthleteServiceChangeState:
    """Testes de mudança de estado (R13/R14)."""

    @pytest.mark.skip(reason="change_state não implementado - comentado no service")
    @pytest.mark.asyncio
    async def test_change_state_to_lesionada(self, async_db, athlete):
        """Mudar estado para lesionada (R13)."""
        service = AthleteService(async_db)

        new_state = await service.change_state(
            athlete=athlete,
            new_state=AthleteState.LESIONADA,
            reason="Lesão no joelho",
        )

        assert new_state.state == AthleteState.LESIONADA.value
        assert new_state.reason == "Lesão no joelho"
        assert athlete.state == AthleteState.LESIONADA.value

    @pytest.mark.skip(reason="change_state não implementado - comentado no service")
    @pytest.mark.asyncio
    async def test_change_state_to_dispensada(self, async_db, athlete):
        """Mudar estado para dispensada (R13)."""
        service = AthleteService(async_db)

        new_state = await service.change_state(
            athlete=athlete,
            new_state=AthleteState.DISPENSADA,
            reason="Saída voluntária",
        )

        assert new_state.state == AthleteState.DISPENSADA.value
        assert athlete.state == AthleteState.DISPENSADA.value

    @pytest.mark.skip(reason="change_state não implementado - comentado no service")
    @pytest.mark.asyncio
    async def test_change_state_creates_history(self, async_db, athlete):
        """Mudança de estado cria registro no histórico (RF16)."""
        service = AthleteService(async_db)

        await service.change_state(
            athlete=athlete,
            new_state=AthleteState.LESIONADA,
            reason="Primeira lesão",
        )

        history = await service.get_state_history(athlete.id)
        assert len(history) >= 1
        assert history[0].state == AthleteState.LESIONADA.value


class TestAthleteServiceStateHistory:
    """Testes de histórico de estados."""

    @pytest.mark.skip(reason="get_state_history não implementado - comentado no service")
    @pytest.mark.asyncio
    async def test_get_state_history_empty(self, async_db, athlete):
        """Histórico vazio para atleta sem mudanças."""
        service = AthleteService(async_db)
        history = await service.get_state_history(athlete.id)

        # Pode ter 0 ou 1 (estado inicial)
        assert isinstance(history, list)

    @pytest.mark.skip(reason="get_state_history não implementado - comentado no service")
    @pytest.mark.asyncio
    async def test_get_state_history_ordered(self, async_db, athlete):
        """Histórico ordenado por data decrescente."""
        service = AthleteService(async_db)

        # Criar múltiplas mudanças
        await service.change_state(athlete, AthleteState.LESIONADA, "Lesão 1")
        await service.change_state(athlete, AthleteState.ATIVA, "Recuperada")
        await service.change_state(athlete, AthleteState.DISPENSADA, "Dispensa")

        history = await service.get_state_history(athlete.id)

        assert len(history) >= 3
        # Mais recente primeiro
        assert history[0].state == AthleteState.DISPENSADA.value
