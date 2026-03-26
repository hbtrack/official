"""
Repositório — módulo competitions.
Fonte: infrastructure/models.py, domain/entities.py
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from competitions.domain.entities import Competition, CompetitionStatus


class CompetitionRepository:
    """
    Repositório de Competition com persistência via ORM Django.
    Importação lazy para evitar falha em testes sem DB.
    """

    def _model(self):
        from competitions.infrastructure.models import CompetitionModel
        return CompetitionModel

    def _to_domain(self, obj) -> Competition:
        return Competition(
            id=obj.id,
            season_id=obj.season_id,
            organization_id=obj.organization_id,
            name=obj.name,
            start_date=obj.start_date,
            end_date=obj.end_date,
            format_label=obj.format_label,
            status_label=CompetitionStatus(obj.status_label),
            stage_labels=list(obj.stage_labels or []),
            registration_team_ids=[uuid.UUID(str(t)) for t in (obj.registration_team_ids or [])],
            standings_summary=obj.standings_summary,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    def save(self, competition: Competition) -> Competition:
        M = self._model()
        obj, _ = M.objects.update_or_create(
            id=competition.id,
            defaults=dict(
                season_id=competition.season_id,
                organization_id=competition.organization_id,
                name=competition.name,
                start_date=competition.start_date,
                end_date=competition.end_date,
                format_label=competition.format_label,
                status_label=competition.status_label.value,
                stage_labels=competition.stage_labels,
                registration_team_ids=[str(t) for t in competition.registration_team_ids],
                standings_summary=competition.standings_summary,
            ),
        )
        return self._to_domain(obj)

    def get_by_id(self, competition_id: uuid.UUID) -> Optional[Competition]:
        M = self._model()
        try:
            obj = M.objects.get(id=competition_id)
            return self._to_domain(obj)
        except M.DoesNotExist:
            return None

    def list_competitions(
        self,
        *,
        season_id: Optional[uuid.UUID] = None,
        organization_id: Optional[uuid.UUID] = None,
        status_label: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Competition], int]:
        M = self._model()
        qs = M.objects.all()
        if season_id is not None:
            qs = qs.filter(season_id=season_id)
        if organization_id is not None:
            qs = qs.filter(organization_id=organization_id)
        if status_label is not None:
            qs = qs.filter(status_label=status_label)
        total = qs.count()
        offset = (page - 1) * page_size
        items = [self._to_domain(o) for o in qs[offset: offset + page_size]]
        return items, total
