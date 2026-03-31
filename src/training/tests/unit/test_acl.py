"""
TM-121 — Extended ACL rules (EXB-ACL-001..007).
Fonte: PERMISSIONS_TRAINING.md, ADR-008.
"""
import uuid

import pytest

from training.domain.rules import (
    InsufficientPrivilege,
    RoleLabel,
    assert_can_create_session,
    assert_can_delete_session,
    assert_can_modify_session,
    assert_can_read_session,
    assert_can_submit_wellness,
)


class TestACLCreateSession:
    """EXB-ACL-001: create session ACL por role."""

    @pytest.mark.parametrize("role", [RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH])
    def test_staff_can_create(self, role):
        assert_can_create_session(role)

    @pytest.mark.parametrize("role", [RoleLabel.ATHLETE, RoleLabel.MEMBER])
    def test_non_staff_cannot_create(self, role):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_session(role)


class TestACLModifySession:
    """EXB-ACL-002: modify session ACL por role."""

    @pytest.mark.parametrize("role", [RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH])
    def test_staff_can_modify(self, role):
        assert_can_modify_session(role)

    @pytest.mark.parametrize("role", [RoleLabel.ATHLETE, RoleLabel.MEMBER])
    def test_non_staff_cannot_modify(self, role):
        with pytest.raises(InsufficientPrivilege):
            assert_can_modify_session(role)


class TestACLDeleteSession:
    """EXB-ACL-003: delete session ACL por role."""

    @pytest.mark.parametrize("role", [RoleLabel.ADMIN, RoleLabel.COORDINATOR])
    def test_admin_coordinator_can_delete(self, role):
        assert_can_delete_session(role)

    @pytest.mark.parametrize("role", [RoleLabel.COACH, RoleLabel.ATHLETE, RoleLabel.MEMBER])
    def test_others_cannot_delete(self, role):
        with pytest.raises(InsufficientPrivilege):
            assert_can_delete_session(role)


class TestACLReadSession:
    """EXB-ACL-004: read session ACL (BOLA)."""

    def test_staff_reads_any(self):
        assert_can_read_session(RoleLabel.ADMIN, uuid.uuid4(), [])

    def test_athlete_reads_own(self):
        actor = uuid.uuid4()
        assert_can_read_session(RoleLabel.ATHLETE, actor, [actor])

    def test_athlete_denied_other(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_session(RoleLabel.ATHLETE, uuid.uuid4(), [uuid.uuid4()])


class TestACLWellness:
    """EXB-ACL-005..007: wellness submission ACL (BOPLA)."""

    def test_athlete_submits_own(self):
        actor = uuid.uuid4()
        assert_can_submit_wellness(RoleLabel.ATHLETE, actor, actor)

    def test_athlete_cannot_submit_for_others(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_submit_wellness(RoleLabel.ATHLETE, uuid.uuid4(), uuid.uuid4())

    def test_staff_submits_for_any(self):
        assert_can_submit_wellness(RoleLabel.COACH, uuid.uuid4(), uuid.uuid4())
