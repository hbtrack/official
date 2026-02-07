"""
Service Membership - Lógica de negócio para vínculos organizacionais (V1.2).

Regras V1.2:
- R5: Papéis não acumuláveis
- R6-R8: Vínculos organizacionais
- RDB9: Exclusividade de vínculo ativo
- RF1.1: Dirigente NÃO cria membership automático
- org_memberships: staff apenas (person_id obrigatório, sem season_id)
- team_registrations: atletas (com season_id)
"""
from typing import Optional
from uuid import UUID
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.membership import OrgMembership


# Role IDs conforme seeds (d001c0ffee01)
ROLE_ATHLETE = 4
ROLE_COACH = 3
ROLE_COORDINATOR = 2
ROLE_DIRECTOR = 1
STAFF_ROLES = [ROLE_COACH, ROLE_COORDINATOR, ROLE_DIRECTOR]


class MembershipService:
    """
    Serviço para gerenciamento de vínculos organizacionais (V1.2).
    
    Regras críticas:
    - RDB9: Exclusividade de vínculo ativo
      - Staff (1-3): 1 vínculo ativo por pessoa em org_memberships
      - Atleta (4): usa team_registrations (não este serviço)
    - RF1.1: Dirigente NÃO cria org_membership automaticamente
      - Vincula-se apenas ao fundar ou solicitar ingresso em org
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_memberships(
        self,
        organization_id: UUID,
        *,
        person_id: Optional[UUID] = None,
        role_id: Optional[int] = None,
        active_only: bool = True,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[OrgMembership], int]:
        """Lista vínculos com filtros (V1.2: sem status, usa end_at)."""
        query = select(OrgMembership).where(
            OrgMembership.organization_id == str(organization_id),
            OrgMembership.deleted_at.is_(None),
        )
        
        if person_id:
            query = query.where(OrgMembership.person_id == str(person_id))
        
        if role_id:
            query = query.where(OrgMembership.role_id == role_id)
        
        if active_only:
            query = query.where(OrgMembership.end_at.is_(None))
        
        # Count total - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        total = await self.db.scalar(count_query) or 0
        
        query = query.offset((page - 1) * limit).limit(limit)
        query = query.order_by(OrgMembership.created_at.desc())
        
        result = await self.db.scalars(query)
        return list(result.all()), total
    
    async def get_by_id(self, membership_id: UUID) -> Optional[OrgMembership]:
        """Busca vínculo por ID."""
        return await self.db.scalar(
            select(OrgMembership).where(
                OrgMembership.id == str(membership_id),
                OrgMembership.deleted_at.is_(None),
            )
        )
    
    async def create(
        self,
        organization_id: UUID,
        person_id: UUID,
        role_id: int,
        *,
        start_at: Optional[date] = None,
    ) -> OrgMembership:
        """
        Cria vínculo organizacional (V1.2).
        
        IMPORTANTE (RF1.1):
        - Dirigente NÃO deve usar este método automaticamente
        - Coordenador/Treinador SIM usam este método
        
        Regras:
        - RDB9: Verifica exclusividade antes de criar
        - V1.2: Usa person_id (não user_id), sem season_id
        
        Raises:
            ValueError("conflict_membership_active"): RDB9 violada
            ValueError("athlete_use_team_registrations"): Atleta não usa esta tabela
        """
        # V1.2: Atleta usa team_registrations, não org_memberships
        if role_id == ROLE_ATHLETE:
            raise ValueError("athlete_use_team_registrations")

        # RDB9: Verificar exclusividade
        if await self._has_active_membership(person_id, role_id):
            raise ValueError("conflict_membership_active")

        membership = OrgMembership(
            organization_id=str(organization_id),
            person_id=str(person_id),
            role_id=role_id,
            start_at=start_at or date.today(),
        )
        self.db.add(membership)
        await self.db.flush()

        return membership
    
    async def end_membership(
        self,
        membership: OrgMembership,
        end_at: Optional[date] = None,
    ) -> OrgMembership:
        """
        Encerra vínculo (R9) - V1.2.
        
        Não altera histórico, apenas define end_at.
        """
        membership.end_at = end_at or date.today()
        await self.db.flush()
        return membership
    
    async def _has_active_membership(
        self,
        person_id: UUID,
        role_id: int,
    ) -> bool:
        """
        RDB9: Verifica exclusividade de vínculo ativo (V1.2).
        
        Staff (1-3): 1 vínculo ativo por pessoa em org_memberships
        (Atleta usa team_registrations, não este método)
        
        O DB tem trigger que também valida isso, mas
        verificamos no backend para dar erro mais amigável.
        """
        query = select(OrgMembership).where(
            OrgMembership.person_id == str(person_id),
            OrgMembership.end_at.is_(None),
            OrgMembership.deleted_at.is_(None),
        )
        
        # Staff: exclusividade geral (não pode ter outro vínculo staff ativo)
        query = query.where(OrgMembership.role_id.in_(STAFF_ROLES))
        
        return await self.db.scalar(query) is not None
    
    async def get_active_by_person(self, person_id: UUID) -> Optional[OrgMembership]:
        """Retorna vínculo ativo da pessoa (V1.2: usa person_id)."""
        return await self.db.scalar(
            select(OrgMembership).where(
                OrgMembership.person_id == str(person_id),
                OrgMembership.end_at.is_(None),
                OrgMembership.deleted_at.is_(None),
            )
        )
    
    # Alias para compatibilidade (deprecated)
    async def get_active_by_user(self, user_id: UUID) -> Optional[OrgMembership]:
        """
        DEPRECATED: Use get_active_by_person.
        V1.2 não tem user_id em org_memberships.
        """
        return None
