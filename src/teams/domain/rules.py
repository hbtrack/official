"""
Domain rules — módulo teams.
Fonte: docs/hbtrack/modulos/teams/DOMAIN_RULES_TEAMS.md
Permissions: docs/hbtrack/modulos/teams/PERMISSIONS_TEAMS.md
"""
from __future__ import annotations

from enum import StrEnum
from uuid import UUID


class TeamRuleError(Exception):
    """Erro de regra de negócio do módulo teams."""


class InsufficientPrivilege(TeamRuleError):
    """Papel RBAC insuficiente para a operação (BFLA/BOLA)."""


class TeamNotFound(TeamRuleError):
    """Equipe não encontrada."""


class InvalidStatusTransition(TeamRuleError):
    """Transição de status inválida."""


# Roles canônicos (ADR-008)
class RoleLabel(StrEnum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


_MANAGEMENT_ROLES = frozenset({RoleLabel.ADMIN, RoleLabel.COORDINATOR})
_VALID_TRANSITIONS: dict[str, frozenset[str]] = {
    "DRAFT": frozenset({"ACTIVE"}),
    "ACTIVE": frozenset({"ARCHIVED"}),
    "ARCHIVED": frozenset(),
}


def assert_can_create_team(actor_role: RoleLabel) -> None:
    """createTeam: apenas admin ou coordinator (BFLA)."""
    if actor_role not in _MANAGEMENT_ROLES:
        raise InsufficientPrivilege(
            f"createTeam exige admin ou coordinator — recebido: {actor_role}"
        )


def assert_can_patch_team(
    actor_role: RoleLabel,
    actor_team_ids: list[UUID],
    team_id: UUID,
) -> None:
    """
    patchTeam: admin e coordinator irrestrito.
    coach pode editar apenas o próprio time (PERM-TEAM-001).
    athlete e member bloqueados.
    """
    if actor_role in _MANAGEMENT_ROLES:
        return
    if actor_role == RoleLabel.COACH:
        if team_id not in actor_team_ids:
            raise InsufficientPrivilege(
                "PERM-TEAM-001: coach só pode editar o próprio time."
            )
        return
    raise InsufficientPrivilege(
        f"patchTeam não permitido para role: {actor_role}"
    )


def assert_can_manage_staff(actor_role: RoleLabel) -> None:
    """addStaffToTeam / removeStaffFromTeam: apenas admin ou coordinator (BFLA)."""
    if actor_role not in _MANAGEMENT_ROLES:
        raise InsufficientPrivilege(
            f"Gerenciamento de staff exige admin ou coordinator — recebido: {actor_role}"
        )


def assert_can_manage_athlete(
    actor_role: RoleLabel,
    actor_team_ids: list[UUID],
    team_id: UUID,
) -> None:
    """
    addAthleteToTeam / removeAthleteFromTeam:
    admin e coordinator irrestrito.
    coach pode gerenciar atletas apenas do próprio time (PERM-TEAM-001).
    """
    if actor_role in _MANAGEMENT_ROLES:
        return
    if actor_role == RoleLabel.COACH:
        if team_id not in actor_team_ids:
            raise InsufficientPrivilege(
                "PERM-TEAM-001: coach só pode gerenciar atletas do próprio time."
            )
        return
    raise InsufficientPrivilege(
        f"Gerenciamento de atletas não permitido para role: {actor_role}"
    )


def assert_can_read_team(
    actor_role: RoleLabel,
    actor_team_ids: list[UUID],
    team_id: UUID,
) -> None:
    """
    getTeam: admin e coordinator irrestrito.
    coach e athlete veem apenas equipes às quais estão vinculados (BOLA).
    member bloqueado.
    """
    if actor_role in _MANAGEMENT_ROLES:
        return
    if actor_role in (RoleLabel.COACH, RoleLabel.ATHLETE):
        if team_id not in actor_team_ids:
            raise InsufficientPrivilege(
                f"BOLA: {actor_role} só pode acessar equipes às quais está vinculado."
            )
        return
    raise InsufficientPrivilege(
        f"getTeam não permitido para role: {actor_role}"
    )


def assert_valid_status_transition(current: str, new: str) -> None:
    """Valida transição DRAFT→ACTIVE→ARCHIVED."""
    allowed = _VALID_TRANSITIONS.get(current, frozenset())
    if new not in allowed:
        raise InvalidStatusTransition(
            f"Transição inválida: {current} → {new}. "
            f"Permitidas: {list(allowed) or 'nenhuma'}"
        )
