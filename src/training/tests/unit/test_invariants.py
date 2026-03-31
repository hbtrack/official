"""
TM-100, TM-112 — Invariantes gerais de TrainingSession.
Fonte: INVARIANTS_TRAINING.md (INV-TRAIN-001, INV-TRAIN-008).
"""
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from .conftest import make_session


# ---------------------------------------------------------------------------
# INV-TRAIN-001: Focus percentages (TM-100)
# ---------------------------------------------------------------------------

class TestFocusPercentagesInvariant:
    """INV-TRAIN-001: soma focus_*_pct ≤ 120 após arredondamento RC-2."""

    def test_valid_focus_sum_passes(self):
        s = make_session(
            focus_attack_positional_pct=Decimal("30"),
            focus_defense_positional_pct=Decimal("30"),
            focus_physical_pct=Decimal("30"),
        )
        s.validate_invariants()  # 90 ≤ 120

    def test_sum_at_boundary_120_passes(self):
        s = make_session(
            focus_attack_positional_pct=Decimal("40"),
            focus_defense_positional_pct=Decimal("40"),
            focus_physical_pct=Decimal("40"),
        )
        s.validate_invariants()

    def test_sum_exceeds_120_raises(self):
        s = make_session(
            focus_attack_positional_pct=Decimal("33.34"),
            focus_defense_positional_pct=Decimal("33.34"),
            focus_transition_offense_pct=Decimal("33.34"),
            focus_transition_defense_pct=Decimal("33.34"),
        )
        with pytest.raises(ValueError, match="INV-TRAIN-001"):
            s.validate_invariants()

    def test_individual_field_above_100_raises(self):
        s = make_session(focus_attack_positional_pct=Decimal("101"))
        with pytest.raises(ValueError, match="INV-TRAIN-001"):
            s.validate_invariants()

    def test_individual_field_below_0_raises(self):
        s = make_session(focus_attack_positional_pct=Decimal("-1"))
        with pytest.raises(ValueError, match="INV-TRAIN-001"):
            s.validate_invariants()

    def test_boundary_33_33_x3_equals_100_passes(self):
        """Caso de borda RC-2: 33.33 + 33.33 + 33.34 = 100.00 ✅."""
        s = make_session(
            focus_attack_positional_pct=Decimal("33.33"),
            focus_defense_positional_pct=Decimal("33.33"),
            focus_physical_pct=Decimal("33.34"),
        )
        s.validate_invariants()


# ---------------------------------------------------------------------------
# INV-TRAIN-008: soft delete consistency
# ---------------------------------------------------------------------------

class TestSoftDeleteInvariant:
    """INV-TRAIN-008: (deleted_at IS NULL AND deleted_reason IS NULL) OR ambos preenchidos."""

    def test_both_none_passes(self):
        s = make_session(deleted_at=None, deleted_reason=None)
        s.validate_invariants()

    def test_both_set_passes(self):
        s = make_session(
            deleted_at=datetime.now(tz=timezone.utc),
            deleted_reason="Por solicitação do coordenador",
        )
        s.validate_invariants()

    def test_deleted_at_without_reason_raises(self):
        s = make_session(
            deleted_at=datetime.now(tz=timezone.utc),
            deleted_reason=None,
        )
        with pytest.raises(ValueError, match="INV-TRAIN-008"):
            s.validate_invariants()

    def test_reason_without_deleted_at_raises(self):
        s = make_session(
            deleted_at=None,
            deleted_reason="Sem motivo oficial",
        )
        with pytest.raises(ValueError, match="INV-TRAIN-008"):
            s.validate_invariants()
