"""Helpers de conversão domínio → schema HTTP (training.api).

Contém os 17 helpers _*_to_out que serializam entidades de domínio
para os schemas Pydantic da camada HTTP.

Extraído de api/_shared.py na Fase 1.4 da refatoração estrutural.
"""
from __future__ import annotations

import uuid

from ..schemas import (
    AthleteIneligibilityDeclarationOut,
    AttendanceRecordOut,
    AttentionQueueItemOut,
    ExecutionRecordOut,
    FeedbackThreadOut,
    MesocycleOut,
    MicrocycleOut,
    RecommendationOut,
    SessionBlockOut,
    SessionObjectiveOut,
    TrainingSessionOut,
    WellnessPostOut,
    WellnessPreOut,
)


def _session_to_out(s) -> TrainingSessionOut:
    return TrainingSessionOut(
        id=s.id,
        organization_id=s.organization_id,
        session_at=s.session_at,
        session_type=s.session_type,
        status=s.status.value,
        created_by_user_id=s.created_by_user_id,
        created_at=s.created_at,
        updated_at=s.updated_at,
        team_id=s.team_id,
        season_id=s.season_id,
        microcycle_id=s.microcycle_id,
        duration_planned_minutes=s.duration_planned_minutes,
        location=s.location,
        main_objective=s.main_objective,
        secondary_objective=s.secondary_objective,
        planned_load=s.planned_load,
        intensity_target=s.intensity_target,
        session_block=s.session_block,
        notes=s.notes,
        group_climate=s.group_climate,
        standalone=s.standalone,
        individualization_mode=s.individualization_mode,
        focus_attack_positional_pct=s.focus_attack_positional_pct,
        focus_defense_positional_pct=s.focus_defense_positional_pct,
        focus_transition_offense_pct=s.focus_transition_offense_pct,
        focus_transition_defense_pct=s.focus_transition_defense_pct,
        focus_attack_technical_pct=s.focus_attack_technical_pct,
        focus_defense_technical_pct=s.focus_defense_technical_pct,
        focus_physical_pct=s.focus_physical_pct,
        phase_focus_defense=s.phase_focus_defense,
        phase_focus_attack=s.phase_focus_attack,
        phase_focus_transition_offense=s.phase_focus_transition_offense,
        phase_focus_transition_defense=s.phase_focus_transition_defense,
    )


def _block_to_out(b) -> SessionBlockOut:
    return SessionBlockOut(
        id=b.id,
        session_id=b.session_id,
        phase=b.phase.value,
        order_index=b.order_index,
        duration_minutes=b.duration_minutes,
        block_objective=b.block_objective,
        intensity=b.intensity.value,
        is_optional=b.is_optional,
        exercise_id=b.exercise_id,
        exercise_version_id=b.exercise_version_id,
        notes=b.notes,
        created_at=b.created_at,
        updated_at=b.updated_at,
    )


def _attendance_to_out(attendance) -> AttendanceRecordOut:
    return AttendanceRecordOut(
        athlete_id=attendance.athlete_id,
        status=attendance.status.value,
        recorded_at=attendance.recorded_at,
        source=attendance.source.value,
        correction_by_user_id=attendance.correction_by_user_id,
        correction_at=attendance.correction_at,
        justification_reason=attendance.justification_reason,
    )


def _wellness_pre_to_out(wellness) -> WellnessPreOut:
    return WellnessPreOut(
        id=wellness.id,
        session_id=wellness.session_id,
        athlete_id=wellness.athlete_id,
        readiness=wellness.readiness,
        sleep_quality=wellness.sleep_quality,
        mood=wellness.mood,
        fatigue=wellness.fatigue,
        muscle_soreness=wellness.muscle_soreness,
        notes=wellness.notes,
        created_at=wellness.created_at,
        updated_at=wellness.updated_at,
    )


def _wellness_post_to_out(wellness) -> WellnessPostOut:
    return WellnessPostOut(
        id=wellness.id,
        session_id=wellness.session_id,
        athlete_id=wellness.athlete_id,
        perceived_exertion=wellness.perceived_exertion,
        enjoyment=wellness.enjoyment,
        technical_learning=wellness.technical_learning,
        notes=wellness.notes,
        created_at=wellness.created_at,
        updated_at=wellness.updated_at,
    )


def _execution_record_to_out(record) -> ExecutionRecordOut:
    return ExecutionRecordOut(
        id=record.id,
        session_id=record.session_id,
        execution_type=record.execution_type.value,
        recorded_at=record.recorded_at,
        created_by_user_id=record.created_by_user_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
        block_id=record.block_id,
        planned_value=record.planned_value,
        actual_value=record.actual_value,
        planned_unit=record.planned_unit,
        actual_unit=record.actual_unit,
        adjustment_reason_type=record.adjustment_reason_type,
        coach_rationale=record.coach_rationale,
        notes=record.notes,
    )


def _session_objective_to_out(obj) -> SessionObjectiveOut:
    return SessionObjectiveOut(
        id=obj.id,
        session_id=obj.session_id,
        origin=obj.origin.value,
        objective_type=obj.objective_type,
        description=obj.description,
        origin_notes=obj.origin_notes,
        priority=obj.priority,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


def _mesocycle_to_out(meso) -> MesocycleOut:
    return MesocycleOut(
        id=meso.id,
        organization_id=meso.organization_id,
        name=meso.name,
        started_at=meso.started_at,
        ended_at=meso.ended_at,
        created_at=meso.created_at,
        updated_at=meso.updated_at,
        season_id=meso.season_id,
        team_id=meso.team_id,
        objective=meso.objective,
        notes=meso.notes,
    )


def _microcycle_to_out(micro) -> MicrocycleOut:
    return MicrocycleOut(
        id=micro.id,
        organization_id=micro.organization_id,
        mesocycle_id=micro.mesocycle_id,
        week_number=micro.week_number,
        started_at=micro.started_at,
        ended_at=micro.ended_at,
        created_at=micro.created_at,
        updated_at=micro.updated_at,
        team_id=micro.team_id,
        name=micro.name,
        objective=micro.objective,
        planned_sessions_count=micro.planned_sessions_count,
        notes=micro.notes,
    )


def _feedback_context_type(thread) -> str:
    if thread.subject in {"SESSION", "BLOCK", "OBJECTIVE", "ATHLETE", "EVIDENCE", "GROUP"}:
        return thread.subject
    if thread.block_id is not None:
        return "BLOCK"
    if thread.objective_id is not None:
        return "OBJECTIVE"
    if thread.athlete_id is not None:
        return "ATHLETE"
    return "SESSION"


def _feedback_context_ref_id(thread) -> uuid.UUID:
    context_type = _feedback_context_type(thread)
    if context_type == "BLOCK" and thread.block_id is not None:
        return thread.block_id
    if context_type == "OBJECTIVE" and thread.objective_id is not None:
        return thread.objective_id
    if context_type == "ATHLETE" and thread.athlete_id is not None:
        return thread.athlete_id
    return thread.session_id


def _feedback_thread_to_out(thread) -> FeedbackThreadOut:
    return FeedbackThreadOut(
        id=thread.id,
        session_id=thread.session_id,
        context_type=_feedback_context_type(thread),
        context_ref_id=_feedback_context_ref_id(thread),
        conversation_outcome=thread.conversation_outcome.value,
        created_by_user_id=thread.created_by_user_id,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
        athlete_id=thread.athlete_id,
        content=thread.body,
        follow_up_at=thread.follow_up_at,
        commitment_text=thread.commitment_text,
        decision_text=thread.decision_text,
    )


def _attention_queue_item_to_out(item) -> AttentionQueueItemOut:
    resolved_at = item.resolved_at or item.dismissed_at or item.escalated_at
    return AttentionQueueItemOut(
        id=item.id,
        session_id=item.session_id,
        severity=item.severity,
        reason_code=item.reason,
        target_entity_type="athlete",
        target_entity_id=item.athlete_id,
        message=item.notes or item.reason,
        created_at=item.created_at,
        resolved_at=resolved_at,
        resolved_by_user_id=item.resolved_by,
    )


def _recommendation_to_out(recommendation) -> RecommendationOut:
    return RecommendationOut(
        id=recommendation.id,
        session_id=recommendation.session_id,
        generated_by_rule=recommendation.generated_by_rule,
        action_type=recommendation.action_type.value,
        description=recommendation.description,
        status=recommendation.status.value,
        generated_by_module=recommendation.generated_by_module,
        created_at=recommendation.created_at,
        updated_at=recommendation.updated_at,
        priority=recommendation.priority.value if recommendation.priority else None,
        coach_note=recommendation.coach_note,
        dismissal_reason=recommendation.dismissal_reason,
        resolved_at=recommendation.resolved_at,
        resolved_by_user_id=recommendation.resolved_by_user_id,
    )


def _ineligibility_to_out(declaration) -> AthleteIneligibilityDeclarationOut:
    return AthleteIneligibilityDeclarationOut(
        id=declaration.id,
        session_id=declaration.session_id,
        athlete_id=declaration.athlete_id,
        reason_flags=declaration.reason_flags,
        reason_other=declaration.reason_other,
        acknowledged_by_coach=declaration.acknowledged_by_coach,
        coach_note=declaration.coach_note,
        declared_at=declaration.declared_at,
        created_at=declaration.created_at,
    )
