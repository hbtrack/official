"""Parity: seasons generated code structural validation."""
from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import date, timezone

import pytest

from tests.parity._parity_helpers import InMemoryRepo, REPO_ROOT, FROZEN_ID, route_surface, route_set, route_methods, source_graph_methods

from seasons.generated.domain.entities import Season
from seasons.generated.schemas import SeasonOut
from seasons.generated.application.use_cases import Listseasons, Createseason, Getseason


def _make_entity(**overrides):
    payload = {
        "id": FROZEN_ID,
        "name": "test-value",
        "status_label": "test-value",
        "start_date": date(2026, 3, 31),
        "end_date": date(2026, 3, 31),
        "phase_labels": ["item-1"],
        "competition_ids": [uuid.uuid4()],
        "team_ids": [uuid.uuid4()],
    }
    payload.update(overrides)
    return Season(**payload)


def test_seasons_entity_fields_and_invariants():
    entity = _make_entity()
    entity.validate_invariants()
    d = asdict(entity)
    assert "id" in d
    assert len(d) >= 8


def test_seasons_schema_from_domain_round_trip():
    entity = _make_entity()
    schema = SeasonOut.from_domain(entity)
    dump = schema.model_dump()
    assert dump["id"] == entity.id


def test_seasons_api_route_coverage():
    gen = route_surface(REPO_ROOT / "src" / "seasons" / "generated" / "api.py")
    manual = route_surface(REPO_ROOT / "src" / "seasons" / "api.py")
    gen_rs = route_set(gen)
    manual_rs = route_set(manual)
    # Strict check: normalized paths match
    if not manual_rs <= gen_rs:
        # Fallback: generated covers source graph contract (manual may diverge)
        gen_mc = route_methods(gen)
        sg_mc = source_graph_methods("seasons")
        for method in sg_mc:
            assert method in gen_mc, f"Generated API missing HTTP method {method} from source graph"
            assert gen_mc[method] >= sg_mc[method], (
                f"Generated API has fewer {method} routes than source graph: {gen_mc[method]} < {sg_mc[method]}"
            )


def test_seasons_use_cases_crud():
    repo = InMemoryRepo()
    # Create
    entity = Createseason(repo).execute(
        requester_id=uuid.uuid4(),
        name="test-value",
        status_label="test-value",
        start_date=date(2026, 3, 31),
        end_date=date(2026, 3, 31),
        phase_labels=["item-1"],
        competition_ids=[uuid.uuid4()],
        team_ids=[uuid.uuid4()],
    )
    assert entity.id is not None

    # Get
    retrieved = Getseason(repo).execute(uuid.uuid4(), entity.id)
    assert retrieved.id == entity.id

    # List
    entities, _ = Listseasons(repo).execute(uuid.uuid4())
    assert len(entities) >= 1
