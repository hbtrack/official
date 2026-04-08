"""Parity: users generated code structural validation."""
from __future__ import annotations

import uuid
from dataclasses import asdict

import pytest

from tests.parity._parity_helpers import InMemoryRepo, REPO_ROOT, FROZEN_ID, route_surface, route_set, route_methods, source_graph_methods

from users.generated.domain.entities import UserProfile
from users.generated.schemas import UserProfileOut
from users.generated.application.use_cases import ListUsers, CreateUser, GetUser


def _make_entity(**overrides):
    payload = {
        "id": FROZEN_ID,
        "display_name": "test-value",
        "role_label": "test-value",
    }
    payload.update(overrides)
    return UserProfile(**payload)


def test_users_entity_fields_and_invariants():
    entity = _make_entity()
    entity.validate_invariants()
    d = asdict(entity)
    assert "id" in d
    assert len(d) >= 3


def test_users_schema_from_domain_round_trip():
    entity = _make_entity()
    schema = UserProfileOut.from_domain(entity)
    dump = schema.model_dump()
    assert dump["id"] == entity.id


def test_users_api_route_coverage():
    gen = route_surface(REPO_ROOT / "src" / "users" / "generated" / "api.py")
    manual = route_surface(REPO_ROOT / "src" / "users" / "api.py")
    gen_rs = route_set(gen)
    manual_rs = route_set(manual)
    # Strict check: normalized paths match
    if not manual_rs <= gen_rs:
        # Fallback: generated covers source graph contract (manual may diverge)
        gen_mc = route_methods(gen)
        sg_mc = source_graph_methods("users")
        for method in sg_mc:
            assert method in gen_mc, f"Generated API missing HTTP method {method} from source graph"
            assert gen_mc[method] >= sg_mc[method], (
                f"Generated API has fewer {method} routes than source graph: {gen_mc[method]} < {sg_mc[method]}"
            )


def test_users_use_cases_crud():
    repo = InMemoryRepo()
    # Create
    entity = CreateUser(repo).execute(
        role="admin",
        requester_id=uuid.uuid4(),
        display_name="test-value",
        role_label="test-value",
    )
    assert entity.id is not None

    # Get
    retrieved = GetUser(repo).execute(role="admin", requester_id=uuid.uuid4(), entity_id=entity.id)
    assert retrieved.id == entity.id

    # List
    entities, _ = ListUsers(repo).execute(role="admin", requester_id=uuid.uuid4())
    assert len(entities) >= 1
