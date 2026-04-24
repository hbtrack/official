from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ...domain.entities import TrainingSession, TrainingSessionStatus
from ...domain.policies.session_access import SessionGuard
from ...domain.rules import (
    assert_can_create_session,
    assert_session_not_historical,
    assert_publish_preconditions,
    assert_schedule_preconditions,
)
from ...infrastructure.repository import TrainingSessionRepository
from .dto import (
    CreateTrainingSessionInput,
    DeleteTrainingSessionInput,
    TransitionTrainingSessionInput,
    UpdateTrainingSessionInput,
)


class CreateTrainingSessionUseCase:
    def __init__(self, repo: TrainingSessionRepository):
        self._repo = repo

    def execute(self, inp: CreateTrainingSessionInput) -> TrainingSession:
        # DR-TRAIN-001
        assert_can_create_session(inp.actor_role)
        session = TrainingSession(
            id=uuid.uuid4(),
            organization_id=inp.organization_id,
            session_at=inp.session_at,
            session_type=inp.session_type,
            status=TrainingSessionStatus.DRAFT,
            created_by_user_id=inp.actor_id,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
            team_id=inp.team_id,
            season_id=inp.season_id,
            microcycle_id=inp.microcycle_id,
            duration_planned_minutes=inp.duration_planned_minutes,
            location=inp.location,
            main_objective=inp.main_objective,
            secondary_objective=inp.secondary_objective,
            planned_load=inp.planned_load,
            intensity_target=inp.intensity_target,
            session_block=inp.session_block,
            standalone=inp.standalone,
            focus_attack_positional_pct=inp.focus_attack_positional_pct,
            focus_defense_positional_pct=inp.focus_defense_positional_pct,
            focus_transition_offense_pct=inp.focus_transition_offense_pct,
            focus_transition_defense_pct=inp.focus_transition_defense_pct,
            focus_attack_technical_pct=inp.focus_attack_technical_pct,
            focus_defense_technical_pct=inp.focus_defense_technical_pct,
            focus_physical_pct=inp.focus_physical_pct,
            phase_focus_defense=inp.phase_focus_defense,
            phase_focus_attack=inp.phase_focus_attack,
            phase_focus_transition_offense=inp.phase_focus_transition_offense,
            phase_focus_transition_defense=inp.phase_focus_transition_defense,
        )
        session.validate_invariants()
        return self._repo.save(session)


class TransitionTrainingSessionUseCase:
    """Handles start/complete/cancel/publish/unpublish/archive operations."""

    def __init__(self, repo: TrainingSessionRepository):
        self._repo = repo
        self._guard = SessionGuard(repo)

    def execute(self, inp: TransitionTrainingSessionInput) -> TrainingSession:
        session = self._guard.load_for_transition(inp.id, inp.target_status, inp.actor_role)
        if inp.target_status == TrainingSessionStatus.PUBLISHED:
            assert_publish_preconditions(session)
        if inp.target_status == TrainingSessionStatus.SCHEDULED:
            assert_schedule_preconditions(session)
        session.status = inp.target_status
        session.updated_at = datetime.now(tz=timezone.utc)
        return self._repo.save(session)


class DeleteTrainingSessionUseCase:
    def __init__(self, repo: TrainingSessionRepository):
        self._repo = repo
        self._guard = SessionGuard(repo)

    def execute(self, inp: DeleteTrainingSessionInput) -> None:
        session = self._guard.load_for_delete(inp.id, inp.actor_role)
        now = datetime.now(tz=timezone.utc)
        session.deleted_at = now
        session.deleted_reason = inp.deleted_reason
        session.updated_at = now
        self._repo.save(session)


class UpdateTrainingSessionUseCase:
    def __init__(self, repo: TrainingSessionRepository):
        self._repo = repo
        self._guard = SessionGuard(repo)

    def execute(self, inp: UpdateTrainingSessionInput) -> TrainingSession:
        session = self._guard.load_for_update(inp.id, inp.actor_role)
        assert_session_not_historical(session.session_at)
        if inp.session_at is not None:
            session.session_at = inp.session_at
        if inp.session_type is not None:
            session.session_type = inp.session_type
        if inp.duration_planned_minutes is not None:
            session.duration_planned_minutes = inp.duration_planned_minutes
        if inp.location is not None:
            session.location = inp.location
        if inp.main_objective is not None:
            session.main_objective = inp.main_objective
        if inp.secondary_objective is not None:
            session.secondary_objective = inp.secondary_objective
        if inp.planned_load is not None:
            session.planned_load = inp.planned_load
        if inp.intensity_target is not None:
            session.intensity_target = inp.intensity_target
        if inp.session_block is not None:
            session.session_block = inp.session_block
        if inp.standalone is not None:
            session.standalone = inp.standalone
        if inp.notes is not None:
            session.notes = inp.notes
        if inp.focus_attack_positional_pct is not None:
            session.focus_attack_positional_pct = inp.focus_attack_positional_pct
        if inp.focus_defense_positional_pct is not None:
            session.focus_defense_positional_pct = inp.focus_defense_positional_pct
        if inp.focus_transition_offense_pct is not None:
            session.focus_transition_offense_pct = inp.focus_transition_offense_pct
        if inp.focus_transition_defense_pct is not None:
            session.focus_transition_defense_pct = inp.focus_transition_defense_pct
        if inp.focus_attack_technical_pct is not None:
            session.focus_attack_technical_pct = inp.focus_attack_technical_pct
        if inp.focus_defense_technical_pct is not None:
            session.focus_defense_technical_pct = inp.focus_defense_technical_pct
        if inp.focus_physical_pct is not None:
            session.focus_physical_pct = inp.focus_physical_pct
        if inp.phase_focus_defense is not None:
            session.phase_focus_defense = inp.phase_focus_defense
        if inp.phase_focus_attack is not None:
            session.phase_focus_attack = inp.phase_focus_attack
        if inp.phase_focus_transition_offense is not None:
            session.phase_focus_transition_offense = inp.phase_focus_transition_offense
        if inp.phase_focus_transition_defense is not None:
            session.phase_focus_transition_defense = inp.phase_focus_transition_defense
        session.updated_at = datetime.now(tz=timezone.utc)
        session.validate_invariants()
        return self._repo.save(session)
