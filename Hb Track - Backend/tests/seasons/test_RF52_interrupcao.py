"""
Testes específicos da regra RF5.2 (temporada interrompida).
Ref: Matriz de enforcement - fluxo-backend-oficial.md

RF5.2: Temporada interrompida bloqueia criação/edição de eventos 
       a partir de interrupted_at.
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.services.season_service import SeasonService
from app.schemas.seasons import SeasonUpdate


class TestRF52TemporadaInterrompida:
    """
    RF5.2: Temporada interrompida bloqueia operações.
    
    Efeitos operacionais (6.1.1):
    - Bloqueia criação/edição de novos eventos a partir de interrupted_at
    - Cancela jogos futuros (TODO: Fase 5.3)
    - Vínculos continuam válidos no histórico
    - Dashboards não recebem novos dados dessa temporada
    """
    
    def test_RF52_interrupt_sets_timestamp(self, db, season_ativa):
        """Interrupção define interrupted_at."""
        service = SeasonService(db)
        before = datetime.now(timezone.utc)
        
        interrupted = service.interrupt(season_ativa, reason="Pandemia")
        
        assert interrupted.interrupted_at is not None
        assert interrupted.interrupted_at >= before
    
    def test_RF52_interrupt_changes_status(self, db, season_ativa):
        """Interrupção muda status para 'interrompida'."""
        service = SeasonService(db)
        
        interrupted = service.interrupt(season_ativa, reason="Pandemia")
        
        assert interrupted.status == "interrompida"
    
    def test_RF52_blocks_update_after_interrupt(self, db, season_ativa):
        """Edição bloqueada após interrupção."""
        service = SeasonService(db)
        service.interrupt(season_ativa, reason="Pandemia")
        
        with pytest.raises(ValueError, match="season_locked"):
            service.update(season_ativa, SeasonUpdate(name="Novo Nome"))
    
    def test_RF52_only_active_can_be_interrupted(self, db, season_planejada):
        """Apenas temporada ativa pode ser interrompida."""
        service = SeasonService(db)
        
        with pytest.raises(ValueError, match="invalid_state_transition"):
            service.interrupt(season_planejada, reason="Teste")
    
    def test_RF52_read_still_allowed(self, db, season_ativa):
        """Leitura permitida após interrupção."""
        service = SeasonService(db)
        service.interrupt(season_ativa, reason="Pandemia")
        
        # Leitura deve funcionar
        found = service.get_by_id(season_ativa.id)
        assert found is not None
        assert found.status == "interrompida"
    
    # TODO: Adicionar quando Team/Match services existirem
    # def test_RF52_blocks_new_match_creation(self):
    # def test_RF52_cancels_future_matches(self):
    # def test_RF52_blocks_training_edit(self):
