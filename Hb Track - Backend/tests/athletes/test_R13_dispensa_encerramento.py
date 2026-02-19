"""
Testes da regra R13/R14 - Estados da atleta.
Ref: Matriz de enforcement

R13: Estados (ativa, lesionada, dispensada) e impactos
R14: "dispensada" encerra participações vigentes

NOTE: AthleteStateHistory não implementado - testes de mudança de estado desabilitados
"""
import pytest
from app.services.athlete_service import AthleteService
from app.models.athlete import Athlete, AthleteState


class TestR13EstadosAtleta:
    """R13: Estados da atleta e transições."""
    
    @pytest.mark.asyncio
    async def test_R13_create_athlete_state_ativa(self, async_db, organization):
        """Atleta criada com estado 'ativa' por padrão."""
        service = AthleteService(async_db)
        
        athlete = await service.create(
            organization_id=organization.id,
            full_name="Maria Silva",
        )
        
        assert athlete.state == AthleteState.ATIVA.value
    
    @pytest.mark.skip(reason="AthleteStateHistory não implementado - change_state() comentado")
    def test_R13_change_to_lesionada(self, db, athlete):
        """Transição para 'lesionada'."""
        pass
    
    @pytest.mark.skip(reason="AthleteStateHistory não implementado - change_state() comentado")
    def test_R13_change_to_dispensada(self, db, athlete):
        """Transição para 'dispensada'."""
        pass
    
    @pytest.mark.skip(reason="AthleteStateHistory não implementado - change_state() comentado")
    def test_RF16_state_change_creates_history(self, db, athlete):
        """RF16: Alteração cria registro no histórico."""
        pass


class TestR13DispensadaEncerraParticipacoes:
    """
    R13 Complemento V1.1: "dispensada" encerra team_registrations.
    TODO: Implementar quando TeamRegistration existir
    """
    
    @pytest.mark.skip(reason="Aguardando TeamRegistration model")
    def test_R13_dispensada_closes_registrations(self, db, athlete, team_registration):
        """Ao dispensar, encerra team_registrations vigentes."""
        pass
