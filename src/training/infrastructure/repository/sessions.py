"""Repositórios do agregado TrainingSession (raiz + SessionObjective)."""
from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from ...domain.entities import (
    SessionObjective,
    SessionObjectiveOrigin,
    TrainingSession,
    TrainingSessionStatus,
)
from ..models import SessionObjectiveModel, TrainingSessionModel


def _to_decimal(val) -> Optional[Decimal]:
    return Decimal(str(val)) if val is not None else None


class TrainingSessionRepository:
    def get_by_id(self, id: uuid.UUID) -> Optional[TrainingSession]:
        try:
            m = TrainingSessionModel.objects.get(pk=id, deleted_at__isnull=True)
            return self._to_domain(m)
        except TrainingSessionModel.DoesNotExist:
            return None

    def save(self, session: TrainingSession) -> TrainingSession:
        defaults = {
            "organization_id": session.organization_id,
            "team_id": session.team_id,
            "season_id": session.season_id,
            "microcycle_id": session.microcycle_id,
            "session_at": session.session_at,
            "duration_planned_minutes": session.duration_planned_minutes,
            "location": session.location or "",
            "session_type": session.session_type,
            "main_objective": session.main_objective or "",
            "secondary_objective": session.secondary_objective or "",
            "planned_load": session.planned_load,
            "intensity_target": session.intensity_target,
            "session_block": session.session_block or "",
            "notes": session.notes or "",
            "group_climate": session.group_climate,
            "standalone": session.standalone,
            "individualization_mode": session.individualization_mode or "",
            "focus_attack_positional_pct": session.focus_attack_positional_pct,
            "focus_defense_positional_pct": session.focus_defense_positional_pct,
            "focus_transition_offense_pct": session.focus_transition_offense_pct,
            "focus_transition_defense_pct": session.focus_transition_defense_pct,
            "focus_attack_technical_pct": session.focus_attack_technical_pct,
            "focus_defense_technical_pct": session.focus_defense_technical_pct,
            "focus_physical_pct": session.focus_physical_pct,
            "phase_focus_defense": session.phase_focus_defense,
            "phase_focus_attack": session.phase_focus_attack,
            "phase_focus_transition_offense": session.phase_focus_transition_offense,
            "phase_focus_transition_defense": session.phase_focus_transition_defense,
            "status": session.status.value,
            "created_by_user_id": session.created_by_user_id,
            "deleted_at": session.deleted_at,
            "deleted_reason": session.deleted_reason or "",
        }
        m, _ = TrainingSessionModel.objects.update_or_create(pk=session.id, defaults=defaults)
        return self._to_domain(m)

    def list(
        self,
        organization_id: Optional[uuid.UUID] = None,
        team_id: Optional[uuid.UUID] = None,
        season_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        page_size: int = 20,
        page_token: Optional[str] = None,
    ) -> list[TrainingSession]:
        qs = TrainingSessionModel.objects.filter(deleted_at__isnull=True).order_by("-session_at")
        if organization_id:
            qs = qs.filter(organization_id=organization_id)
        if team_id:
            qs = qs.filter(team_id=team_id)
        if season_id:
            qs = qs.filter(season_id=season_id)
        if status:
            qs = qs.filter(status=status)
        if page_token:
            try:
                qs = qs.filter(session_at__lt=page_token)
            except Exception:
                pass
        return [self._to_domain(m) for m in qs[:page_size]]

    def _to_domain(self, m: TrainingSessionModel) -> TrainingSession:
        return TrainingSession(
            id=m.id,
            organization_id=m.organization_id,
            team_id=m.team_id,
            season_id=m.season_id,
            microcycle_id=m.microcycle_id,
            session_at=m.session_at,
            duration_planned_minutes=m.duration_planned_minutes,
            location=m.location or None,
            session_type=m.session_type,
            main_objective=m.main_objective or None,
            secondary_objective=m.secondary_objective or None,
            planned_load=m.planned_load,
            intensity_target=m.intensity_target,
            session_block=m.session_block or None,
            notes=m.notes or None,
            group_climate=m.group_climate,
            standalone=m.standalone,
            individualization_mode=m.individualization_mode or None,
            focus_attack_positional_pct=_to_decimal(m.focus_attack_positional_pct),
            focus_defense_positional_pct=_to_decimal(m.focus_defense_positional_pct),
            focus_transition_offense_pct=_to_decimal(m.focus_transition_offense_pct),
            focus_transition_defense_pct=_to_decimal(m.focus_transition_defense_pct),
            focus_attack_technical_pct=_to_decimal(m.focus_attack_technical_pct),
            focus_defense_technical_pct=_to_decimal(m.focus_defense_technical_pct),
            focus_physical_pct=_to_decimal(m.focus_physical_pct),
            phase_focus_defense=m.phase_focus_defense,
            phase_focus_attack=m.phase_focus_attack,
            phase_focus_transition_offense=m.phase_focus_transition_offense,
            phase_focus_transition_defense=m.phase_focus_transition_defense,
            status=TrainingSessionStatus(m.status),
            created_by_user_id=m.created_by_user_id,
            created_at=m.created_at,
            updated_at=m.updated_at,
            deleted_at=m.deleted_at,
            deleted_reason=m.deleted_reason or None,
        )


class SessionObjectiveRepository:
    def list_by_session(self, session_id: uuid.UUID) -> list[SessionObjective]:
        return [
            self._to_domain(m)
            for m in SessionObjectiveModel.objects.filter(session_id=session_id).order_by("priority")
        ]

    def save(self, obj: SessionObjective) -> SessionObjective:
        defaults = {
            "session_id": obj.session_id,
            "origin": obj.origin.value,
            "objective_type": obj.objective_type,
            "description": obj.description,
            "origin_notes": obj.origin_notes or "",
            "priority": obj.priority,
        }
        m, _ = SessionObjectiveModel.objects.update_or_create(pk=obj.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: SessionObjectiveModel) -> SessionObjective:
        return SessionObjective(
            id=m.id,
            session_id=m.session_id,
            origin=SessionObjectiveOrigin(m.origin),
            objective_type=m.objective_type,
            description=m.description,
            origin_notes=m.origin_notes or None,
            priority=m.priority,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


__all__ = ["TrainingSessionRepository", "SessionObjectiveRepository"]
