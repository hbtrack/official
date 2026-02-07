"""
Testes da regra RDB9 - Exclusividade de vínculo ativo.
Ref: Matriz de enforcement

RDB9: 
- Staff: 1 vínculo ativo por pessoa
- Atleta: 1 vínculo ativo por pessoa + temporada
"""
import pytest
from app.services.membership_service import (
    MembershipService,
    ROLE_ATHLETE,
    ROLE_COACH,
    ROLE_COORDINATOR,
)


class TestRDB9ExclusividadeStaff:
    """RDB9: Staff tem apenas 1 vínculo ativo."""
    
    def test_RDB9_create_first_staff_ok(self, db, organization, user):
        """Primeiro vínculo staff é permitido."""
        service = MembershipService(db)
        
        membership = service.create(
            organization_id=organization.id,
            user_id=user.id,
            role_id=ROLE_COACH,
        )
        
        assert membership.id is not None
    
    def test_RDB9_duplicate_staff_fails(self, db, organization, user, membership_coach):
        """Segundo vínculo staff para mesma pessoa falha."""
        service = MembershipService(db)
        
        with pytest.raises(ValueError, match="conflict_membership_active"):
            service.create(
                organization_id=organization.id,
                user_id=user.id,  # mesmo usuário
                role_id=ROLE_COORDINATOR,  # papel diferente, mas ainda staff
            )


class TestRDB9ExclusividadeAtleta:
    """RDB9: Atleta tem apenas 1 vínculo ativo por temporada."""
    
    @pytest.mark.skip(reason="Aguardando season_id no modelo Membership")
    def test_RDB9_athlete_different_seasons_ok(
        self, db, organization, user, season_2024, season_2025
    ):
        """Atleta pode ter vínculo em temporadas diferentes."""
        service = MembershipService(db)
        
        m1 = service.create(
            organization_id=organization.id,
            user_id=user.id,
            role_id=ROLE_ATHLETE,
            season_id=season_2024.id,
        )
        
        m2 = service.create(
            organization_id=organization.id,
            user_id=user.id,
            role_id=ROLE_ATHLETE,
            season_id=season_2025.id,  # temporada diferente
        )
        
        assert m1.id != m2.id
    
    @pytest.mark.skip(reason="Aguardando season_id no modelo Membership")
    def test_RDB9_athlete_same_season_fails(
        self, db, organization, user, season_2024, membership_athlete
    ):
        """Segundo vínculo atleta na mesma temporada falha."""
        service = MembershipService(db)
        
        with pytest.raises(ValueError, match="conflict_membership_active"):
            service.create(
                organization_id=organization.id,
                user_id=user.id,
                role_id=ROLE_ATHLETE,
                season_id=season_2024.id,  # mesma temporada
            )
