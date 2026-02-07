"""
Testes do Model Season.
"""
import pytest
from datetime import date, timedelta
from uuid import uuid4

from app.models.season import Season


class TestSeasonModel:
    """Testes do modelo Season."""
    
    def test_create_season_with_valid_dates(self, db, organization_id, membership_id):
        """Criar season com datas válidas."""
        season = Season(
            organization_id=organization_id,
            created_by_membership_id=membership_id,
            year=2025,
            name="Test Season",
            starts_at=date(2025, 1, 1),
            ends_at=date(2025, 12, 31),
        )
        db.add(season)
        db.flush()
        
        assert season.id is not None
        assert season.name == "Test Season"
        assert season.created_at is not None
    
    def test_status_planejada(self, db, organization_id, membership_id):
        """Status 'planejada' quando starts_at é futuro."""
        season = Season(
            organization_id=organization_id,
            created_by_membership_id=membership_id,
            year=2026,
            name="Future Season",
            starts_at=date.today() + timedelta(days=30),
            ends_at=date.today() + timedelta(days=365),
        )
        db.add(season)
        db.flush()
        
        assert season.status == "planejada"
    
    def test_status_ativa(self, db, organization_id, membership_id):
        """Status 'ativa' quando dentro do período."""
        season = Season(
            organization_id=organization_id,
            created_by_membership_id=membership_id,
            year=2024,
            name="Active Season",
            starts_at=date.today() - timedelta(days=30),
            ends_at=date.today() + timedelta(days=300),
        )
        db.add(season)
        db.flush()
        
        assert season.status == "ativa"
    
    def test_status_encerrada(self, db, organization_id, membership_id):
        """Status 'encerrada' quando ends_at passou."""
        season = Season(
            organization_id=organization_id,
            created_by_membership_id=membership_id,
            year=2023,
            name="Past Season",
            starts_at=date.today() - timedelta(days=365),
            ends_at=date.today() - timedelta(days=30),
        )
        db.add(season)
        db.flush()
        
        assert season.status == "encerrada"
    
    def test_status_interrompida(self, db, season_ativa):
        """Status 'interrompida' quando interrupted_at preenchido."""
        from datetime import datetime, timezone
        
        season_ativa.interrupted_at = datetime.now(timezone.utc)
        db.flush()
        
        assert season_ativa.status == "interrompida"
    
    def test_status_cancelada(self, db, season_planejada):
        """Status 'cancelada' quando canceled_at preenchido."""
        from datetime import datetime, timezone
        
        season_planejada.canceled_at = datetime.now(timezone.utc)
        db.flush()
        
        assert season_planejada.status == "cancelada"
