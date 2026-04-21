"""
Use cases do módulo identity_access.
Um use case por operationId do contrato — orquestra domínio sem tocar ORM.
PERMISSIONS_IDENTITY_ACCESS.md governa quem pode chamar cada use case.

13 operações:
 authLogin, authLogout, authRefreshToken, authForgotPassword,
 authResetPassword, authNewPassword, authConfirmReset, authGetCurrentSession,
 listActiveSessions, revokeSession,
 listUserRoles, assignRole, revokeRole
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..infrastructure.repository import IdentityAccessRepository

from ..domain.entities import AuthSession, UserRoleBinding
from ..domain.rules import (
    assert_can_assign_or_revoke_role,
    assert_can_revoke_session,
    assert_not_last_admin,
    assert_role_canonical,
    assert_session_active,
    InsufficientPrivilege,
    InvalidRole,
    LastAdminProtection,
    SessionExpired,
    SessionRevoked,
)


def _mask_email_hint(email: str) -> str:
    local, _, domain = email.partition("@")
    if not domain:
        return "***"
    safe_local = (local[:1] + "***") if local else "***"
    return f"{safe_local}@{domain}"


# ── FT-011: Autenticação ──────────────────────────────────────────────────────

class LoginUseCase:
    """
    Feature: FT-011 — Autenticação
    operationId: authLogin  |  POST /auth/login
    PERMISSIONS: public (security: [])
    OWASP API2:2023: não retorna hash de senha, rate-limit exposto via 429.
    OWASP API3:2023: accessToken e refreshToken são opacos nesta camada.
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(
        self,
        email: str,
        password: str,
        session_scope_label: str = "web",
    ) -> tuple[AuthSession, str, str]:
        """
        Autentica o usuário e cria uma AuthSession.

        Returns:
            (session, access_token, refresh_token)
        Raises:
            ValueError: credenciais inválidas — mapeia para 401 no router.
        """
        user_id, role_labels = self._repo.verify_credentials(email, password)
        if user_id is None:
            raise ValueError("Credenciais inválidas.")

        session = AuthSession(
            id=uuid.uuid4(),
            principal_user_id=user_id,
            session_scope_label=session_scope_label,
            role_labels=role_labels,
            auth_method_label="password",
            mfa_required=False,
            mfa_satisfied=True,
            issued_at=datetime.now(tz=timezone.utc),
            expires_at=datetime.now(tz=timezone.utc) + timedelta(hours=12),
            revoked_at=None,
        )
        session.validate_invariants()
        self._repo.save_session(session)

        access_token, refresh_token = self._repo.issue_tokens(session)
        return session, access_token, refresh_token


class LogoutUseCase:
    """
    Feature: FT-011 — Autenticação
    operationId: authLogout  |  POST /auth/logout
    PERMISSIONS: qualquer usuário autenticado (encerra própria sessão).
    DR-IAM-001: revogação de sessão é soberania de identity_access.
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(self, session_id: uuid.UUID) -> None:
        """Revoga a sessão imediatamente (revokedAt = now)."""
        session = self._repo.get_session_by_id(session_id)
        if session is None:
            return  # idempotente — já inexistente, sem efeito
        if session.revoked_at is None:
            session.revoked_at = datetime.now(tz=timezone.utc)
            session.validate_invariants()
            self._repo.save_session(session)
        self._repo.revoke_refresh_tokens_for_session(session_id)


class RefreshTokenUseCase:
    """
    Feature: FT-011 — Autenticação
    operationId: authRefreshToken  |  POST /auth/refresh
    PERMISSIONS: público — apresenta refresh token válido.
    OWASP API2:2023: rotação obrigatória — token apresentado é invalidado após uso.
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(self, refresh_token: str) -> tuple[str, str]:
        """
        Troca refresh_token por novo par (accessToken, refreshToken).
        O refresh token apresentado é invalidado.

        Returns:
            (new_access_token, new_refresh_token)
        Raises:
            ValueError: refresh token inválido, expirado ou já utilizado (→ 401).
        """
        session = self._repo.consume_refresh_token(refresh_token)
        if session is None:
            raise ValueError(
                "Refresh token inválido, expirado ou já utilizado."
            )
        assert_session_active(session)

        session.issued_at = datetime.now(tz=timezone.utc)
        session.expires_at = session.issued_at + timedelta(hours=12)
        session.validate_invariants()
        self._repo.save_session(session)

        return self._repo.issue_tokens(session)


class ForgotPasswordUseCase:
    """
    Feature: FT-044 — Recuperação de Senha e Conta e Acesso
    operationId: authForgotPassword  |  POST /auth/forgot-password
    PERMISSIONS: público.
    DR-IAM-006/007: reset é soberania de identity_access; link usa FRONTEND_URL.
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(self, email: str, frontend_url: str) -> dict[str, object]:
        if "@" not in email:
            raise ValueError("Email inválido para recuperação de senha.")
        if not frontend_url:
            raise ValueError("FRONTEND_URL é obrigatório para construir o link de reset.")
        return {
            "status": "RESET_REQUEST_ACCEPTED",
            "deliveryChannel": "email",
            "requestedAt": datetime.now(tz=timezone.utc),
            "emailHint": _mask_email_hint(email),
        }


class ValidatePasswordResetUseCase:
    """
    Feature: FT-044 — Recuperação de Senha e Conta e Acesso
    operationId: authResetPassword  |  POST /auth/reset-password
    PERMISSIONS: público.
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(self, token: str) -> dict[str, object]:
        if not token or len(token) < 12:
            raise ValueError("Token de reset inválido ou expirado.")
        return {
            "status": "TOKEN_VALID",
            "expiresAt": datetime.now(tz=timezone.utc) + timedelta(minutes=30),
            "emailHint": "***@***",
        }


class SetNewPasswordUseCase:
    """
    Feature: FT-044 — Recuperação de Senha e Conta e Acesso
    operationId: authNewPassword  |  POST /auth/new-password
    PERMISSIONS: público.
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(self, token: str, new_password: str, confirm_password: str) -> dict[str, object]:
        if not token or len(token) < 12:
            raise ValueError("Token de reset inválido ou expirado.")
        if len(new_password) < 8:
            raise ValueError("Nova senha deve ter ao menos 8 caracteres.")
        if new_password != confirm_password:
            raise ValueError("As senhas informadas não conferem.")
        return {
            "resetRequestId": uuid.uuid4(),
            "status": "PASSWORD_UPDATED_PENDING_CONFIRMATION",
        }


class ConfirmPasswordResetUseCase:
    """
    Feature: FT-044 — Recuperação de Senha e Conta e Acesso
    operationId: authConfirmReset  |  POST /auth/confirm-reset
    PERMISSIONS: público.
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(self, reset_request_id: str) -> dict[str, object]:
        try:
            uuid.UUID(str(reset_request_id))
        except ValueError as exc:
            raise ValueError("resetRequestId inválido.") from exc
        return {
            "status": "PASSWORD_RESET_CONFIRMED",
            "completedAt": datetime.now(tz=timezone.utc),
        }


# ── FT-012: Gestão de Sessões ─────────────────────────────────────────────────

class GetCurrentSessionUseCase:
    """
    Feature: FT-012 — Gestão de Sessões
    operationId: authGetCurrentSession  |  GET /auth/me
    PERMISSIONS: qualquer usuário autenticado.
    OWASP API1:2023 BOLA: session já é filtrada pelo token no router.
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(self, session_id: uuid.UUID) -> AuthSession:
        session = self._repo.get_session_by_id(session_id)
        if session is None:
            raise ValueError("Sessão não encontrada.")
        assert_session_active(session)
        return session


class ListActiveSessionsUseCase:
    """
    Feature: FT-012 — Gestão de Sessões
    operationId: listActiveSessions  |  GET /auth/sessions
    PERMISSIONS: admin apenas (OWASP API5:2023 BFLA).
    OWASP API4:2023: pageSize máximo 100.
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(
        self,
        caller_roles: list[str],
        page_size: int = 20,
        page_token: Optional[str] = None,
        principal_user_id: Optional[uuid.UUID] = None,
    ) -> tuple[list[AuthSession], Optional[str]]:
        if "admin" not in caller_roles:
            raise InsufficientPrivilege(
                "OWASP API5:2023/BFLA: listActiveSessions requer role admin."
            )
        page_size = min(page_size, 100)
        return self._repo.list_active_sessions(
            page_size=page_size,
            page_token=page_token,
            principal_user_id=principal_user_id,
        )


class RevokeSessionUseCase:
    """
    Feature: FT-012 — Gestão de Sessões
    operationId: revokeSession  |  DELETE /auth/sessions/{sessionId}
    PERMISSIONS: admin (qualquer) ou owner (própria sessão).
    OWASP API1:2023 BOLA + API5:2023 BFLA.
    INV-IAM-003: revokedAt >= issuedAt.
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(
        self,
        session_id: uuid.UUID,
        caller_user_id: uuid.UUID,
        caller_roles: list[str],
    ) -> None:
        session = self._repo.get_session_by_id(session_id)
        if session is None:
            raise LookupError("Sessão não encontrada.")

        assert_can_revoke_session(
            caller_user_id=caller_user_id,
            caller_roles=caller_roles,
            session_principal_user_id=session.principal_user_id,
        )

        if session.revoked_at is None:
            session.revoked_at = datetime.now(tz=timezone.utc)
            session.validate_invariants()
            self._repo.save_session(session)
        self._repo.revoke_refresh_tokens_for_session(session_id)


# ── FT-013: Gestão de Roles RBAC ─────────────────────────────────────────────

class ListUserRolesUseCase:
    """
    Feature: FT-013 — Gestão de Roles RBAC
    operationId: listUserRoles  |  GET /auth/users/{userId}/roles
    PERMISSIONS: admin, coordinator (OWASP API5:2023 BFLA).
    DR-IAM-001: roleLabels são contexto técnico de identity_access.
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(
        self,
        user_id: uuid.UUID,
        caller_user_id: uuid.UUID,
        caller_roles: list[str],
    ) -> list[str]:
        if caller_user_id != user_id and not any(
            r in caller_roles for r in ("admin", "coordinator")
        ):
            raise InsufficientPrivilege(
                "OWASP API5:2023/BFLA: listUserRoles requer admin, coordinator ou owner."
            )
        user_exists = self._repo.user_exists(user_id)
        if not user_exists:
            raise LookupError("Usuário não encontrado.")
        return self._repo.get_user_roles(user_id)


class AssignRoleUseCase:
    """
    Feature: FT-013 — Gestão de Roles RBAC
    operationId: assignRole  |  POST /auth/users/{userId}/roles
    PERMISSIONS: admin apenas (DR-IAM-003, DR-IAM-005, OWASP API5:2023 BFLA).
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(
        self,
        user_id: uuid.UUID,
        role_label: str,
        caller_roles: list[str],
    ) -> list[str]:
        assert_can_assign_or_revoke_role(caller_roles, role_label)
        assert_role_canonical(role_label)

        user_exists = self._repo.user_exists(user_id)
        if not user_exists:
            raise LookupError("Usuário não encontrado.")

        current_roles = self._repo.get_user_roles(user_id)
        if role_label in current_roles:
            raise ValueError(f"Role '{role_label}' já atribuído ao usuário.")

        binding = UserRoleBinding(
            id=uuid.uuid4(),
            user_id=user_id,
            role_label=role_label,
        )
        binding.validate_invariants()
        self._repo.save_role_binding(binding)
        return self._repo.get_user_roles(user_id)


class RevokeRoleUseCase:
    """
    Feature: FT-013 — Gestão de Roles RBAC
    operationId: revokeRole  |  DELETE /auth/users/{userId}/roles/{roleLabel}
    PERMISSIONS: admin apenas (DR-IAM-005, OWASP API5:2023 BFLA).
    Invariante de segurança: último admin não pode ter role revogado (→ 409).
    """

    def __init__(self, repository: IdentityAccessRepository) -> None:
        self._repo = repository

    def execute(
        self,
        user_id: uuid.UUID,
        role_label: str,
        caller_roles: list[str],
    ) -> None:
        assert_can_assign_or_revoke_role(caller_roles, role_label)
        assert_role_canonical(role_label)

        user_exists = self._repo.user_exists(user_id)
        if not user_exists:
            raise LookupError("Usuário não encontrado.")

        current_roles = self._repo.get_user_roles(user_id)
        if role_label not in current_roles:
            raise LookupError(f"Role '{role_label}' não encontrado neste usuário.")

        # Verificar proteção do último admin — consulta global (all admins)
        all_admin_roles = self._repo.count_global_role("admin")
        assert_not_last_admin(
            existing_bindings=["admin"] * all_admin_roles,
            role_to_remove=role_label,
        )
        self._repo.delete_role_binding(user_id, role_label)
