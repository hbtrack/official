"""
Shared fixtures and helpers — training unit tests.
Derivado de TEST_MATRIX_TRAINING.md + INVARIANTS_TRAINING.md.
"""
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from training.domain.entities.blocks import SessionBlock
from training.domain.entities.sessions import TrainingSession
from training.domain.common.enums import SessionBlockIntensity, SessionBlockPhase, TrainingSessionStatus


def make_session(**kwargs) -> TrainingSession:
    """Factory de TrainingSession com defaults válidos."""
    defaults = dict(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        session_at=datetime.now(tz=timezone.utc) + timedelta(hours=4),
        session_type="TACTICAL",
        status=TrainingSessionStatus.DRAFT,
        created_by_user_id=uuid.uuid4(),
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )
    defaults.update(kwargs)
    return TrainingSession(**defaults)


def make_block(**kwargs) -> SessionBlock:
    """Factory de SessionBlock com defaults válidos."""
    defaults = dict(
        id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        phase=SessionBlockPhase.TACTICAL,
        order_index=0,
        duration_minutes=20,
        block_objective="Treinar transição ofensiva",
        intensity=SessionBlockIntensity.HIGH,
        is_optional=False,
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )
    defaults.update(kwargs)
    return SessionBlock(**defaults)
