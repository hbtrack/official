"""
Domain rules — módulo users.
Fonte: docs/hbtrack/modulos/users/DOMAIN_RULES_USERS.md
Permissões: docs/hbtrack/modulos/users/PERMISSIONS_USERS.md
"""
from __future__ import annotations

from uuid import UUID

from .entities import RoleLabel, UserProfile, UserStatus


# ---------------------------------------------------------------------------
# Exceções de domínio
# ---------------------------------------------------------------------------

class UserDomainError(Exception):
    """Base para erros de domínio do módulo users."""


class InvalidRoleLabel(UserDomainError):
    """roleLabel não pertence aos 5 canônicos (DR-USR-002)."""


class UserNotFound(UserDomainError):
    """Perfil de usuário não encontrado."""


class UserConflict(UserDomainError):
    """Conflito de unicidade (409)."""


class InsufficientPrivilege(UserDomainError):
    """Operação exige role mais elevado (BFLA)."""


class AuthnFieldForbidden(UserDomainError):
    """Tentativa de gravar campo de autenticação proibido (INV-USR-003)."""


# ---------------------------------------------------------------------------
# Regras de domínio
# ---------------------------------------------------------------------------

_CREATOR_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR}
_EDITOR_FULL_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR}
_ROLE_LABEL_EDITORS = {RoleLabel.ADMIN, RoleLabel.COORDINATOR}

# Campos absolutamente proibidos em qualquer payload (INV-USR-003, PERM-USR-010)
FORBIDDEN_AUTHN_FIELDS = frozenset({
    "password_hash", "password", "refresh_token",
    "mfa_secret", "jwt", "access_token", "otp_secret",
})


def assert_can_create_user(actor_role: RoleLabel) -> None:
    """PERM-USR-002: apenas admin e coordinator criam perfis (BFLA)."""
    if actor_role not in _CREATOR_ROLES:
        raise InsufficientPrivilege(
            f"DR-USR-002 / PERM-USR-002: roleLabel '{actor_role}' não pode criar perfis. "
            "Requer admin ou coordinator."
        )


def assert_can_read_user(actor_id: UUID, actor_role: RoleLabel, target_id: UUID,
                          actor_team_ids: list[UUID], target_team_ids: list[UUID]) -> None:
    """
    PERM-USR-003 / PERM-USR-005 / PERM-USR-006: regras de leitura (BOLA).
    - owner sempre pode
    - admin/coordinator podem ver qualquer perfil
    - coach vê apenas membros do seu time
    - member não pode ver perfis alheios
    """
    if actor_id == target_id:
        return  # PERM-USR-003: owner sempre pode
    if actor_role in {RoleLabel.ADMIN, RoleLabel.COORDINATOR}:
        return
    if actor_role == RoleLabel.COACH:
        # PERM-USR-006: coach vê apenas membros do seu time
        teams_overlap = set(actor_team_ids) & set(target_team_ids)
        if not teams_overlap:
            raise InsufficientPrivilege(
                "PERM-USR-006: coach só pode ver perfis de membros do próprio time."
            )
        return
    # member e outros não têm acesso (PERM-USR-005)
    raise InsufficientPrivilege(
        f"PERM-USR-005: roleLabel '{actor_role}' não tem permissão para ver perfis de outros usuários."
    )


def assert_can_patch_user(actor_id: UUID, actor_role: RoleLabel, target_id: UUID) -> None:
    """
    PERM-USR-003 / PERM-USR-004: regras de edição (BOLA/BFLA).
    - owner pode editar próprio perfil (exceto roleLabel)
    - admin/coordinator podem editar qualquer perfil
    """
    if actor_id == target_id:
        return  # PERM-USR-003: owner pode editar próprio perfil
    if actor_role in _EDITOR_FULL_ROLES:
        return
    raise InsufficientPrivilege(
        f"PERM-USR-003: roleLabel '{actor_role}' pode editar apenas o próprio perfil."
    )


def assert_can_patch_role_label(actor_id: UUID, actor_role: RoleLabel, target_id: UUID) -> None:
    """PERM-USR-004: apenas admin/coordinator alteram roleLabel; owner não pode promover-se."""
    if actor_role not in _ROLE_LABEL_EDITORS:
        raise InsufficientPrivilege(
            "PERM-USR-004: alteração de roleLabel requer admin ou coordinator."
        )


def assert_no_authn_fields(payload_keys: set[str]) -> None:
    """INV-USR-003 / PERM-USR-010: campos de authn nunca aceitos em nenhum payload."""
    forbidden = FORBIDDEN_AUTHN_FIELDS & payload_keys
    if forbidden:
        raise AuthnFieldForbidden(
            f"INV-USR-003: campos de autenticação proibidos no payload: {forbidden}"
        )


def apply_status_transition(current: UserStatus, new_status: UserStatus,
                             actor_id: UUID, actor_role: RoleLabel, target_id: UUID) -> None:
    """
    PERMISSIONS_USERS.md patchUser.statusLabel:
    - Owner ativa próprio perfil (PENDING_ACTIVATION → ACTIVE)
    - admin pode qualquer transição
    - coordinator pode ACTIVE/PENDING
    """
    if actor_role == RoleLabel.ADMIN:
        return  # admin pode qualquer transição
    if actor_role == RoleLabel.COORDINATOR:
        if new_status == UserStatus.SUSPENDED:
            return  # pode suspender
        if new_status in {UserStatus.ACTIVE, UserStatus.PENDING_ACTIVATION}:
            return
        raise InsufficientPrivilege("Coordinator só pode transicionar para ACTIVE ou PENDING_ACTIVATION.")
    if actor_id == target_id and new_status == UserStatus.ACTIVE:
        if current == UserStatus.PENDING_ACTIVATION:
            return  # dono ativa próprio perfil
    raise InsufficientPrivilege(
        f"Transição de status '{current}' → '{new_status}' não permitida para este ator."
    )
