"""
Testes do SeasonService.
Regras testadas: RF4, RF5, RF5.1, RF5.2
"""
import pytest
from datetime import date, timedelta
from uuid import uuid4

from app.services.season_service import SeasonService
from app.schemas.seasons import SeasonCreate, SeasonUpdate


class TestSeasonServiceCreate:
    """Testes de criação - RF4."""
    
    def test_create_season_RF4(self, db, organization_id, membership_id):
        """RF4: Criar temporada com sucesso."""
        service = SeasonService(db)
        
        data = SeasonCreate(
            year=2025,
            name="Temporada 2025",
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=365),
        )
        
        season = service.create(data, organization_id=organization_id, membership_id=membership_id)
        
        assert season.id is not None
        assert season.name == "Temporada 2025"
        assert str(season.organization_id) == str(organization_id)
        assert season.status == "planejada"


class TestSeasonServiceUpdate:
    """Testes de atualização - RF5."""
    
    def test_update_season_RF5(self, db, season_planejada):
        """RF5: Atualizar temporada planejada."""
        service = SeasonService(db)
        
        data = SeasonUpdate(name="Nome Atualizado")
        updated = service.update(season_planejada, data)
        
        assert updated.name == "Nome Atualizado"
    
    def test_update_blocked_when_interrupted_RF52(self, db, season_ativa):
        """RF5.2: Não permite editar temporada interrompida."""
        from datetime import datetime, timezone
        
        service = SeasonService(db)
        season_ativa.interrupted_at = datetime.now(timezone.utc)
        db.flush()
        
        with pytest.raises(ValueError, match="season_locked"):
            service.update(season_ativa, SeasonUpdate(name="Novo Nome"))


class TestSeasonServiceInterrupt:
    """Testes de interrupção - RF5.2."""
    
    def test_interrupt_active_season_RF52(self, db, season_ativa):
        """RF5.2: Interromper temporada ativa."""
        service = SeasonService(db)
        
        interrupted = service.interrupt(season_ativa, reason="Pandemia")
        
        assert interrupted.interrupted_at is not None
        assert interrupted.status == "interrompida"
    
    def test_interrupt_planejada_fails_RF52(self, db, season_planejada):
        """RF5.2: Não interromper temporada planejada."""
        service = SeasonService(db)
        
        with pytest.raises(ValueError, match="invalid_state_transition"):
            service.interrupt(season_planejada, reason="Teste")


class TestSeasonServiceCancel:
    """Testes de cancelamento - RF5.1."""
    
    def test_cancel_planejada_without_data_RF51(self, db, season_planejada):
        """RF5.1: Cancelar temporada planejada sem dados."""
        service = SeasonService(db)
        
        canceled = service.cancel(season_planejada, reason="Cancelamento")
        
        assert canceled.canceled_at is not None
        assert canceled.status == "cancelada"
    
    def test_cancel_ativa_fails_RF51(self, db, season_ativa):
        """RF5.1: Não cancelar temporada ativa."""
        service = SeasonService(db)
        
        with pytest.raises(ValueError, match="invalid_state_transition"):
            service.cancel(season_ativa, reason="Teste")
