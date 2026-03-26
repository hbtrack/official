"""
Repository — módulo seasons.
Paginação page/pageSize (offset-based, conforme contrato OpenAPI seasons).
ADR-031: Django ORM.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from ..domain.entities import Season, SeasonStatus
from ..domain.rules import SeasonNotFound

if TYPE_CHECKING:
    pass


def _to_entity(obj: object) -> Season:
    """Converte SeasonModel → Season (domain entity)."""
    from .models import SeasonModel
    assert isinstance(obj, SeasonModel)
    return Season(
        id=obj.id,
        name=obj.name,
        start_date=obj.start_date,
        end_date=obj.end_date,
        status_label=SeasonStatus(obj.status_label),
        organization_id=obj.organization_id,
        sport_cycle_label=obj.sport_cycle_label or None,
        phase_labels=list(obj.phase_labels or []),
        team_ids=[UUID(t) for t in (obj.team_ids or [])],
        competition_ids=[UUID(c) for c in (obj.competition_ids or [])],
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class SeasonsRepository:
    """
    Repositório de temporadas.
    Paginação: page/pageSize offset-based (contrato GET /seasons).
    """

    def list_seasons(
        self,
        status_label: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Season], int]:
        from .models import SeasonModel

        qs = SeasonModel.objects.all()
        if status_label:
            qs = qs.filter(status_label=status_label)

        total = qs.count()
        offset = (page - 1) * page_size
        rows = qs[offset : offset + page_size]
        return [_to_entity(r) for r in rows], total

    def get_by_id(self, season_id: UUID) -> Season:
        from .models import SeasonModel

        try:
            obj = SeasonModel.objects.get(id=season_id)
        except SeasonModel.DoesNotExist:
            raise SeasonNotFound(f"Temporada {season_id} não encontrada.")
        return _to_entity(obj)

    def save(self, season: Season) -> Season:
        from .models import SeasonModel

        obj = SeasonModel(
            id=season.id,
            organization_id=season.organization_id,
            name=season.name,
            sport_cycle_label=season.sport_cycle_label,
            status_label=season.status_label.value,
            start_date=season.start_date,
            end_date=season.end_date,
            phase_labels=season.phase_labels,
            team_ids=[str(t) for t in season.team_ids],
            competition_ids=[str(c) for c in season.competition_ids],
        )
        obj.save()
        return _to_entity(obj)

    def update(self, season: Season) -> Season:
        from .models import SeasonModel

        try:
            obj = SeasonModel.objects.get(id=season.id)
        except SeasonModel.DoesNotExist:
            raise SeasonNotFound(f"Temporada {season.id} não encontrada.")

        obj.name = season.name
        obj.sport_cycle_label = season.sport_cycle_label
        obj.status_label = season.status_label.value
        obj.start_date = season.start_date
        obj.end_date = season.end_date
        obj.phase_labels = season.phase_labels
        obj.team_ids = [str(t) for t in season.team_ids]
        obj.competition_ids = [str(c) for c in season.competition_ids]
        obj.save()
        return _to_entity(obj)
