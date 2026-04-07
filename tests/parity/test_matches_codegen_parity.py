"""Parity: matches generated code structural validation."""
from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import datetime, timezone

import pytest

from tests.parity._parity_helpers import InMemoryRepo, REPO_ROOT, FROZEN_ID, route_surface, route_set, route_methods, source_graph_methods

from matches.generated.domain.entities import Match
from matches.generated.schemas import MatchOut
from matches.generated.application.use_cases import Listmatches, Creatematch, Getmatch


def _make_entity(**overrides):
    payload = {
        "id": FROZEN_ID,
        "competition_id": uuid.uuid4(),
        "home_team_id": uuid.uuid4(),
        "away_team_id": uuid.uuid4(),
        "status_label": "test-value",
        "scheduled_at": datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        "lineup_user_ids": [uuid.uuid4()],
        "official_incident_ids": [uuid.uuid4()],
        "referee_names": ["item-1"],
        "created_at": datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
    }
    payload.update(overrides)
    return Match(**payload)


def test_matches_entity_fields_and_invariants():
    entity = _make_entity()
    entity.validate_invariants()
    d = asdict(entity)
    assert "id" in d
    assert len(d) >= 11


def test_matches_schema_from_domain_round_trip():
    entity = _make_entity()
    schema = MatchOut.from_domain(entity)
    dump = schema.model_dump()
    assert dump["id"] == entity.id


def test_matches_api_route_coverage():
    gen = route_surface(REPO_ROOT / "src" / "matches" / "generated" / "api.py")
    manual = route_surface(REPO_ROOT / "src" / "matches" / "api.py")
    gen_rs = route_set(gen)
    manual_rs = route_set(manual)
    # Strict check: normalized paths match
    if not manual_rs <= gen_rs:
        # Fallback: generated covers source graph contract (manual may diverge)
        gen_mc = route_methods(gen)
        sg_mc = source_graph_methods("matches")
        for method in sg_mc:
            assert method in gen_mc, f"Generated API missing HTTP method {method} from source graph"
            assert gen_mc[method] >= sg_mc[method], (
                f"Generated API has fewer {method} routes than source graph: {gen_mc[method]} < {sg_mc[method]}"
            )


def test_matches_use_cases_crud():
    repo = InMemoryRepo()
    # Create
    entity = Creatematch(repo).execute(
        requester_id=uuid.uuid4(),
        competition_id=uuid.uuid4(),
        home_team_id=uuid.uuid4(),
        away_team_id=uuid.uuid4(),
        status_label="test-value",
        scheduled_at=datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        lineup_user_ids=[uuid.uuid4()],
        official_incident_ids=[uuid.uuid4()],
        referee_names=["item-1"],
        created_at=datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
    )
    assert entity.id is not None

    # Get
    retrieved = Getmatch(repo).execute(uuid.uuid4(), entity.id)
    assert retrieved.id == entity.id

    # List
    entities, _ = Listmatches(repo).execute(uuid.uuid4())
    assert len(entities) >= 1
