"""
Adversarial / fuzz inputs — training domain.
Fonte: TEST_MATRIX_TRAINING.md (adversarial_inputs).
Testa resiliência do domain layer a inputs maliciosos.
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from .conftest import make_session, make_block


class TestAdversarialFocusValues:
    """Inputs adversariais nos campos focus_*_pct."""

    def test_extremely_large_focus_raises(self):
        s = make_session(focus_attack_positional_pct=Decimal("999999"))
        with pytest.raises(ValueError, match="INV-TRAIN-001"):
            s.validate_invariants()

    def test_negative_focus_raises(self):
        s = make_session(focus_physical_pct=Decimal("-50"))
        with pytest.raises(ValueError, match="INV-TRAIN-001"):
            s.validate_invariants()

    def test_very_small_decimal_passes(self):
        s = make_session(focus_attack_positional_pct=Decimal("0.01"))
        s.validate_invariants()


class TestAdversarialStringFields:
    """Inputs adversariais em campos texto."""

    def test_empty_block_objective_raises(self):
        b = make_block(block_objective="")
        with pytest.raises(ValueError):
            b.validate_invariants()

    def test_unicode_block_objective_passes(self):
        b = make_block(block_objective="Treino tático — 日本語テスト")
        b.validate_invariants()

    def test_max_length_location_boundary(self):
        s = make_session(location="a" * 120)
        s.validate_invariants()

    def test_over_max_location_raises(self):
        s = make_session(location="a" * 121)
        with pytest.raises(ValueError):
            s.validate_invariants()


class TestAdversarialDurationValues:
    """Inputs adversariais em campos numéricos de duração."""

    def test_negative_duration_raises(self):
        b = make_block(duration_minutes=-1)
        with pytest.raises(ValueError):
            b.validate_invariants()

    def test_zero_duration_raises(self):
        b = make_block(duration_minutes=0)
        with pytest.raises(ValueError):
            b.validate_invariants()

    def test_extreme_duration_raises(self):
        b = make_block(duration_minutes=99999)
        with pytest.raises(ValueError):
            b.validate_invariants()
