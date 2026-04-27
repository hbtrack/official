"""
TM-037, TM-038, TM-111 — Eligibility restrictions e overrides.
Fonte: DOMAIN_RULES_TRAINING.md, INVARIANTS_TRAINING.md.
target-state: regras de eligibility/restriction não implementadas em domain layer.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from training.application.eligibility.commands import SubmitIneligibilityDeclarationUseCase
from training.application.eligibility.dto import SubmitIneligibilityDeclarationInput
from training.domain.common.enums import TrainingSessionStatus
from training.domain.entities.eligibility import AthleteIneligibilityDeclaration
from training.domain.rules import (
    IneligibilityStateConflict,
    InsufficientPrivilege,
    RoleLabel,
    assert_can_modify_session,
)

from .conftest import make_session


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

    def test_declaration_requires_published_or_in_progress_session(self):
        session_repo = MagicMock()
        session_repo.get_by_id.return_value = make_session(status=TrainingSessionStatus.DRAFT)
        ineligibility_repo = MagicMock()
        use_case = SubmitIneligibilityDeclarationUseCase(session_repo, ineligibility_repo)

        with pytest.raises(IneligibilityStateConflict, match="PUBLISHED ou IN_PROGRESS"):
            use_case.execute(
                SubmitIneligibilityDeclarationInput(
                    session_id=uuid.uuid4(),
                    actor_role=RoleLabel.ATHLETE,
                    actor_id=uuid.uuid4(),
                    athlete_id=uuid.uuid4(),
                    reason_flags=["INJURY_PAIN"],
                )
            )

    def test_resubmission_resets_coach_acknowledgment_and_preserves_created_at(self):
        actor_id = uuid.uuid4()
        created_at = datetime(2026, 4, 1, tzinfo=timezone.utc)
        existing = AthleteIneligibilityDeclaration(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            athlete_id=actor_id,
            declared_at=created_at,
            created_at=created_at,
            reason_flags=["INJURY_PAIN"],
            acknowledged_by_coach=True,
            coach_note="Avaliado",
        )
        session_repo = MagicMock()
        session_repo.get_by_id.return_value = make_session(status=TrainingSessionStatus.PUBLISHED)
        ineligibility_repo = MagicMock()
        ineligibility_repo.get_by_session_athlete.return_value = existing
        ineligibility_repo.save.side_effect = lambda declaration: declaration
        use_case = SubmitIneligibilityDeclarationUseCase(session_repo, ineligibility_repo)

        result = use_case.execute(
            SubmitIneligibilityDeclarationInput(
                session_id=existing.session_id,
                actor_role=RoleLabel.ATHLETE,
                actor_id=actor_id,
                athlete_id=actor_id,
                reason_flags=["ACTIVE_RECOVERY_ONLY"],
            )
        )

        assert result.id == existing.id
        assert result.created_at == created_at
        assert result.acknowledged_by_coach is False
        assert result.coach_note is None
