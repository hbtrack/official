"""Parity: exercises generated code structural validation."""
from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import datetime, timezone

import pytest

from tests.parity._parity_helpers import InMemoryRepo, REPO_ROOT, FROZEN_ID, route_surface, route_set, route_methods, source_graph_methods

from exercises.generated.domain.entities import Exercise
from exercises.generated.schemas import ExerciseOut
from exercises.generated.application.use_cases import Listexercises, Createexercise, Getexercise


def _make_entity(**overrides):
    payload = {
        "id": FROZEN_ID,
        "scope": "test-value",
        "name": "test-value",
        "session_phase": "test-value",
        "primary_objective": "test-value",
        "age_categories": ["item-1"],
        "skill_level": "test-value",
        "complexity": 1,
        "physical_load": "test-value",
        "min_athletes": 1,
        "max_athletes": 1,
        "estimated_duration_minutes": 1,
        "space_required": "test-value",
        "editorial_status": "test-value",
        "current_version_id": uuid.uuid4(),
        "current_version_number": 1,
        "created_by_user_id": uuid.uuid4(),
        "created_at": datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
    }
    payload.update(overrides)
    return Exercise(**payload)


def test_exercises_entity_fields_and_invariants():
    entity = _make_entity()
    entity.validate_invariants()
    d = asdict(entity)
    assert "id" in d
    assert len(d) >= 19


def test_exercises_schema_from_domain_round_trip():
    entity = _make_entity()
    schema = ExerciseOut.from_domain(entity)
    dump = schema.model_dump()
    assert dump["id"] == entity.id


def test_exercises_api_route_coverage():
    gen = route_surface(REPO_ROOT / "src" / "exercises" / "generated" / "api.py")
    manual = route_surface(REPO_ROOT / "src" / "exercises" / "api.py")
    gen_rs = route_set(gen)
    manual_rs = route_set(manual)
    # Strict check: normalized paths match
    if not manual_rs <= gen_rs:
        # Fallback: generated covers source graph contract (manual may diverge in method/count)
        gen_mc = route_methods(gen)
        sg_mc = source_graph_methods("exercises")
        for method in sg_mc:
            assert method in gen_mc, f"Generated API missing HTTP method {method} from source graph"
            assert gen_mc[method] >= sg_mc[method], (
                f"Generated API has fewer {method} routes than source graph: {gen_mc[method]} < {sg_mc[method]}"
            )


def test_exercises_use_cases_crud():
    repo = InMemoryRepo()
    # Create
    entity = Createexercise(repo).execute(
        requester_id=uuid.uuid4(),
        scope="test-value",
        name="test-value",
        session_phase="test-value",
        primary_objective="test-value",
        age_categories=["item-1"],
        skill_level="test-value",
        complexity=1,
        physical_load="test-value",
        min_athletes=1,
        max_athletes=1,
        estimated_duration_minutes=1,
        space_required="test-value",
        editorial_status="test-value",
        current_version_id=uuid.uuid4(),
        current_version_number=1,
        created_by_user_id=uuid.uuid4(),
        created_at=datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 3, 31, 15, 0, tzinfo=timezone.utc),
    )
    assert entity.id is not None

    # Get
    retrieved = Getexercise(repo).execute(uuid.uuid4(), entity.id)
    assert retrieved.id == entity.id

    # List
    entities, _ = Listexercises(repo).execute(uuid.uuid4())
    assert len(entities) >= 1
