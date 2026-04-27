"""
TM-048, TM-049 — Dados sensíveis.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-039, DR-TRAIN-040).
target-state: regras de dados sensíveis não implementadas em domain layer.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from training.api.mappers import _wellness_pre_to_out
from training.application.wellness.dto import GetWellnessPreInput
from training.application.wellness.queries import GetWellnessPreUseCase
from training.domain.entities.wellness import WellnessPre
from training.domain.rules import InsufficientPrivilege, RoleLabel

from .conftest import make_session


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

    def test_wellness_response_excludes_soft_delete_fields(self):
        entity = WellnessPre(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            athlete_id=uuid.uuid4(),
            readiness=4,
            notes="sensível",
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
            deleted_at=datetime.now(tz=timezone.utc),
            deleted_reason="soft delete interno",
        )
        payload = _wellness_pre_to_out(entity).model_dump(by_alias=True)
        assert "trainingSessionId" in payload
        assert "deletedAt" not in payload
        assert "deletedReason" not in payload

    def test_athlete_cannot_read_other_athlete_wellness_record(self):
        actor_id = uuid.uuid4()
        session_repo = MagicMock()
        session_repo.get_by_id.return_value = make_session()
        wellness_repo = MagicMock()
        use_case = GetWellnessPreUseCase(session_repo, wellness_repo)

        with pytest.raises(InsufficientPrivilege, match="próprio registro"):
            use_case.execute(
                GetWellnessPreInput(
                    session_id=uuid.uuid4(),
                    actor_role=RoleLabel.ATHLETE,
                    actor_id=actor_id,
                    athlete_id=uuid.uuid4(),
                )
            )
        wellness_repo.get_active.assert_not_called()
