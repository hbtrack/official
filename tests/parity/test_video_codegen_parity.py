"""Parity: video generated code structural validation."""
from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import datetime, timezone

import pytest

from tests.parity._parity_helpers import InMemoryRepo, REPO_ROOT, FROZEN_ID, route_surface, route_set, route_methods, source_graph_methods

from video.generated.domain.entities import MatchMediaSession
from video.generated.schemas import MatchMediaSessionOut
from video.generated.application.use_cases import Listsessions, Createsession, Getsession


def _make_entity(**overrides):
    payload = {
        "id": FROZEN_ID,
        "match_id": uuid.uuid4(),
        "state": "test-value",
        "capture_mode": "test-value",
        "retention_policy": "test-value",
        "created_at": datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        "created_by_user_id": uuid.uuid4(),
    }
    payload.update(overrides)
    return MatchMediaSession(**payload)


def test_video_entity_fields_and_invariants():
    entity = _make_entity()
    entity.validate_invariants()
    d = asdict(entity)
    assert "id" in d
    assert len(d) >= 7


def test_video_schema_from_domain_round_trip():
    entity = _make_entity()
    schema = MatchMediaSessionOut.from_domain(entity)
    dump = schema.model_dump()
    assert dump["id"] == entity.id


def test_video_api_route_coverage():
    gen = route_surface(REPO_ROOT / "src" / "video" / "generated" / "api.py")
    manual = route_surface(REPO_ROOT / "src" / "video" / "api.py")
    gen_rs = route_set(gen)
    manual_rs = route_set(manual)
    # Strict check: normalized paths match
    if not manual_rs <= gen_rs:
        # Fallback: generated covers source graph contract (manual may diverge in method/count)
        gen_mc = route_methods(gen)
        sg_mc = source_graph_methods("video")
        for method in sg_mc:
            assert method in gen_mc, f"Generated API missing HTTP method {method} from source graph"
            assert gen_mc[method] >= sg_mc[method], (
                f"Generated API has fewer {method} routes than source graph: {gen_mc[method]} < {sg_mc[method]}"
            )


def test_video_use_cases_crud():
    repo = InMemoryRepo()
    # Create
    entity = Createsession(repo).execute(
        requester_id=uuid.uuid4(),
        match_id=uuid.uuid4(),
        state="test-value",
        capture_mode="test-value",
        retention_policy="test-value",
        created_at=datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        created_by_user_id=uuid.uuid4(),
    )
    assert entity.id is not None

    # Get
    retrieved = Getsession(repo).execute(uuid.uuid4(), entity.id)
    assert retrieved.id == entity.id

    # List
    entities, _ = Listsessions(repo).execute(uuid.uuid4())
    assert len(entities) >= 1
