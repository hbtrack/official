"""Repositórios de periodização: Mesocycle + Microcycle."""
from __future__ import annotations

import uuid
from typing import Optional

from ...domain.entities import Mesocycle, Microcycle
from ..models import MesocycleModel, MicrocycleModel


class MesocycleRepository:
    def list(self, organization_id: Optional[uuid.UUID] = None) -> list[Mesocycle]:
        qs = MesocycleModel.objects.order_by("-started_at")
        if organization_id:
            qs = qs.filter(organization_id=organization_id)
        return [self._to_domain(m) for m in qs]

    def get_by_id(self, id: uuid.UUID) -> Optional[Mesocycle]:
        try:
            return self._to_domain(MesocycleModel.objects.get(pk=id))
        except MesocycleModel.DoesNotExist:
            return None

    def save(self, meso: Mesocycle) -> Mesocycle:
        defaults = {
            "organization_id": meso.organization_id,
            "season_id": meso.season_id,
            "team_id": meso.team_id,
            "name": meso.name,
            "started_at": meso.started_at,
            "ended_at": meso.ended_at,
            "objective": meso.objective or "",
            "notes": meso.notes or "",
        }
        m, _ = MesocycleModel.objects.update_or_create(pk=meso.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: MesocycleModel) -> Mesocycle:
        return Mesocycle(
            id=m.id,
            organization_id=m.organization_id,
            season_id=m.season_id,
            team_id=m.team_id,
            name=m.name,
            started_at=m.started_at,
            ended_at=m.ended_at,
            objective=m.objective or None,
            notes=m.notes or None,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class MicrocycleRepository:
    def list(
        self,
        organization_id: Optional[uuid.UUID] = None,
        mesocycle_id: Optional[uuid.UUID] = None,
    ) -> list[Microcycle]:
        qs = MicrocycleModel.objects.order_by("week_number")
        if organization_id:
            qs = qs.filter(organization_id=organization_id)
        if mesocycle_id:
            qs = qs.filter(mesocycle_id=mesocycle_id)
        return [self._to_domain(m) for m in qs]

    def get_by_id(self, id: uuid.UUID) -> Optional[Microcycle]:
        try:
            return self._to_domain(MicrocycleModel.objects.get(pk=id))
        except MicrocycleModel.DoesNotExist:
            return None

    def save(self, micro: Microcycle) -> Microcycle:
        defaults = {
            "organization_id": micro.organization_id,
            "mesocycle_id": micro.mesocycle_id,
            "team_id": micro.team_id,
            "week_number": micro.week_number,
            "name": micro.name or "",
            "started_at": micro.started_at,
            "ended_at": micro.ended_at,
            "objective": micro.objective or "",
            "planned_sessions_count": micro.planned_sessions_count,
            "notes": micro.notes or "",
        }
        m, _ = MicrocycleModel.objects.update_or_create(pk=micro.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: MicrocycleModel) -> Microcycle:
        return Microcycle(
            id=m.id,
            organization_id=m.organization_id,
            mesocycle_id=m.mesocycle_id,
            team_id=m.team_id,
            week_number=m.week_number,
            name=m.name or None,
            started_at=m.started_at,
            ended_at=m.ended_at,
            objective=m.objective or None,
            planned_sessions_count=m.planned_sessions_count,
            notes=m.notes or None,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


__all__ = ["MesocycleRepository", "MicrocycleRepository"]
