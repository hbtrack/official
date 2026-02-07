"""
Service para Competitions e CompetitionSeasons.

Regras implementadas:
- R25/R26: Permissões por papel e escopo
- R29: Exclusão lógica obrigatória (nota: tabela atual não tem deleted_at)
- R33: Regra de ouro
- R34: Clube único na V1
- RF4: Referência a temporadas
"""

import logging
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.context import ExecutionContext
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    ForbiddenError,
    ConflictError,
)
from app.models.competition import Competition
from app.models.competition_season import CompetitionSeason
from app.models.season import Season
from app.schemas.competitions import (
    CompetitionCreate,
    CompetitionUpdate,
    CompetitionSeasonCreate,
    CompetitionSeasonUpdate,
)

logger = logging.getLogger(__name__)


class CompetitionService:
    """
    Service de Competições.
    """

    def __init__(self, db: AsyncSession, context: ExecutionContext):
        self.db = db
        self.context = context

    # =========================================================================
    # COMPETITIONS
    # =========================================================================

    async def list_competitions(
        self,
        *,
        page: int = 1,
        limit: int = 50,
        order_by: str = "created_at",
        order_dir: str = "desc",
        name: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> Tuple[List[Competition], int]:
        """
        Lista competições da organização com filtros e paginação.
        """
        query = select(Competition)

        # Filtro por organização (R34: clube único)
        if not self.context.is_superadmin:
            query = query.where(Competition.organization_id == str(self.context.organization_id))

        # Filtros opcionais
        if name:
            query = query.where(Competition.name.ilike(f"%{name}%"))

        if kind:
            query = query.where(Competition.kind == kind)

        # Contagem total - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        result_count = await self.db.execute(count_query)
        total = result_count.scalar_one_or_none() or 0

        # Ordenação
        order_column = getattr(Competition, order_by, Competition.created_at)
        if order_dir == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Paginação
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        competitions = list(result.scalars().all())

        logger.info(
            f"Listed {len(competitions)} competitions for org {self.context.organization_id}"
        )
        return competitions, total

    async def get_competition_by_id(self, competition_id: UUID) -> Competition:
        """
        Busca competição por ID.
        """
        query = select(Competition).where(Competition.id == str(competition_id))

        if not self.context.is_superadmin:
            query = query.where(Competition.organization_id == str(self.context.organization_id))

        result = await self.db.execute(query)
        competition = result.scalar_one_or_none()

        if not competition:
            raise NotFoundError(f"Competition {competition_id} not found")

        return competition

    async def create_competition(self, data: CompetitionCreate) -> Competition:
        """
        Cria nova competição.
        
        A organization_id é obtida automaticamente do contexto (R34 - Clube único).
        """
        # Usar organization_id do contexto de autenticação
        org_id = str(self.context.organization_id)

        competition = Competition(
            organization_id=org_id,
            name=data.name,
            kind=data.kind,
        )

        self.db.add(competition)
        await self.db.flush()
        await self.db.refresh(competition)

        logger.info(
            f"Created competition {competition.id} for org {org_id} "
            f"by user {self.context.user_id}"
        )
        return competition

    async def update_competition(
        self,
        competition_id: UUID,
        data: CompetitionUpdate,
    ) -> Competition:
        """
        Atualiza competição existente.
        """
        competition = await self.get_competition_by_id(competition_id)

        # Atualizar campos
        if data.name is not None:
            competition.name = data.name
        if data.kind is not None:
            competition.kind = data.kind

        await self.db.flush()
        await self.db.refresh(competition)

        logger.info(
            f"Updated competition {competition_id} by user {self.context.user_id}"
        )
        return competition

    # =========================================================================
    # COMPETITION SEASONS
    # =========================================================================

    async def list_competition_seasons(
        self,
        competition_id: UUID,
        *,
        season_id: Optional[UUID] = None,
    ) -> List[CompetitionSeason]:
        """
        Lista temporadas vinculadas a uma competição.
        """
        # Verificar se competição existe e pertence à org
        await self.get_competition_by_id(competition_id)

        query = select(CompetitionSeason).where(
            CompetitionSeason.competition_id == str(competition_id)
        )

        if season_id:
            query = query.where(CompetitionSeason.season_id == str(season_id))

        query = query.order_by(CompetitionSeason.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_competition_season_by_id(
        self,
        competition_season_id: UUID,
    ) -> CompetitionSeason:
        """
        Busca vínculo competição-temporada por ID.
        """
        query = (
            select(CompetitionSeason)
            .join(Competition, Competition.id == CompetitionSeason.competition_id)
            .where(CompetitionSeason.id == str(competition_season_id))
        )

        if not self.context.is_superadmin:
            query = query.where(Competition.organization_id == str(self.context.organization_id))

        result = await self.db.execute(query)
        cs = result.scalar_one_or_none()

        if not cs:
            raise NotFoundError(f"CompetitionSeason {competition_season_id} not found")

        return cs

    async def create_competition_season(
        self,
        competition_id: UUID,
        data: CompetitionSeasonCreate,
    ) -> CompetitionSeason:
        """
        Cria vínculo entre competição e temporada.
        """
        # Verificar competição
        await self.get_competition_by_id(competition_id)

        # Verificar se temporada existe
        season_query = select(Season).where(Season.id == str(data.season_id))
        season_result = await self.db.execute(season_query)
        season = season_result.scalar_one_or_none()

        if not season:
            raise NotFoundError(f"Season {data.season_id} not found")

        # Criar vínculo
        cs = CompetitionSeason(
            competition_id=str(competition_id),
            season_id=str(data.season_id),
            name=data.name,
        )

        try:
            self.db.add(cs)
            await self.db.flush()
            await self.db.refresh(cs)
        except IntegrityError as e:
            self.db.rollback()
            if "uq_competition_seasons_competition_season" in str(e) or "unique" in str(e).lower():
                raise ConflictError(
                    f"CompetitionSeason already exists for competition {competition_id} "
                    f"and season {data.season_id}"
                )
            raise

        logger.info(
            f"Created competition_season {cs.id} "
            f"(comp={competition_id}, season={data.season_id}) "
            f"by user {self.context.user_id}"
        )
        return cs

    async def update_competition_season(
        self,
        competition_season_id: UUID,
        data: CompetitionSeasonUpdate,
    ) -> CompetitionSeason:
        """
        Atualiza vínculo competição-temporada.
        """
        cs = await self.get_competition_season_by_id(competition_season_id)

        if data.name is not None:
            cs.name = data.name

        await self.db.flush()
        await self.db.refresh(cs)

        logger.info(
            f"Updated competition_season {competition_season_id} "
            f"by user {self.context.user_id}"
        )
        return cs

    async def list_all_competition_seasons(
        self,
        *,
        page: int = 1,
        limit: int = 50,
        competition_id: Optional[UUID] = None,
        season_id: Optional[UUID] = None,
    ) -> Tuple[List[CompetitionSeason], int]:
        """
        Lista todos os vínculos competição-temporada (admin).
        """
        query = (
            select(CompetitionSeason)
            .join(Competition, Competition.id == CompetitionSeason.competition_id)
        )

        if not self.context.is_superadmin:
            query = query.where(Competition.organization_id == str(self.context.organization_id))

        if competition_id:
            query = query.where(CompetitionSeason.competition_id == str(competition_id))

        if season_id:
            query = query.where(CompetitionSeason.season_id == str(season_id))

        # Contagem - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        result_count = await self.db.execute(count_query)
        total = result_count.scalar_one_or_none() or 0

        # Paginação
        query = query.order_by(CompetitionSeason.created_at.desc())
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total
