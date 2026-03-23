"""
Testes unitários — módulo training.
Derivados de TEST_MATRIX_TRAINING.md, INVARIANTS_TRAINING.md, DOMAIN_RULES_TRAINING.md.
Sem banco de dados — apenas lógica de domínio pura.
"""
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import pytest

from training.domain.entities import (
    ConversationOutcome,
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
    WellnessPre,
    WellnessPost,
)
from training.domain.rules import (
    VALID_TRANSITIONS,
    ElasticSumRuleViolation,
    InsufficientPrivilege,
    InvalidStatusTransition,
    RoleLabel,
    SessionNotMutable,
    WellnessWindowClosed,
    assert_can_create_session,
    assert_can_delete_session,
    assert_can_read_session,
    assert_can_submit_wellness,
    assert_elastic_sum_rule,
    assert_session_mutable,
    assert_session_not_historical,
    assert_valid_transition,
    assert_wellness_post_window,
    assert_wellness_pre_window,
)


def _make_session(**kwargs) -> TrainingSession:
    defaults = dict(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        session_at=datetime.now(tz=timezone.utc) + timedelta(hours=4),
        session_type="TACTICAL",
        status=TrainingSessionStatus.DRAFT,
        created_by_user_id=uuid.uuid4(),
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )
    defaults.update(kwargs)
    return TrainingSession(**defaults)


def _make_block(**kwargs) -> SessionBlock:
    defaults = dict(
        id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        phase=SessionBlockPhase.TACTICAL,
        order_index=0,
        duration_minutes=20,
        block_objective="Treinar transição ofensiva",
        intensity=SessionBlockIntensity.HIGH,
        is_optional=False,
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )
    defaults.update(kwargs)
    return SessionBlock(**defaults)


# ---------------------------------------------------------------------------
# INV-TRAIN-001: Focus percentages
# ---------------------------------------------------------------------------

class TestFocusPercentagesInvariant:
    def test_valid_focus_sum_passes(self):
        s = _make_session(
            focus_attack_positional_pct=Decimal("30"),
            focus_defense_positional_pct=Decimal("30"),
            focus_physical_pct=Decimal("30"),
        )
        s.validate_invariants()  # deve passar (90 ≤ 120)

    def test_sum_at_boundary_120_passes(self):
        # exatamente 120
        s = _make_session(
            focus_attack_positional_pct=Decimal("40"),
            focus_defense_positional_pct=Decimal("40"),
            focus_physical_pct=Decimal("40"),
        )
        s.validate_invariants()

    def test_sum_exceeds_120_raises(self):
        s = _make_session(
            focus_attack_positional_pct=Decimal("33.34"),
            focus_defense_positional_pct=Decimal("33.34"),
            focus_transition_offense_pct=Decimal("33.34"),
            focus_transition_defense_pct=Decimal("33.34"),
        )
        with pytest.raises(ValueError, match="INV-TRAIN-001"):
            s.validate_invariants()

    def test_individual_field_above_100_raises(self):
        s = _make_session(focus_attack_positional_pct=Decimal("101"))
        with pytest.raises(ValueError, match="INV-TRAIN-001"):
            s.validate_invariants()

    def test_individual_field_below_0_raises(self):
        s = _make_session(focus_attack_positional_pct=Decimal("-1"))
        with pytest.raises(ValueError, match="INV-TRAIN-001"):
            s.validate_invariants()

    def test_boundary_33_33_x3_equals_100_passes(self):
        s = _make_session(
            focus_attack_positional_pct=Decimal("33.33"),
            focus_defense_positional_pct=Decimal("33.33"),
            focus_physical_pct=Decimal("33.34"),
        )
        s.validate_invariants()


# ---------------------------------------------------------------------------
# INV-TRAIN-006: FSM transitions
# ---------------------------------------------------------------------------

class TestTrainingSessionFSM:
    def test_draft_to_scheduled_valid(self):
        assert_valid_transition(TrainingSessionStatus.DRAFT, TrainingSessionStatus.SCHEDULED)

    def test_draft_to_published_valid(self):
        assert_valid_transition(TrainingSessionStatus.DRAFT, TrainingSessionStatus.PUBLISHED)

    def test_draft_to_completed_invalid(self):
        with pytest.raises(InvalidStatusTransition, match="INV-TRAIN-006"):
            assert_valid_transition(TrainingSessionStatus.DRAFT, TrainingSessionStatus.COMPLETED)

    def test_completed_to_archived_valid(self):
        assert_valid_transition(TrainingSessionStatus.COMPLETED, TrainingSessionStatus.ARCHIVED)

    def test_archived_terminal(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_transition(TrainingSessionStatus.ARCHIVED, TrainingSessionStatus.DRAFT)

    def test_cancelled_terminal(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_transition(TrainingSessionStatus.CANCELLED, TrainingSessionStatus.DRAFT)

    def test_in_progress_to_completed_valid(self):
        assert_valid_transition(TrainingSessionStatus.IN_PROGRESS, TrainingSessionStatus.COMPLETED)

    def test_in_progress_to_cancelled_valid(self):
        assert_valid_transition(TrainingSessionStatus.IN_PROGRESS, TrainingSessionStatus.CANCELLED)

    def test_assert_session_mutable_draft_ok(self):
        assert_session_mutable(TrainingSessionStatus.DRAFT)

    def test_assert_session_mutable_completed_raises(self):
        with pytest.raises(SessionNotMutable):
            assert_session_mutable(TrainingSessionStatus.COMPLETED)

    def test_assert_session_mutable_archived_raises(self):
        with pytest.raises(SessionNotMutable):
            assert_session_mutable(TrainingSessionStatus.ARCHIVED)


# ---------------------------------------------------------------------------
# DR-TRAIN-001: RBAC para criação de sessão
# ---------------------------------------------------------------------------

class TestCreateSessionRBAC:
    def test_coach_can_create(self):
        assert_can_create_session(RoleLabel.COACH)

    def test_coordinator_can_create(self):
        assert_can_create_session(RoleLabel.COORDINATOR)

    def test_admin_can_create(self):
        assert_can_create_session(RoleLabel.ADMIN)

    def test_athlete_cannot_create(self):
        with pytest.raises(InsufficientPrivilege, match="DR-TRAIN-001"):
            assert_can_create_session(RoleLabel.ATHLETE)

    def test_member_cannot_create(self):
        with pytest.raises(InsufficientPrivilege, match="DR-TRAIN-001"):
            assert_can_create_session(RoleLabel.MEMBER)


# ---------------------------------------------------------------------------
# BOLA: leitura de sessão
# ---------------------------------------------------------------------------

class TestReadSessionBOLA:
    def test_admin_reads_any_session(self):
        actor_id = uuid.uuid4()
        assert_can_read_session(RoleLabel.ADMIN, actor_id, [])

    def test_coach_reads_any_session(self):
        actor_id = uuid.uuid4()
        assert_can_read_session(RoleLabel.COACH, actor_id, [])

    def test_athlete_reads_own_session(self):
        actor_id = uuid.uuid4()
        assert_can_read_session(RoleLabel.ATHLETE, actor_id, [actor_id])

    def test_athlete_denied_for_other_session(self):
        actor_id = uuid.uuid4()
        with pytest.raises(InsufficientPrivilege, match="BOLA"):
            assert_can_read_session(RoleLabel.ATHLETE, actor_id, [uuid.uuid4()])

    def test_member_always_denied(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_session(RoleLabel.MEMBER, uuid.uuid4(), [])


# ---------------------------------------------------------------------------
# SessionBlock: invariantes TRAIN-DEC-047 e INV-TRAIN-083
# ---------------------------------------------------------------------------

class TestSessionBlockInvariants:
    def test_valid_block_passes(self):
        b = _make_block()
        b.validate_invariants()

    def test_exercise_id_without_version_raises(self):
        b = _make_block(exercise_id=uuid.uuid4(), exercise_version_id=None)
        with pytest.raises(ValueError, match="TRAIN-DEC-047"):
            b.validate_invariants()

    def test_exercise_id_with_version_passes(self):
        b = _make_block(exercise_id=uuid.uuid4(), exercise_version_id=uuid.uuid4())
        b.validate_invariants()

    def test_duration_min_1_passes(self):
        b = _make_block(duration_minutes=1)
        b.validate_invariants()

    def test_duration_0_raises(self):
        b = _make_block(duration_minutes=0)
        with pytest.raises(ValueError):
            b.validate_invariants()

    def test_duration_240_passes(self):
        b = _make_block(duration_minutes=240)
        b.validate_invariants()

    def test_duration_241_raises(self):
        b = _make_block(duration_minutes=241)
        with pytest.raises(ValueError):
            b.validate_invariants()

    def test_block_objective_too_short_raises(self):
        b = _make_block(block_objective="ab")
        with pytest.raises(ValueError):
            b.validate_invariants()

    def test_block_objective_min_3_passes(self):
        b = _make_block(block_objective="abc")
        b.validate_invariants()

    def test_negative_order_index_raises(self):
        b = _make_block(order_index=-1)
        with pytest.raises(ValueError):
            b.validate_invariants()


# ---------------------------------------------------------------------------
# INV-TRAIN-083: Elastic Sum Rule
# ---------------------------------------------------------------------------

class TestElasticSumRule:
    def test_passes_within_limit(self):
        assert_elastic_sum_rule(
            duration_planned_minutes=60,
            blocks_total_minutes=40,
            new_block_minutes=15,
        )

    def test_passes_at_exact_planned(self):
        assert_elastic_sum_rule(
            duration_planned_minutes=60,
            blocks_total_minutes=50,
            new_block_minutes=10,
        )

    def test_passes_within_tolerance(self):
        # tolerance = min(60 * 0.10, 10) = 6 → hard limit = 66
        assert_elastic_sum_rule(
            duration_planned_minutes=60,
            blocks_total_minutes=55,
            new_block_minutes=10,
        )

    def test_fails_beyond_tolerance(self):
        with pytest.raises(ElasticSumRuleViolation, match="INV-TRAIN-083"):
            assert_elastic_sum_rule(
                duration_planned_minutes=60,
                blocks_total_minutes=60,
                new_block_minutes=10,
            )

    def test_no_planned_passes(self):
        # Sem durationPlannedMinutes não valida
        assert_elastic_sum_rule(None, 1000, 1000)


# ---------------------------------------------------------------------------
# Wellness pre temporal invariant
# ---------------------------------------------------------------------------

class TestWellnessPreWindow:
    def test_far_future_session_passes(self):
        session_at = datetime.now(tz=timezone.utc) + timedelta(hours=10)
        assert_wellness_pre_window(session_at)

    def test_deadline_passed_raises(self):
        # session_at está no passado — deadline = session_at - 2h já passou
        session_at = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        with pytest.raises(WellnessWindowClosed, match="INV-TRAIN-002"):
            assert_wellness_pre_window(session_at)

    def test_just_before_deadline_passes(self):
        # deadline = NOW + 2h - 30s → session_at deve ser >= NOW + 2h - 30s + 2h?
        # session_at = NOW + 2h + 1min → dentro da janela
        session_at = datetime.now(tz=timezone.utc) + timedelta(hours=2, minutes=1)
        assert_wellness_pre_window(session_at)


# ---------------------------------------------------------------------------
# SessionObjective invariants: DR-TRAIN-013
# ---------------------------------------------------------------------------

class TestSessionObjectiveInvariants:
    def test_manual_rationale_requires_origin_notes(self):
        obj = SessionObjective(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            origin=SessionObjectiveOrigin.MANUAL_COACH_RATIONALE,
            objective_type="TACTICAL",
            description="Melhora da transição",
            origin_notes=None,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        with pytest.raises(ValueError, match="DR-TRAIN-013"):
            obj.validate_invariants()

    def test_manual_rationale_with_notes_passes(self):
        obj = SessionObjective(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            origin=SessionObjectiveOrigin.MANUAL_COACH_RATIONALE,
            objective_type="TACTICAL",
            description="Melhora da transição",
            origin_notes="Treinador identificou problema tático na última partida",
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        obj.validate_invariants()

    def test_other_origins_no_notes_required(self):
        obj = SessionObjective(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            origin=SessionObjectiveOrigin.COMPETITIVE_FOCUS,
            objective_type="TACTICAL",
            description="Preparação para jogo",
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        obj.validate_invariants()


# ---------------------------------------------------------------------------
# FeedbackThread: DR-TRAIN-022
# ---------------------------------------------------------------------------

class TestFeedbackThreadInvariants:
    def _make_thread(self, **kwargs):
        defaults = dict(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            created_by_user_id=uuid.uuid4(),
            conversation_outcome=ConversationOutcome.REFLECTION_DOCUMENTED,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        defaults.update(kwargs)
        return FeedbackThread(**defaults)

    def test_followup_scheduled_without_followup_at_raises(self):
        thread = self._make_thread(
            conversation_outcome=ConversationOutcome.FOLLOWUP_SCHEDULED,
            follow_up_at=None,
        )
        with pytest.raises(ValueError, match="DR-TRAIN-022"):
            thread.validate_invariants()

    def test_followup_scheduled_with_date_passes(self):
        thread = self._make_thread(
            conversation_outcome=ConversationOutcome.FOLLOWUP_SCHEDULED,
            follow_up_at=datetime.now(tz=timezone.utc) + timedelta(days=7),
        )
        thread.validate_invariants()

    def test_commitment_made_requires_text(self):
        thread = self._make_thread(
            conversation_outcome=ConversationOutcome.COMMITMENT_MADE,
            commitment_text=None,
        )
        with pytest.raises(ValueError, match="DR-TRAIN-022"):
            thread.validate_invariants()

    def test_decision_recorded_requires_text(self):
        thread = self._make_thread(
            conversation_outcome=ConversationOutcome.DECISION_RECORDED,
            decision_text=None,
        )
        with pytest.raises(ValueError, match="DR-TRAIN-022"):
            thread.validate_invariants()


# ---------------------------------------------------------------------------
# Mesocycle invariants
# ---------------------------------------------------------------------------

class TestMesocycleInvariants:
    def test_valid_mesocycle_passes(self):
        m = Mesocycle(
            id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            name="Mesociclo Pré-Temporada",
            started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ended_at=datetime(2026, 1, 28, tzinfo=timezone.utc),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        m.validate_invariants()

    def test_start_after_end_raises(self):
        m = Mesocycle(
            id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            name="Inválido",
            started_at=datetime(2026, 1, 28, tzinfo=timezone.utc),
            ended_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        with pytest.raises(ValueError):
            m.validate_invariants()

    def test_empty_name_raises(self):
        m = Mesocycle(
            id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            name="",
            started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ended_at=datetime(2026, 1, 28, tzinfo=timezone.utc),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        with pytest.raises(ValueError):
            m.validate_invariants()


# ---------------------------------------------------------------------------
# WellnessPost invariants
# ---------------------------------------------------------------------------

class TestWellnessPostInvariants:
    def test_valid_post_passes(self):
        w = WellnessPost(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            athlete_id=uuid.uuid4(),
            perceived_exertion=7,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        w.validate_invariants()

    def test_rpe_above_10_raises(self):
        w = WellnessPost(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            athlete_id=uuid.uuid4(),
            perceived_exertion=11,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        with pytest.raises(ValueError):
            w.validate_invariants()

    def test_rpe_below_1_raises(self):
        w = WellnessPost(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            athlete_id=uuid.uuid4(),
            perceived_exertion=0,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        with pytest.raises(ValueError):
            w.validate_invariants()


# ---------------------------------------------------------------------------
# INV-TRAIN-008: soft delete consistency
# ---------------------------------------------------------------------------

class TestSoftDeleteInvariant:
    def test_both_none_passes(self):
        s = _make_session(deleted_at=None, deleted_reason=None)
        s.validate_invariants()

    def test_both_set_passes(self):
        s = _make_session(
            deleted_at=datetime.now(tz=timezone.utc),
            deleted_reason="Por solicitação do coordenador",
        )
        s.validate_invariants()

    def test_deleted_at_without_reason_raises(self):
        s = _make_session(
            deleted_at=datetime.now(tz=timezone.utc),
            deleted_reason=None,
        )
        with pytest.raises(ValueError, match="INV-TRAIN-008"):
            s.validate_invariants()

    def test_reason_without_deleted_at_raises(self):
        s = _make_session(
            deleted_at=None,
            deleted_reason="Sem motivo oficial",
        )
        with pytest.raises(ValueError, match="INV-TRAIN-008"):
            s.validate_invariants()


# ---------------------------------------------------------------------------
# Wellness BOPLA
# ---------------------------------------------------------------------------

class TestWellnessBOPLA:
    def test_athlete_submits_own(self):
        actor_id = uuid.uuid4()
        assert_can_submit_wellness(RoleLabel.ATHLETE, actor_id, actor_id)

    def test_athlete_submits_for_other_denied(self):
        actor_id = uuid.uuid4()
        other_id = uuid.uuid4()
        with pytest.raises(InsufficientPrivilege, match="BOPLA"):
            assert_can_submit_wellness(RoleLabel.ATHLETE, actor_id, other_id)

    def test_coach_submits_for_any_athlete(self):
        assert_can_submit_wellness(RoleLabel.COACH, uuid.uuid4(), uuid.uuid4())

    def test_admin_submits_for_any_athlete(self):
        assert_can_submit_wellness(RoleLabel.ADMIN, uuid.uuid4(), uuid.uuid4())


# ---------------------------------------------------------------------------
# Delete session RBAC
# ---------------------------------------------------------------------------

class TestDeleteSessionRBAC:
    def test_admin_can_delete(self):
        assert_can_delete_session(RoleLabel.ADMIN)

    def test_coordinator_can_delete(self):
        assert_can_delete_session(RoleLabel.COORDINATOR)

    def test_coach_cannot_delete(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_delete_session(RoleLabel.COACH)

    def test_athlete_cannot_delete(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_delete_session(RoleLabel.ATHLETE)
