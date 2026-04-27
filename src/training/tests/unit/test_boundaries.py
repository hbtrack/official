"""
TM-054..TM-059, TM-114..TM-118 — Boundary invariants (cross-module).
Fonte: INVARIANTS_TRAINING.md, MODULE_REGISTRY.yaml.
target-state: validações cross-module não implementadas em domain layer.
"""
import inspect
import uuid
from datetime import datetime, timezone, timedelta

import pytest

from .conftest import make_session
from training.domain.policies.session_access import SessionAccessPolicy


class TestOrganizationBoundary:
    """TM-054: sessão só acessível dentro do organization_id do ator."""

    def test_session_has_organization_id(self):
        s = make_session()
        assert s.organization_id is not None

    def test_read_policy_boundary_depends_on_membership_inputs_not_org_lookup(self):
        params = list(inspect.signature(SessionAccessPolicy.require_readable).parameters)
        assert params == ["self", "session", "role", "actor_id", "athlete_ids"]


class TestTeamBoundary:
    """TM-055: associação team_id segue regras de validação."""

    def test_session_without_team_is_valid(self):
        s = make_session(team_id=None)
        s.validate_invariants()

    def test_session_with_team_is_valid(self):
        s = make_session(team_id=uuid.uuid4())
        s.validate_invariants()


class TestSessionFieldConstraints:
    """TM-114..TM-118: validações de fronteira numérica/texto."""

    def test_session_type_max_32_chars(self):
        s = make_session(session_type="a" * 32)
        s.validate_invariants()

    def test_session_type_too_long_raises(self):
        s = make_session(session_type="a" * 33)
        with pytest.raises(ValueError):
            s.validate_invariants()

    def test_location_max_120_chars(self):
        s = make_session(location="a" * 120)
        s.validate_invariants()

    def test_location_too_long_raises(self):
        s = make_session(location="a" * 121)
        with pytest.raises(ValueError):
            s.validate_invariants()

    def test_main_objective_max_255_chars(self):
        s = make_session(main_objective="a" * 255)
        s.validate_invariants()

    def test_main_objective_too_long_raises(self):
        s = make_session(main_objective="a" * 256)
        with pytest.raises(ValueError):
            s.validate_invariants()

    def test_duration_planned_in_range(self):
        s = make_session(duration_planned_minutes=60)
        s.validate_invariants()

    def test_duration_planned_0_raises(self):
        s = make_session(duration_planned_minutes=0)
        with pytest.raises(ValueError):
            s.validate_invariants()

    def test_duration_planned_1441_raises(self):
        s = make_session(duration_planned_minutes=1441)
        with pytest.raises(ValueError):
            s.validate_invariants()

    def test_intensity_target_in_range(self):
        s = make_session(intensity_target=3)
        s.validate_invariants()

    def test_intensity_target_0_raises(self):
        s = make_session(intensity_target=0)
        with pytest.raises(ValueError):
            s.validate_invariants()

    def test_intensity_target_6_raises(self):
        s = make_session(intensity_target=6)
        with pytest.raises(ValueError):
            s.validate_invariants()
