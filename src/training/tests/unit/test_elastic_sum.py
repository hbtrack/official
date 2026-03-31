"""
TM-119 — Elastic Sum Rule.
Fonte: INVARIANTS_TRAINING.md (INV-TRAIN-083).
"""
import pytest

from training.domain.rules import (
    ElasticSumRuleViolation,
    assert_elastic_sum_rule,
)


class TestElasticSumRule:
    """INV-TRAIN-083: SUM(durationMinutes) ≤ durationPlannedMinutes + tolerance."""

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

    def test_tolerance_capped_at_10(self):
        # planned=200 → tolerance=min(20, 10)=10 → limit=210
        assert_elastic_sum_rule(
            duration_planned_minutes=200,
            blocks_total_minutes=200,
            new_block_minutes=10,
        )
        with pytest.raises(ElasticSumRuleViolation):
            assert_elastic_sum_rule(
                duration_planned_minutes=200,
                blocks_total_minutes=200,
                new_block_minutes=11,
            )
