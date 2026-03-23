from __future__ import annotations
from enum import Enum
from typing import Optional
from uuid import UUID


class RoleLabel(str, Enum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


class InsufficientPrivilege(Exception):
    pass


class ExerciseNotFound(Exception):
    pass


class ExerciseConflict(Exception):
    pass


def assert_can_create_exercise(role: RoleLabel) -> None:
    if role in (RoleLabel.ATHLETE, RoleLabel.MEMBER):
        raise InsufficientPrivilege("Apenas admin, coordinator ou coach podem criar exercicios")


def assert_can_modify_exercise(
    role: RoleLabel,
    actor_id: UUID,
    exercise_scope: str,
    exercise_created_by: UUID,
) -> None:
    """INV-EXB-008: ORG user cannot edit SYSTEM exercise"""
    if exercise_scope == "SYSTEM" and role != RoleLabel.ADMIN:
        raise InsufficientPrivilege("Apenas admins podem editar exercicios SYSTEM")
    if exercise_scope == "ORG" and role not in (RoleLabel.ADMIN, RoleLabel.COORDINATOR):
        # Coach can only edit own exercises
        if role == RoleLabel.COACH and actor_id != exercise_created_by:
            raise InsufficientPrivilege("Coach so pode editar exercicios que criou")
        elif role in (RoleLabel.ATHLETE, RoleLabel.MEMBER):
            raise InsufficientPrivilege("Sem permissao para editar exercicio")


def assert_can_delete_exercise(
    role: RoleLabel,
    actor_id: UUID,
    exercise_scope: str,
    exercise_created_by: UUID,
) -> None:
    if role in (RoleLabel.ATHLETE, RoleLabel.MEMBER):
        raise InsufficientPrivilege("Sem permissao para excluir exercicio")
    if exercise_scope == "SYSTEM" and role != RoleLabel.ADMIN:
        raise InsufficientPrivilege("Apenas admin pode excluir exercicios SYSTEM")
    if exercise_scope == "ORG" and role == RoleLabel.COACH and actor_id != exercise_created_by:
        raise InsufficientPrivilege("Coach so pode excluir exercicios que criou")


def can_read_exercise(
    role: RoleLabel,
    actor_id: UUID,
    exercise_scope: str,
    exercise_visibility_mode: str,
    exercise_org_id: Optional[UUID],
    actor_org_id: Optional[UUID],
    exercise_created_by: UUID,
    acl_user_ids: list,
) -> bool:
    """DR-EXB-003: SYSTEM + ACTIVE visivel a todos autenticados.
    DR-EXB-004: ORG RESTRICTED = criador + ACL; ORG_WIDE = qualquer membro da org."""
    if exercise_scope == "SYSTEM":
        return True
    # ORG scope
    if exercise_org_id != actor_org_id:
        return False
    if exercise_visibility_mode == "ORG_WIDE":
        return True
    # RESTRICTED: criador ou ACL
    if actor_id == exercise_created_by:
        return True
    return actor_id in acl_user_ids


def assert_can_manage_acl(
    role: RoleLabel,
    actor_id: UUID,
    exercise_scope: str,
    exercise_created_by: UUID,
    exercise_visibility_mode: str,
) -> None:
    """INV-EXB-010: ACL somente para ORG/RESTRICTED"""
    if exercise_scope == "SYSTEM":
        raise ExerciseConflict("ACL nao se aplica a exercicios SYSTEM")
    if exercise_visibility_mode != "RESTRICTED":
        raise ExerciseConflict("ACL somente para visibilityMode=RESTRICTED")
    if role in (RoleLabel.ATHLETE, RoleLabel.MEMBER):
        raise InsufficientPrivilege("Sem permissao para gerenciar ACL")
    if role == RoleLabel.COACH and actor_id != exercise_created_by:
        raise InsufficientPrivilege("Coach so pode gerenciar ACL de exercicios que criou")


def assert_can_manage_relations(
    role: RoleLabel,
    actor_id: UUID,
    from_exercise_created_by: UUID,
) -> None:
    if role in (RoleLabel.ATHLETE, RoleLabel.MEMBER):
        raise InsufficientPrivilege("Sem permissao para gerenciar relacoes")
    if role == RoleLabel.COACH and actor_id != from_exercise_created_by:
        raise InsufficientPrivilege("Coach so pode gerenciar relacoes de exercicios que criou")
