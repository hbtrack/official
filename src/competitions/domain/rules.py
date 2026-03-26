"""
Regras de domínio — módulo competitions.
Fonte: PERMISSIONS_COMPETITIONS.md, DOMAIN_RULES_COMPETITIONS.md,
       INVARIANTS_COMPETITIONS.md, ADR-008 (RBAC 5 roles)
"""
from __future__ import annotations

import uuid
from enum import Enum
from typing import List

from .entities import CompetitionStatus


class RoleLabel(str, Enum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


# ---------------------------------------------------------------------------
# Exceções de domínio
# ---------------------------------------------------------------------------

class CompetitionNotFound(Exception):
    """Competição não encontrada."""


class InsufficientPrivilege(Exception):
    """Papel RBAC insuficiente para a operação."""


class InvalidStatusTransition(Exception):
    """Transição de status inválida (FSM)."""


class TeamAlreadyRegistered(Exception):
    """INV-COMP-003: equipe já inscrita na competição."""


class TeamNotRegistered(Exception):
    """Equipe não está inscrita na competição."""


# ---------------------------------------------------------------------------
# FSM: draft → active → archived
# ---------------------------------------------------------------------------

VALID_TRANSITIONS: dict[CompetitionStatus, list[CompetitionStatus]] = {
    CompetitionStatus.DRAFT: [CompetitionStatus.ACTIVE],
    CompetitionStatus.ACTIVE: [CompetitionStatus.ARCHIVED],
    CompetitionStatus.ARCHIVED: [],
}


def assert_valid_transition(
    current: CompetitionStatus,
    target: CompetitionStatus,
) -> None:
    """INV-COMP: FSM — valida transição de status."""
    allowed = VALID_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise InvalidStatusTransition(
            f"Transição inválida: {current.value} → {target.value}. "
            f"Permitidas: {[s.value for s in allowed]}."
        )


# ---------------------------------------------------------------------------
# RBAC — DR-COMP / PERMISSIONS_COMPETITIONS.md
# ---------------------------------------------------------------------------

_MANAGEMENT_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR}
_ALL_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH,
              RoleLabel.ATHLETE, RoleLabel.MEMBER}


def assert_can_list_competitions(role: RoleLabel) -> None:
    """listCompetitions: todos os roles (PERM-COMP-003)."""
    if role not in _ALL_ROLES:
        raise InsufficientPrivilege(
            "DR-COMP-001: role desconhecido não pode listar competições."
        )


def assert_can_create_competition(role: RoleLabel) -> None:
    """createCompetition: admin | coordinator."""
    if role not in _MANAGEMENT_ROLES:
        raise InsufficientPrivilege(
            "DR-COMP-001: createCompetition requer role admin ou coordinator."
        )


def assert_can_read_competition(role: RoleLabel) -> None:
    """getCompetition: todos os roles (dados públicos)."""
    if role not in _ALL_ROLES:
        raise InsufficientPrivilege(
            "DR-COMP-001: role desconhecido não pode ler competições."
        )


def assert_can_patch_competition(role: RoleLabel, status: CompetitionStatus) -> None:
    """patchCompetition: admin | coordinator; status ACTIVE → somente admin (PERM-COMP-002)."""
    if role not in _MANAGEMENT_ROLES:
        raise InsufficientPrivilege(
            "DR-COMP-001: patchCompetition requer role admin ou coordinator."
        )
    if status == CompetitionStatus.ACTIVE and role != RoleLabel.ADMIN:
        raise InsufficientPrivilege(
            "PERM-COMP-002: patch em competição ACTIVE requer role admin."
        )


def assert_can_register_team(role: RoleLabel) -> None:
    """registerTeamInCompetition: admin | coordinator."""
    if role not in _MANAGEMENT_ROLES:
        raise InsufficientPrivilege(
            "DR-COMP-001: registerTeamInCompetition requer role admin ou coordinator."
        )


def assert_can_unregister_team(role: RoleLabel) -> None:
    """unregisterTeamFromCompetition: admin | coordinator."""
    if role not in _MANAGEMENT_ROLES:
        raise InsufficientPrivilege(
            "DR-COMP-001: unregisterTeamFromCompetition requer role admin ou coordinator."
        )


# ---------------------------------------------------------------------------
# Inscrição de equipe — DR-COMP-003 / INV-COMP-003
# ---------------------------------------------------------------------------

def assert_team_not_registered(
    registration_team_ids: List[uuid.UUID],
    team_id: uuid.UUID,
) -> None:
    """INV-COMP-003: equipe não pode ser inscrita duas vezes."""
    if team_id in registration_team_ids:
        raise TeamAlreadyRegistered(
            f"INV-COMP-003: equipe {team_id} já está inscrita na competição."
        )


def assert_team_registered(
    registration_team_ids: List[uuid.UUID],
    team_id: uuid.UUID,
) -> None:
    """Verifica que equipe está inscrita (para remoção)."""
    if team_id not in registration_team_ids:
        raise TeamNotRegistered(
            f"Equipe {team_id} não está inscrita na competição."
        )
