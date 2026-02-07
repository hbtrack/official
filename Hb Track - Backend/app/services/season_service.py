"""
Service Season - Lógica de negócio para temporadas.
Regras: RF4, RF5, RF5.1, RF5.2, R37
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.season import Season
from app.models.team import Team
from app.schemas.seasons import SeasonCreate, SeasonUpdate


class SeasonService:
    """
    Service para operações de Season.

    Fronteira de transação: chamador (route) controla commit/rollback.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_seasons(
        self,
        organization_id: UUID,
        *,
        page: int = 1,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> tuple[list[Season], int]:
        """
        Lista temporadas com paginação.
        Regras: R25/R26 (filtro por organização implícito)
        """
        org_id = UUID(str(organization_id))

        query = (
            select(Season)
            .join(Team, Season.team_id == Team.id)
            .where(Team.organization_id == org_id)
        )

        if not include_deleted:
            query = query.where(Season.deleted_at.is_(None))

        # Count total - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        total = await self.db.scalar(count_query) or 0

        query = query.order_by(Season.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        results = await self.db.scalars(query)
        return list(results.all()), total

    async def get_by_id(self, season_id: UUID) -> Optional[Season]:
        """Busca temporada por ID."""
        return await self.db.get(Season, str(season_id))

    async def create(
        self,
        data: SeasonCreate,
        organization_id: UUID,
        membership_id: Optional[UUID] = None,
        created_by_user_id: Optional[UUID] = None,
    ) -> Season:
        """
        Cria nova temporada.

        Regras:
        - RF4: temporada criada no status "planejada"
        - RDB8: start_date < end_date (validado pelo DB)
        """
        team = await self.db.get(Team, data.team_id)
        if not team:
            raise ValueError("team_not_found")
        if str(team.organization_id) != str(organization_id):
            raise ValueError("team_out_of_org")

        season = Season(
            team_id=str(data.team_id),
            created_by_user_id=str(created_by_user_id) if created_by_user_id else None,
            year=data.year,
            name=data.name,
            competition_type=data.competition_type,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        self.db.add(season)
        await self.db.flush()  # Gera ID sem commit (transação do chamador)
        return season

    async def update(self, season: Season, data: SeasonUpdate) -> Season:
        """
        Atualiza temporada.

        Regras:
        - RF5: edição permitida
        - RF5.2: NÃO editar se interrompida
        - R37: edição pós-encerramento exigiria auditoria (não implementado ainda)

        Raises:
            ValueError("season_locked"): se temporada interrompida
        """
        if season.interrupted_at is not None:
            raise ValueError("season_locked")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "start_date":
                season.start_date = value
            elif field == "end_date":
                season.end_date = value
            else:
                setattr(season, field, value)

        await self.db.flush()
        return season

    async def interrupt(self, season: Season, reason: str) -> Season:
        """
        Interrompe temporada ativa (RF5.2).

        Regras:
        - RF5.2: só temporada "ativa" pode ser interrompida
        - 6.1.1: transição ativa -> interrompida

        Raises:
            ValueError("invalid_state_transition"): se não estiver ativa
        """
        from datetime import datetime, timezone

        if season.status != "ativa":
            raise ValueError("invalid_state_transition")

        season.interrupted_at = datetime.now(timezone.utc)
        # TODO (Fase 6): Registrar audit_log
        # TODO (Fase 5.3): Cancelar jogos futuros

        await self.db.flush()
        return season

    async def cancel(self, season: Season, reason: str) -> Season:
        """
        Cancela temporada planejada (RF5.1).

        Regras:
        - RF5.1: só temporada "planejada" sem dados vinculados
        - 6.1.1: transição planejada -> cancelada

        Raises:
            ValueError("invalid_state_transition"): se não estiver planejada
            ValueError("season_has_linked_data"): se houver dados vinculados
        """
        from datetime import datetime, timezone

        if season.status != "planejada":
            raise ValueError("invalid_state_transition")

        if self._has_linked_data(season.id):
            raise ValueError("season_has_linked_data")

        season.canceled_at = datetime.now(timezone.utc)
        await self.db.flush()
        return season

    def _has_linked_data(self, season_id: UUID) -> bool:
        """
        Verifica se temporada tem dados vinculados.
        TODO: Implementar verificação real quando Team model existir.
        """
        # Por enquanto, retorna False (será implementado com Teams)
        return False
