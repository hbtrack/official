"""
TM-024..TM-026 — SessionObjective invariants.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-011, DR-TRAIN-012, DR-TRAIN-013).
"""
import uuid
from datetime import datetime, timezone

import pytest

from training.domain.entities import (
    SessionObjective,
    SessionObjectiveOrigin,
)


class TestSessionObjectiveInvariants:
    """DR-TRAIN-013: MANUAL_COACH_RATIONALE exige originNotes >= 10 chars."""

    def test_manual_rationale_requires_origin_notes(self):
        obj = SessionObjective(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            origin=SessionObjectiveOrigin.MANUAL_COACH_RATIONALE,
            objective_type="TACTICAL",
            description="Melhora da transição",
            origin_notes=None,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        with pytest.raises(ValueError, match="DR-TRAIN-013"):
            obj.validate_invariants()

    def test_manual_rationale_with_notes_passes(self):
        obj = SessionObjective(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            origin=SessionObjectiveOrigin.MANUAL_COACH_RATIONALE,
            objective_type="TACTICAL",
            description="Melhora da transição",
            origin_notes="Treinador identificou problema tático na última partida",
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        obj.validate_invariants()

    def test_other_origins_no_notes_required(self):
        obj = SessionObjective(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            origin=SessionObjectiveOrigin.COMPETITIVE_FOCUS,
            objective_type="TACTICAL",
            description="Preparação para jogo",
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        obj.validate_invariants()

    def test_manual_rationale_short_notes_raises(self):
        obj = SessionObjective(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            origin=SessionObjectiveOrigin.MANUAL_COACH_RATIONALE,
            objective_type="TACTICAL",
            description="Melhora da transição",
            origin_notes="curta",
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        with pytest.raises(ValueError, match="DR-TRAIN-013"):
            obj.validate_invariants()
