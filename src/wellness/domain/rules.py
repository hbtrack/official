"""
Regras de domínio — módulo wellness.
Fonte: PERMISSIONS_WELLNESS.md, DOMAIN_RULES_WELLNESS.md, INVARIANTS_WELLNESS.md
ADR-008 (RBAC 5 roles), ADR-010 (dados PII saúde)
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


# ---------------------------------------------------------------------------
# Exceções de domínio
# ---------------------------------------------------------------------------

class WellnessEntryNotFound(Exception):
    """Entrada de wellness não encontrada."""


class InsufficientPrivilege(Exception):
    """Papel RBAC insuficiente ou BOLA violado."""


class AthleteNotFound(Exception):
    """Atleta não encontrado."""


# ---------------------------------------------------------------------------
# RBAC — PERMISSIONS_WELLNESS.md
# ---------------------------------------------------------------------------

_STAFF_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH}
_MANAGEMENT_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR}
_NO_MEMBER = {RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH, RoleLabel.ATHLETE}


def assert_can_create_entry(
    role: RoleLabel,
    actor_user_id: uuid.UUID,
    athlete_user_id: uuid.UUID,
) -> None:
    """
    createWellnessEntry:
    - admin/coordinator/coach: podem criar para qualquer atleta
    - athlete: somente para si mesmo (BOLA — PERM-WEL-002)
    - member: negado
    """
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege(
            "DR-WELL-001: member não pode registrar entrada de wellness."
        )
    if role == RoleLabel.ATHLETE and actor_user_id != athlete_user_id:
        raise InsufficientPrivilege(
            "BOLA/PERM-WEL-002: athlete só pode registrar wellness para si mesmo."
        )


def assert_can_read_entry(
    role: RoleLabel,
    actor_user_id: uuid.UUID,
    entry_athlete_user_id: uuid.UUID,
    actor_team_athlete_ids: Optional[List[uuid.UUID]] = None,
) -> None:
    """
    getWellnessEntry / listWellnessEntries:
    - admin/coordinator: acesso irrestrito
    - coach: atletas da equipe (actor_team_athlete_ids)
    - athlete: apenas a própria entrada (BOLA — PERM-WEL-002)
    - member: negado
    """
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege(
            "DR-WELL-001: member não pode acessar dados de wellness."
        )
    if role == RoleLabel.ATHLETE:
        if actor_user_id != entry_athlete_user_id:
            raise InsufficientPrivilege(
                "BOLA/PERM-WEL-002: athlete não pode acessar wellness de outro atleta."
            )
    if role == RoleLabel.COACH:
        team_ids = actor_team_athlete_ids or []
        if entry_athlete_user_id not in team_ids:
            raise InsufficientPrivilege(
                "BOLA/PERM-WEL-003: coach só acessa wellness de atletas do seu time."
            )


def assert_can_read_athlete_wellness(
    role: RoleLabel,
    actor_user_id: uuid.UUID,
    target_athlete_id: uuid.UUID,
    actor_team_athlete_ids: Optional[List[uuid.UUID]] = None,
) -> None:
    """
    listAthleteWellnessEntries / getAthleteWellnessSummary:
    - admin/coordinator: acesso irrestrito
    - coach: atletas da equipe
    - athlete: apenas o próprio
    - member: negado
    """
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege(
            "DR-WELL-001: member não pode acessar dados de wellness."
        )
    if role == RoleLabel.ATHLETE:
        if actor_user_id != target_athlete_id:
            raise InsufficientPrivilege(
                "BOLA/PERM-WEL-002: athlete só pode acessar o próprio acervo de wellness."
            )
    if role == RoleLabel.COACH:
        team_ids = actor_team_athlete_ids or []
        if target_athlete_id not in team_ids:
            raise InsufficientPrivilege(
                "BOLA/PERM-WEL-003: coach só acessa wellness de atletas do seu time."
            )


def check_high_pain_alert(pain_score: Optional[int]) -> bool:
    """PERM-WEL-004: pain_score >= 7 dispara alerta para coach/coordinator."""
    return pain_score is not None and pain_score >= 7
