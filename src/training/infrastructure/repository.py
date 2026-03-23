"""
Repositórios — módulo training.
Implementam acesso a dados sem lógica de negócio.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from .models import (
    AttentionQueueItemModel,
    ExecutionRecordModel,
    FeedbackThreadModel,
    MesocycleModel,
    MicrocycleModel,
    SessionBlockModel,
    SessionObjectiveModel,
    TrainingSessionModel,
    WellnessPostModel,
    WellnessPreModel,
)
from ..domain.entities import (
    AttentionQueueItem,
    ExecutionRecord,
    ExecutionType,
    FeedbackThread,
    Mesocycle,
    Microcycle,
    SessionBlock,
    SessionBlockIntensity,
    SessionBlockPhase,
    SessionObjective,
    SessionObjectiveOrigin,
    TrainingSession,
    TrainingSessionStatus,
    WellnessPost,
    WellnessPre,
    ConversationOutcome,
)


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


class SessionBlockRepository:
    def get_by_id(self, id: uuid.UUID) -> Optional[SessionBlock]:
        try:
            m = SessionBlockModel.objects.get(pk=id)
            return self._to_domain(m)
        except SessionBlockModel.DoesNotExist:
            return None

    def list_by_session(self, session_id: uuid.UUID) -> list[SessionBlock]:
        return [
            self._to_domain(m)
            for m in SessionBlockModel.objects.filter(session_id=session_id).order_by("order_index")
        ]

    def save(self, block: SessionBlock) -> SessionBlock:
        defaults = {
            "session_id": block.session_id,
            "phase": block.phase.value,
            "order_index": block.order_index,
            "duration_minutes": block.duration_minutes,
            "block_objective": block.block_objective,
            "intensity": block.intensity.value,
            "is_optional": block.is_optional,
            "exercise_id": block.exercise_id,
            "exercise_version_id": block.exercise_version_id,
            "notes": block.notes or "",
        }
        m, _ = SessionBlockModel.objects.update_or_create(pk=block.id, defaults=defaults)
        return self._to_domain(m)

    def delete(self, id: uuid.UUID) -> None:
        SessionBlockModel.objects.filter(pk=id).delete()

    def total_duration_for_session(self, session_id: uuid.UUID, exclude_id: Optional[uuid.UUID] = None) -> int:
        qs = SessionBlockModel.objects.filter(session_id=session_id)
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return sum(b.duration_minutes for b in qs)

    def _to_domain(self, m: SessionBlockModel) -> SessionBlock:
        return SessionBlock(
            id=m.id,
            session_id=m.session_id,
            phase=SessionBlockPhase(m.phase),
            order_index=m.order_index,
            duration_minutes=m.duration_minutes,
            block_objective=m.block_objective,
            intensity=SessionBlockIntensity(m.intensity),
            is_optional=m.is_optional,
            exercise_id=m.exercise_id,
            exercise_version_id=m.exercise_version_id,
            notes=m.notes or None,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class WellnessPreRepository:
    def get_active(self, session_id: uuid.UUID, athlete_id: uuid.UUID) -> Optional[WellnessPre]:
        try:
            m = WellnessPreModel.objects.get(
                session_id=session_id, athlete_id=athlete_id, deleted_at__isnull=True
            )
            return self._to_domain(m)
        except WellnessPreModel.DoesNotExist:
            return None

    def save(self, wellness: WellnessPre) -> WellnessPre:
        defaults = {
            "session_id": wellness.session_id,
            "athlete_id": wellness.athlete_id,
            "readiness": wellness.readiness,
            "sleep_quality": wellness.sleep_quality,
            "mood": wellness.mood,
            "fatigue": wellness.fatigue,
            "muscle_soreness": wellness.muscle_soreness,
            "notes": wellness.notes or "",
            "deleted_at": wellness.deleted_at,
            "deleted_reason": wellness.deleted_reason or "",
        }
        m, _ = WellnessPreModel.objects.update_or_create(pk=wellness.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: WellnessPreModel) -> WellnessPre:
        return WellnessPre(
            id=m.id,
            session_id=m.session_id,
            athlete_id=m.athlete_id,
            readiness=m.readiness,
            sleep_quality=m.sleep_quality,
            mood=m.mood,
            fatigue=m.fatigue,
            muscle_soreness=m.muscle_soreness,
            notes=m.notes or None,
            created_at=m.created_at,
            updated_at=m.updated_at,
            deleted_at=m.deleted_at,
            deleted_reason=m.deleted_reason or None,
        )


class WellnessPostRepository:
    def get_active(self, session_id: uuid.UUID, athlete_id: uuid.UUID) -> Optional[WellnessPost]:
        try:
            m = WellnessPostModel.objects.get(
                session_id=session_id, athlete_id=athlete_id, deleted_at__isnull=True
            )
            return self._to_domain(m)
        except WellnessPostModel.DoesNotExist:
            return None

    def save(self, wellness: WellnessPost) -> WellnessPost:
        defaults = {
            "session_id": wellness.session_id,
            "athlete_id": wellness.athlete_id,
            "perceived_exertion": wellness.perceived_exertion,
            "enjoyment": wellness.enjoyment,
            "technical_learning": wellness.technical_learning,
            "notes": wellness.notes or "",
            "deleted_at": wellness.deleted_at,
            "deleted_reason": wellness.deleted_reason or "",
        }
        m, _ = WellnessPostModel.objects.update_or_create(pk=wellness.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: WellnessPostModel) -> WellnessPost:
        return WellnessPost(
            id=m.id,
            session_id=m.session_id,
            athlete_id=m.athlete_id,
            perceived_exertion=m.perceived_exertion,
            enjoyment=m.enjoyment,
            technical_learning=m.technical_learning,
            notes=m.notes or None,
            created_at=m.created_at,
            updated_at=m.updated_at,
            deleted_at=m.deleted_at,
            deleted_reason=m.deleted_reason or None,
        )


class ExecutionRecordRepository:
    def list_by_session(self, session_id: uuid.UUID) -> list[ExecutionRecord]:
        return [
            self._to_domain(m)
            for m in ExecutionRecordModel.objects.filter(session_id=session_id).order_by("recorded_at")
        ]

    def save(self, record: ExecutionRecord) -> ExecutionRecord:
        defaults = {
            "session_id": record.session_id,
            "block_id": record.block_id,
            "execution_type": record.execution_type.value,
            "recorded_at": record.recorded_at,
            "planned_value": record.planned_value,
            "actual_value": record.actual_value,
            "planned_unit": record.planned_unit or "",
            "actual_unit": record.actual_unit or "",
            "adjustment_reason_type": record.adjustment_reason_type or "",
            "coach_rationale": record.coach_rationale or "",
            "notes": record.notes or "",
            "created_by_user_id": record.created_by_user_id,
        }
        m, _ = ExecutionRecordModel.objects.update_or_create(pk=record.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: ExecutionRecordModel) -> ExecutionRecord:
        return ExecutionRecord(
            id=m.id,
            session_id=m.session_id,
            block_id=m.block_id,
            execution_type=ExecutionType(m.execution_type),
            recorded_at=m.recorded_at,
            planned_value=m.planned_value,
            actual_value=m.actual_value,
            planned_unit=m.planned_unit or None,
            actual_unit=m.actual_unit or None,
            adjustment_reason_type=m.adjustment_reason_type or None,
            coach_rationale=m.coach_rationale or None,
            notes=m.notes or None,
            created_by_user_id=m.created_by_user_id,
            created_at=m.created_at,
            updated_at=m.updated_at,
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


class FeedbackThreadRepository:
    def list_by_session(self, session_id: uuid.UUID) -> list[FeedbackThread]:
        return [
            self._to_domain(m)
            for m in FeedbackThreadModel.objects.filter(session_id=session_id).order_by("-created_at")
        ]

    def save(self, thread: FeedbackThread) -> FeedbackThread:
        defaults = {
            "session_id": thread.session_id,
            "block_id": thread.block_id,
            "athlete_id": thread.athlete_id,
            "objective_id": thread.objective_id,
            "created_by_user_id": thread.created_by_user_id,
            "subject": thread.subject or "",
            "body": thread.body or "",
            "conversation_outcome": thread.conversation_outcome.value,
            "follow_up_at": thread.follow_up_at,
            "commitment_text": thread.commitment_text or "",
            "decision_text": thread.decision_text or "",
            "closed_at": thread.closed_at,
        }
        m, _ = FeedbackThreadModel.objects.update_or_create(pk=thread.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: FeedbackThreadModel) -> FeedbackThread:
        return FeedbackThread(
            id=m.id,
            session_id=m.session_id,
            block_id=m.block_id,
            athlete_id=m.athlete_id,
            objective_id=m.objective_id,
            created_by_user_id=m.created_by_user_id,
            subject=m.subject or None,
            body=m.body or None,
            conversation_outcome=ConversationOutcome(m.conversation_outcome),
            follow_up_at=m.follow_up_at,
            commitment_text=m.commitment_text or None,
            decision_text=m.decision_text or None,
            closed_at=m.closed_at,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class AttentionQueueRepository:
    def list_by_session(self, session_id: uuid.UUID) -> list[AttentionQueueItem]:
        return [
            self._to_domain(m)
            for m in AttentionQueueItemModel.objects.filter(
                session_id=session_id, resolved_at__isnull=True, dismissed_at__isnull=True
            ).order_by("-created_at")
        ]

    def get_by_id(self, id: uuid.UUID) -> Optional[AttentionQueueItem]:
        try:
            return self._to_domain(AttentionQueueItemModel.objects.get(pk=id))
        except AttentionQueueItemModel.DoesNotExist:
            return None

    def save(self, item: AttentionQueueItem) -> AttentionQueueItem:
        defaults = {
            "session_id": item.session_id,
            "athlete_id": item.athlete_id,
            "reason": item.reason,
            "severity": item.severity,
            "resolved_at": item.resolved_at,
            "resolved_by": item.resolved_by,
            "dismissed_at": item.dismissed_at,
            "escalated_at": item.escalated_at,
            "notes": item.notes or "",
        }
        m, _ = AttentionQueueItemModel.objects.update_or_create(pk=item.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: AttentionQueueItemModel) -> AttentionQueueItem:
        return AttentionQueueItem(
            id=m.id,
            session_id=m.session_id,
            athlete_id=m.athlete_id,
            reason=m.reason,
            severity=m.severity,
            resolved_at=m.resolved_at,
            resolved_by=m.resolved_by,
            dismissed_at=m.dismissed_at,
            escalated_at=m.escalated_at,
            notes=m.notes or None,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


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
