"""Repositórios do agregado TrainingSession (raiz + SessionObjective)."""
from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from ...domain.entities.sessions import SessionObjective, TrainingSession
from ...domain.common.enums import SessionObjectiveOrigin, TrainingSessionStatus
from ..models.sessions import SessionObjectiveModel, TrainingSessionModel


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
            # ── Campos de execução (migration 0007) ───────────────────────────
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "closed_at": session.closed_at,
            "closed_by_user_id": session.closed_by_user_id,
            "deviation_justification": session.deviation_justification,
            "planning_deviation_flag": session.planning_deviation_flag,
            "duration_actual_minutes": session.duration_actual_minutes,
            "execution_outcome": session.execution_outcome,
            "delay_minutes": session.delay_minutes,
            "cancellation_reason": session.cancellation_reason,
            "actual_load_recorded": session.actual_load_recorded,
            "post_review_completed_at": session.post_review_completed_at,
            "post_review_completed_by_user_id": session.post_review_completed_by_user_id,
            "post_review_deadline_at": session.post_review_deadline_at,
            "post_review_completed": session.post_review_completed,
            "planned_content_snapshot": session.planned_content_snapshot,
            "objective_origin": session.objective_origin,
            "continuity_notes": session.continuity_notes,
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
        page_id: Optional[uuid.UUID] = None,
    ) -> list[TrainingSession]:
        qs = TrainingSessionModel.objects.filter(deleted_at__isnull=True).order_by("-session_at", "-id")
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
                if page_id is not None:
                    # Cursor composto: (session_at, id) — tie-break determinístico (V12 fix)
                    from django.db.models import Q  # noqa: PLC0415
                    qs = qs.filter(
                        Q(session_at__lt=page_token)
                        | Q(session_at=page_token, id__lt=page_id)
                    )
                else:
                    # Fallback legado: apenas session_at (tokens pré-Fase 2)
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
            # ── Campos de execução (migration 0007) ───────────────────────────
            started_at=m.started_at,
            ended_at=m.ended_at,
            closed_at=m.closed_at,
            closed_by_user_id=m.closed_by_user_id,
            deviation_justification=m.deviation_justification,
            planning_deviation_flag=m.planning_deviation_flag,
            duration_actual_minutes=m.duration_actual_minutes,
            execution_outcome=m.execution_outcome,
            delay_minutes=m.delay_minutes,
            cancellation_reason=m.cancellation_reason,
            actual_load_recorded=m.actual_load_recorded,
            post_review_completed_at=m.post_review_completed_at,
            post_review_completed_by_user_id=m.post_review_completed_by_user_id,
            post_review_deadline_at=m.post_review_deadline_at,
            post_review_completed=m.post_review_completed,
            planned_content_snapshot=m.planned_content_snapshot,
            objective_origin=m.objective_origin,
            continuity_notes=m.continuity_notes,
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
