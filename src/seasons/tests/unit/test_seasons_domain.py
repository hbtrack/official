"""
Testes unitários — módulo seasons.
Camada: domain + application (sem Django, sem DB).
Contrato: contracts/openapi/paths/seasons.yaml
Invariantes: docs/hbtrack/modulos/seasons/INVARIANTS_SEASONS.md
"""
from __future__ import annotations

import uuid
from datetime import date
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest

from seasons.domain.entities import Season, SeasonStatus
from seasons.domain.rules import (
    DuplicateTeamAssociation,
    InsufficientPrivilege,
    InvalidDateRange,
    InvalidStatusTransition,
    RoleLabel,
    SeasonNotFound,
    assert_can_manage_season,
    assert_can_patch_season,
    assert_can_remove_team,
    assert_date_range,
    assert_team_not_in_season,
    assert_valid_status_transition,
)
from seasons.application.use_cases import (
    AddTeamToSeasonInput,
    AddTeamToSeasonUseCase,
    CreateSeasonInput,
    CreateSeasonUseCase,
    GetSeasonInput,
    GetSeasonUseCase,
    ListSeasonsInput,
    ListSeasonsUseCase,
    PatchSeasonInput,
    PatchSeasonUseCase,
    RemoveTeamFromSeasonInput,
    RemoveTeamFromSeasonUseCase,
)

# ---------------------------------------------------------------------------
# Fixtures helpers
# ---------------------------------------------------------------------------

def _make_season(**kwargs) -> Season:
    defaults = dict(
        id=uuid.uuid4(),
        name="Temporada 2026",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        status_label=SeasonStatus.DRAFT,
        phase_labels=["pre-temporada", "fase-regular"],
        team_ids=[],
        competition_ids=[],
        organization_id=None,
        sport_cycle_label=None,
    )
    defaults.update(kwargs)
    return Season(**defaults)


def _mock_repo(season: Season | None = None) -> MagicMock:
    repo = MagicMock()
    if season is not None:
        repo.get_by_id.return_value = season
        repo.save.return_value = season
        repo.update.return_value = season
    return repo


# ===========================================================================
# DOMAIN ENTITIES — SeasonStatus
# ===========================================================================

class TestSeasonStatus:
    def test_values(self):
        assert SeasonStatus.DRAFT == "DRAFT"
        assert SeasonStatus.ACTIVE == "ACTIVE"
        assert SeasonStatus.ARCHIVED == "ARCHIVED"

    def test_is_str_enum(self):
        assert isinstance(SeasonStatus.DRAFT, str)


# ===========================================================================
# DOMAIN ENTITIES — Season + validate_invariants
# ===========================================================================

class TestSeasonEntity:
    def test_valid_season_passes(self):
        s = _make_season()
        s.validate_invariants()  # não levanta

    def test_inv_seas_002_start_after_end_raises(self):
        s = _make_season(start_date=date(2026, 12, 31), end_date=date(2026, 1, 1))
        with pytest.raises(ValueError, match="INV-SEAS-002"):
            s.validate_invariants()

    def test_inv_seas_002_same_dates_ok(self):
        s = _make_season(start_date=date(2026, 6, 1), end_date=date(2026, 6, 1))
        s.validate_invariants()

    def test_inv_seas_003_duplicate_phase_labels_raises(self):
        s = _make_season(phase_labels=["fase-a", "fase-a"])
        with pytest.raises(ValueError, match="INV-SEAS-003"):
            s.validate_invariants()

    def test_inv_seas_003_duplicate_team_ids_raises(self):
        tid = uuid.uuid4()
        s = _make_season(team_ids=[tid, tid])
        with pytest.raises(ValueError, match="INV-SEAS-003"):
            s.validate_invariants()

    def test_inv_seas_003_duplicate_competition_ids_raises(self):
        cid = uuid.uuid4()
        s = _make_season(competition_ids=[cid, cid])
        with pytest.raises(ValueError, match="INV-SEAS-003"):
            s.validate_invariants()

    def test_inv_seas_001_empty_name_raises(self):
        s = _make_season(name="   ")
        with pytest.raises(ValueError, match="INV-SEAS-001"):
            s.validate_invariants()

    def test_inv_seas_001_name_too_long_raises(self):
        s = _make_season(name="x" * 121)
        with pytest.raises(ValueError, match="INV-SEAS-001"):
            s.validate_invariants()

    def test_boundary_no_score_fields(self):
        # INV-SEAS-004: Season não tem campos de scorekeeper, scout ou auth
        s = _make_season()
        assert not hasattr(s, "score")
        assert not hasattr(s, "scout_data")
        assert not hasattr(s, "password")
        assert not hasattr(s, "jwt_token")


# ===========================================================================
# DOMAIN RULES — Guards de permissão
# ===========================================================================

class TestAssertCanManageSeason:
    def test_admin_allowed(self):
        assert_can_manage_season(RoleLabel.ADMIN)

    def test_coordinator_allowed(self):
        assert_can_manage_season(RoleLabel.COORDINATOR)

    def test_coach_blocked(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_manage_season(RoleLabel.COACH)

    def test_athlete_blocked(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_manage_season(RoleLabel.ATHLETE)

    def test_member_blocked(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_manage_season(RoleLabel.MEMBER)


class TestAssertCanRemoveTeam:
    def test_admin_can_remove_from_active(self):
        assert_can_remove_team(RoleLabel.ADMIN, "ACTIVE")

    def test_coordinator_blocked_on_active(self):
        # PERM-SEA-001
        with pytest.raises(InsufficientPrivilege, match="PERM-SEA-001"):
            assert_can_remove_team(RoleLabel.COORDINATOR, "ACTIVE")

    def test_coordinator_can_remove_from_draft(self):
        assert_can_remove_team(RoleLabel.COORDINATOR, "DRAFT")

    def test_coordinator_can_remove_from_archived(self):
        assert_can_remove_team(RoleLabel.COORDINATOR, "ARCHIVED")

    def test_coach_always_blocked(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_remove_team(RoleLabel.COACH, "DRAFT")


class TestAssertCanPatchSeason:
    def test_admin_can_patch_archived(self):
        assert_can_patch_season(RoleLabel.ADMIN, "ARCHIVED")

    def test_coordinator_blocked_on_archived(self):
        # PERM-SEA-002
        with pytest.raises(InsufficientPrivilege, match="PERM-SEA-002"):
            assert_can_patch_season(RoleLabel.COORDINATOR, "ARCHIVED")

    def test_coordinator_can_patch_draft(self):
        assert_can_patch_season(RoleLabel.COORDINATOR, "DRAFT")

    def test_coordinator_can_patch_active(self):
        assert_can_patch_season(RoleLabel.COORDINATOR, "ACTIVE")

    def test_athlete_always_blocked(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_patch_season(RoleLabel.ATHLETE, "DRAFT")


class TestAssertDateRange:
    def test_start_before_end_ok(self):
        assert_date_range(date(2026, 1, 1), date(2026, 12, 31))

    def test_same_date_ok(self):
        assert_date_range(date(2026, 6, 1), date(2026, 6, 1))

    def test_start_after_end_raises(self):
        with pytest.raises(InvalidDateRange, match="INV-SEAS-002"):
            assert_date_range(date(2026, 12, 31), date(2026, 1, 1))


class TestAssertValidStatusTransition:
    def test_draft_to_active_ok(self):
        assert_valid_status_transition("DRAFT", "ACTIVE")

    def test_active_to_archived_ok(self):
        assert_valid_status_transition("ACTIVE", "ARCHIVED")

    def test_draft_to_archived_raises(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_status_transition("DRAFT", "ARCHIVED")

    def test_active_to_draft_raises(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_status_transition("ACTIVE", "DRAFT")

    def test_archived_to_anything_raises(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_status_transition("ARCHIVED", "ACTIVE")

    def test_archived_to_draft_raises(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_status_transition("ARCHIVED", "DRAFT")


class TestAssertTeamNotInSeason:
    def test_new_team_ok(self):
        team_id = uuid.uuid4()
        assert_team_not_in_season(team_id, [])

    def test_duplicate_raises(self):
        team_id = uuid.uuid4()
        with pytest.raises(DuplicateTeamAssociation, match="INV-SEAS-003"):
            assert_team_not_in_season(team_id, [team_id])

    def test_different_team_ok(self):
        t1 = uuid.uuid4()
        t2 = uuid.uuid4()
        assert_team_not_in_season(t1, [t2])


# ===========================================================================
# APPLICATION — ListSeasonsUseCase
# ===========================================================================

class TestListSeasonsUseCase:
    def test_returns_paginated_result(self):
        season = _make_season()
        repo = MagicMock()
        repo.list_seasons.return_value = ([season], 1)
        uc = ListSeasonsUseCase(repo)
        result = uc.execute(ListSeasonsInput(actor_role=RoleLabel.ADMIN))
        assert result.total == 1
        assert len(result.data) == 1
        assert result.page == 1

    def test_page_size_capped_at_100(self):
        repo = MagicMock()
        repo.list_seasons.return_value = ([], 0)
        uc = ListSeasonsUseCase(repo)
        uc.execute(ListSeasonsInput(actor_role=RoleLabel.ADMIN, page_size=9999))
        _, kwargs = repo.list_seasons.call_args
        assert kwargs["page_size"] == 100

    def test_all_roles_can_list(self):
        repo = MagicMock()
        repo.list_seasons.return_value = ([], 0)
        uc = ListSeasonsUseCase(repo)
        for role in RoleLabel:
            uc.execute(ListSeasonsInput(actor_role=role))  # não levanta

    def test_status_filter_normalized_uppercase(self):
        repo = MagicMock()
        repo.list_seasons.return_value = ([], 0)
        uc = ListSeasonsUseCase(repo)
        uc.execute(ListSeasonsInput(actor_role=RoleLabel.ADMIN, status_label="active"))
        _, kwargs = repo.list_seasons.call_args
        assert kwargs["status_label"] == "ACTIVE"

    def test_none_status_filter_passes_none(self):
        repo = MagicMock()
        repo.list_seasons.return_value = ([], 0)
        uc = ListSeasonsUseCase(repo)
        uc.execute(ListSeasonsInput(actor_role=RoleLabel.ADMIN, status_label=None))
        _, kwargs = repo.list_seasons.call_args
        assert kwargs["status_label"] is None


# ===========================================================================
# APPLICATION — CreateSeasonUseCase
# ===========================================================================

class TestCreateSeasonUseCase:
    def test_admin_creates_season(self):
        season = _make_season()
        repo = MagicMock()
        repo.save.return_value = season
        uc = CreateSeasonUseCase(repo)
        result = uc.execute(CreateSeasonInput(
            actor_role=RoleLabel.ADMIN,
            name="Temporada 2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        ))
        assert result is season
        repo.save.assert_called_once()

    def test_coordinator_creates_season(self):
        season = _make_season()
        repo = MagicMock()
        repo.save.return_value = season
        uc = CreateSeasonUseCase(repo)
        uc.execute(CreateSeasonInput(
            actor_role=RoleLabel.COORDINATOR,
            name="Temporada 2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        ))
        repo.save.assert_called_once()

    def test_coach_cannot_create(self):
        repo = MagicMock()
        uc = CreateSeasonUseCase(repo)
        with pytest.raises(InsufficientPrivilege):
            uc.execute(CreateSeasonInput(
                actor_role=RoleLabel.COACH,
                name="T",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 31),
            ))

    def test_invalid_date_range_raises(self):
        repo = MagicMock()
        uc = CreateSeasonUseCase(repo)
        with pytest.raises(InvalidDateRange):
            uc.execute(CreateSeasonInput(
                actor_role=RoleLabel.ADMIN,
                name="T",
                start_date=date(2026, 12, 31),
                end_date=date(2026, 1, 1),
            ))

    def test_new_season_starts_as_draft(self):
        repo = MagicMock()
        created = None

        def capture_save(s):
            nonlocal created
            created = s
            return s

        repo.save.side_effect = capture_save
        uc = CreateSeasonUseCase(repo)
        uc.execute(CreateSeasonInput(
            actor_role=RoleLabel.ADMIN,
            name="T",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        ))
        assert created.status_label == SeasonStatus.DRAFT

    def test_duplicate_phase_labels_deduplicated(self):
        repo = MagicMock()
        created = None

        def capture_save(s):
            nonlocal created
            created = s
            return s

        repo.save.side_effect = capture_save
        uc = CreateSeasonUseCase(repo)
        uc.execute(CreateSeasonInput(
            actor_role=RoleLabel.ADMIN,
            name="T",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            phase_labels=["fase-a", "fase-a", "fase-b"],
        ))
        assert created.phase_labels == ["fase-a", "fase-b"]


# ===========================================================================
# APPLICATION — GetSeasonUseCase
# ===========================================================================

class TestGetSeasonUseCase:
    def test_all_roles_can_get(self):
        season = _make_season()
        for role in RoleLabel:
            repo = _mock_repo(season)
            uc = GetSeasonUseCase(repo)
            result = uc.execute(GetSeasonInput(actor_role=role, season_id=season.id))
            assert result is season

    def test_not_found_propagates(self):
        repo = MagicMock()
        repo.get_by_id.side_effect = SeasonNotFound("not found")
        uc = GetSeasonUseCase(repo)
        with pytest.raises(SeasonNotFound):
            uc.execute(GetSeasonInput(actor_role=RoleLabel.ADMIN, season_id=uuid.uuid4()))


# ===========================================================================
# APPLICATION — PatchSeasonUseCase
# ===========================================================================

class TestPatchSeasonUseCase:
    def test_patch_name(self):
        season = _make_season()
        repo = _mock_repo(season)
        uc = PatchSeasonUseCase(repo)
        uc.execute(PatchSeasonInput(
            actor_role=RoleLabel.ADMIN,
            season_id=season.id,
            name="Novo Nome",
        ))
        assert season.name == "Novo Nome"

    def test_patch_status_draft_to_active(self):
        season = _make_season(status_label=SeasonStatus.DRAFT)
        repo = _mock_repo(season)
        uc = PatchSeasonUseCase(repo)
        uc.execute(PatchSeasonInput(
            actor_role=RoleLabel.ADMIN,
            season_id=season.id,
            status_label="active",
        ))
        assert season.status_label == SeasonStatus.ACTIVE

    def test_invalid_date_range_on_patch_raises(self):
        season = _make_season()
        repo = _mock_repo(season)
        uc = PatchSeasonUseCase(repo)
        with pytest.raises((InvalidDateRange, ValueError)):
            uc.execute(PatchSeasonInput(
                actor_role=RoleLabel.ADMIN,
                season_id=season.id,
                start_date=date(2026, 12, 31),
                end_date=date(2026, 1, 1),
            ))

    def test_coordinator_blocked_on_archived(self):
        season = _make_season(status_label=SeasonStatus.ARCHIVED)
        repo = _mock_repo(season)
        uc = PatchSeasonUseCase(repo)
        with pytest.raises(InsufficientPrivilege, match="PERM-SEA-002"):
            uc.execute(PatchSeasonInput(
                actor_role=RoleLabel.COORDINATOR,
                season_id=season.id,
                name="Novo",
            ))

    def test_coach_cannot_patch(self):
        season = _make_season()
        repo = _mock_repo(season)
        uc = PatchSeasonUseCase(repo)
        with pytest.raises(InsufficientPrivilege):
            uc.execute(PatchSeasonInput(
                actor_role=RoleLabel.COACH,
                season_id=season.id,
                name="Novo",
            ))

    def test_invalid_status_transition_raises(self):
        season = _make_season(status_label=SeasonStatus.ARCHIVED)
        repo = _mock_repo(season)
        uc = PatchSeasonUseCase(repo)
        # Admin pode editar ARCHIVED mas não pode transicionar
        with pytest.raises(InvalidStatusTransition):
            uc.execute(PatchSeasonInput(
                actor_role=RoleLabel.ADMIN,
                season_id=season.id,
                status_label="DRAFT",
            ))

    def test_phase_labels_replace_full_array(self):
        season = _make_season(phase_labels=["velha"])
        repo = _mock_repo(season)
        uc = PatchSeasonUseCase(repo)
        uc.execute(PatchSeasonInput(
            actor_role=RoleLabel.ADMIN,
            season_id=season.id,
            phase_labels=["nova1", "nova2"],
        ))
        assert season.phase_labels == ["nova1", "nova2"]


# ===========================================================================
# APPLICATION — AddTeamToSeasonUseCase
# ===========================================================================

class TestAddTeamToSeasonUseCase:
    def test_admin_adds_team(self):
        team_id = uuid.uuid4()
        season = _make_season(team_ids=[])
        repo = _mock_repo(season)
        uc = AddTeamToSeasonUseCase(repo)
        uc.execute(AddTeamToSeasonInput(
            actor_role=RoleLabel.ADMIN,
            season_id=season.id,
            team_id=team_id,
        ))
        repo.update.assert_called_once()

    def test_duplicate_team_raises(self):
        team_id = uuid.uuid4()
        season = _make_season(team_ids=[team_id])
        repo = _mock_repo(season)
        uc = AddTeamToSeasonUseCase(repo)
        with pytest.raises(DuplicateTeamAssociation):
            uc.execute(AddTeamToSeasonInput(
                actor_role=RoleLabel.ADMIN,
                season_id=season.id,
                team_id=team_id,
            ))

    def test_coach_cannot_add_team(self):
        team_id = uuid.uuid4()
        season = _make_season(team_ids=[])
        repo = _mock_repo(season)
        uc = AddTeamToSeasonUseCase(repo)
        with pytest.raises(InsufficientPrivilege):
            uc.execute(AddTeamToSeasonInput(
                actor_role=RoleLabel.COACH,
                season_id=season.id,
                team_id=team_id,
            ))

    def test_team_added_to_list(self):
        t1 = uuid.uuid4()
        t2 = uuid.uuid4()
        season = _make_season(team_ids=[t1])
        updated = None

        def capture_update(s):
            nonlocal updated
            updated = s
            return s

        repo = MagicMock()
        repo.get_by_id.return_value = season
        repo.update.side_effect = capture_update
        uc = AddTeamToSeasonUseCase(repo)
        uc.execute(AddTeamToSeasonInput(
            actor_role=RoleLabel.ADMIN,
            season_id=season.id,
            team_id=t2,
        ))
        assert t2 in updated.team_ids

    def test_missing_season_raises_not_found(self):
        repo = MagicMock()
        repo.get_by_id.return_value = None
        uc = AddTeamToSeasonUseCase(repo)

        with pytest.raises(SeasonNotFound, match="não encontrada"):
            uc.execute(AddTeamToSeasonInput(
                actor_role=RoleLabel.ADMIN,
                season_id=uuid.uuid4(),
                team_id=uuid.uuid4(),
            ))


# ===========================================================================
# APPLICATION — RemoveTeamFromSeasonUseCase
# ===========================================================================

class TestRemoveTeamFromSeasonUseCase:
    def test_admin_removes_team_from_active(self):
        team_id = uuid.uuid4()
        season = _make_season(team_ids=[team_id], status_label=SeasonStatus.ACTIVE)
        repo = _mock_repo(season)
        uc = RemoveTeamFromSeasonUseCase(repo)
        uc.execute(RemoveTeamFromSeasonInput(
            actor_role=RoleLabel.ADMIN,
            season_id=season.id,
            team_id=team_id,
        ))
        repo.update.assert_called_once()

    def test_coordinator_blocked_on_active_season(self):
        team_id = uuid.uuid4()
        season = _make_season(team_ids=[team_id], status_label=SeasonStatus.ACTIVE)
        repo = _mock_repo(season)
        uc = RemoveTeamFromSeasonUseCase(repo)
        with pytest.raises(InsufficientPrivilege, match="PERM-SEA-001"):
            uc.execute(RemoveTeamFromSeasonInput(
                actor_role=RoleLabel.COORDINATOR,
                season_id=season.id,
                team_id=team_id,
            ))

    def test_team_not_in_season_raises(self):
        team_id = uuid.uuid4()
        season = _make_season(team_ids=[])
        repo = _mock_repo(season)
        uc = RemoveTeamFromSeasonUseCase(repo)
        with pytest.raises(SeasonNotFound):
            uc.execute(RemoveTeamFromSeasonInput(
                actor_role=RoleLabel.ADMIN,
                season_id=season.id,
                team_id=team_id,
            ))

    def test_team_removed_from_list(self):
        t1 = uuid.uuid4()
        t2 = uuid.uuid4()
        season = _make_season(team_ids=[t1, t2], status_label=SeasonStatus.DRAFT)
        updated = None

        def capture_update(s):
            nonlocal updated
            updated = s
            return s

        repo = MagicMock()
        repo.get_by_id.return_value = season
        repo.update.side_effect = capture_update
        uc = RemoveTeamFromSeasonUseCase(repo)
        uc.execute(RemoveTeamFromSeasonInput(
            actor_role=RoleLabel.ADMIN,
            season_id=season.id,
            team_id=t1,
        ))
        assert t1 not in updated.team_ids
        assert t2 in updated.team_ids

    def test_athlete_cannot_remove_team(self):
        team_id = uuid.uuid4()
        season = _make_season(team_ids=[team_id])
        repo = _mock_repo(season)
        uc = RemoveTeamFromSeasonUseCase(repo)
        with pytest.raises(InsufficientPrivilege):
            uc.execute(RemoveTeamFromSeasonInput(
                actor_role=RoleLabel.ATHLETE,
                season_id=season.id,
                team_id=team_id,
            ))
