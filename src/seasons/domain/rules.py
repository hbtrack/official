"""
Domain rules — módulo seasons.
Fonte: docs/hbtrack/modulos/seasons/DOMAIN_RULES_SEASONS.md
Permissions: docs/hbtrack/modulos/seasons/PERMISSIONS_SEASONS.md
"""
from __future__ import annotations

from datetime import date
from enum import StrEnum
from uuid import UUID


class SeasonRuleError(Exception):
    """Erro de regra de negócio do módulo seasons."""


class InsufficientPrivilege(SeasonRuleError):
    """Papel RBAC insuficiente para a operação (BFLA)."""


class SeasonNotFound(SeasonRuleError):
    """Temporada não encontrada."""


class DuplicateTeamAssociation(SeasonRuleError):
    """Equipe já associada à temporada (INV-SEAS-003)."""


class InvalidDateRange(SeasonRuleError):
    """startDate > endDate viola INV-SEAS-002."""


class InvalidStatusTransition(SeasonRuleError):
    """Transição de status inválida."""


# Roles canônicos (ADR-008)
class RoleLabel(StrEnum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


_MANAGEMENT_ROLES = frozenset({RoleLabel.ADMIN, RoleLabel.COORDINATOR})
# Transições de status permitidas: DRAFT→ACTIVE, ACTIVE→ARCHIVED
_VALID_TRANSITIONS: dict[str, frozenset[str]] = {
    "DRAFT": frozenset({"ACTIVE"}),
    "ACTIVE": frozenset({"ARCHIVED"}),
    "ARCHIVED": frozenset(),
}


def assert_can_manage_season(actor_role: RoleLabel) -> None:
    """
    PERM-SEA: createSeason, patchSeason, addTeamToSeason, removeTeamFromSeason
    requerem admin ou coordinator (BFLA).
    """
    if actor_role not in _MANAGEMENT_ROLES:
        raise InsufficientPrivilege(
            f"Operação exige admin ou coordinator — recebido: {actor_role}"
        )


def assert_can_remove_team(actor_role: RoleLabel, status_label: str) -> None:
    """
    PERM-SEA-001: Temporadas ACTIVE só permitem remoção de times por admin.
    Coordinator não pode remover times de temporadas ativas.
    """
    assert_can_manage_season(actor_role)
    if status_label == "ACTIVE" and actor_role == RoleLabel.COORDINATOR:
        raise InsufficientPrivilege(
            "PERM-SEA-001: Coordinator não pode remover times de temporada ACTIVE — apenas admin."
        )


def assert_can_patch_season(actor_role: RoleLabel, status_label: str) -> None:
    """
    PERM-SEA-002: Patches em temporadas ARCHIVED são somente para admin (dados históricos).
    """
    assert_can_manage_season(actor_role)
    if status_label == "ARCHIVED" and actor_role == RoleLabel.COORDINATOR:
        raise InsufficientPrivilege(
            "PERM-SEA-002: Coordinator não pode editar temporada ARCHIVED — apenas admin."
        )


def assert_date_range(start_date: date, end_date: date) -> None:
    """INV-SEAS-002: startDate deve ser <= endDate."""
    if start_date > end_date:
        raise InvalidDateRange(
            f"INV-SEAS-002: startDate ({start_date}) deve ser <= endDate ({end_date})"
        )


def assert_valid_status_transition(current: str, new: str) -> None:
    """Valida transição de status: DRAFT→ACTIVE→ARCHIVED."""
    allowed = _VALID_TRANSITIONS.get(current, frozenset())
    if new not in allowed:
        raise InvalidStatusTransition(
            f"Transição de status inválida: {current} → {new}. "
            f"Permitidas: {list(allowed) or 'nenhuma'}"
        )


def assert_team_not_in_season(team_id: UUID, team_ids: list[UUID]) -> None:
    """INV-SEAS-003: rejeita duplicata de vínculo equipe-temporada."""
    if team_id in team_ids:
        raise DuplicateTeamAssociation(
            f"INV-SEAS-003: equipe {team_id} já está associada à temporada."
        )
