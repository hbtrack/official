"""
Service para Partidas (Matches) alinhado ao schema real do banco.
"""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import ExecutionContext
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    ForbiddenError,
)
from app.models.match import Match, MatchStatus
from app.models.team import Team
from app.schemas.matches import MatchCreate, MatchUpdate, MatchStatusUpdate

logger = logging.getLogger(__name__)


class MatchService:
    """
    Service de Partidas.
    """

    def __init__(self, db: AsyncSession, context: ExecutionContext):
        self.db = db
        self.context = context

    async def get_all(
        self,
        *,
        team_id: Optional[UUID] = None,
        season_id: Optional[UUID] = None,
        status: Optional[MatchStatus] = None,
        include_deleted: bool = False,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Match], int]:
        """
        Lista partidas com filtros.
        """
        query = select(Match).join(Team, Team.id == Match.team_id)

        if not self.context.is_superadmin:
            query = query.where(Team.organization_id == self.context.organization_id)

        if not include_deleted:
            query = query.where(Match.deleted_at.is_(None))

        if team_id:
            query = query.where(Match.team_id == team_id)

        if season_id:
            query = query.where(Match.season_id == season_id)

        if status:
            query = query.where(Match.status == status)

        # Count total - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        result_count = await self.db.execute(count_query)
        total = result_count.scalar_one_or_none() or 0

        # Paginate
        query = query.order_by(Match.match_date.desc())
        query = query.offset((page - 1) * size).limit(size)

        result = await self.db.execute(query)
        matches = list(result.scalars().all())

        logger.info(
            f"Listed {len(matches)} matches for org {self.context.organization_id}"
        )
        return matches, total

    async def get_by_id(
        self,
        match_id: UUID,
        *,
        include_deleted: bool = False,
        with_events: bool = False,
    ) -> Match:
        """
        Busca partida por ID.
        """
        query = select(Match).join(Team, Team.id == Match.team_id).where(
            Match.id == match_id,
        )

        if not self.context.is_superadmin:
            query = query.where(Team.organization_id == self.context.organization_id)

        if not include_deleted:
            query = query.where(Match.deleted_at.is_(None))

        if with_events:
            query = query.options(selectinload(Match.events))

        result = await self.db.execute(query)
        match = result.scalar_one_or_none()

        if not match:
            raise NotFoundError(f"Match {match_id} not found")

        return match

    async def create(self, data: MatchCreate) -> Match:
        """
        Cria nova partida.
        """
        team_result = await self.db.execute(select(Team).where(Team.id == data.team_id))
        team = team_result.scalar_one_or_none()

        if not team:
            raise NotFoundError(f"Team {data.team_id} not found")

        if not self.context.is_superadmin and team.organization_id != self.context.organization_id:
            raise ForbiddenError("Team belongs to another organization")

        match = Match(
            season_id=team.season_id,
            team_id=team.id,
            home_team_id=team.id,
            away_team_id=team.id,
            match_date=data.match_date,
            opponent_name=data.opponent_name,
            match_type=data.match_type,
            location=data.location,
            status=MatchStatus.scheduled,
        )

        self.db.add(match)
        await self.db.flush()
        await self.db.refresh(match)

        logger.info(
            f"Created match {match.id} for team {team.id} "
            f"by user {self.context.user_id}"
        )
        return match

    async def update(self, match_id: UUID, data: MatchUpdate) -> Match:
        """
        Atualiza partida (campos livres, respeitando finalizaÇõÇœo).
        """
        match = await self.get_by_id(match_id)

        if match.status == MatchStatus.finished and not self.context.is_superadmin:
            raise ForbiddenError(
                "Cannot edit finished match. Only SuperAdmin can reopen."
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(match, field, value)

        await self.db.flush()
        await self.db.refresh(match)

        logger.info(
            f"Updated match {match_id} by user {self.context.user_id}"
        )
        return match

    async def update_status(
        self,
        match_id: UUID,
        data: MatchStatusUpdate,
    ) -> Match:
        """
        Atualiza status da partida (schema real: scheduled/in_progress/finished/cancelled)
        """
        match = await self.get_by_id(match_id)
        old_status = match.status
        new_status = data.status

        self._validate_status_transition(match, new_status)

        match.status = new_status

        await self.db.flush()
        await self.db.refresh(match)

        logger.info(
            f"Match {match_id} status changed: {old_status} -> {new_status} "
            f"by user {self.context.user_id}"
        )
        return match

    async def soft_delete(
        self,
        match_id: UUID,
        reason: str,
    ) -> Match:
        """
        Soft delete de partida.
        """
        match = await self.get_by_id(match_id)

        if match.status == MatchStatus.finished and not self.context.is_superadmin:
            raise ForbiddenError("Cannot delete finished match")

        match.deleted_at = datetime.utcnow()
        match.deleted_reason = reason

        await self.db.flush()
        await self.db.refresh(match)

        logger.info(
            f"Soft deleted match {match_id} by user {self.context.user_id}: {reason}"
        )
        return match

    async def restore(self, match_id: UUID) -> Match:
        """
        Restaura partida deletada.
        """
        match = await self.get_by_id(match_id, include_deleted=True)

        if match.deleted_at is None:
            raise ValidationError("Match is not deleted")

        match.deleted_at = None
        match.deleted_reason = None

        await self.db.flush()
        await self.db.refresh(match)

        logger.info(
            f"Restored match {match_id} by user {self.context.user_id}"
        )
        return match

    async def get_by_team_and_date(
        self,
        team_id: UUID,
        match_date,
    ) -> Optional[Match]:
        """
        Busca partida por time e data (para evitar duplicatas).
        """
        query = select(Match).where(
            Match.team_id == team_id,
            Match.match_date == match_date,
            Match.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    def _validate_status_transition(
        self,
        match: Match,
        new_status: MatchStatus,
    ) -> None:
        old_status = match.status

        if old_status == new_status:
            return

        if old_status in [MatchStatus.finished, MatchStatus.cancelled]:
            if not self.context.is_superadmin:
                raise ForbiddenError("Only superadmin can change a finished/cancelled match")
            return

        if old_status == MatchStatus.scheduled:
            if new_status not in [MatchStatus.in_progress, MatchStatus.finished, MatchStatus.cancelled]:
                raise ValidationError(f"Invalid transition: {old_status} -> {new_status}")
            return

        if old_status == MatchStatus.in_progress:
            if new_status not in [MatchStatus.finished, MatchStatus.cancelled]:
                raise ValidationError(f"Invalid transition: {old_status} -> {new_status}")
            return

        raise ValidationError(f"Invalid transition: {old_status} -> {new_status}")
