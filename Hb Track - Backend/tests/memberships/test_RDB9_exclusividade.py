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
    
    @pytest.mark.asyncio
    async def test_RDB9_create_first_staff_ok(self, async_db, organization, user, person_id):
        """Primeiro vínculo staff é permitido."""
        service = MembershipService(async_db)
        
        membership = await service.create(
            organization_id=organization.id,
            person_id=person_id,
            role_id=ROLE_COACH,
        )
        
        assert membership.id is not None
    
    @pytest.mark.asyncio
    async def test_RDB9_duplicate_staff_fails(self, async_db, organization, user, membership_coach, person_id):
        """Segundo vínculo staff para mesma pessoa falha."""
        service = MembershipService(async_db)
        
        with pytest.raises(ValueError, match="conflict_membership_active"):
            await service.create(
                organization_id=organization.id,
                person_id=person_id,  # mesma pessoa
                role_id=ROLE_COORDINATOR,  # papel diferente, mas ainda staff
            )


class TestRDB9ExclusividadeAtleta:
    """RDB9: Atleta tem apenas 1 vínculo ativo por temporada."""
    
    @pytest.mark.skip(reason="Aguardando season_id no modelo Membership")
    @pytest.mark.asyncio
    async def test_RDB9_athlete_different_seasons_ok(
        self, async_db, organization, user, person_id, season_2024, season_2025
    ):
        """Atleta pode ter vínculo em temporadas diferentes."""
        service = MembershipService(async_db)
        
        m1 = await service.create(
            organization_id=organization.id,
            person_id=person_id,
            role_id=ROLE_ATHLETE,
            season_id=season_2024.id,
        )
        
        m2 = await service.create(
            organization_id=organization.id,
            person_id=person_id,
            role_id=ROLE_ATHLETE,
            season_id=season_2025.id,  # temporada diferente
        )
        
        assert m1.id != m2.id
    
    @pytest.mark.skip(reason="Aguardando season_id no modelo Membership")
    @pytest.mark.asyncio
    async def test_RDB9_athlete_same_season_fails(
        self, async_db, organization, user, person_id, season_2024, membership_athlete
    ):
        """Segundo vínculo atleta na mesma temporada falha."""
        service = MembershipService(async_db)
        
        with pytest.raises(ValueError, match="conflict_membership_active"):
            await service.create(
                organization_id=organization.id,
                person_id=person_id,
                role_id=ROLE_ATHLETE,
                season_id=season_2024.id,  # mesma temporada
            )
