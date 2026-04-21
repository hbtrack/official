"""
Use Cases — módulo users.
Um use case por operationId do contrato OpenAPI.
Contratos: contracts/openapi/paths/users.yaml
Features: FT-014 (listUsers), FT-015 (createUser), FT-016 (getUser), FT-017 (patchUser)
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from ..domain.entities import RoleLabel, UserProfile, UserStatus
from ..domain.rules import (
    apply_status_transition,
    assert_can_create_user,
    assert_can_patch_role_label,
    assert_can_patch_user,
    assert_can_read_user,
    assert_no_authn_fields,
)

if TYPE_CHECKING:
    from ..infrastructure.repository import UsersRepository


# ---------------------------------------------------------------------------
# FT-014 — listUsers
# ---------------------------------------------------------------------------

@dataclass
class ListUsersInput:
    actor_id: UUID
    actor_role: RoleLabel
    actor_team_ids: list[UUID]
    organization_id: UUID | None = None
    team_id: UUID | None = None
    role_label: RoleLabel | None = None
    page_size: int = 50
    page_token: str | None = None


@dataclass
class ListUsersOutput:
    items: list[UserProfile]
    next_page_token: str | None = None


class ListUsersUseCase:
    """
    Feature: FT-014 — listUsers
    Contrato: GET /users
    DR-USR-001, PERM-USR-001, PERM-USR-005, PERM-USR-006
    """
    def __init__(self, repository: "UsersRepository") -> None:
        self._repo = repository

    def execute(self, inp: ListUsersInput) -> ListUsersOutput:
        # PERM-USR-005: member não lista usuários
        if inp.actor_role == RoleLabel.MEMBER:
            from ..domain.rules import InsufficientPrivilege
            raise InsufficientPrivilege("PERM-USR-005: member não pode listar usuários.")

        # PERM-USR-006: coach filtra apenas por times que pertence
        effective_team_id = inp.team_id
        if inp.actor_role == RoleLabel.COACH and inp.team_id is not None:
            if inp.team_id not in inp.actor_team_ids:
                from ..domain.rules import InsufficientPrivilege
                raise InsufficientPrivilege("PERM-USR-006: coach só pode filtrar por times do próprio vínculo.")

        items, next_token = self._repo.list_users(
            organization_id=inp.organization_id,
            team_id=effective_team_id,
            role_label=inp.role_label,
            page_size=min(inp.page_size, 100),  # OWASP API4:2023
            page_token=inp.page_token,
        )
        return ListUsersOutput(items=items, next_page_token=next_token)


# ---------------------------------------------------------------------------
# FT-015 — createUser
# ---------------------------------------------------------------------------

@dataclass
class CreateUserInput:
    actor_role: RoleLabel
    display_name: str
    role_label: RoleLabel
    organization_id: UUID | None = None
    first_name: str | None = None
    last_name: str | None = None
    position_label: str | None = None
    preferred_language: str | None = None
    avatar_url: str | None = None
    preference_tags: list[str] | None = None
    team_ids: list[UUID] | None = None
    season_ids: list[UUID] | None = None


class CreateUserUseCase:
    """
    Feature: FT-015 — createUser
    Contrato: POST /users
    DR-USR-001, PERM-USR-002, INV-USR-001, INV-USR-002, INV-USR-003
    """
    def __init__(self, repository: "UsersRepository") -> None:
        self._repo = repository

    def execute(self, inp: CreateUserInput) -> UserProfile:
        # PERM-USR-002: apenas admin/coordinator criam perfis (BFLA)
        assert_can_create_user(inp.actor_role)

        profile = UserProfile(
            id=uuid.uuid4(),
            display_name=inp.display_name,
            role_label=inp.role_label,
            organization_id=inp.organization_id,
            first_name=inp.first_name,
            last_name=inp.last_name,
            status_label=UserStatus.PENDING_ACTIVATION,  # DEC-USERS-002
            position_label=inp.position_label,
            preferred_language=inp.preferred_language,
            avatar_url=inp.avatar_url,
            preference_tags=list(dict.fromkeys(inp.preference_tags or [])),
            team_ids=list(dict.fromkeys(inp.team_ids or [])),
            season_ids=list(dict.fromkeys(inp.season_ids or [])),
        )
        profile.validate_invariants()
        return self._repo.save(profile)


# ---------------------------------------------------------------------------
# FT-016 — getUser
# ---------------------------------------------------------------------------

@dataclass
class GetUserInput:
    actor_id: UUID
    actor_role: RoleLabel
    actor_team_ids: list[UUID]
    target_user_id: UUID


class GetUserUseCase:
    """
    Feature: FT-016 — getUser
    Contrato: GET /users/{userId}
    DR-USR-001, PERM-USR-003, PERM-USR-005, PERM-USR-006, INV-USR-003
    """
    def __init__(self, repository: "UsersRepository") -> None:
        self._repo = repository

    def execute(self, inp: GetUserInput) -> UserProfile:
        profile = self._repo.get_by_id(inp.target_user_id)
        if profile is None:
            from ..domain.rules import UserNotFound
            raise UserNotFound(f"Usuário '{inp.target_user_id}' não encontrado.")

        assert_can_read_user(
            actor_id=inp.actor_id,
            actor_role=inp.actor_role,
            target_id=profile.id,
            actor_team_ids=inp.actor_team_ids,
            target_team_ids=profile.team_ids,
        )
        return profile


# ---------------------------------------------------------------------------
# FT-017 — patchUser
# ---------------------------------------------------------------------------

@dataclass
class PatchUserInput:
    actor_id: UUID
    actor_role: RoleLabel
    target_user_id: UUID
    # Campos patcháveis (PERM-USR-007 allowlist)
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    role_label: RoleLabel | None = None
    status_label: UserStatus | None = None
    position_label: str | None = None
    preferred_language: str | None = None
    avatar_url: str | None = None
    preference_tags: list[str] | None = None
    team_ids: list[UUID] | None = None
    season_ids: list[UUID] | None = None


class PatchUserUseCase:
    """
    Feature: FT-017 — patchUser
    Contrato: PATCH /users/{userId}
    DR-USR-001..004, PERM-USR-003..009, INV-USR-002, INV-USR-003
    """
    def __init__(self, repository: "UsersRepository") -> None:
        self._repo = repository

    def execute(self, inp: PatchUserInput) -> UserProfile:
        # Verificar que perfil existe
        profile = self._repo.get_by_id(inp.target_user_id)
        if profile is None:
            from ..domain.rules import UserNotFound
            raise UserNotFound(f"Usuário '{inp.target_user_id}' não encontrado.")

        # BOLA: owner pode editar próprio perfil; admin/coordinator editam qualquer
        assert_can_patch_user(inp.actor_id, inp.actor_role, profile.id)

        # PERM-USR-004: roleLabel só por admin/coordinator
        if inp.role_label is not None:
            assert_can_patch_role_label(inp.actor_id, inp.actor_role, profile.id)
            profile.role_label = inp.role_label

        # statusLabel: regras de transição
        if inp.status_label is not None:
            apply_status_transition(
                current=profile.status_label,
                new_status=inp.status_label,
                actor_id=inp.actor_id,
                actor_role=inp.actor_role,
                target_id=profile.id,
            )
            profile.status_label = inp.status_label

        # Allowlist de campos (PERM-USR-007)
        if inp.first_name is not None:
            profile.first_name = inp.first_name
        if inp.last_name is not None:
            profile.last_name = inp.last_name
        if inp.display_name is not None:
            profile.display_name = inp.display_name
        if inp.position_label is not None:
            profile.position_label = inp.position_label
        if inp.preferred_language is not None:
            profile.preferred_language = inp.preferred_language
        if inp.avatar_url is not None:
            profile.avatar_url = inp.avatar_url
        if inp.preference_tags is not None:
            # INV-USR-002: uniqueItems
            profile.preference_tags = list(dict.fromkeys(inp.preference_tags))
        if inp.team_ids is not None:
            profile.team_ids = list(dict.fromkeys(inp.team_ids))
        if inp.season_ids is not None:
            profile.season_ids = list(dict.fromkeys(inp.season_ids))

        profile.validate_invariants()
        return self._repo.save(profile)
