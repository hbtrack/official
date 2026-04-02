"""
Testes unitários do módulo identity_access.
Testam entidades, regras de domínio e use cases isolados (mock repository).
Sem dependência de Django, PostgreSQL ou JWT — domínio puro.
"""
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

import pytest

from identity_access.domain.entities import AuthSession, RoleLabel, UserRoleBinding
from identity_access.domain.rules import (
    InvalidRole,
    InsufficientPrivilege,
    LastAdminProtection,
    SessionExpired,
    SessionRevoked,
    assert_can_assign_or_revoke_role,
    assert_can_revoke_session,
    assert_not_last_admin,
    assert_role_canonical,
    assert_session_active,
)
from identity_access.application.use_cases import (
    AssignRoleUseCase,
    GetCurrentSessionUseCase,
    ListActiveSessionsUseCase,
    ListUserRolesUseCase,
    LoginUseCase,
    LogoutUseCase,
    RevokeRoleUseCase,
    RevokeSessionUseCase,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

NOW = datetime.now(tz=timezone.utc)
FUTURE = NOW + timedelta(hours=12)
PAST = NOW - timedelta(hours=1)


def make_session(**kwargs) -> AuthSession:
    defaults = dict(
        id=uuid.uuid4(),
        principal_user_id=uuid.uuid4(),
        session_scope_label="web",
        role_labels=["coach"],
        auth_method_label="password",
        mfa_required=False,
        mfa_satisfied=True,
        issued_at=NOW,
        expires_at=FUTURE,
        revoked_at=None,
    )
    defaults.update(kwargs)
    return AuthSession(**defaults)


# ── Entidades: AuthSession ────────────────────────────────────────────────────

class TestAuthSessionInvariants:
    def test_valid_session_passes(self):
        session = make_session()
        session.validate_invariants()  # sem exceção

    def test_empty_scope_label_raises(self):
        session = make_session(session_scope_label="")
        with pytest.raises(ValueError, match="INV-IAM-001"):
            session.validate_invariants()

    def test_scope_label_too_long_raises(self):
        session = make_session(session_scope_label="x" * 81)
        with pytest.raises(ValueError, match="INV-IAM-001"):
            session.validate_invariants()

    def test_duplicate_role_labels_raises(self):
        session = make_session(role_labels=["admin", "admin"])
        with pytest.raises(ValueError, match="INV-IAM-002"):
            session.validate_invariants()

    def test_expired_at_before_issued_at_raises(self):
        session = make_session(issued_at=FUTURE, expires_at=NOW)
        with pytest.raises(ValueError, match="INV-IAM-003"):
            session.validate_invariants()

    def test_revoked_at_before_issued_at_raises(self):
        session = make_session(revoked_at=PAST - timedelta(hours=2))
        session.issued_at = NOW
        with pytest.raises(ValueError, match="INV-IAM-003"):
            session.validate_invariants()

    def test_is_active_revoked_returns_false(self):
        session = make_session(revoked_at=PAST)
        assert not session.is_active()

    def test_is_active_expired_returns_false(self):
        session = make_session(expires_at=PAST)
        assert not session.is_active()

    def test_is_active_valid_returns_true(self):
        session = make_session()
        assert session.is_active()


# ── Entidades: UserRoleBinding ────────────────────────────────────────────────

class TestUserRoleBinding:
    def test_canonical_role_passes(self):
        binding = UserRoleBinding(id=uuid.uuid4(), user_id=uuid.uuid4(), role_label="admin")
        binding.validate_invariants()

    def test_non_canonical_role_raises(self):
        binding = UserRoleBinding(id=uuid.uuid4(), user_id=uuid.uuid4(), role_label="superuser")
        with pytest.raises(ValueError, match="DR-IAM-003"):
            binding.validate_invariants()


# ── Regras de domínio ─────────────────────────────────────────────────────────

class TestDomainRules:
    def test_assert_session_active_revoked(self):
        session = make_session(revoked_at=PAST)
        with pytest.raises(SessionRevoked):
            assert_session_active(session)

    def test_assert_session_active_expired(self):
        session = make_session(expires_at=PAST)
        with pytest.raises(SessionExpired):
            assert_session_active(session)

    def test_assert_role_canonical_valid(self):
        for role in ["admin", "coordinator", "coach", "athlete", "member"]:
            assert_role_canonical(role)  # sem exceção

    def test_assert_role_canonical_invalid(self):
        with pytest.raises(InvalidRole):
            assert_role_canonical("root")

    def test_assert_not_last_admin_blocks_if_only_one(self):
        with pytest.raises(LastAdminProtection):
            assert_not_last_admin(["admin"], "admin")

    def test_assert_not_last_admin_allows_if_multiple(self):
        assert_not_last_admin(["admin", "admin"], "admin")  # sem exceção

    def test_assert_not_last_admin_non_admin_role_always_passes(self):
        assert_not_last_admin(["admin"], "coordinator")  # sem exceção

    def test_assert_can_revoke_session_admin_can_revoke_any(self):
        assert_can_revoke_session(
            caller_user_id=uuid.uuid4(),
            caller_roles=["admin"],
            session_principal_user_id=uuid.uuid4(),
        )

    def test_assert_can_revoke_session_owner_can_revoke_own(self):
        uid = uuid.uuid4()
        assert_can_revoke_session(
            caller_user_id=uid,
            caller_roles=["coach"],
            session_principal_user_id=uid,
        )

    def test_assert_can_revoke_session_non_owner_raises(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_revoke_session(
                caller_user_id=uuid.uuid4(),
                caller_roles=["coach"],
                session_principal_user_id=uuid.uuid4(),
            )

    def test_assert_can_assign_role_admin_allowed(self):
        assert_can_assign_or_revoke_role(["admin"], "coach")

    def test_assert_can_assign_role_non_admin_raises(self):
        with pytest.raises(InsufficientPrivilege):
            assert_can_assign_or_revoke_role(["coordinator"], "athlete")


# ── Use Cases ─────────────────────────────────────────────────────────────────

class TestLoginUseCase:
    def test_valid_credentials_return_session_and_tokens(self):
        repo = MagicMock()
        user_id = uuid.uuid4()
        repo.verify_credentials.return_value = (user_id, ["coach"])
        repo.issue_tokens.return_value = ("access_tok", "refresh_tok")

        session, access, refresh = LoginUseCase(repo).execute("a@b.com", "password123")

        assert session.principal_user_id == user_id
        assert session.role_labels == ["coach"]
        assert access == "access_tok"
        assert refresh == "refresh_tok"
        repo.save_session.assert_called_once()

    def test_invalid_credentials_raise_value_error(self):
        repo = MagicMock()
        repo.verify_credentials.return_value = (None, [])

        with pytest.raises(ValueError, match="Credenciais inválidas"):
            LoginUseCase(repo).execute("a@b.com", "wrong")


class TestLogoutUseCase:
    def test_revokes_active_session(self):
        repo = MagicMock()
        session = make_session()
        repo.get_session_by_id.return_value = session

        LogoutUseCase(repo).execute(session.id)

        assert session.revoked_at is not None
        repo.save_session.assert_called_once()
        repo.revoke_refresh_tokens_for_session.assert_called_once_with(session.id)

    def test_idempotent_for_nonexistent_session(self):
        repo = MagicMock()
        repo.get_session_by_id.return_value = None

        LogoutUseCase(repo).execute(uuid.uuid4())  # sem exceção

        repo.save_session.assert_not_called()

    def test_revokes_session_even_when_existing_timestamps_are_stale(self):
        repo = MagicMock()
        session = make_session(issued_at=FUTURE + timedelta(hours=1))
        repo.get_session_by_id.return_value = session

        LogoutUseCase(repo).execute(session.id)

        assert session.revoked_at is not None
        repo.save_session.assert_called_once_with(session)
        repo.revoke_refresh_tokens_for_session.assert_called_once_with(session.id)


class TestGetCurrentSessionUseCase:
    def test_returns_active_session(self):
        repo = MagicMock()
        session = make_session()
        repo.get_session_by_id.return_value = session

        result = GetCurrentSessionUseCase(repo).execute(session.id)
        assert result.id == session.id

    def test_raises_for_nonexistent_session(self):
        repo = MagicMock()
        repo.get_session_by_id.return_value = None

        with pytest.raises(ValueError, match="não encontrada"):
            GetCurrentSessionUseCase(repo).execute(uuid.uuid4())

    def test_raises_for_revoked_session(self):
        repo = MagicMock()
        session = make_session(revoked_at=PAST)
        repo.get_session_by_id.return_value = session

        with pytest.raises(SessionRevoked):
            GetCurrentSessionUseCase(repo).execute(session.id)


class TestListActiveSessionsUseCase:
    def test_admin_can_list(self):
        repo = MagicMock()
        repo.list_active_sessions.return_value = ([], None)

        ListActiveSessionsUseCase(repo).execute(caller_roles=["admin"])
        repo.list_active_sessions.assert_called_once()

    def test_non_admin_raises(self):
        repo = MagicMock()

        with pytest.raises(InsufficientPrivilege):
            ListActiveSessionsUseCase(repo).execute(caller_roles=["coach"])


class TestAssignRoleUseCase:
    def test_admin_can_assign_role(self):
        repo = MagicMock()
        user_id = uuid.uuid4()
        repo.user_exists.return_value = True
        repo.get_user_roles.side_effect = [[], ["coach"]]

        roles = AssignRoleUseCase(repo).execute(
            user_id=user_id, role_label="coach", caller_roles=["admin"]
        )
        repo.save_role_binding.assert_called_once()
        assert "coach" in roles

    def test_non_admin_cannot_assign(self):
        repo = MagicMock()
        with pytest.raises(InsufficientPrivilege):
            AssignRoleUseCase(repo).execute(
                user_id=uuid.uuid4(), role_label="coach", caller_roles=["coordinator"]
            )

    def test_duplicate_role_raises(self):
        repo = MagicMock()
        repo.user_exists.return_value = True
        repo.get_user_roles.return_value = ["coach"]

        with pytest.raises(ValueError, match="já atribuído"):
            AssignRoleUseCase(repo).execute(
                user_id=uuid.uuid4(), role_label="coach", caller_roles=["admin"]
            )


class TestRevokeRoleUseCase:
    def test_admin_can_revoke_non_last_admin(self):
        repo = MagicMock()
        user_id = uuid.uuid4()
        repo.user_exists.return_value = True
        repo.get_user_roles.return_value = ["admin"]
        repo.count_global_role.return_value = 2  # há outro admin

        RevokeRoleUseCase(repo).execute(
            user_id=user_id, role_label="admin", caller_roles=["admin"]
        )
        repo.delete_role_binding.assert_called_once_with(user_id, "admin")

    def test_last_admin_protection(self):
        repo = MagicMock()
        repo.user_exists.return_value = True
        repo.get_user_roles.return_value = ["admin"]
        repo.count_global_role.return_value = 1  # único admin

        with pytest.raises(LastAdminProtection):
            RevokeRoleUseCase(repo).execute(
                user_id=uuid.uuid4(), role_label="admin", caller_roles=["admin"]
            )

    def test_non_admin_cannot_revoke(self):
        repo = MagicMock()
        with pytest.raises(InsufficientPrivilege):
            RevokeRoleUseCase(repo).execute(
                user_id=uuid.uuid4(), role_label="coach", caller_roles=["coordinator"]
            )
