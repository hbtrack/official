"""
Testes unitários — módulo competitions.
Derivados de INVARIANTS_COMPETITIONS.md, DOMAIN_RULES_COMPETITIONS.md,
PERMISSIONS_COMPETITIONS.md.
Sem banco de dados — apenas lógica de domínio pura.
"""
import uuid
from datetime import date, datetime, timezone

import pytest

from competitions.domain.entities import Competition, CompetitionStatus
from competitions.domain.rules import (
    CompetitionNotFound,
    InsufficientPrivilege,
    InvalidStatusTransition,
    RoleLabel,
    TeamAlreadyRegistered,
    TeamNotRegistered,
    assert_can_create_competition,
    assert_can_list_competitions,
    assert_can_patch_competition,
    assert_can_read_competition,
    assert_can_register_team,
    assert_can_unregister_team,
    assert_team_not_registered,
    assert_team_registered,
    assert_valid_transition,
)


def _make_competition(**kwargs) -> Competition:
    defaults = dict(
        id=uuid.uuid4(),
        season_id=uuid.uuid4(),
        name="Campeonato Regional 2026",
        start_date=date(2026, 1, 10),
        status_label=CompetitionStatus.DRAFT,
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )
    defaults.update(kwargs)
    return Competition(**defaults)


# ---------------------------------------------------------------------------
# INV-COMP-001: campos obrigatórios
# ---------------------------------------------------------------------------

class TestCompetitionRequiredFields:
    def test_valid_competition_passes(self):
        c = _make_competition()
        c.validate_invariants()

    def test_empty_name_raises(self):
        c = _make_competition(name="")
        with pytest.raises(ValueError, match="INV-COMP-001"):
            c.validate_invariants()

    def test_whitespace_name_raises(self):
        c = _make_competition(name="   ")
        with pytest.raises(ValueError, match="INV-COMP-001"):
            c.validate_invariants()

    def test_name_max_140_passes(self):
        c = _make_competition(name="A" * 140)
        c.validate_invariants()

    def test_name_over_140_raises(self):
        c = _make_competition(name="A" * 141)
        with pytest.raises(ValueError, match="INV-COMP-001"):
            c.validate_invariants()


# ---------------------------------------------------------------------------
# INV-COMP-002: startDate <= endDate
# ---------------------------------------------------------------------------

class TestDateTemporalInvariant:
    def test_start_before_end_passes(self):
        c = _make_competition(
            start_date=date(2026, 1, 10),
            end_date=date(2026, 3, 20),
        )
        c.validate_invariants()

    def test_start_equals_end_passes(self):
        c = _make_competition(
            start_date=date(2026, 1, 10),
            end_date=date(2026, 1, 10),
        )
        c.validate_invariants()

    def test_start_after_end_raises(self):
        c = _make_competition(
            start_date=date(2026, 3, 20),
            end_date=date(2026, 1, 10),
        )
        with pytest.raises(ValueError, match="INV-COMP-002"):
            c.validate_invariants()

    def test_no_end_date_passes(self):
        c = _make_competition(start_date=date(2026, 1, 10), end_date=None)
        c.validate_invariants()


# ---------------------------------------------------------------------------
# INV-COMP-003: unicidade de stage_labels e registration_team_ids
# ---------------------------------------------------------------------------

class TestUniquenessInvariants:
    def test_unique_stage_labels_passes(self):
        c = _make_competition(stage_labels=["Fase de Grupos", "Semifinal", "Final"])
        c.validate_invariants()

    def test_duplicate_stage_labels_raises(self):
        c = _make_competition(stage_labels=["Final", "Final"])
        with pytest.raises(ValueError, match="INV-COMP-003"):
            c.validate_invariants()

    def test_unique_team_ids_passes(self):
        ids = [uuid.uuid4() for _ in range(3)]
        c = _make_competition(registration_team_ids=ids)
        c.validate_invariants()

    def test_duplicate_team_ids_raises(self):
        tid = uuid.uuid4()
        c = _make_competition(registration_team_ids=[tid, tid])
        with pytest.raises(ValueError, match="INV-COMP-003"):
            c.validate_invariants()

    def test_empty_stage_label_raises(self):
        c = _make_competition(stage_labels=[""])
        with pytest.raises(ValueError, match="INV-COMP-003"):
            c.validate_invariants()

    def test_stage_label_over_80_chars_raises(self):
        c = _make_competition(stage_labels=["X" * 81])
        with pytest.raises(ValueError, match="INV-COMP-003"):
            c.validate_invariants()

    def test_format_label_max_80_passes(self):
        c = _make_competition(format_label="Liga" * 20)
        c.validate_invariants()

    def test_format_label_over_80_raises(self):
        c = _make_competition(format_label="X" * 81)
        with pytest.raises(ValueError):
            c.validate_invariants()

    def test_standings_summary_max_500_passes(self):
        c = _make_competition(standings_summary="X" * 500)
        c.validate_invariants()

    def test_standings_summary_over_500_raises(self):
        c = _make_competition(standings_summary="X" * 501)
        with pytest.raises(ValueError):
            c.validate_invariants()


# ---------------------------------------------------------------------------
# FSM: draft → active → archived
# ---------------------------------------------------------------------------

class TestCompetitionFSM:
    def test_draft_to_active_valid(self):
        assert_valid_transition(CompetitionStatus.DRAFT, CompetitionStatus.ACTIVE)

    def test_active_to_archived_valid(self):
        assert_valid_transition(CompetitionStatus.ACTIVE, CompetitionStatus.ARCHIVED)

    def test_draft_to_archived_invalid(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_transition(CompetitionStatus.DRAFT, CompetitionStatus.ARCHIVED)

    def test_archived_terminal(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_transition(CompetitionStatus.ARCHIVED, CompetitionStatus.DRAFT)

    def test_active_to_draft_invalid(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_transition(CompetitionStatus.ACTIVE, CompetitionStatus.DRAFT)


# ---------------------------------------------------------------------------
# RBAC — PERMISSIONS_COMPETITIONS.md
# ---------------------------------------------------------------------------

class TestListCompetitionsRBAC:
    """PERM-COMP-003: listagem é aberta a todos os roles."""
    def test_all_roles_can_list(self):
        for role in RoleLabel:
            assert_can_list_competitions(role)


class TestCreateCompetitionRBAC:
    def test_admin_can_create(self):
        assert_can_create_competition(RoleLabel.ADMIN)

    def test_coordinator_can_create(self):
        assert_can_create_competition(RoleLabel.COORDINATOR)

    def test_coach_cannot_create(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_competition(RoleLabel.COACH)

    def test_athlete_cannot_create(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_competition(RoleLabel.ATHLETE)

    def test_member_cannot_create(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_competition(RoleLabel.MEMBER)


class TestReadCompetitionRBAC:
    def test_all_roles_can_read(self):
        for role in RoleLabel:
            assert_can_read_competition(role)


class TestPatchCompetitionRBAC:
    def test_admin_can_patch_draft(self):
        assert_can_patch_competition(RoleLabel.ADMIN, CompetitionStatus.DRAFT)

    def test_coordinator_can_patch_draft(self):
        assert_can_patch_competition(RoleLabel.COORDINATOR, CompetitionStatus.DRAFT)

    def test_coach_cannot_patch(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_patch_competition(RoleLabel.COACH, CompetitionStatus.DRAFT)

    def test_athlete_cannot_patch(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_patch_competition(RoleLabel.ATHLETE, CompetitionStatus.DRAFT)

    def test_coordinator_cannot_patch_active(self):
        """PERM-COMP-002: competição ACTIVE só admin pode editar."""
        with pytest.raises(InsufficientPrivilege, match="PERM-COMP-002"):
            assert_can_patch_competition(RoleLabel.COORDINATOR, CompetitionStatus.ACTIVE)

    def test_admin_can_patch_active(self):
        assert_can_patch_competition(RoleLabel.ADMIN, CompetitionStatus.ACTIVE)


class TestRegisterTeamRBAC:
    def test_admin_can_register(self):
        assert_can_register_team(RoleLabel.ADMIN)

    def test_coordinator_can_register(self):
        assert_can_register_team(RoleLabel.COORDINATOR)

    def test_coach_cannot_register(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_register_team(RoleLabel.COACH)

    def test_athlete_cannot_register(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_register_team(RoleLabel.ATHLETE)

    def test_member_cannot_register(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_register_team(RoleLabel.MEMBER)


class TestUnregisterTeamRBAC:
    def test_admin_can_unregister(self):
        assert_can_unregister_team(RoleLabel.ADMIN)

    def test_coordinator_can_unregister(self):
        assert_can_unregister_team(RoleLabel.COORDINATOR)

    def test_coach_cannot_unregister(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_unregister_team(RoleLabel.COACH)


# ---------------------------------------------------------------------------
# INV-COMP-003: regras de inscrição de equipe
# ---------------------------------------------------------------------------

class TestTeamRegistrationRules:
    def test_register_new_team_passes(self):
        existing = [uuid.uuid4(), uuid.uuid4()]
        new_team = uuid.uuid4()
        assert_team_not_registered(existing, new_team)

    def test_register_duplicate_team_raises(self):
        tid = uuid.uuid4()
        with pytest.raises(TeamAlreadyRegistered, match="INV-COMP-003"):
            assert_team_not_registered([tid, uuid.uuid4()], tid)

    def test_unregister_existing_team_passes(self):
        tid = uuid.uuid4()
        assert_team_registered([tid, uuid.uuid4()], tid)

    def test_unregister_absent_team_raises(self):
        with pytest.raises(TeamNotRegistered):
            assert_team_registered([uuid.uuid4()], uuid.uuid4())
