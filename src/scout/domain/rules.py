from __future__ import annotations
from enum import Enum
from typing import Optional, List
from uuid import UUID


class RoleLabel(str, Enum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


class InsufficientPrivilege(Exception):
    pass


class ScoutEventNotFound(Exception):
    pass


def assert_team_id_provided_for_coordinator_coach(
    role: RoleLabel, team_id: Optional[UUID]
) -> None:
    """PERM-SCOUT-001: coordinator/coach sem teamId -> 403 (nao 400)"""
    if role in (RoleLabel.COORDINATOR, RoleLabel.COACH) and team_id is None:
        raise InsufficientPrivilege("teamId obrigatorio para coordinator/coach")


def assert_can_create_event(role: RoleLabel) -> None:
    """PERM-SCOUT-005: admin/coordinator/coach only"""
    if role in (RoleLabel.ATHLETE, RoleLabel.MEMBER):
        raise InsufficientPrivilege("Apenas admin, coordinator ou coach podem criar eventos scout")


def assert_can_read_event(
    role: RoleLabel,
    actor_id: UUID,
    event_athlete_user_id: Optional[UUID],
    event_team_id: Optional[UUID],
    actor_team_ids: Optional[List[UUID]] = None,
) -> None:
    """PERM-SCOUT-002: BOLA enforcement"""
    if role == RoleLabel.ADMIN:
        return
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege("member nao tem acesso a eventos scout")
    if role == RoleLabel.ATHLETE:
        if event_athlete_user_id != actor_id:
            raise InsufficientPrivilege("athlete so pode ver seus proprios eventos")
        return
    # coordinator / coach: deve ser do time do evento
    actor_team_ids = actor_team_ids or []
    if event_team_id is None or event_team_id not in actor_team_ids:
        raise InsufficientPrivilege("coordinator/coach so pode ver eventos do seu time")


def assert_can_list_events(
    role: RoleLabel,
    team_id: Optional[UUID],
) -> None:
    """PERM-SCOUT-001 aplicado a listagem"""
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege("member nao tem permissao")
    assert_team_id_provided_for_coordinator_coach(role, team_id)


def assert_can_complete_session(role: RoleLabel) -> None:
    """PERM-SCOUT-005: admin/coordinator/coach only"""
    if role in (RoleLabel.ATHLETE, RoleLabel.MEMBER):
        raise InsufficientPrivilege("Apenas admin, coordinator ou coach podem finalizar sessao scout")


def assert_can_get_aggregations(
    role: RoleLabel,
    team_id: Optional[UUID],
) -> None:
    """PERM-SCOUT-001 aplicado a agregacoes"""
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege("member nao tem permissao")
    assert_team_id_provided_for_coordinator_coach(role, team_id)
