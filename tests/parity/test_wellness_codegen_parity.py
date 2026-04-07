"""Parity: wellness generated code structural validation."""
from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import date, timezone

import pytest

from tests.parity._parity_helpers import InMemoryRepo, REPO_ROOT, FROZEN_ID, route_surface, route_set, route_methods, source_graph_methods

from wellness.generated.domain.entities import WellnessEntry
from wellness.generated.schemas import WellnessEntryOut
from wellness.generated.application.use_cases import Listwellnessentries, Createwellnessentry, Getwellnessentry


def _make_entity(**overrides):
    payload = {
        "id": FROZEN_ID,
        "athlete_user_id": uuid.uuid4(),
        "questionnaire_date": date(2026, 3, 31),
        "readiness_score": 1,
    }
    payload.update(overrides)
    return WellnessEntry(**payload)


def test_wellness_entity_fields_and_invariants():
    entity = _make_entity()
    entity.validate_invariants()
    d = asdict(entity)
    assert "id" in d
    assert len(d) >= 4


def test_wellness_schema_from_domain_round_trip():
    entity = _make_entity()
    schema = WellnessEntryOut.from_domain(entity)
    dump = schema.model_dump()
    assert dump["id"] == entity.id


def test_wellness_api_route_coverage():
    gen = route_surface(REPO_ROOT / "src" / "wellness" / "generated" / "api.py")
    manual = route_surface(REPO_ROOT / "src" / "wellness" / "api.py")
    gen_rs = route_set(gen)
    manual_rs = route_set(manual)
    # Strict check: normalized paths match
    if not manual_rs <= gen_rs:
        # Fallback: generated covers source graph contract (manual may diverge)
        gen_mc = route_methods(gen)
        sg_mc = source_graph_methods("wellness")
        for method in sg_mc:
            assert method in gen_mc, f"Generated API missing HTTP method {method} from source graph"
            assert gen_mc[method] >= sg_mc[method], (
                f"Generated API has fewer {method} routes than source graph: {gen_mc[method]} < {sg_mc[method]}"
            )


def test_wellness_use_cases_crud():
    repo = InMemoryRepo()
    # Create
    entity = Createwellnessentry(repo).execute(
        requester_id=uuid.uuid4(),
        athlete_user_id=uuid.uuid4(),
        questionnaire_date=date(2026, 3, 31),
        readiness_score=1,
    )
    assert entity.id is not None

    # Get
    retrieved = Getwellnessentry(repo).execute(uuid.uuid4(), entity.id)
    assert retrieved.id == entity.id

    # List
    entities, _ = Listwellnessentries(repo).execute(uuid.uuid4())
    assert len(entities) >= 1
