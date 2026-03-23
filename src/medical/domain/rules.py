"""
Regras de domínio — módulo medical.
Fonte: PERMISSIONS_MEDICAL.md, DOMAIN_RULES_MEDICAL.md, INVARIANTS_MEDICAL.md
ADR-008 (RBAC 5 roles), ADR-007 (JWT Bearer), ADR-010 (PHI/PII)
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
# Exceções
# ---------------------------------------------------------------------------

class MedicalRecordNotFound(Exception):
    """Registro médico não encontrado."""


class InsufficientPrivilege(Exception):
    """Papel RBAC insuficiente para operação médica."""


# ---------------------------------------------------------------------------
# RBAC — PERMISSIONS_MEDICAL.md
# ---------------------------------------------------------------------------

_STAFF = {RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH}
_WRITE_ROLES = {RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH}
_READ_MGMT = {RoleLabel.ADMIN, RoleLabel.COORDINATOR}


def assert_can_create_record(role: RoleLabel) -> None:
    """createMedicalRecord: admin/coordinator/coach; athlete/member negados."""
    if role not in _WRITE_ROLES:
        raise InsufficientPrivilege(
            "PERM-MED: somente admin, coordinator ou coach podem criar registros médicos."
        )


def assert_can_read_record(
    role: RoleLabel,
    actor_user_id: uuid.UUID,
    record_athlete_id: uuid.UUID,
    actor_team_athlete_ids: Optional[List[uuid.UUID]] = None,
) -> None:
    """
    getMedicalRecord / listMedicalRecords:
    - admin/coordinator: acesso irrestrito
    - coach: apenas atletas do seu time (BOLA/PERM-MED-001)
    - athlete: apenas o próprio registro (BOLA/PERM-MED-001)
    - member: negado
    """
    if role == RoleLabel.MEMBER:
        raise InsufficientPrivilege(
            "PERM-MED: member não pode acessar dados médicos."
        )
    if role == RoleLabel.ATHLETE:
        if actor_user_id != record_athlete_id:
            raise InsufficientPrivilege(
                "BOLA/PERM-MED-001: athlete só acessa seus próprios registros médicos."
            )
    if role == RoleLabel.COACH:
        team_ids = actor_team_athlete_ids or []
        if record_athlete_id not in team_ids:
            raise InsufficientPrivilege(
                "BOLA/PERM-MED-004: coach só acessa dados médicos de atletas do seu time."
            )


def assert_can_update_record(role: RoleLabel) -> None:
    """updateMedicalRecord: admin/coordinator/coach; athlete/member negados."""
    if role not in _WRITE_ROLES:
        raise InsufficientPrivilege(
            "PERM-MED: somente admin, coordinator ou coach podem atualizar registros médicos."
        )


def assert_can_delete_record(role: RoleLabel) -> None:
    """deleteMedicalRecord: somente admin (LGPD compliance, PERM-MED-003)."""
    if role != RoleLabel.ADMIN:
        raise InsufficientPrivilege(
            "PERM-MED-003: somente admin pode deletar registros médicos (soft-delete, LGPD)."
        )
