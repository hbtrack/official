"""
TM-010..TM-016, TM-021..TM-023, TM-041, TM-050, TM-051, TM-062 — Regras de domínio.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-001..DR-TRAIN-030).
"""
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import pytest

from training.domain.common.enums import IndividualizationMode, TrainingSessionStatus
from training.domain.entities.planning import Mesocycle, Microcycle
from training.domain.entities.wellness import WellnessPost
from training.domain.rules import (
    InsufficientPrivilege,
    RoleLabel,
    assert_can_create_session,
    assert_can_delete_session,
    assert_can_modify_session,
    assert_can_read_session,
    assert_can_submit_wellness,
)
from .conftest import make_session


# ---------------------------------------------------------------------------
# DR-TRAIN-001: RBAC para criação de sessão (TM-010)
# ---------------------------------------------------------------------------

class TestCreateSessionRBAC:
    """DR-TRAIN-001: sessões só podem ser criadas por coach/coordinator/admin."""

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
# BOLA: leitura de sessão (TM-010 adj)
# ---------------------------------------------------------------------------

class TestReadSessionBOLA:
    """BOLA — OWASP API1:2023. Athlete só acessa sessão onde está incluído."""

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
# BOPLA: wellness submission (TM-adj)
# ---------------------------------------------------------------------------

class TestWellnessBOPLA:
    """BOPLA — OWASP API3:2023. Athlete submete apenas o próprio wellness."""

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
# Delete session RBAC (PERMISSIONS_TRAINING.md)
# ---------------------------------------------------------------------------

class TestDeleteSessionRBAC:
    """Apenas admin/coordinator podem excluir sessões."""

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


# ---------------------------------------------------------------------------
# DR-TRAIN-030: individualizationMode enum fechado (TM-062)
# ---------------------------------------------------------------------------

class TestIndividualizationMode:
    """DR-TRAIN-030: individualizationMode deve ser um dos 3 valores canônicos."""

    def test_valid_modes(self):
        for mode in IndividualizationMode:
            assert mode.value in (
                "COLLECTIVE_UNIFORM",
                "COLLECTIVE_WITH_VARIANTS",
                "INDIVIDUAL_ONLY",
            )

    def test_enum_has_exactly_3_values(self):
        assert len(IndividualizationMode) == 3


# ---------------------------------------------------------------------------
# Mesocycle / Microcycle invariants (DR-TRAIN-H04: periodização)
# ---------------------------------------------------------------------------

class TestMesocycleInvariants:
    """Mesociclo: validação de nome e datas."""

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


class TestMicrocycleInvariants:
    """Microciclo: validação de weekNumber e datas."""

    def test_valid_microcycle_passes(self):
        m = Microcycle(
            id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            mesocycle_id=uuid.uuid4(),
            week_number=1,
            started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ended_at=datetime(2026, 1, 7, tzinfo=timezone.utc),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        m.validate_invariants()

    def test_week_number_zero_raises(self):
        m = Microcycle(
            id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            mesocycle_id=uuid.uuid4(),
            week_number=0,
            started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ended_at=datetime(2026, 1, 7, tzinfo=timezone.utc),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        with pytest.raises(ValueError):
            m.validate_invariants()

    def test_start_after_end_raises(self):
        m = Microcycle(
            id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            mesocycle_id=uuid.uuid4(),
            week_number=1,
            started_at=datetime(2026, 1, 7, tzinfo=timezone.utc),
            ended_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        with pytest.raises(ValueError):
            m.validate_invariants()


# ---------------------------------------------------------------------------
# WellnessPost entity invariants (DR-adj)
# ---------------------------------------------------------------------------

class TestWellnessPostInvariants:
    """WellnessPost: validação de RPE 1-10."""

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
