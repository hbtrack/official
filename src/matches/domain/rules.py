"""
Regras de domínio — módulo matches.
Fonte: PERMISSIONS_MATCHES.md, DOMAIN_RULES_MATCHES.md, INVARIANTS_MATCHES.md
ADR-008 (RBAC), HBR-008 (max 16 jogadores), HBR-013 (fases da partida)
"""
from __future__ import annotations
import uuid
from enum import Enum
from typing import List, Optional


class RoleLabel(str, Enum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


class MatchNotFound(Exception):
    """Partida não encontrada."""


class InsufficientPrivilege(Exception):
    """Papel RBAC insuficiente."""


class MatchStateError(Exception):
    """Transição de estado inválida ou operação bloqueada pelo status."""


_MGMT_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR}
_OPERATIONAL_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH}
_LINEUP_EDIT_STATUSES = {"SCHEDULED", "PRE_MATCH"}
MAX_LINEUP = 16  # HBR-008


def assert_can_create_match(role: RoleLabel) -> None:
    """createMatch: admin/coordinator apenas."""
    if role not in _MGMT_ROLES:
        raise InsufficientPrivilege(
            "PERM-MATCH: somente admin ou coordinator podem criar partidas."
        )


def assert_can_patch_match(role: RoleLabel) -> None:
    """patchMatch: admin/coordinator/coach."""
    if role not in _OPERATIONAL_ROLES:
        raise InsufficientPrivilege(
            "PERM-MATCH: somente admin, coordinator ou coach podem atualizar partidas."
        )


def assert_can_edit_lineup(role: RoleLabel, status_label: str) -> None:
    """
    addPlayerToLineup / removePlayerFromLineup:
    - role: admin/coordinator/coach
    - PERM-MATCH-001: COMPLETED é read-only
    - PERM-MATCH-002: edição de lineup só SCHEDULED/PRE_MATCH
    """
    if role not in _OPERATIONAL_ROLES:
        raise InsufficientPrivilege(
            "PERM-MATCH: somente admin, coordinator ou coach podem editar lineup."
        )
    if status_label not in _LINEUP_EDIT_STATUSES:
        raise MatchStateError(
            f"PERM-MATCH-002: edição de lineup permitida apenas nos status {sorted(_LINEUP_EDIT_STATUSES)}. "
            f"Status atual: {status_label}."
        )


def assert_not_completed(status_label: str) -> None:
    """PERM-MATCH-001: partidas COMPLETED são read-only."""
    if status_label == "COMPLETED":
        raise MatchStateError("PERM-MATCH-001: partida COMPLETED é read-only.")
