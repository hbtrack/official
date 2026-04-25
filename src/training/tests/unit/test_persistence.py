"""
TM-042, TM-043, TM-060 — Persistence rules.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-029, DR-TRAIN-030, DR-TRAIN-031).
target-state: regras de persistência são enforced na camada de infraestrutura.
"""
import pytest

from .conftest import make_session
from training.domain.common.enums import TrainingSessionStatus


class TestPersistenceSoftDelete:
    """DR-TRAIN-029: soft delete não remove registro físico."""

    def test_session_has_soft_delete_fields(self):
        s = make_session()
        assert hasattr(s, "deleted_at")
        assert hasattr(s, "deleted_reason")
        assert s.deleted_at is None

    def test_session_status_field_exists(self):
        s = make_session(status=TrainingSessionStatus.DRAFT)
        assert s.status == TrainingSessionStatus.DRAFT


class TestIndividualizationModeField:
    """DR-TRAIN-030: individualizationMode obrigatório no contrato."""

    def test_field_exists_on_session(self):
        s = make_session()
        assert hasattr(s, "individualization_mode")

    def test_field_accepts_valid_value(self):
        s = make_session(individualization_mode="COLLECTIVE_UNIFORM")
        assert s.individualization_mode == "COLLECTIVE_UNIFORM"


class TestAppendOnlyExecutionRecords:
    """DR-TRAIN-031: ExecutionRecords são append-only — sem update/delete."""

    @pytest.mark.skip(reason="target-state: append-only enforcement is at repository/DB layer")
    def test_execution_record_cannot_be_updated(self):
        pass

    @pytest.mark.skip(reason="target-state: append-only enforcement is at repository/DB layer")
    def test_execution_record_cannot_be_deleted(self):
        pass
