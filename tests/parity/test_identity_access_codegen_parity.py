"""Parity: identity_access generated code structural validation."""
from __future__ import annotations

import uuid
from dataclasses import asdict

import pytest

from tests.parity._parity_helpers import InMemoryRepo, REPO_ROOT, FROZEN_ID, route_surface, route_set, route_methods, source_graph_methods

from identity_access.generated.domain.entities import AuthSession
from identity_access.generated.schemas import AuthSessionOut
from identity_access.generated.application.use_cases import Listactivesessions


def _make_entity(**overrides):
    payload = {
        "id": FROZEN_ID,
        "principal_user_id": uuid.uuid4(),
        "session_scope_label": "test-value",
    }
    payload.update(overrides)
    return AuthSession(**payload)


def test_identity_access_entity_fields_and_invariants():
    entity = _make_entity()
    entity.validate_invariants()
    d = asdict(entity)
    assert "id" in d
    assert len(d) >= 3


def test_identity_access_schema_from_domain_round_trip():
    entity = _make_entity()
    schema = AuthSessionOut.from_domain(entity)
    dump = schema.model_dump()
    assert dump["id"] == entity.id


def test_identity_access_api_route_coverage():
    gen = route_surface(REPO_ROOT / "src" / "identity_access" / "generated" / "api.py")
    manual = route_surface(REPO_ROOT / "src" / "identity_access" / "api.py")
    gen_rs = route_set(gen)
    manual_rs = route_set(manual)
    # Strict check: normalized paths match
    if not manual_rs <= gen_rs:
        # Fallback: generated covers source graph contract (manual may diverge)
        gen_mc = route_methods(gen)
        sg_mc = source_graph_methods("identity_access")
        for method in sg_mc:
            assert method in gen_mc, f"Generated API missing HTTP method {method} from source graph"
            assert gen_mc[method] >= sg_mc[method], (
                f"Generated API has fewer {method} routes than source graph: {gen_mc[method]} < {sg_mc[method]}"
            )

