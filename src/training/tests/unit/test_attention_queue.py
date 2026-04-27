"""
TM-040, TM-052, TM-053, TM-113 — AttentionQueueItem invariants.
Fonte: DOMAIN_RULES_TRAINING.md, INVARIANTS_TRAINING.md.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from training.api.mappers import _attention_queue_item_to_out
from training.application.communication.commands import EscalateAttentionQueueItemUseCase
from training.application.communication.dto import EscalateAttentionQueueItemInput
from training.domain.entities.communication import AttentionQueueItem
from training.domain.rules import RoleLabel

from .conftest import make_session


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

    def test_mapper_projects_reason_and_target_fields_to_http_contract(self):
        item = _make_attention_item(reason="WELLNESS_ALERT", notes=None)
        out = _attention_queue_item_to_out(item).model_dump()
        assert out["reason_code"] == "WELLNESS_ALERT"
        assert out["target_entity_type"] == "athlete"
        assert out["target_entity_id"] == item.athlete_id
        assert out["message"] == "WELLNESS_ALERT"

    def test_escalation_rejects_unknown_target_before_repo_lookup(self):
        session_repo = MagicMock()
        session_repo.get_by_id.return_value = make_session()
        queue_repo = MagicMock()

        use_case = EscalateAttentionQueueItemUseCase(session_repo, queue_repo)
        with pytest.raises(ValueError, match="escalationTarget inválido"):
            use_case.execute(
                EscalateAttentionQueueItemInput(
                    session_id=uuid.uuid4(),
                    item_id=uuid.uuid4(),
                    actor_role=RoleLabel.COACH,
                    actor_id=uuid.uuid4(),
                    escalation_target="INVALID",
                    escalation_note="Escalada de teste",
                )
            )
        queue_repo.get_by_id.assert_not_called()
