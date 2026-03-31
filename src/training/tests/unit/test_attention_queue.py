"""
TM-040, TM-052, TM-053, TM-113 — AttentionQueueItem invariants.
Fonte: DOMAIN_RULES_TRAINING.md, INVARIANTS_TRAINING.md.
"""
import uuid
from datetime import datetime, timezone

import pytest

from training.domain.entities import AttentionQueueItem


def _make_attention_item(**kwargs):
    defaults = dict(
        id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        athlete_id=uuid.uuid4(),
        reason="WELLNESS_ANOMALY",
        severity="HIGH",
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )
    defaults.update(kwargs)
    return AttentionQueueItem(**defaults)


class TestAttentionQueueItemCreation:
    """TM-040: criação básica de AttentionQueueItem."""

    def test_valid_item_creates(self):
        item = _make_attention_item()
        assert item.reason == "WELLNESS_ANOMALY"
        assert item.severity == "HIGH"
        assert item.resolved_at is None

    def test_item_with_resolved_at(self):
        item = _make_attention_item(resolved_at=datetime.now(tz=timezone.utc))
        assert item.resolved_at is not None

    def test_item_with_dismissed_at(self):
        item = _make_attention_item(dismissed_at=datetime.now(tz=timezone.utc))
        assert item.dismissed_at is not None


class TestAttentionQueueItemFields:
    """TM-052, TM-053, TM-113: campos e estados do item de atenção."""

    def test_item_has_required_fields(self):
        item = _make_attention_item()
        assert item.session_id is not None
        assert item.athlete_id is not None
        assert item.reason is not None
        assert item.severity is not None

    @pytest.mark.skip(reason="target-state: AttentionQueueItem.validate_invariants() not yet implemented")
    def test_invalid_severity_raises(self):
        pass

    @pytest.mark.skip(reason="target-state: escalation rules not yet in domain layer")
    def test_escalation_requires_reason(self):
        pass
