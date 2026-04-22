"""
Enums canônicos do módulo training — SSOT.

Derivados de:
- contracts/schemas/training/*.schema.json
- docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md
- docs/hbtrack/modulos/training/DOMAIN_RULES_TRAINING.md
- ADR-008 (RBAC flat), ADR-017 (FSM TrainingSession)

Os módulos `domain.entities` e `domain.rules` re-exportam estes símbolos
como shim para preservar a surface pública existente.
"""
from __future__ import annotations

from enum import StrEnum


class RoleLabel(StrEnum):
    """5 roles canônicos — ADR-008."""
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    COACH = "coach"
    ATHLETE = "athlete"
    MEMBER = "member"


class TrainingSessionStatus(StrEnum):
    """FSM canônica ADR-017 — 7 estados (INV-TRAIN-006)."""
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class SessionBlockPhase(StrEnum):
    WARMUP = "WARMUP"
    ACTIVATION = "ACTIVATION"
    TECHNICAL = "TECHNICAL"
    DECISION_MAKING = "DECISION_MAKING"
    TACTICAL = "TACTICAL"
    REDUCED_GAME = "REDUCED_GAME"
    COOLDOWN = "COOLDOWN"


class SessionBlockIntensity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    MAXIMUM = "MAXIMUM"


class AttendanceStatus(StrEnum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    JUSTIFIED = "JUSTIFIED"
    PRECONFIRMED = "PRECONFIRMED"


class AttendanceSource(StrEnum):
    COACH_INPUT = "coach_input"
    ATHLETE_SELFCHECK = "athlete_selfcheck"
    CORRECTION = "correction"


class ExecutionType(StrEnum):
    SESSION_EXECUTION = "SESSION_EXECUTION"
    BLOCK_EXECUTION = "BLOCK_EXECUTION"
    LIVE_ADJUSTMENT = "LIVE_ADJUSTMENT"
    CONSTRAINT_OVERRIDE = "CONSTRAINT_OVERRIDE"
    ALTERNATE_EXERCISE = "ALTERNATE_EXERCISE"
    LOAD_RECALCULATION = "LOAD_RECALCULATION"


class IndividualizationMode(StrEnum):
    COLLECTIVE_UNIFORM = "COLLECTIVE_UNIFORM"
    COLLECTIVE_WITH_VARIANTS = "COLLECTIVE_WITH_VARIANTS"
    INDIVIDUAL_ONLY = "INDIVIDUAL_ONLY"


class SessionObjectiveOrigin(StrEnum):
    NEED_DETECTED = "NEED_DETECTED"
    COMPETITIVE_FOCUS = "COMPETITIVE_FOCUS"
    DEVELOPMENT_GOAL = "DEVELOPMENT_GOAL"
    MANUAL_COACH_RATIONALE = "MANUAL_COACH_RATIONALE"


class ConversationOutcome(StrEnum):
    REFLECTION_DOCUMENTED = "REFLECTION_DOCUMENTED"
    COMMITMENT_MADE = "COMMITMENT_MADE"
    FOLLOWUP_SCHEDULED = "FOLLOWUP_SCHEDULED"
    DECISION_RECORDED = "DECISION_RECORDED"
    PENDING_FOLLOWUP = "PENDING_FOLLOWUP"


class RecommendationActionType(StrEnum):
    MODIFY_FOCUS = "MODIFY_FOCUS"
    ADD_BLOCK = "ADD_BLOCK"
    REMOVE_BLOCK = "REMOVE_BLOCK"
    ADJUST_DURATION = "ADJUST_DURATION"
    ADD_OBJECTIVE = "ADD_OBJECTIVE"
    ADJUST_LOAD = "ADJUST_LOAD"
    REVIEW_ATHLETE = "REVIEW_ATHLETE"


class RecommendationStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DISMISSED = "DISMISSED"


class RecommendationPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


__all__ = [
    "RoleLabel",
    "TrainingSessionStatus",
    "SessionBlockPhase",
    "SessionBlockIntensity",
    "AttendanceStatus",
    "AttendanceSource",
    "ExecutionType",
    "IndividualizationMode",
    "SessionObjectiveOrigin",
    "ConversationOutcome",
    "RecommendationActionType",
    "RecommendationStatus",
    "RecommendationPriority",
]
