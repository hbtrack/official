"""
Repository — módulo teams.
Paginação page/pageSize (offset-based, conforme contrato OpenAPI teams).
ADR-031: Django ORM.
"""
from __future__ import annotations

from uuid import UUID

from ..domain.entities import Team, TeamStatus
from ..domain.rules import TeamNotFound


def _to_entity(obj) -> Team:
    """Converte TeamModel → Team (domain entity)."""
    from .models import TeamModel
    assert isinstance(obj, TeamModel)
    return Team(
        id=obj.id,
        organization_id=obj.organization_id,
        name=obj.name,
        category_label=obj.category_label,
        status_label=TeamStatus(obj.status_label),
        season_id=obj.season_id,
        short_name=obj.short_name or None,
        athlete_ids=[UUID(a) for a in (obj.athlete_ids or [])],
        staff_user_ids=[UUID(s) for s in (obj.staff_user_ids or [])],
        roster_notes=obj.roster_notes or None,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class TeamsRepository:
    """Repositório de equipes. Paginação page/pageSize offset-based."""

    def list_teams(
        self,
        organization_id: UUID | None = None,
        season_id: UUID | None = None,
        category_label: str | None = None,
        status_label: str | None = None,
        team_ids_filter: list[UUID] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Team], int]:
        from .models import TeamModel

        qs = TeamModel.objects.all()
        if organization_id:
            qs = qs.filter(organization_id=organization_id)
        if season_id:
            qs = qs.filter(season_id=season_id)
        if category_label:
            qs = qs.filter(category_label=category_label)
        if status_label:
            qs = qs.filter(status_label=status_label)
        if team_ids_filter is not None:
            qs = qs.filter(id__in=[str(t) for t in team_ids_filter])

        total = qs.count()
        offset = (page - 1) * page_size
        rows = qs[offset : offset + page_size]
        return [_to_entity(r) for r in rows], total

    def get_by_id(self, team_id: UUID) -> Team:
        from .models import TeamModel

        try:
            obj = TeamModel.objects.get(id=team_id)
        except TeamModel.DoesNotExist:
            raise TeamNotFound(f"Equipe {team_id} não encontrada.")
        return _to_entity(obj)

    def save(self, team: Team) -> Team:
        from .models import TeamModel

        obj = TeamModel(
            id=team.id,
            organization_id=team.organization_id,
            season_id=team.season_id,
            name=team.name,
            short_name=team.short_name,
            category_label=team.category_label,
            status_label=team.status_label.value,
            athlete_ids=[str(a) for a in team.athlete_ids],
            staff_user_ids=[str(s) for s in team.staff_user_ids],
            roster_notes=team.roster_notes,
        )
        obj.save()
        return _to_entity(obj)

    def update(self, team: Team) -> Team:
        from .models import TeamModel

        try:
            obj = TeamModel.objects.get(id=team.id)
        except TeamModel.DoesNotExist:
            raise TeamNotFound(f"Equipe {team.id} não encontrada.")

        obj.name = team.name
        obj.short_name = team.short_name
        obj.category_label = team.category_label
        obj.status_label = team.status_label.value
        obj.season_id = team.season_id
        obj.athlete_ids = [str(a) for a in team.athlete_ids]
        obj.staff_user_ids = [str(s) for s in team.staff_user_ids]
        obj.roster_notes = team.roster_notes
        obj.save()
        return _to_entity(obj)
