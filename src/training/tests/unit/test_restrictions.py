"""
TM-037, TM-038, TM-111 — Eligibility restrictions e overrides.
Fonte: DOMAIN_RULES_TRAINING.md, INVARIANTS_TRAINING.md.
target-state: regras de eligibility/restriction não implementadas em domain layer.
"""
import pytest

from training.domain.rules import assert_can_modify_session, InsufficientPrivilege, RoleLabel


class TestModifySessionRestrictions:
    """Restrições de modificação de sessão por role."""

    def test_coach_can_modify(self):
        assert_can_modify_session(RoleLabel.COACH)

    def test_coordinator_can_modify(self):
        assert_can_modify_session(RoleLabel.COORDINATOR)

    def test_admin_can_modify(self):
        assert_can_modify_session(RoleLabel.ADMIN)

    def test_athlete_cannot_modify(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_modify_session(RoleLabel.ATHLETE)

    def test_member_cannot_modify(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_modify_session(RoleLabel.MEMBER)


class TestEligibilityOverrides:
    """TM-111: override de restrições requer justificativa."""

    @pytest.mark.skip(reason="target-state: eligibility restrictions not yet in domain layer")
    def test_override_requires_rationale(self):
        pass

    @pytest.mark.skip(reason="target-state: eligibility restrictions not yet in domain layer")
    def test_override_logged_in_audit_trail(self):
        pass
