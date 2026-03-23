"""Testes unitários — módulo wellness."""
import uuid
from datetime import date
from decimal import Decimal

import pytest

from wellness.domain.entities import WellnessEntry, WellnessSummary
from wellness.domain.rules import (
    RoleLabel,
    WellnessEntryNotFound,
    InsufficientPrivilege,
    assert_can_create_entry,
    assert_can_read_entry,
    assert_can_read_athlete_wellness,
    check_high_pain_alert,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_entry(**kwargs) -> WellnessEntry:
    defaults = dict(
        id=uuid.uuid4(),
        athlete_user_id=uuid.uuid4(),
        training_session_id=None,
        questionnaire_date=date(2026, 3, 1),
        questionnaire_label="Pré-treino",
        readiness_score=8,
        fatigue_score=3,
        pain_score=2,
        recovery_score=7,
        sleep_hours=Decimal("7.5"),
        notes=None,
    )
    defaults.update(kwargs)
    return WellnessEntry(**defaults)


# ---------------------------------------------------------------------------
# INV-WELL-001: campos obrigatórios
# ---------------------------------------------------------------------------

class TestInvariantRequiredFields:
    def test_valid_entry_passes(self):
        entry = make_entry()
        entry.validate_invariants()  # não levanta

    def test_missing_questionnaire_date_raises(self):
        with pytest.raises(ValueError, match="questionnaire_date"):
            make_entry(questionnaire_date=None).validate_invariants()


# ---------------------------------------------------------------------------
# INV-WELL-002: scores ∈ [0..10]
# ---------------------------------------------------------------------------

class TestInvariantScoreRange:
    @pytest.mark.parametrize("field", [
        "readiness_score", "fatigue_score", "pain_score", "recovery_score"
    ])
    def test_score_below_zero_raises(self, field):
        with pytest.raises(ValueError):
            make_entry(**{field: -1}).validate_invariants()

    @pytest.mark.parametrize("field", [
        "readiness_score", "fatigue_score", "pain_score", "recovery_score"
    ])
    def test_score_above_ten_raises(self, field):
        with pytest.raises(ValueError):
            make_entry(**{field: 11}).validate_invariants()

    @pytest.mark.parametrize("field,value", [
        ("readiness_score", 0), ("pain_score", 10), ("recovery_score", 5),
    ])
    def test_boundary_values_pass(self, field, value):
        make_entry(**{field: value}).validate_invariants()


# ---------------------------------------------------------------------------
# INV-WELL-003: sleep_hours ∈ [0..24]
# ---------------------------------------------------------------------------

class TestInvariantSleepHours:
    def test_negative_sleep_raises(self):
        with pytest.raises(ValueError, match="sleep_hours"):
            make_entry(sleep_hours=Decimal("-1")).validate_invariants()

    def test_above_24_raises(self):
        with pytest.raises(ValueError, match="sleep_hours"):
            make_entry(sleep_hours=Decimal("24.1")).validate_invariants()

    def test_zero_passes(self):
        make_entry(sleep_hours=Decimal("0")).validate_invariants()

    def test_24_passes(self):
        make_entry(sleep_hours=Decimal("24")).validate_invariants()


# ---------------------------------------------------------------------------
# INV-WELL-004: nenhum campo clínico
# ---------------------------------------------------------------------------

class TestInvariantNoClinicalFields:
    @pytest.mark.parametrize("field", [
        "diagnosis", "treatment", "prescription",
        "procedure", "medical_record", "clinical_note",
    ])
    def test_clinical_field_rejected(self, field):
        entry = make_entry()
        with pytest.raises(ValueError, match="clínico|clinical|forbidden"):
            entry.validate_no_clinical_field(field)


# ---------------------------------------------------------------------------
# DR-WELL-005: limites de texto
# ---------------------------------------------------------------------------

class TestTextLimits:
    def test_questionnaire_label_max_80(self):
        with pytest.raises(ValueError):
            make_entry(questionnaire_label="x" * 81).validate_invariants()

    def test_notes_max_500(self):
        with pytest.raises(ValueError):
            make_entry(notes="n" * 501).validate_invariants()

    def test_questionnaire_label_exactly_80_passes(self):
        make_entry(questionnaire_label="x" * 80).validate_invariants()

    def test_notes_exactly_500_passes(self):
        make_entry(notes="n" * 500).validate_invariants()


# ---------------------------------------------------------------------------
# PERM-WEL-004: alerta de dor alta
# ---------------------------------------------------------------------------

class TestHighPainAlert:
    @pytest.mark.parametrize("score,expected", [
        (0, False), (6, False), (7, True), (8, True), (10, True),
    ])
    def test_alert_threshold(self, score, expected):
        assert check_high_pain_alert(score) is expected


# ---------------------------------------------------------------------------
# RBAC — create
# ---------------------------------------------------------------------------

class TestCreateEntryRBAC:
    def test_athlete_creates_own_entry(self):
        uid = uuid.uuid4()
        assert_can_create_entry(RoleLabel.ATHLETE, uid, uid)  # não levanta

    def test_athlete_cannot_create_for_other(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_entry(RoleLabel.ATHLETE, uuid.uuid4(), uuid.uuid4())

    def test_member_denied(self):
        uid = uuid.uuid4()
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_entry(RoleLabel.MEMBER, uid, uid)

    def test_coach_can_create_for_any(self):
        assert_can_create_entry(RoleLabel.COACH, uuid.uuid4(), uuid.uuid4())

    def test_coordinator_can_create_for_any(self):
        assert_can_create_entry(RoleLabel.COORDINATOR, uuid.uuid4(), uuid.uuid4())


# ---------------------------------------------------------------------------
# RBAC — read entry (PERM-WEL-002 / PERM-WEL-003)
# ---------------------------------------------------------------------------

class TestReadEntryBOLA:
    def test_athlete_reads_own_entry(self):
        uid = uuid.uuid4()
        assert_can_read_entry(RoleLabel.ATHLETE, uid, uid, [])

    def test_athlete_cannot_read_other(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_entry(RoleLabel.ATHLETE, uuid.uuid4(), uuid.uuid4(), [])

    def test_coach_reads_entry_within_team(self):
        athlete_id = uuid.uuid4()
        assert_can_read_entry(RoleLabel.COACH, uuid.uuid4(), athlete_id, [athlete_id])

    def test_coordinator_reads_any(self):
        assert_can_read_entry(RoleLabel.COORDINATOR, uuid.uuid4(), uuid.uuid4(), [])

    def test_member_denied(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_entry(RoleLabel.MEMBER, uuid.uuid4(), uuid.uuid4(), [])


# ---------------------------------------------------------------------------
# RBAC — read athlete wellness (listAthleteWellnessEntries / summary)
# ---------------------------------------------------------------------------

class TestAthleteWellnessBOLA:
    def test_athlete_reads_own(self):
        uid = uuid.uuid4()
        assert_can_read_athlete_wellness(RoleLabel.ATHLETE, uid, uid, [])

    def test_athlete_cannot_read_other(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_athlete_wellness(RoleLabel.ATHLETE, uuid.uuid4(), uuid.uuid4(), [])

    def test_coach_allowed(self):
        athlete_id = uuid.uuid4()
        assert_can_read_athlete_wellness(RoleLabel.COACH, uuid.uuid4(), athlete_id, [athlete_id])

    def test_admin_allowed(self):
        assert_can_read_athlete_wellness(RoleLabel.ADMIN, uuid.uuid4(), uuid.uuid4(), [])

    def test_member_denied(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_athlete_wellness(RoleLabel.MEMBER, uuid.uuid4(), uuid.uuid4(), [])
