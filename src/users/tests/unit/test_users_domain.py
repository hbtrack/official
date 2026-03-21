"""
Testes unitários — módulo users.
Cobertura: domain/entities.py, domain/rules.py, application/use_cases.py
Sem dependências de Django ou psycopg2 (TYPE_CHECKING guard em use_cases.py).
"""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from users.domain.entities import RoleLabel, UserProfile, UserStatus
from users.domain.rules import (
    AuthnFieldForbidden,
    InsufficientPrivilege,
    UserNotFound,
    apply_status_transition,
    assert_can_create_user,
    assert_can_patch_role_label,
    assert_can_patch_user,
    assert_can_read_user,
    assert_no_authn_fields,
)
from users.application.use_cases import (
    CreateUserInput,
    CreateUserUseCase,
    GetUserInput,
    GetUserUseCase,
    ListUsersInput,
    ListUsersUseCase,
    PatchUserInput,
    PatchUserUseCase,
)


def _make_profile(**kwargs) -> UserProfile:
    defaults = dict(
        id=uuid.uuid4(),
        display_name="Ana Silva",
        role_label=RoleLabel.ATHLETE,
        status_label=UserStatus.ACTIVE,
    )
    defaults.update(kwargs)
    return UserProfile(**defaults)


# ===========================================================================
# TestUserProfileInvariants
# ===========================================================================

class TestUserProfileInvariants:
    """INV-USR-001, INV-USR-002, INV-USR-003"""

    def test_valid_profile_passes(self):
        p = _make_profile()
        p.validate_invariants()  # não levanta

    def test_missing_display_name_raises(self):
        p = _make_profile(display_name="")
        with pytest.raises(ValueError, match="INV-USR-001"):
            p.validate_invariants()

    def test_invalid_role_label_raises(self):
        p = _make_profile()
        p.role_label = "superuser"  # type: ignore
        with pytest.raises(ValueError, match="INV-USR-001"):
            p.validate_invariants()

    def test_duplicate_team_ids_raises(self):
        uid = uuid.uuid4()
        p = _make_profile(team_ids=[uid, uid])
        with pytest.raises(ValueError, match="INV-USR-002"):
            p.validate_invariants()

    def test_duplicate_season_ids_raises(self):
        uid = uuid.uuid4()
        p = _make_profile(season_ids=[uid, uid])
        with pytest.raises(ValueError, match="INV-USR-002"):
            p.validate_invariants()

    def test_duplicate_preference_tags_raises(self):
        p = _make_profile(preference_tags=["dark-mode", "dark-mode"])
        with pytest.raises(ValueError, match="INV-USR-002"):
            p.validate_invariants()

    def test_all_five_canonical_roles(self):
        for role in RoleLabel:
            p = _make_profile(role_label=role)
            p.validate_invariants()

    def test_all_status_values(self):
        for status in UserStatus:
            p = _make_profile(status_label=status)
            p.validate_invariants()


# ===========================================================================
# TestDomainRules
# ===========================================================================

class TestDomainRules:
    """Testes das funções de regra de domínio."""

    def test_assert_can_create_user_admin_ok(self):
        assert_can_create_user(RoleLabel.ADMIN)

    def test_assert_can_create_user_coordinator_ok(self):
        assert_can_create_user(RoleLabel.COORDINATOR)

    def test_assert_can_create_user_coach_denied(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_user(RoleLabel.COACH)

    def test_assert_can_create_user_athlete_denied(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_create_user(RoleLabel.ATHLETE)

    def test_assert_can_read_owner_always_ok(self):
        uid = uuid.uuid4()
        assert_can_read_user(uid, RoleLabel.ATHLETE, uid, [], [])

    def test_assert_can_read_admin_any_user(self):
        assert_can_read_user(uuid.uuid4(), RoleLabel.ADMIN, uuid.uuid4(), [], [])

    def test_assert_can_read_coach_same_team_ok(self):
        team = uuid.uuid4()
        assert_can_read_user(uuid.uuid4(), RoleLabel.COACH, uuid.uuid4(), [team], [team])

    def test_assert_can_read_coach_different_team_denied(self):
        with pytest.raises(InsufficientPrivilege, match="PERM-USR-006"):
            assert_can_read_user(uuid.uuid4(), RoleLabel.COACH, uuid.uuid4(), [uuid.uuid4()], [uuid.uuid4()])

    def test_assert_can_read_member_denied(self):
        with pytest.raises(InsufficientPrivilege, match="PERM-USR-005"):
            assert_can_read_user(uuid.uuid4(), RoleLabel.MEMBER, uuid.uuid4(), [], [])

    def test_assert_can_patch_owner_ok(self):
        uid = uuid.uuid4()
        assert_can_patch_user(uid, RoleLabel.ATHLETE, uid)

    def test_assert_can_patch_admin_others_ok(self):
        assert_can_patch_user(uuid.uuid4(), RoleLabel.ADMIN, uuid.uuid4())

    def test_assert_can_patch_coach_others_denied(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_patch_user(uuid.uuid4(), RoleLabel.COACH, uuid.uuid4())

    def test_assert_can_patch_role_label_admin_ok(self):
        assert_can_patch_role_label(uuid.uuid4(), RoleLabel.ADMIN, uuid.uuid4())

    def test_assert_can_patch_role_label_athlete_denied(self):
        with pytest.raises(InsufficientPrivilege, match="PERM-USR-004"):
            assert_can_patch_role_label(uuid.uuid4(), RoleLabel.ATHLETE, uuid.uuid4())

    def test_assert_no_authn_fields_clean(self):
        assert_no_authn_fields({"firstName", "displayName"})

    def test_assert_no_authn_fields_password_denied(self):
        with pytest.raises(AuthnFieldForbidden, match="INV-USR-003"):
            assert_no_authn_fields({"password_hash"})

    def test_assert_no_authn_fields_jwt_denied(self):
        with pytest.raises(AuthnFieldForbidden, match="INV-USR-003"):
            assert_no_authn_fields({"jwt", "firstName"})


# ===========================================================================
# TestListUsersUseCase
# ===========================================================================

class TestListUsersUseCase:
    def _repo(self, profiles=None):
        repo = MagicMock()
        repo.list_users.return_value = (profiles or [], None)
        return repo

    def test_member_cannot_list(self):
        inp = ListUsersInput(
            actor_id=uuid.uuid4(),
            actor_role=RoleLabel.MEMBER,
            actor_team_ids=[],
        )
        with pytest.raises(InsufficientPrivilege, match="PERM-USR-005"):
            ListUsersUseCase(self._repo()).execute(inp)

    def test_admin_can_list(self):
        profile = _make_profile()
        repo = self._repo([profile])
        inp = ListUsersInput(
            actor_id=uuid.uuid4(),
            actor_role=RoleLabel.ADMIN,
            actor_team_ids=[],
        )
        result = ListUsersUseCase(repo).execute(inp)
        assert len(result.items) == 1

    def test_page_size_capped_at_100(self):
        repo = self._repo()
        inp = ListUsersInput(
            actor_id=uuid.uuid4(),
            actor_role=RoleLabel.ADMIN,
            actor_team_ids=[],
            page_size=500,
        )
        ListUsersUseCase(repo).execute(inp)
        _, kwargs = repo.list_users.call_args
        assert kwargs["page_size"] == 100  # OWASP API4:2023

    def test_coach_filter_allowed_team(self):
        team = uuid.uuid4()
        repo = self._repo()
        inp = ListUsersInput(
            actor_id=uuid.uuid4(),
            actor_role=RoleLabel.COACH,
            actor_team_ids=[team],
            team_id=team,
        )
        ListUsersUseCase(repo).execute(inp)

    def test_coach_filter_disallowed_team_denied(self):
        team_a = uuid.uuid4()
        team_b = uuid.uuid4()
        repo = self._repo()
        inp = ListUsersInput(
            actor_id=uuid.uuid4(),
            actor_role=RoleLabel.COACH,
            actor_team_ids=[team_a],
            team_id=team_b,
        )
        with pytest.raises(InsufficientPrivilege, match="PERM-USR-006"):
            ListUsersUseCase(repo).execute(inp)


# ===========================================================================
# TestCreateUserUseCase
# ===========================================================================

class TestCreateUserUseCase:
    def _repo(self):
        repo = MagicMock()
        repo.save.side_effect = lambda p: p
        return repo

    def test_admin_creates_athlete(self):
        inp = CreateUserInput(
            actor_role=RoleLabel.ADMIN,
            display_name="João",
            role_label=RoleLabel.ATHLETE,
        )
        profile = CreateUserUseCase(self._repo()).execute(inp)
        assert profile.display_name == "João"
        assert profile.status_label == UserStatus.PENDING_ACTIVATION

    def test_coordinator_creates_coach(self):
        inp = CreateUserInput(
            actor_role=RoleLabel.COORDINATOR,
            display_name="Maria",
            role_label=RoleLabel.COACH,
        )
        profile = CreateUserUseCase(self._repo()).execute(inp)
        assert profile.role_label == RoleLabel.COACH

    def test_coach_cannot_create(self):
        inp = CreateUserInput(
            actor_role=RoleLabel.COACH,
            display_name="X",
            role_label=RoleLabel.ATHLETE,
        )
        with pytest.raises(InsufficientPrivilege, match="PERM-USR-002"):
            CreateUserUseCase(self._repo()).execute(inp)

    def test_deduplicates_preference_tags(self):
        inp = CreateUserInput(
            actor_role=RoleLabel.ADMIN,
            display_name="Ana",
            role_label=RoleLabel.ATHLETE,
            preference_tags=["dark-mode", "dark-mode", "mobile"],
        )
        profile = CreateUserUseCase(self._repo()).execute(inp)
        assert len(profile.preference_tags) == 2


# ===========================================================================
# TestGetUserUseCase
# ===========================================================================

class TestGetUserUseCase:
    def test_returns_profile_for_owner(self):
        uid = uuid.uuid4()
        profile = _make_profile(id=uid)
        repo = MagicMock()
        repo.get_by_id.return_value = profile

        result = GetUserUseCase(repo).execute(GetUserInput(
            actor_id=uid,
            actor_role=RoleLabel.ATHLETE,
            actor_team_ids=[],
            target_user_id=uid,
        ))
        assert result.id == uid

    def test_raises_not_found(self):
        repo = MagicMock()
        repo.get_by_id.return_value = None
        with pytest.raises(UserNotFound):
            GetUserUseCase(repo).execute(GetUserInput(
                actor_id=uuid.uuid4(),
                actor_role=RoleLabel.ADMIN,
                actor_team_ids=[],
                target_user_id=uuid.uuid4(),
            ))

    def test_member_denied_for_other(self):
        uid = uuid.uuid4()
        profile = _make_profile(id=uuid.uuid4())
        repo = MagicMock()
        repo.get_by_id.return_value = profile
        with pytest.raises(InsufficientPrivilege):
            GetUserUseCase(repo).execute(GetUserInput(
                actor_id=uid,
                actor_role=RoleLabel.MEMBER,
                actor_team_ids=[],
                target_user_id=profile.id,
            ))


# ===========================================================================
# TestPatchUserUseCase
# ===========================================================================

class TestPatchUserUseCase:
    def test_owner_patches_own_display_name(self):
        uid = uuid.uuid4()
        profile = _make_profile(id=uid)
        repo = MagicMock()
        repo.get_by_id.return_value = profile
        repo.save.side_effect = lambda p: p

        result = PatchUserUseCase(repo).execute(PatchUserInput(
            actor_id=uid,
            actor_role=RoleLabel.ATHLETE,
            target_user_id=uid,
            display_name="Novo Nome",
        ))
        assert result.display_name == "Novo Nome"

    def test_athlete_cannot_patch_role_label(self):
        uid = uuid.uuid4()
        profile = _make_profile(id=uuid.uuid4())
        repo = MagicMock()
        repo.get_by_id.return_value = profile
        with pytest.raises(InsufficientPrivilege):
            PatchUserUseCase(repo).execute(PatchUserInput(
                actor_id=uid,
                actor_role=RoleLabel.ATHLETE,
                target_user_id=profile.id,
                role_label=RoleLabel.ADMIN,
            ))

    def test_admin_patches_role_label(self):
        uid = uuid.uuid4()
        profile = _make_profile(id=uuid.uuid4())
        repo = MagicMock()
        repo.get_by_id.return_value = profile
        repo.save.side_effect = lambda p: p

        result = PatchUserUseCase(repo).execute(PatchUserInput(
            actor_id=uid,
            actor_role=RoleLabel.ADMIN,
            target_user_id=profile.id,
            role_label=RoleLabel.COACH,
        ))
        assert result.role_label == RoleLabel.COACH

    def test_not_found_raises(self):
        repo = MagicMock()
        repo.get_by_id.return_value = None
        with pytest.raises(UserNotFound):
            PatchUserUseCase(repo).execute(PatchUserInput(
                actor_id=uuid.uuid4(),
                actor_role=RoleLabel.ADMIN,
                target_user_id=uuid.uuid4(),
                display_name="X",
            ))
