"""
TM-048, TM-049 — Dados sensíveis.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-039, DR-TRAIN-040).
target-state: regras de dados sensíveis não implementadas em domain layer.
"""
import uuid
from datetime import datetime, timezone

import pytest

from training.domain.entities.wellness import WellnessPre


class TestWellnessPreFieldConstraints:
    """Validação de campos sensíveis em WellnessPre (ranges [1..5])."""

    def _make_wellness_pre(self, **kwargs):
        defaults = dict(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            athlete_id=uuid.uuid4(),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        defaults.update(kwargs)
        return WellnessPre(**defaults)

    @pytest.mark.parametrize("field_name,field_key", [
        ("readiness", "readiness"),
        ("sleep_quality", "sleep_quality"),
        ("mood", "mood"),
        ("fatigue", "fatigue"),
        ("muscle_soreness", "muscle_soreness"),
    ])
    def test_field_in_range_passes(self, field_name, field_key):
        w = self._make_wellness_pre(**{field_key: 3})
        w.validate_invariants()

    @pytest.mark.parametrize("field_name,field_key", [
        ("readiness", "readiness"),
        ("sleep_quality", "sleep_quality"),
        ("mood", "mood"),
        ("fatigue", "fatigue"),
        ("muscle_soreness", "muscle_soreness"),
    ])
    def test_field_above_5_raises(self, field_name, field_key):
        w = self._make_wellness_pre(**{field_key: 6})
        with pytest.raises(ValueError):
            w.validate_invariants()

    @pytest.mark.parametrize("field_name,field_key", [
        ("readiness", "readiness"),
        ("sleep_quality", "sleep_quality"),
        ("mood", "mood"),
        ("fatigue", "fatigue"),
        ("muscle_soreness", "muscle_soreness"),
    ])
    def test_field_below_1_raises(self, field_name, field_key):
        w = self._make_wellness_pre(**{field_key: 0})
        with pytest.raises(ValueError):
            w.validate_invariants()


class TestSensitiveDataFiltering:
    """DR-TRAIN-039/040: dados sensíveis não devem ser expostos em responses."""

    @pytest.mark.skip(reason="target-state: sensitive data filtering rules not yet in domain layer")
    def test_wellness_data_filtered_for_non_staff(self):
        pass

    @pytest.mark.skip(reason="target-state: sensitive data filtering rules not yet in domain layer")
    def test_personal_notes_excluded_from_aggregations(self):
        pass
