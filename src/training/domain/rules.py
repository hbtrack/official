"""
Regras de domínio — módulo training.
Derivadas de:
  - docs/hbtrack/modulos/training/DOMAIN_RULES_TRAINING.md
  - docs/hbtrack/modulos/training/PERMISSIONS_TRAINING.md
  - docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md
ADR-008: RBAC flat de 5 roles.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from .common.enums import RoleLabel  # SSOT; re-exportado para compat
from .entities import AttendanceSource, AttendanceStatus, TrainingSessionStatus


# ---------------------------------------------------------------------------
# Exceções de domínio
# ---------------------------------------------------------------------------

class InsufficientPrivilege(Exception):
    """BFLA: ator não tem permissão para a operação."""


class TrainingSessionNotFound(Exception):
    pass


class SessionBlockNotFound(Exception):
    pass


class InvalidStatusTransition(Exception):
    """FSM: transição de estado inválida (INV-TRAIN-006)."""


class SessionNotMutable(Exception):
    """Sessão em estado que não permite edição destrutiva."""


class WellnessWindowClosed(Exception):
    """Janela temporal de wellness fechada (INV-TRAIN-002/003)."""


class DuplicateWellnessEntry(Exception):
    """INV-TRAIN-009/010: já existe wellness ativo."""


class WellnessEntryNotFound(Exception):
    """Registro de wellness não encontrado para sessão/atleta."""


class AttendanceRecordNotFound(Exception):
    """Registro de presença não encontrado."""


class MesocycleNotFound(Exception):
    """Mesociclo não encontrado."""


class MicrocycleNotFound(Exception):
    """Microciclo não encontrado."""


class ExecutionRecordNotFound(Exception):
    """Registro de execução não encontrado."""


class FeedbackThreadNotFound(Exception):
    """Thread de feedback não encontrada."""


class AttentionQueueItemNotFound(Exception):
    """Item da attention queue não encontrado."""


class AttentionQueueConflict(Exception):
    """Item da attention queue já foi actionado ou está em estado inválido."""


class RecommendationNotFound(Exception):
    """Recommendation não encontrada."""


class RecommendationConflict(Exception):
    """Recommendation não está em estado compatível com a ação solicitada."""


class IneligibilityDeclarationNotFound(Exception):
    """Declaração de indisponibilidade não encontrada."""


class ElasticSumRuleViolation(Exception):
    """INV-TRAIN-083: soma de duração dos blocos excede limite elástico."""


# ---------------------------------------------------------------------------
# Exceções de conflito de estado (ValueError semântico → 409)
# ---------------------------------------------------------------------------

class FeedbackThreadAlreadyClosed(ValueError):
    """Thread de feedback já está fechada — não pode ser fechada novamente."""


class IneligibilityStateConflict(ValueError):
    """Declaração de indisponibilidade não permitida para o estado atual da sessão."""


class SuggestionStateConflict(ValueError):
    """Sugestão não pode ser submetida para sessão neste estado."""


# ---------------------------------------------------------------------------
# FSM da TrainingSession — INV-TRAIN-006
# ---------------------------------------------------------------------------

VALID_TRANSITIONS: dict[TrainingSessionStatus, set[TrainingSessionStatus]] = {
    TrainingSessionStatus.DRAFT: {
        TrainingSessionStatus.SCHEDULED,
        TrainingSessionStatus.PUBLISHED,
        TrainingSessionStatus.CANCELLED,
    },
    TrainingSessionStatus.SCHEDULED: {
        TrainingSessionStatus.PUBLISHED,
        TrainingSessionStatus.IN_PROGRESS,
        TrainingSessionStatus.CANCELLED,
    },
    TrainingSessionStatus.PUBLISHED: {
        TrainingSessionStatus.SCHEDULED,
        TrainingSessionStatus.IN_PROGRESS,
        TrainingSessionStatus.CANCELLED,
    },
    TrainingSessionStatus.IN_PROGRESS: {
        TrainingSessionStatus.COMPLETED,
        TrainingSessionStatus.CANCELLED,
    },
    TrainingSessionStatus.COMPLETED: {
        TrainingSessionStatus.ARCHIVED,
    },
    TrainingSessionStatus.CANCELLED: set(),
    TrainingSessionStatus.ARCHIVED: set(),
}

MUTABLE_STATES: set[TrainingSessionStatus] = {
    TrainingSessionStatus.DRAFT,
    TrainingSessionStatus.SCHEDULED,
    TrainingSessionStatus.PUBLISHED,
}


def assert_valid_transition(
    current: TrainingSessionStatus,
    target: TrainingSessionStatus,
) -> None:
    """INV-TRAIN-006: transição deve estar no grafo FSM."""
    if target not in VALID_TRANSITIONS.get(current, set()):
        raise InvalidStatusTransition(
            f"INV-TRAIN-006: transição {current} → {target} é inválida"
        )


def assert_session_mutable(status: TrainingSessionStatus) -> None:
    """Sessão deve estar em estado mutável (DRAFT/SCHEDULED/PUBLISHED)."""
    if status not in MUTABLE_STATES:
        raise SessionNotMutable(
            f"Sessão em estado {status} não permite edição de blocos"
        )


# ---------------------------------------------------------------------------
# Permissões — DR-TRAIN-001, PERMISSIONS_TRAINING.md
# ---------------------------------------------------------------------------

STAFF_ROLES: frozenset[RoleLabel] = frozenset({
    RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH
})

CAN_CREATE_SESSION: frozenset[RoleLabel] = frozenset({
    RoleLabel.ADMIN, RoleLabel.COORDINATOR, RoleLabel.COACH
})

CAN_DELETE_SESSION: frozenset[RoleLabel] = frozenset({
    RoleLabel.ADMIN, RoleLabel.COORDINATOR
})

CAN_ARCHIVE_SESSION: frozenset[RoleLabel] = frozenset({
    RoleLabel.ADMIN, RoleLabel.COORDINATOR
})


def assert_can_create_session(role: RoleLabel) -> None:
    """DR-TRAIN-001: apenas coach/coordinator/admin podem criar sessões."""
    if role not in CAN_CREATE_SESSION:
        raise InsufficientPrivilege(
            f"DR-TRAIN-001: role={role} não pode criar sessões de treino"
        )


def assert_can_modify_session(role: RoleLabel) -> None:
    """Apenas staff pode modificar sessões."""
    if role not in STAFF_ROLES:
        raise InsufficientPrivilege(
            f"role={role} não tem permissão para modificar sessões"
        )


def assert_can_delete_session(role: RoleLabel) -> None:
    """Apenas admin/coordinator podem excluir sessões."""
    if role not in CAN_DELETE_SESSION:
        raise InsufficientPrivilege(
            f"role={role} não pode excluir sessões (somente admin/coordinator)"
        )


def assert_can_read_session(
    role: RoleLabel,
    actor_id: uuid.UUID,
    session_athlete_ids: list[uuid.UUID],
) -> None:
    """
    BOLA — OWASP API1:2023.
    Staff acessa qualquer sessão. Athlete só acessa sessão onde está incluído.
    """
    if role in STAFF_ROLES:
        return
    if role == RoleLabel.ATHLETE:
        if actor_id not in session_athlete_ids:
            raise InsufficientPrivilege(
                "BOLA: athlete não pertence a esta sessão"
            )
        return
    raise InsufficientPrivilege(f"role={role} não tem acesso a sessões de treino")


def assert_can_submit_wellness(
    role: RoleLabel,
    actor_id: uuid.UUID,
    target_athlete_id: uuid.UUID,
) -> None:
    """
    Athlete envia wellness de si mesmo. Staff pode enviar por qualquer atleta.
    BOPLA — OWASP API3:2023.
    """
    if role in STAFF_ROLES:
        return
    if role == RoleLabel.ATHLETE and actor_id == target_athlete_id:
        return
    raise InsufficientPrivilege(
        "BOPLA: athlete só pode submeter wellness de si mesmo"
    )


def assert_can_view_athlete_record(
    role: RoleLabel,
    actor_id: uuid.UUID,
    target_athlete_id: uuid.UUID,
) -> None:
    """Staff pode ver qualquer registro de atleta; athlete só pode ver o próprio."""
    if role in STAFF_ROLES:
        return
    if role == RoleLabel.ATHLETE and actor_id == target_athlete_id:
        return
    raise InsufficientPrivilege("BOLA: athlete só pode acessar o próprio registro")


def assert_can_record_attendance(
    role: RoleLabel,
    actor_id: uuid.UUID,
    target_athlete_id: uuid.UUID,
    status: AttendanceStatus,
    source: AttendanceSource,
) -> None:
    """Staff registra qualquer presença; athlete só pode fazer self-check PRECONFIRMED."""
    if role in STAFF_ROLES:
        return
    if (
        role == RoleLabel.ATHLETE
        and actor_id == target_athlete_id
        and status == AttendanceStatus.PRECONFIRMED
        and source == AttendanceSource.ATHLETE_SELFCHECK
    ):
        return
    raise InsufficientPrivilege(
        "attendance: athlete só pode registrar PRECONFIRMED de si mesmo via athlete_selfcheck"
    )


# ---------------------------------------------------------------------------
# Janelas temporais
# ---------------------------------------------------------------------------

def assert_wellness_pre_window(session_at: datetime) -> None:
    """
    INV-TRAIN-002: submissão/edição é bloqueada quando NOW_UTC >= session_at - 2h + 30s.
    """
    now = datetime.now(tz=timezone.utc)
    deadline = session_at - timedelta(hours=2) + timedelta(seconds=30)
    if now >= deadline:
        raise WellnessWindowClosed(
            f"INV-TRAIN-002: janela wellness_pre fechada. deadline_utc={deadline.isoformat()}"
        )


def assert_wellness_post_window(created_at: datetime) -> None:
    """
    INV-TRAIN-003: edição bloqueada quando NOW_UTC >= created_at + 24h.
    Tolerância de ±30s de clock skew.
    """
    now = datetime.now(tz=timezone.utc)
    deadline = created_at + timedelta(hours=24) + timedelta(seconds=30)
    if now >= deadline:
        raise WellnessWindowClosed(
            f"INV-TRAIN-003: janela wellness_post fechada. deadline_utc={deadline.isoformat()}"
        )


def assert_session_not_historical(session_at: datetime) -> None:
    """INV-TRAIN-005: sessões com session_at > 60 dias são somente leitura."""
    now = datetime.now(tz=timezone.utc)
    if (now - session_at).days > 60:
        raise SessionNotMutable(
            "INV-TRAIN-005: sessão com mais de 60 dias é somente leitura"
        )


# ---------------------------------------------------------------------------
# INV-TRAIN-083 — Elastic Sum Rule
# ---------------------------------------------------------------------------

def assert_elastic_sum_rule(
    duration_planned_minutes: Optional[int],
    blocks_total_minutes: int,
    new_block_minutes: int,
) -> None:
    """
    INV-TRAIN-083: SUM(durationMinutes) ≤ durationPlannedMinutes + MIN(durationPlannedMinutes × 0.10, 10).
    Violação dentro da tolerância → warning (não lança). Fora → ElasticSumRuleViolation (422).
    """
    if duration_planned_minutes is None:
        return  # sem planned, não há como validar
    total = blocks_total_minutes + new_block_minutes
    tolerance = min(duration_planned_minutes * 0.10, 10)
    hard_limit = duration_planned_minutes + tolerance
    if total > hard_limit:
        raise ElasticSumRuleViolation(
            f"INV-TRAIN-083: total de blocos ({total}min) excede limite "
            f"({hard_limit:.1f}min = {duration_planned_minutes}min + {tolerance:.1f}min tolerância)"
        )
