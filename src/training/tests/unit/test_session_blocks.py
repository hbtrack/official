"""
TM-061, TM-120 — SessionBlock invariants.
Fonte: INVARIANTS_TRAINING.md (TRAIN-DEC-047), session_block.schema.json.
"""
import uuid

import pytest

from .conftest import make_block


class TestSessionBlockInvariants:
    """TRAIN-DEC-047: exerciseVersionId obrigatório quando exerciseId presente."""

    def test_valid_block_passes(self):
        b = make_block()
        b.validate_invariants()

    def test_exercise_id_without_version_raises(self):
        b = make_block(exercise_id=uuid.uuid4(), exercise_version_id=None)
        with pytest.raises(ValueError, match="TRAIN-DEC-047"):
            b.validate_invariants()

    def test_exercise_id_with_version_passes(self):
        b = make_block(exercise_id=uuid.uuid4(), exercise_version_id=uuid.uuid4())
        b.validate_invariants()

    def test_duration_min_1_passes(self):
        b = make_block(duration_minutes=1)
        b.validate_invariants()

    def test_duration_0_raises(self):
        b = make_block(duration_minutes=0)
        with pytest.raises(ValueError):
            b.validate_invariants()

    def test_duration_240_passes(self):
        b = make_block(duration_minutes=240)
        b.validate_invariants()

    def test_duration_241_raises(self):
        b = make_block(duration_minutes=241)
        with pytest.raises(ValueError):
            b.validate_invariants()

    def test_block_objective_too_short_raises(self):
        b = make_block(block_objective="ab")
        with pytest.raises(ValueError):
            b.validate_invariants()

    def test_block_objective_min_3_passes(self):
        b = make_block(block_objective="abc")
        b.validate_invariants()

    def test_negative_order_index_raises(self):
        b = make_block(order_index=-1)
        with pytest.raises(ValueError):
            b.validate_invariants()

    def test_notes_exceeds_1000_raises(self):
        b = make_block(notes="a" * 1001)
        with pytest.raises(ValueError):
            b.validate_invariants()

    def test_block_objective_300_passes(self):
        b = make_block(block_objective="a" * 300)
        b.validate_invariants()

    def test_block_objective_301_raises(self):
        b = make_block(block_objective="a" * 301)
        with pytest.raises(ValueError):
            b.validate_invariants()
