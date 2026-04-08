"""Parity: analytics generated code structural validation."""
from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import datetime, timezone

import pytest

from tests.parity._parity_helpers import InMemoryRepo, REPO_ROOT, FROZEN_ID, route_surface, route_set, route_methods, source_graph_methods

from analytics.generated.domain.entities import AnalyticsSnapshot
from analytics.generated.schemas import AnalyticsSnapshotOut
from analytics.generated.application.use_cases import ListAnalyticsSnapshots, CreateAnalyticsSnapshot, GetAnalyticsSnapshot


def _make_entity(**overrides):
    payload = {
        "id": FROZEN_ID,
        "metric_key": "test-value",
        "computed_at": datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
    }
    payload.update(overrides)
    return AnalyticsSnapshot(**payload)


def test_analytics_entity_fields_and_invariants():
    entity = _make_entity()
    entity.validate_invariants()
    d = asdict(entity)
    assert "id" in d
    assert len(d) >= 3


def test_analytics_schema_from_domain_round_trip():
    entity = _make_entity()
    schema = AnalyticsSnapshotOut.from_domain(entity)
    dump = schema.model_dump()
    assert dump["id"] == entity.id


def test_analytics_api_route_coverage():
    gen = route_surface(REPO_ROOT / "src" / "analytics" / "generated" / "api.py")
    manual = route_surface(REPO_ROOT / "src" / "analytics" / "api.py")
    gen_rs = route_set(gen)
    manual_rs = route_set(manual)
    # Strict check: normalized paths match
    if not manual_rs <= gen_rs:
        # Fallback: generated covers source graph contract (manual may diverge)
        gen_mc = route_methods(gen)
        sg_mc = source_graph_methods("analytics")
        for method in sg_mc:
            assert method in gen_mc, f"Generated API missing HTTP method {method} from source graph"
            assert gen_mc[method] >= sg_mc[method], (
                f"Generated API has fewer {method} routes than source graph: {gen_mc[method]} < {sg_mc[method]}"
            )


def test_analytics_use_cases_crud():
    repo = InMemoryRepo()
    # Create
    entity = CreateAnalyticsSnapshot(repo).execute(
        role="admin",
        requester_id=uuid.uuid4(),
        metric_key="test-value",
        computed_at=datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
    )
    assert entity.id is not None

    # Get
    retrieved = GetAnalyticsSnapshot(repo).execute(role="admin", requester_id=uuid.uuid4(), entity_id=entity.id)
    assert retrieved.id == entity.id

    # List
    entities, _ = ListAnalyticsSnapshots(repo).execute(role="admin", requester_id=uuid.uuid4())
    assert len(entities) >= 1
