"""Testes unitários — módulo medical."""
import uuid
from datetime import date

import pytest

from medical.domain.entities import MedicalRecord
from medical.domain.rules import (
    RoleLabel,
    InsufficientPrivilege,
    assert_can_create_record,
    assert_can_read_record,
    assert_can_update_record,
    assert_can_delete_record,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_record(**kwargs) -> MedicalRecord:
    defaults = dict(
        id=uuid.uuid4(),
        athlete_user_id=uuid.uuid4(),
        record_date=date(2026, 3, 1),
        record_label="Avaliação mensal",
    )
    defaults.update(kwargs)
    return MedicalRecord(**defaults)


# ---------------------------------------------------------------------------
# INV-MED-001: campos obrigatórios
# ---------------------------------------------------------------------------

class TestInvariantRequiredFields:
    def test_valid_record_passes(self):
        make_record().validate_invariants()

    def test_empty_record_label_raises(self):
        with pytest.raises(ValueError, match="record_label"):
            make_record(record_label="").validate_invariants()

    def test_record_label_too_long_raises(self):
        with pytest.raises(ValueError):
            make_record(record_label="x" * 121).validate_invariants()

    def test_record_label_exactly_120_passes(self):
        make_record(record_label="x" * 120).validate_invariants()


# ---------------------------------------------------------------------------
# INV-MED-002: returnToPlay=True implica returnToTraining=True
# ---------------------------------------------------------------------------

class TestInvariantReturnToPlay:
    def test_play_without_training_raises(self):
        with pytest.raises(ValueError, match="INV-MED-002"):
            make_record(
                return_to_play_authorized=True,
                return_to_training_authorized=False,
            ).validate_invariants()

    def test_play_without_training_none_raises(self):
        with pytest.raises(ValueError, match="INV-MED-002"):
            make_record(
                return_to_play_authorized=True,
                return_to_training_authorized=None,
            ).validate_invariants()

    def test_both_true_passes(self):
        make_record(
            return_to_play_authorized=True,
            return_to_training_authorized=True,
        ).validate_invariants()

    def test_training_true_play_false_passes(self):
        make_record(
            return_to_play_authorized=False,
            return_to_training_authorized=True,
        ).validate_invariants()

    def test_both_none_passes(self):
        make_record(
            return_to_play_authorized=None,
            return_to_training_authorized=None,
        ).validate_invariants()


# ---------------------------------------------------------------------------
# Limites de texto
# ---------------------------------------------------------------------------

class TestTextLimits:
    def test_assessment_summary_max_1000(self):
        with pytest.raises(ValueError):
            make_record(assessment_summary="a" * 1001).validate_invariants()

    def test_restriction_summary_max_1000(self):
        with pytest.raises(ValueError):
            make_record(restriction_summary="r" * 1001).validate_invariants()

    def test_clinical_notes_max_2000(self):
        with pytest.raises(ValueError):
            make_record(clinical_notes="n" * 2001).validate_invariants()

    def test_clinical_notes_2000_passes(self):
        make_record(clinical_notes="n" * 2000).validate_invariants()


# ---------------------------------------------------------------------------
# RBAC — createMedicalRecord
# ---------------------------------------------------------------------------

class TestCreateRBAC:
    def test_admin_can_create(self):
        assert_can_create_record(RoleLabel.ADMIN)

    def test_coordinator_can_create(self):
        assert_can_create_record(RoleLabel.COORDINATOR)

    def test_coach_can_create(self):
        assert_can_create_record(RoleLabel.COACH)

    def test_athlete_cannot_create(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_record(RoleLabel.ATHLETE)

    def test_member_cannot_create(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_record(RoleLabel.MEMBER)


# ---------------------------------------------------------------------------
# RBAC — getMedicalRecord / listMedicalRecords  (BOLA/PERM-MED-001)
# ---------------------------------------------------------------------------

class TestReadRBAC:
    def test_admin_reads_any(self):
        assert_can_read_record(RoleLabel.ADMIN, uuid.uuid4(), uuid.uuid4(), [])

    def test_coordinator_reads_any(self):
        assert_can_read_record(RoleLabel.COORDINATOR, uuid.uuid4(), uuid.uuid4(), [])

    def test_athlete_reads_own(self):
        uid = uuid.uuid4()
        assert_can_read_record(RoleLabel.ATHLETE, uid, uid, [])

    def test_athlete_cannot_read_other(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_record(RoleLabel.ATHLETE, uuid.uuid4(), uuid.uuid4(), [])

    def test_coach_reads_athlete_in_team(self):
        athlete_id = uuid.uuid4()
        assert_can_read_record(RoleLabel.COACH, uuid.uuid4(), athlete_id, [athlete_id])

    def test_coach_cannot_read_athlete_outside_team(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_record(RoleLabel.COACH, uuid.uuid4(), uuid.uuid4(), [])

    def test_member_denied(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_record(RoleLabel.MEMBER, uuid.uuid4(), uuid.uuid4(), [])


# ---------------------------------------------------------------------------
# RBAC — updateMedicalRecord
# ---------------------------------------------------------------------------

class TestUpdateRBAC:
    def test_admin_can_update(self):
        assert_can_update_record(RoleLabel.ADMIN)

    def test_coach_can_update(self):
        assert_can_update_record(RoleLabel.COACH)

    def test_athlete_cannot_update(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_update_record(RoleLabel.ATHLETE)

    def test_member_cannot_update(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_update_record(RoleLabel.MEMBER)


# ---------------------------------------------------------------------------
# RBAC — deleteMedicalRecord (somente admin — PERM-MED-003 / LGPD)
# ---------------------------------------------------------------------------

class TestDeleteRBAC:
    def test_admin_can_delete(self):
        assert_can_delete_record(RoleLabel.ADMIN)

    def test_coordinator_cannot_delete(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_delete_record(RoleLabel.COORDINATOR)

    def test_coach_cannot_delete(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_delete_record(RoleLabel.COACH)

    def test_athlete_cannot_delete(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_delete_record(RoleLabel.ATHLETE)
