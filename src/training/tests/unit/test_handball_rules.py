"""
TM-017..TM-020 — Handball-specific domain rules.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-H01..DR-TRAIN-H04).
"""
import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from training.domain.common.enums import SessionBlockPhase
from training.domain.entities.planning import Mesocycle, Microcycle

_REPO_ROOT = Path(__file__).resolve().parents[4]


def _load_schema(name: str) -> dict:
    path = _REPO_ROOT / "contracts/schemas/training" / name
    return json.loads(path.read_text(encoding="utf-8"))


class TestMesocycleRules:
    """DR-TRAIN-H04: regras de periodização — Mesocycle."""

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


class TestMicrocycleRules:
    """DR-TRAIN-H04: regras de periodização — Microcycle."""

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

    def test_week_number_0_raises(self):
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

    def test_handball_position_context_is_supported_in_training_contracts(self):
        schema = _load_schema("athlete_chat_conversation.schema.json")
        athlete_position = schema["properties"]["athletePosition"]
        assert athlete_position["type"] == "string"
        assert athlete_position["maxLength"] == 32

    def test_handball_phase_structure_is_supported_by_session_and_block_contracts(self):
        session_schema = _load_schema("training_session.schema.json")
        block_schema = _load_schema("session_block.schema.json")
        assert "phaseFocusAttack" in session_schema["properties"]
        assert "phaseFocusDefense" in session_schema["properties"]
        assert "phaseFocusTransitionOffense" in session_schema["properties"]
        assert "phaseFocusTransitionDefense" in session_schema["properties"]
        phase_enum = block_schema["properties"]["phase"]["enum"]
        assert {
            SessionBlockPhase.TECHNICAL.value,
            SessionBlockPhase.TACTICAL.value,
            SessionBlockPhase.DECISION_MAKING.value,
            SessionBlockPhase.REDUCED_GAME.value,
        } <= set(phase_enum)
        assert set(phase_enum) == {phase.value for phase in SessionBlockPhase}

    def test_age_group_support_is_present_in_training_contracts(self):
        schema = _load_schema("athlete_chat_conversation.schema.json")
        assert schema["properties"]["athleteAgeGroup"]["enum"] == [
            "U10",
            "U12",
            "U14",
            "U16",
            "U18",
            "ADULT",
        ]
