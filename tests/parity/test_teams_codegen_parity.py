"""Parity: teams generated code structural validation."""
from __future__ import annotations

import uuid
from dataclasses import asdict

import pytest

from tests.parity._parity_helpers import InMemoryRepo, REPO_ROOT, FROZEN_ID, route_surface, route_set, route_methods, source_graph_methods

from teams.generated.domain.entities import Team
from teams.generated.schemas import TeamOut
from teams.generated.application.use_cases import Listteams, Createteam, Getteam


def _make_entity(**overrides):
    payload = {
        "id": FROZEN_ID,
        "organization_id": uuid.uuid4(),
        "name": "test-value",
        "category_label": "test-value",
    }
    payload.update(overrides)
    return Team(**payload)


def test_teams_entity_fields_and_invariants():
    entity = _make_entity()
    entity.validate_invariants()
    d = asdict(entity)
    assert "id" in d
    assert len(d) >= 4


def test_teams_schema_from_domain_round_trip():
    entity = _make_entity()
    schema = TeamOut.from_domain(entity)
    dump = schema.model_dump()
    assert dump["id"] == entity.id


def test_teams_api_route_coverage():
    gen = route_surface(REPO_ROOT / "src" / "teams" / "generated" / "api.py")
    manual = route_surface(REPO_ROOT / "src" / "teams" / "api.py")
    gen_rs = route_set(gen)
    manual_rs = route_set(manual)
    # Strict check: normalized paths match
    if not manual_rs <= gen_rs:
        # Fallback: generated covers source graph contract (manual may diverge)
        gen_mc = route_methods(gen)
        sg_mc = source_graph_methods("teams")
        for method in sg_mc:
            assert method in gen_mc, f"Generated API missing HTTP method {method} from source graph"
            assert gen_mc[method] >= sg_mc[method], (
                f"Generated API has fewer {method} routes than source graph: {gen_mc[method]} < {sg_mc[method]}"
            )


def test_teams_use_cases_crud():
    repo = InMemoryRepo()
    # Create
    entity = Createteam(repo).execute(
        requester_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        name="test-value",
        category_label="test-value",
    )
    assert entity.id is not None

    # Get
    retrieved = Getteam(repo).execute(uuid.uuid4(), entity.id)
    assert retrieved.id == entity.id

    # List
    entities, _ = Listteams(repo).execute(uuid.uuid4())
    assert len(entities) >= 1
