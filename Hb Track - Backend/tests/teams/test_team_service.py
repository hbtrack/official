"""Testes do TeamService."""
import pytest
from app.services.team_service import TeamService


class TestTeamServiceCreate:
    """Testes de criação - RF6."""
    
    def test_create_team_RF6(self, db, organization, season_ativa):
        """RF6: Criar equipe vinculada à temporada."""
        service = TeamService(db)
        
        team = service.create(
            name="Sub-17",
            organization_id=organization.id,
            season_id=season_ativa.id,
        )
        
        assert team.id is not None
        assert team.season_id == season_ativa.id
    
    def test_create_team_blocked_when_season_interrupted_RF52(
        self, db, organization, season_interrompida
    ):
        """RF5.2: Não criar equipe em temporada interrompida."""
        service = TeamService(db)
        
        with pytest.raises(ValueError, match="season_locked"):
            service.create(
                name="Sub-17",
                organization_id=organization.id,
                season_id=season_interrompida.id,
            )


class TestTeamServiceCoach:
    """Testes de associação treinador - RF7."""
    
    def test_assign_coach_RF7(self, db, team, membership):
        """RF7: Associar treinador à equipe."""
        service = TeamService(db)
        
        updated = service.assign_coach(team, membership.id)
        
        assert updated.coach_membership_id == membership.id


class TestTeamServiceSoftDelete:
    """Testes de soft delete - RF8/RDB4."""
    
    def test_soft_delete_RF8(self, db, team):
        """RF8/RDB4: Soft delete define deleted_at."""
        service = TeamService(db)
        
        deleted = service.soft_delete(team)
        
        assert deleted.deleted_at is not None
        assert deleted.is_active is False
