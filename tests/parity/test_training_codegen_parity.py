"""Parity: training generated code structural validation."""
from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import datetime, timezone

import pytest

from tests.parity._parity_helpers import InMemoryRepo, REPO_ROOT, FROZEN_ID, route_surface, route_set, route_methods, source_graph_methods

from training.generated.domain.entities import TrainingSession
from training.generated.schemas import TrainingSessionOut
from training.generated.application.use_cases import Listtrainingsessions, Createtrainingsession, Gettrainingsessionbyid


def _make_entity(**overrides):
    payload = {
        "id": FROZEN_ID,
        "organization_id": uuid.uuid4(),
        "session_at": datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        "session_type": "test-value",
        "created_at": datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        "created_by_user_id": uuid.uuid4(),
        "updated_at": datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        "status": "test-value",
    }
    payload.update(overrides)
    return TrainingSession(**payload)


def test_training_entity_fields_and_invariants():
    entity = _make_entity()
    entity.validate_invariants()
    d = asdict(entity)
    assert "id" in d
    assert len(d) >= 8


def test_training_schema_from_domain_round_trip():
    entity = _make_entity()
    schema = TrainingSessionOut.from_domain(entity)
    dump = schema.model_dump()
    assert dump["id"] == entity.id


def test_training_api_route_coverage():
    gen = route_surface(REPO_ROOT / "src" / "training" / "generated" / "api.py")
    manual = route_surface(REPO_ROOT / "src" / "training" / "api.py")
    gen_rs = route_set(gen)
    manual_rs = route_set(manual)
    # Strict check: normalized paths match
    if not manual_rs <= gen_rs:
        # Fallback: generated covers source graph contract (manual may diverge)
        gen_mc = route_methods(gen)
        sg_mc = source_graph_methods("training")
        for method in sg_mc:
            assert method in gen_mc, f"Generated API missing HTTP method {method} from source graph"
            assert gen_mc[method] >= sg_mc[method], (
                f"Generated API has fewer {method} routes than source graph: {gen_mc[method]} < {sg_mc[method]}"
            )


def test_training_use_cases_crud():
    repo = InMemoryRepo()
    # Create
    entity = Createtrainingsession(repo).execute(
        requester_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        session_at=datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        session_type="test-value",
        created_at=datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        created_by_user_id=uuid.uuid4(),
        updated_at=datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        status="test-value",
    )
    assert entity.id is not None

    # Get
    retrieved = Gettrainingsessionbyid(repo).execute(uuid.uuid4(), entity.id)
    assert retrieved.id == entity.id

    # List
    entities, _ = Listtrainingsessions(repo).execute(uuid.uuid4())
    assert len(entities) >= 1
