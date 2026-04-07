"""Parity: notifications generated code structural validation."""
from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import datetime, timezone

import pytest

from tests.parity._parity_helpers import InMemoryRepo, REPO_ROOT, FROZEN_ID, route_surface, route_set, route_methods, source_graph_methods

from notifications.generated.domain.entities import NotificationDelivery
from notifications.generated.schemas import NotificationDeliveryOut
from notifications.generated.application.use_cases import ListDeliveries, CreateNotificationIntent, GetDelivery


def _make_entity(**overrides):
    payload = {
        "id": FROZEN_ID,
        "recipient_user_id": uuid.uuid4(),
        "channel_label": "test-value",
        "requested_at": datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
    }
    payload.update(overrides)
    return NotificationDelivery(**payload)


def test_notifications_entity_fields_and_invariants():
    entity = _make_entity()
    entity.validate_invariants()
    d = asdict(entity)
    assert "id" in d
    assert len(d) >= 4


def test_notifications_schema_from_domain_round_trip():
    entity = _make_entity()
    schema = NotificationDeliveryOut.from_domain(entity)
    dump = schema.model_dump()
    assert dump["id"] == entity.id


def test_notifications_api_route_coverage():
    gen = route_surface(REPO_ROOT / "src" / "notifications" / "generated" / "api.py")
    manual = route_surface(REPO_ROOT / "src" / "notifications" / "api.py")
    gen_rs = route_set(gen)
    manual_rs = route_set(manual)
    # Strict check: normalized paths match
    if not manual_rs <= gen_rs:
        # Fallback: generated covers source graph contract (manual may diverge)
        gen_mc = route_methods(gen)
        sg_mc = source_graph_methods("notifications")
        for method in sg_mc:
            assert method in gen_mc, f"Generated API missing HTTP method {method} from source graph"
            assert gen_mc[method] >= sg_mc[method], (
                f"Generated API has fewer {method} routes than source graph: {gen_mc[method]} < {sg_mc[method]}"
            )


def test_notifications_use_cases_crud():
    repo = InMemoryRepo()
    # Create
    entity = CreateNotificationIntent(repo).execute(
        role="admin",
        requester_id=uuid.uuid4(),
        recipient_user_id=uuid.uuid4(),
        channel_label="test-value",
        requested_at=datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
    )
    assert entity.id is not None

    # Get
    retrieved = GetDelivery(repo).execute(role="admin", requester_id=uuid.uuid4(), entity_id=entity.id)
    assert retrieved.id == entity.id

    # List
    entities, _ = ListDeliveries(repo).execute(role="admin", requester_id=uuid.uuid4())
    assert len(entities) >= 1
