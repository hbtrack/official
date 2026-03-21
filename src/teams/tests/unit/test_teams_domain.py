"""
Testes unitários — módulo teams.
Camada: domain + application (sem Django, sem DB).
Contrato: contracts/openapi/paths/teams.yaml
Invariantes: docs/hbtrack/modulos/teams/INVARIANTS_TEAMS.md
"""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from teams.domain.entities import Team, TeamStatus
from teams.domain.rules import (
    InsufficientPrivilege,
    InvalidStatusTransition,
    RoleLabel,
    TeamNotFound,
    assert_can_create_team,
    assert_can_manage_athlete,
    assert_can_manage_staff,
    assert_can_patch_team,
    assert_can_read_team,
    assert_valid_status_transition,
)
from teams.application.use_cases import (
    AddAthleteToTeamInput,
    AddAthleteToTeamUseCase,
    AddStaffToTeamInput,
    AddStaffToTeamUseCase,
    CreateTeamInput,
    CreateTeamUseCase,
    GetTeamInput,
    GetTeamUseCase,
    ListTeamsInput,
    ListTeamsUseCase,
    PatchTeamInput,
    PatchTeamUseCase,
    RemoveAthleteFromTeamInput,
    RemoveAthleteFromTeamUseCase,
    RemoveStaffFromTeamInput,
    RemoveStaffFromTeamUseCase,
)

# ---------------------------------------------------------------------------
# Fixtures helpers
# ---------------------------------------------------------------------------

ORG_ID = uuid.uuid4()
TEAM_ID = uuid.uuid4()
ATHLETE_1 = uuid.uuid4()
ATHLETE_2 = uuid.uuid4()
STAFF_1 = uuid.uuid4()


def _make_team(**kwargs) -> Team:
    defaults = dict(
        id=TEAM_ID,
        organization_id=ORG_ID,
        name="Handebol Masculino Sub-18",
        category_label="Sub-18",
        status_label=TeamStatus.DRAFT,
        athlete_ids=[],
        staff_user_ids=[],
        season_id=None,
        short_name=None,
        roster_notes=None,
        created_at=None,
        updated_at=None,
    )
    defaults.update(kwargs)
    return Team(**defaults)


def _mock_repo(team: Team | None = None) -> MagicMock:
    repo = MagicMock()
    if team is not None:
        repo.get_by_id.return_value = team
        repo.save.return_value = team
        repo.update.return_value = team
    return repo


# ===========================================================================
# DOMAIN ENTITIES — TeamStatus
# ===========================================================================

class TestTeamStatus:
    def test_values(self):
        assert TeamStatus.DRAFT == "DRAFT"
        assert TeamStatus.ACTIVE == "ACTIVE"
        assert TeamStatus.ARCHIVED == "ARCHIVED"

    def test_is_str_enum(self):
        assert isinstance(TeamStatus.DRAFT, str)


# ===========================================================================
# DOMAIN ENTITIES — Team + validate_invariants
# ===========================================================================

class TestTeamEntity:
    def test_valid_team_passes(self):
        t = _make_team()
        t.validate_invariants()

    def test_inv_team_001_missing_name_raises(self):
        t = _make_team(name="")
        with pytest.raises(ValueError, match="name"):
            t.validate_invariants()

    def test_inv_team_001_missing_category_label_raises(self):
        t = _make_team(category_label="")
        with pytest.raises(ValueError, match="categoryLabel"):
            t.validate_invariants()

    def test_inv_team_001_name_too_long_raises(self):
        t = _make_team(name="A" * 121)
        with pytest.raises(ValueError, match="120"):
            t.validate_invariants()

    def test_inv_team_001_category_label_too_long_raises(self):
        t = _make_team(category_label="B" * 81)
        with pytest.raises(ValueError, match="80"):
            t.validate_invariants()

    def test_inv_team_002_duplicate_athlete_raises(self):
        aid = uuid.uuid4()
        t = _make_team(athlete_ids=[aid, aid])
        with pytest.raises(ValueError, match="uniqueItems"):
            t.validate_invariants()

    def test_inv_team_002_duplicate_staff_raises(self):
        sid = uuid.uuid4()
        t = _make_team(staff_user_ids=[sid, sid])
        with pytest.raises(ValueError, match="uniqueItems"):
            t.validate_invariants()

    def test_unique_athletes_valid(self):
        t = _make_team(athlete_ids=[ATHLETE_1, ATHLETE_2])
        t.validate_invariants()  # não levanta


# ===========================================================================
# DOMAIN RULES — assert_can_create_team
# ===========================================================================

class TestAssertCanCreateTeam:
    @pytest.mark.parametrize("role", [RoleLabel.ADMIN, RoleLabel.COORDINATOR])
    def test_management_roles_allowed(self, role):
        assert_can_create_team(role)  # não levanta

    @pytest.mark.parametrize("role", [RoleLabel.COACH, RoleLabel.ATHLETE, RoleLabel.MEMBER])
    def test_non_management_blocked(self, role):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_team(role)


# ===========================================================================
# DOMAIN RULES — assert_can_patch_team
# ===========================================================================

class TestAssertCanPatchTeam:
    @pytest.mark.parametrize("role", [RoleLabel.ADMIN, RoleLabel.COORDINATOR])
    def test_management_pass_any_team(self, role):
        assert_can_patch_team(role, [], uuid.uuid4())

    def test_coach_own_team_allowed(self):
        tid = uuid.uuid4()
        assert_can_patch_team(RoleLabel.COACH, [tid], tid)

    def test_coach_other_team_blocked(self):
        with pytest.raises(InsufficientPrivilege, match="PERM-TEAM-001"):
            assert_can_patch_team(RoleLabel.COACH, [], uuid.uuid4())

    @pytest.mark.parametrize("role", [RoleLabel.ATHLETE, RoleLabel.MEMBER])
    def test_athlete_member_blocked(self, role):
        with pytest.raises(InsufficientPrivilege):
            assert_can_patch_team(role, [], uuid.uuid4())


# ===========================================================================
# DOMAIN RULES — assert_can_manage_staff
# ===========================================================================

class TestAssertCanManageStaff:
    @pytest.mark.parametrize("role", [RoleLabel.ADMIN, RoleLabel.COORDINATOR])
    def test_management_allowed(self, role):
        assert_can_manage_staff(role)

    @pytest.mark.parametrize("role", [RoleLabel.COACH, RoleLabel.ATHLETE, RoleLabel.MEMBER])
    def test_others_blocked(self, role):
        with pytest.raises(InsufficientPrivilege):
            assert_can_manage_staff(role)


# ===========================================================================
# DOMAIN RULES — assert_can_manage_athlete
# ===========================================================================

class TestAssertCanManageAthlete:
    @pytest.mark.parametrize("role", [RoleLabel.ADMIN, RoleLabel.COORDINATOR])
    def test_management_pass(self, role):
        assert_can_manage_athlete(role, [], uuid.uuid4())

    def test_coach_own_team_allowed(self):
        tid = uuid.uuid4()
        assert_can_manage_athlete(RoleLabel.COACH, [tid], tid)

    def test_coach_other_team_blocked(self):
        with pytest.raises(InsufficientPrivilege, match="PERM-TEAM-001"):
            assert_can_manage_athlete(RoleLabel.COACH, [], uuid.uuid4())

    @pytest.mark.parametrize("role", [RoleLabel.ATHLETE, RoleLabel.MEMBER])
    def test_athlete_member_blocked(self, role):
        with pytest.raises(InsufficientPrivilege):
            assert_can_manage_athlete(role, [], uuid.uuid4())


# ===========================================================================
# DOMAIN RULES — assert_can_read_team (BOLA)
# ===========================================================================

class TestAssertCanReadTeam:
    @pytest.mark.parametrize("role", [RoleLabel.ADMIN, RoleLabel.COORDINATOR])
    def test_management_pass(self, role):
        assert_can_read_team(role, [], uuid.uuid4())

    @pytest.mark.parametrize("role", [RoleLabel.COACH, RoleLabel.ATHLETE])
    def test_linked_actor_allowed(self, role):
        tid = uuid.uuid4()
        assert_can_read_team(role, [tid], tid)

    @pytest.mark.parametrize("role", [RoleLabel.COACH, RoleLabel.ATHLETE])
    def test_unlinked_actor_blocked(self, role):
        with pytest.raises(InsufficientPrivilege, match="BOLA"):
            assert_can_read_team(role, [], uuid.uuid4())

    def test_member_always_blocked(self):
        tid = uuid.uuid4()
        with pytest.raises(InsufficientPrivilege):
            assert_can_read_team(RoleLabel.MEMBER, [tid], tid)


# ===========================================================================
# DOMAIN RULES — assert_valid_status_transition
# ===========================================================================

class TestAssertValidStatusTransition:
    def test_draft_to_active_ok(self):
        assert_valid_status_transition("DRAFT", "ACTIVE")

    def test_active_to_archived_ok(self):
        assert_valid_status_transition("ACTIVE", "ARCHIVED")

    def test_draft_to_archived_invalid(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_status_transition("DRAFT", "ARCHIVED")

    def test_archived_to_active_invalid(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_status_transition("ARCHIVED", "ACTIVE")

    def test_archived_to_draft_invalid(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_status_transition("ARCHIVED", "DRAFT")

    def test_active_to_draft_invalid(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_status_transition("ACTIVE", "DRAFT")


# ===========================================================================
# APPLICATION — ListTeamsUseCase (FT-024)
# ===========================================================================

class TestListTeamsUseCase:
    def test_admin_gets_all(self):
        repo = MagicMock()
        repo.list_teams.return_value = ([_make_team()], 1)
        result = ListTeamsUseCase(repo).execute(
            ListTeamsInput(actor_role=RoleLabel.ADMIN)
        )
        assert result.total == 1
        repo.list_teams.assert_called_once()

    def test_member_returns_empty(self):
        repo = MagicMock()
        result = ListTeamsUseCase(repo).execute(
            ListTeamsInput(actor_role=RoleLabel.MEMBER)
        )
        assert result.data == []
        assert result.total == 0
        repo.list_teams.assert_not_called()

    def test_coach_bola_filter_applied(self):
        tid = uuid.uuid4()
        repo = MagicMock()
        repo.list_teams.return_value = ([], 0)
        ListTeamsUseCase(repo).execute(
            ListTeamsInput(actor_role=RoleLabel.COACH, actor_team_ids=[tid])
        )
        call_kwargs = repo.list_teams.call_args.kwargs
        assert call_kwargs["team_ids_filter"] == [tid]

    def test_page_size_capped_at_100(self):
        repo = MagicMock()
        repo.list_teams.return_value = ([], 0)
        result = ListTeamsUseCase(repo).execute(
            ListTeamsInput(actor_role=RoleLabel.ADMIN, page_size=999)
        )
        assert result.page_size == 100


# ===========================================================================
# APPLICATION — CreateTeamUseCase (FT-025)
# ===========================================================================

class TestCreateTeamUseCase:
    def test_admin_creates_team(self):
        team = _make_team()
        repo = _mock_repo(team)
        result = CreateTeamUseCase(repo).execute(
            CreateTeamInput(
                actor_role=RoleLabel.ADMIN,
                organization_id=ORG_ID,
                name="Time A",
                category_label="Sub-21",
            )
        )
        repo.save.assert_called_once()
        assert result is team

    def test_coordinator_creates_team(self):
        team = _make_team()
        repo = _mock_repo(team)
        CreateTeamUseCase(repo).execute(
            CreateTeamInput(
                actor_role=RoleLabel.COORDINATOR,
                organization_id=ORG_ID,
                name="Time B",
                category_label="Adulto",
            )
        )
        repo.save.assert_called_once()

    def test_coach_cannot_create(self):
        repo = MagicMock()
        with pytest.raises(InsufficientPrivilege):
            CreateTeamUseCase(repo).execute(
                CreateTeamInput(
                    actor_role=RoleLabel.COACH,
                    organization_id=ORG_ID,
                    name="Time X",
                    category_label="Sub-18",
                )
            )

    def test_status_starts_as_draft(self):
        repo = MagicMock()
        saved_teams = []
        def capture_save(t): saved_teams.append(t); return t
        repo.save.side_effect = capture_save
        CreateTeamUseCase(repo).execute(
            CreateTeamInput(
                actor_role=RoleLabel.ADMIN,
                organization_id=ORG_ID,
                name="Time Draft",
                category_label="Sub-18",
            )
        )
        assert saved_teams[0].status_label == TeamStatus.DRAFT

    def test_duplicate_athlete_ids_deduped(self):
        aid = uuid.uuid4()
        repo = MagicMock()
        captured = []
        def capture_save(t): captured.append(t); return t
        repo.save.side_effect = capture_save
        CreateTeamUseCase(repo).execute(
            CreateTeamInput(
                actor_role=RoleLabel.ADMIN,
                organization_id=ORG_ID,
                name="Time C",
                category_label="Sub-18",
                athlete_ids=[aid, aid],
            )
        )
        assert captured[0].athlete_ids == [aid]


# ===========================================================================
# APPLICATION — GetTeamUseCase (FT-026)
# ===========================================================================

class TestGetTeamUseCase:
    def test_admin_reads_any(self):
        team = _make_team()
        repo = _mock_repo(team)
        result = GetTeamUseCase(repo).execute(
            GetTeamInput(actor_role=RoleLabel.ADMIN, actor_team_ids=[], team_id=TEAM_ID)
        )
        assert result is team

    def test_coach_linked_reads(self):
        team = _make_team()
        repo = _mock_repo(team)
        result = GetTeamUseCase(repo).execute(
            GetTeamInput(actor_role=RoleLabel.COACH, actor_team_ids=[TEAM_ID], team_id=TEAM_ID)
        )
        assert result is team

    def test_coach_unlinked_blocked(self):
        repo = MagicMock()
        with pytest.raises(InsufficientPrivilege):
            GetTeamUseCase(repo).execute(
                GetTeamInput(actor_role=RoleLabel.COACH, actor_team_ids=[], team_id=TEAM_ID)
            )

    def test_member_blocked(self):
        repo = MagicMock()
        with pytest.raises(InsufficientPrivilege):
            GetTeamUseCase(repo).execute(
                GetTeamInput(actor_role=RoleLabel.MEMBER, actor_team_ids=[TEAM_ID], team_id=TEAM_ID)
            )


# ===========================================================================
# APPLICATION — PatchTeamUseCase (FT-027)
# ===========================================================================

class TestPatchTeamUseCase:
    def test_admin_patches_name(self):
        team = _make_team()
        repo = _mock_repo(team)
        repo.update.return_value = team
        PatchTeamUseCase(repo).execute(
            PatchTeamInput(
                actor_role=RoleLabel.ADMIN,
                actor_team_ids=[],
                team_id=TEAM_ID,
                name="Novo Nome",
            )
        )
        repo.update.assert_called_once()

    def test_coach_own_team_patches(self):
        team = _make_team()
        repo = _mock_repo(team)
        repo.update.return_value = team
        PatchTeamUseCase(repo).execute(
            PatchTeamInput(
                actor_role=RoleLabel.COACH,
                actor_team_ids=[TEAM_ID],
                team_id=TEAM_ID,
                roster_notes="Notas de treino",
            )
        )
        repo.update.assert_called_once()

    def test_coach_other_team_blocked(self):
        repo = MagicMock()
        with pytest.raises(InsufficientPrivilege):
            PatchTeamUseCase(repo).execute(
                PatchTeamInput(
                    actor_role=RoleLabel.COACH,
                    actor_team_ids=[],
                    team_id=TEAM_ID,
                    name="X",
                )
            )

    def test_invalid_status_transition_raises(self):
        team = _make_team(status_label=TeamStatus.DRAFT)
        repo = _mock_repo(team)
        with pytest.raises(InvalidStatusTransition):
            PatchTeamUseCase(repo).execute(
                PatchTeamInput(
                    actor_role=RoleLabel.ADMIN,
                    actor_team_ids=[],
                    team_id=TEAM_ID,
                    status_label="ARCHIVED",
                )
            )

    def test_season_null_string_unlinks(self):
        sid = uuid.uuid4()
        team = _make_team(season_id=sid)
        repo = _mock_repo(team)
        captured = []
        def capture_update(t): captured.append(t); return t
        repo.update.side_effect = capture_update
        PatchTeamUseCase(repo).execute(
            PatchTeamInput(
                actor_role=RoleLabel.ADMIN,
                actor_team_ids=[],
                team_id=TEAM_ID,
                season_id="null",
            )
        )
        assert captured[0].season_id is None


# ===========================================================================
# APPLICATION — AddAthleteToTeamUseCase (FT-028)
# ===========================================================================

class TestAddAthleteToTeamUseCase:
    def test_admin_adds_athlete(self):
        team = _make_team()
        repo = _mock_repo(team)
        updated = _make_team(athlete_ids=[ATHLETE_1])
        repo.update.return_value = updated
        result = AddAthleteToTeamUseCase(repo).execute(
            AddAthleteToTeamInput(
                actor_role=RoleLabel.ADMIN,
                actor_team_ids=[],
                team_id=TEAM_ID,
                athlete_user_id=ATHLETE_1,
            )
        )
        repo.update.assert_called_once()
        assert result is updated

    def test_idempotent_already_present(self):
        team = _make_team(athlete_ids=[ATHLETE_1])
        repo = _mock_repo(team)
        repo.update.return_value = team
        AddAthleteToTeamUseCase(repo).execute(
            AddAthleteToTeamInput(
                actor_role=RoleLabel.ADMIN,
                actor_team_ids=[],
                team_id=TEAM_ID,
                athlete_user_id=ATHLETE_1,
            )
        )
        # update é chamado mas athlete_ids não cresce
        updated_team = repo.update.call_args[0][0]
        assert updated_team.athlete_ids.count(ATHLETE_1) == 1

    def test_coach_own_team_adds(self):
        team = _make_team()
        repo = _mock_repo(team)
        repo.update.return_value = team
        AddAthleteToTeamUseCase(repo).execute(
            AddAthleteToTeamInput(
                actor_role=RoleLabel.COACH,
                actor_team_ids=[TEAM_ID],
                team_id=TEAM_ID,
                athlete_user_id=ATHLETE_1,
            )
        )
        repo.update.assert_called_once()

    def test_athlete_blocked(self):
        repo = MagicMock()
        with pytest.raises(InsufficientPrivilege):
            AddAthleteToTeamUseCase(repo).execute(
                AddAthleteToTeamInput(
                    actor_role=RoleLabel.ATHLETE,
                    actor_team_ids=[TEAM_ID],
                    team_id=TEAM_ID,
                    athlete_user_id=ATHLETE_2,
                )
            )


# ===========================================================================
# APPLICATION — RemoveAthleteFromTeamUseCase (FT-029)
# ===========================================================================

class TestRemoveAthleteFromTeamUseCase:
    def test_admin_removes_athlete(self):
        team = _make_team(athlete_ids=[ATHLETE_1])
        repo = _mock_repo(team)
        updated = _make_team(athlete_ids=[])
        repo.update.return_value = updated
        result = RemoveAthleteFromTeamUseCase(repo).execute(
            RemoveAthleteFromTeamInput(
                actor_role=RoleLabel.ADMIN,
                actor_team_ids=[],
                team_id=TEAM_ID,
                athlete_user_id=ATHLETE_1,
            )
        )
        assert result is updated

    def test_idempotent_not_present(self):
        team = _make_team(athlete_ids=[])
        repo = _mock_repo(team)
        repo.update.return_value = team
        RemoveAthleteFromTeamUseCase(repo).execute(
            RemoveAthleteFromTeamInput(
                actor_role=RoleLabel.ADMIN,
                actor_team_ids=[],
                team_id=TEAM_ID,
                athlete_user_id=ATHLETE_2,
            )
        )
        # não levanta, apenas chama update
        repo.update.assert_called_once()

    def test_coach_own_team_removes(self):
        team = _make_team(athlete_ids=[ATHLETE_1])
        repo = _mock_repo(team)
        repo.update.return_value = team
        RemoveAthleteFromTeamUseCase(repo).execute(
            RemoveAthleteFromTeamInput(
                actor_role=RoleLabel.COACH,
                actor_team_ids=[TEAM_ID],
                team_id=TEAM_ID,
                athlete_user_id=ATHLETE_1,
            )
        )
        repo.update.assert_called_once()

    def test_member_blocked(self):
        repo = MagicMock()
        with pytest.raises(InsufficientPrivilege):
            RemoveAthleteFromTeamUseCase(repo).execute(
                RemoveAthleteFromTeamInput(
                    actor_role=RoleLabel.MEMBER,
                    actor_team_ids=[TEAM_ID],
                    team_id=TEAM_ID,
                    athlete_user_id=ATHLETE_1,
                )
            )


# ===========================================================================
# APPLICATION — AddStaffToTeamUseCase (FT-030)
# ===========================================================================

class TestAddStaffToTeamUseCase:
    def test_admin_adds_staff(self):
        team = _make_team()
        repo = _mock_repo(team)
        updated = _make_team(staff_user_ids=[STAFF_1])
        repo.update.return_value = updated
        result = AddStaffToTeamUseCase(repo).execute(
            AddStaffToTeamInput(
                actor_role=RoleLabel.ADMIN,
                team_id=TEAM_ID,
                staff_user_id=STAFF_1,
            )
        )
        repo.update.assert_called_once()
        assert result is updated

    def test_idempotent_already_present(self):
        team = _make_team(staff_user_ids=[STAFF_1])
        repo = _mock_repo(team)
        repo.update.return_value = team
        AddStaffToTeamUseCase(repo).execute(
            AddStaffToTeamInput(
                actor_role=RoleLabel.ADMIN,
                team_id=TEAM_ID,
                staff_user_id=STAFF_1,
            )
        )
        updated_team = repo.update.call_args[0][0]
        assert updated_team.staff_user_ids.count(STAFF_1) == 1

    def test_coach_blocked(self):
        repo = MagicMock()
        with pytest.raises(InsufficientPrivilege):
            AddStaffToTeamUseCase(repo).execute(
                AddStaffToTeamInput(
                    actor_role=RoleLabel.COACH,
                    team_id=TEAM_ID,
                    staff_user_id=STAFF_1,
                )
            )

    def test_coordinator_adds_staff(self):
        team = _make_team()
        repo = _mock_repo(team)
        repo.update.return_value = team
        AddStaffToTeamUseCase(repo).execute(
            AddStaffToTeamInput(
                actor_role=RoleLabel.COORDINATOR,
                team_id=TEAM_ID,
                staff_user_id=STAFF_1,
            )
        )
        repo.update.assert_called_once()


# ===========================================================================
# APPLICATION — RemoveStaffFromTeamUseCase (FT-031)
# ===========================================================================

class TestRemoveStaffFromTeamUseCase:
    def test_admin_removes_staff(self):
        team = _make_team(staff_user_ids=[STAFF_1])
        repo = _mock_repo(team)
        updated = _make_team(staff_user_ids=[])
        repo.update.return_value = updated
        result = RemoveStaffFromTeamUseCase(repo).execute(
            RemoveStaffFromTeamInput(
                actor_role=RoleLabel.ADMIN,
                team_id=TEAM_ID,
                staff_user_id=STAFF_1,
            )
        )
        assert result is updated

    def test_idempotent_not_present(self):
        team = _make_team(staff_user_ids=[])
        repo = _mock_repo(team)
        repo.update.return_value = team
        RemoveStaffFromTeamUseCase(repo).execute(
            RemoveStaffFromTeamInput(
                actor_role=RoleLabel.ADMIN,
                team_id=TEAM_ID,
                staff_user_id=STAFF_1,
            )
        )
        repo.update.assert_called_once()

    def test_athlete_blocked(self):
        repo = MagicMock()
        with pytest.raises(InsufficientPrivilege):
            RemoveStaffFromTeamUseCase(repo).execute(
                RemoveStaffFromTeamInput(
                    actor_role=RoleLabel.ATHLETE,
                    team_id=TEAM_ID,
                    staff_user_id=STAFF_1,
                )
            )

    def test_coordinator_removes_staff(self):
        team = _make_team(staff_user_ids=[STAFF_1])
        repo = _mock_repo(team)
        repo.update.return_value = team
        RemoveStaffFromTeamUseCase(repo).execute(
            RemoveStaffFromTeamInput(
                actor_role=RoleLabel.COORDINATOR,
                team_id=TEAM_ID,
                staff_user_id=STAFF_1,
            )
        )
        repo.update.assert_called_once()
