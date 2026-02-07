"""
Service Team - Lógica de negócio para equipes.

Regras:
- RF6: Criação de equipe vinculada à temporada
- RF7: Associação treinador-equipe (⚠️ pendente migration coach_membership_id)
- RF8: Soft delete de equipe (⚠️ pendente migration deleted_at)
- RDB4: deleted_at obrigatório (⚠️ pendente migration)
- R25/R26: Permissões por papel
- R34: Contexto organizacional obrigatório
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.models.season import Season
from app.models.organization import Organization
from app.models.team_membership import TeamMembership
from app.models.membership import OrgMembership


class TeamService:
    """
    Service para operações de Team.

    Fronteira de transação: chamador (route) controla commit/rollback.
    
    Regras implementadas:
    - RF6: Criação de equipe (dirigente/coordenador)
    - RF7: Troca de treinador responsável
    - RF8: Encerramento/soft delete de equipes
    - RDB4: Exclusão lógica obrigatória
    - R34: Escopo organizacional
    
    Constraints (DB):
    - UNIQUE(season_id, category_id, name)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ═══════════════════════════════════════════════════════════════════
    # Operações de Leitura
    # ═══════════════════════════════════════════════════════════════════

    async def list_teams(
        self,
        organization_id: UUID,
        *,
        person_id: Optional[UUID] = None,
        is_superadmin: bool = False,
        season_id: Optional[UUID] = None,
        page: int = 1,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> tuple[list[Team], int]:
        """
        Lista equipes da organização.
        
        Regras: 
        - R25/R26: RBAC por papel
        - R34: Escopo organizacional
        - RDB10: Usuário comum vê apenas equipes vinculadas via team_membership
        - R3: Superadmin bypassa filtros de vínculo
        
        Args:
            organization_id: UUID da organização (R34)
            person_id: UUID da pessoa para filtrar equipes vinculadas (None = superadmin)
            is_superadmin: Se True, retorna todas as equipes da org (bypass)
            season_id: Filtrar por temporada (opcional)
            page: Página atual (≥1)
            limit: Itens por página (1-100)
            include_deleted: Incluir soft-deleted (default False)
            
        Returns:
            Tupla (lista de teams, total de registros)
        """
        query = select(Team).where(Team.organization_id == organization_id)
        
        # REGRA: Superadmin vê todas, usuário comum apenas equipes vinculadas
        if not is_superadmin and person_id is not None:
            # JOIN com team_memberships para filtrar equipes onde person_id está vinculado
            query = query.join(
                TeamMembership,
                (TeamMembership.team_id == Team.id) & (TeamMembership.person_id == person_id)
            ).where(
                TeamMembership.status.in_(['ativo', 'pendente'])
            )
        
        if season_id:
            query = query.where(Team.season_id == season_id)
        
        # Filtro soft delete (RDB4)
        # Por padrão, incluir equipes arquivadas (mostrar com badge cinza no frontend)
        if not include_deleted:
            query = query.where(Team.deleted_at.is_(None))

        # Count total - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        total = await self.db.scalar(count_query) or 0

        # Ordenação e paginação
        query = query.offset((page - 1) * limit).limit(limit)
        query = query.order_by(Team.created_at.desc())

        results = (await self.db.scalars(query)).all()
        
        # Adicionar organization_name a cada team
        teams_list = []
        for team in results:
            org = await self.db.get(Organization, team.organization_id)
            team.organization_name = org.name if org else None
            teams_list.append(team)
        
        return teams_list, total

    async def get_by_id(self, team_id: UUID) -> Optional[Team]:
        """Busca equipe por ID."""
        team = await self.db.get(Team, team_id)
        if team:
            org = await self.db.get(Organization, team.organization_id)
            team.organization_name = org.name if org else None
        return team

    async def get_by_season_category_name(
        self,
        season_id: UUID,
        category_id: int,
        name: str,
    ) -> Optional[Team]:
        """
        Busca equipe por constraint única (season_id, category_id, name).
        
        Útil para verificar duplicidade antes de criar.
        
        Args:
            season_id: UUID da temporada
            category_id: ID da categoria
            name: Nome da equipe
            
        Returns:
            Team ou None se não encontrada
        """
        query = select(Team).where(
            Team.season_id == season_id,
            Team.category_id == category_id,
            Team.name == name,
        )
        return await self.db.scalar(query)

    # ═══════════════════════════════════════════════════════════════════
    # Operações de Escrita
    # ═══════════════════════════════════════════════════════════════════

    async def create(
        self,
        name: str,
        organization_id: UUID,
        category_id: int,
        gender: str,
        is_our_team: bool = True,
        season_id: Optional[UUID] = None,
        coach_membership_id: Optional[UUID] = None,
        created_by_user_id: Optional[UUID] = None,
        creator_person_id: Optional[UUID] = None,
        creator_org_membership_id: Optional[UUID] = None,
    ) -> Team:
        """
        Cria nova equipe.

        Regras:
        - RF6: Equipe pertence a uma organização
        - RF7: Coach opcional na criação
        - Auto-adiciona criador como membro do team (owner)

        Args:
            name: Nome da equipe
            organization_id: UUID da organização (R34)
            category_id: ID da categoria
            gender: 'masculino' ou 'feminino'
            is_our_team: Se é nossa equipe ou adversário
            season_id: UUID da temporada (opcional)
            coach_membership_id: UUID do treinador (RF7, opcional)
            created_by_user_id: UUID do usuário que está criando (auditoria/owner)
            creator_person_id: UUID da pessoa que está criando (para team_membership)
            creator_org_membership_id: UUID do org_membership do criador (para team_membership e auditoria)

        Returns:
            Team criada (com criador já adicionado como membro)
        """
        # Validar duplicação: mesma org, categoria, gênero e nome
        existing = (await self.db.execute(
            select(Team).where(
                Team.organization_id == organization_id,
                Team.category_id == category_id,
                Team.gender == gender,
                Team.name == name,
                Team.deleted_at.is_(None)  # Apenas equipes ativas
            )
        )).scalar_one_or_none()
        
        if existing:
            raise ValueError(f"Já existe uma equipe {name} na categoria {category_id} com gênero {gender}")
        
        # Preparar dados do team
        team_data = {
            "name": name,
            "organization_id": organization_id,
            "category_id": category_id,
            "gender": gender,
            "is_our_team": is_our_team,
        }
        
        if created_by_user_id is not None:
            team_data["created_by_user_id"] = created_by_user_id
        
        # Vincular a temporada (opcional)
        if season_id is not None:
            team_data["season_id"] = season_id
        
        # RF7: Atribuição de treinador principal
        if coach_membership_id is not None:
            team_data["coach_membership_id"] = coach_membership_id
        
        # Auditoria: membership do criador
        if creator_org_membership_id is not None:
            team_data["created_by_membership_id"] = creator_org_membership_id
        
        team = Team(**team_data)
        self.db.add(team)
        await self.db.flush()

        # Auto-adicionar criador como membro do team (owner)
        # Isso garante que o criador possa criar training sessions, gerenciar membros, etc.
        if creator_person_id and creator_org_membership_id:
            team_membership = TeamMembership(
                team_id=team.id,
                person_id=creator_person_id,
                org_membership_id=creator_org_membership_id,
                status="ativo",
                start_at=datetime.now(timezone.utc),
                resend_count=0,
            )
            self.db.add(team_membership)
            await self.db.flush()
        
        # Step 5: Criar TeamMembership para coach (se diferente do criador)
        if coach_membership_id and coach_membership_id != creator_org_membership_id:
            coach = await self.db.get(OrgMembership, coach_membership_id)
            if coach:
                coach_team_membership = TeamMembership(
                    team_id=team.id,
                    person_id=coach.person_id,
                    org_membership_id=coach_membership_id,
                    status="ativo",
                    start_at=datetime.now(timezone.utc),
                    resend_count=0,
                )
                self.db.add(coach_team_membership)
                await self.db.flush()
        
        # Step 6: Validação de integridade - verificar se coach tem TeamMembership
        if coach_membership_id:
            team_membership_exists = (await self.db.execute(
                select(TeamMembership).filter(
                    TeamMembership.team_id == team.id,
                    TeamMembership.org_membership_id == coach_membership_id,
                    TeamMembership.status == "ativo",
                    TeamMembership.end_at.is_(None)
                )
            )).scalar_one_or_none()
            
            if not team_membership_exists:
                raise ValueError("COACH_MEMBERSHIP_INTEGRITY_ERROR")

        return team

    async def update(self, team: Team, **kwargs) -> Team:
        """
        Atualiza equipe.
        
        Regras:
        - RF7: Pode alterar coach_membership_id
        """
        for field, value in kwargs.items():
            if hasattr(team, field) and value is not None:
                setattr(team, field, value)
        
        await self.db.flush()
        return team

    async def update_settings(self, team: Team, alert_threshold_multiplier: float) -> Team:
        """
        Atualiza configurações da equipe (Step 15).
        
        Args:
            team: Instância do Team a atualizar
            alert_threshold_multiplier: Multiplicador de threshold (1.0-3.0)
            
        Returns:
            Team atualizado
        """
        team.alert_threshold_multiplier = alert_threshold_multiplier
        team.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return team

    # ═══════════════════════════════════════════════════════════════════
    # RF7: Associação Treinador-Equipe
    # ═══════════════════════════════════════════════════════════════════

    async def assign_coach(self, team: Team, coach_membership_id: UUID) -> Team:
        """
        Associa treinador à equipe (RF7).
        
        Regras:
        - RF7: Treinador deve ter membership ativo
        - Validação de papel COACH pode ser adicionada no futuro
        """
        team.coach_membership_id = coach_membership_id
        await self.db.flush()
        return team

    # ═══════════════════════════════════════════════════════════════════
    # RF8/RDB4: Soft Delete
    # ═══════════════════════════════════════════════════════════════════

    async def soft_delete(self, team: Team, *, reason: Optional[str] = None) -> Team:
        """
        Soft delete (RF8/RDB4).
        
        Regras:
        - R29: Sem delete físico
        - RDB4: deleted_at obrigatório
        """
        team.deleted_at = datetime.now(timezone.utc)
        team.deleted_reason = reason
        await self.db.flush()
        return team

    # ═══════════════════════════════════════════════════════════════════
    # Métodos Auxiliares
    # ═══════════════════════════════════════════════════════════════════

    async def _check_season_locked(self, season_id: UUID) -> None:
        """Verifica se temporada está bloqueada (RF5.2)."""
        season = await self.db.get(Season, season_id)
        if season and season.interrupted_at:
            raise ValueError("season_locked")

    async def restore(self, team: Team) -> Team:
        """
        Restaura equipe soft-deleted.
        
        Uso administrativo com auditoria.
        """
        team.deleted_at = None
        team.deleted_reason = None
        await self.db.flush()
        return team

    async def count_by_season(self, season_id: UUID) -> int:
        """
        Conta equipes em uma temporada.
        
        Útil para validações (ex: RF5.1 - temporada tem dados vinculados).
        """
        query = select(func.count()).select_from(Team).where(
            Team.season_id == season_id
        )
        return await self.db.scalar(query) or 0

    async def exists_in_organization(self, team_id: UUID, organization_id: UUID) -> bool:
        """
        Verifica se equipe pertence à organização.
        
        Útil para validação de permissões (R25/R26).
        """
        query = select(func.count()).select_from(Team).where(
            Team.id == team_id,
            Team.organization_id == organization_id,
        )
        return (await self.db.scalar(query) or 0) > 0
