"""
Regras de domínio do módulo identity_access.
Fonte: docs/hbtrack/modulos/identity_access/DOMAIN_RULES_IDENTITY_ACCESS.md
       docs/hbtrack/modulos/identity_access/INVARIANTS_IDENTITY_ACCESS.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entities import AuthSession, RoleLabel


class AuthError(Exception):
    """Erro de autenticação/autorização de domínio."""


class SessionRevoked(AuthError):
    """DR-IAM-004: sessão já foi revogada."""


class SessionExpired(AuthError):
    """DR-IAM-004: sessão expirou."""


class InvalidRole(AuthError):
    """DR-IAM-003: role não é canônico."""


class LastAdminProtection(AuthError):
    """INV-IAM segurança: último admin não pode ter o role revogado."""


class InsufficientPrivilege(AuthError):
    """OWASP API5:2023 BFLA: role insuficiente para a operação."""


def assert_session_active(session: AuthSession) -> None:
    """
    DR-IAM-004: mfa_satisfied e ciclo de vida rastreáveis.
    INV-IAM-003: garante que a sessão não está revogada nem expirada.
    """
    if session.revoked_at is not None:
        raise SessionRevoked(
            f"DR-IAM-004: sessão {session.id} foi revogada em {session.revoked_at}."
        )
    if session.expires_at is not None:
        now = datetime.now(tz=timezone.utc)
        if session.expires_at < now:
            raise SessionExpired(
                f"DR-IAM-004: sessão {session.id} expirou em {session.expires_at}."
            )


def assert_role_canonical(role_label: str) -> None:
    """DR-IAM-003: roleLabel deve ser um dos 5 canônicos (ADR-008)."""
    from .entities import RoleLabel
    canonical = {r.value for r in RoleLabel}
    if role_label not in canonical:
        raise InvalidRole(
            f"DR-IAM-003: '{role_label}' não é canônico. Válidos: {canonical}"
        )


def assert_not_last_admin(
    existing_bindings: list[str],
    role_to_remove: str,
) -> None:
    """
    Invariante de segurança: o último admin ativo não pode ter o role revogado.
    Isso é verificado ANTES de persistir — contrato retorna 409 neste caso.
    """
    if role_to_remove != "admin":
        return
    admin_count = sum(1 for r in existing_bindings if r == "admin")
    if admin_count <= 1:
        raise LastAdminProtection(
            "Não é possível revogar o último role 'admin' ativo na plataforma."
        )


def assert_can_revoke_session(
    caller_user_id: object,
    caller_roles: list[str],
    session_principal_user_id: object,
) -> None:
    """
    OWASP API1:2023 BOLA + API5:2023 BFLA.
    Admin pode revogar qualquer sessão.
    Outros usuários só podem revogar suas próprias sessões.
    """
    if "admin" in caller_roles:
        return
    if caller_user_id != session_principal_user_id:
        raise InsufficientPrivilege(
            "OWASP API1:2023/BOLA + API5:2023/BFLA: "
            "usuário não autorizado a revogar esta sessão."
        )


def assert_can_assign_or_revoke_role(
    caller_roles: list[str],
    target_role: str,
) -> None:
    """
    OWASP API5:2023 BFLA: somente admin pode atribuir/revogar roles.
    DR-IAM-005: bindings de role não são delegados a módulos operacionais.
    """
    if "admin" not in caller_roles:
        raise InsufficientPrivilege(
            "DR-IAM-005 + OWASP API5:2023/BFLA: "
            "apenas admin pode atribuir ou revogar roles."
        )
