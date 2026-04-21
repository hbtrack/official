"""
Entities package — decomposição por agregado (Fase 5.3).

Re-exporta as 13 dataclasses em submódulos (sessions, blocks, wellness,
attendance, execution, communication, eligibility, planning) e o facade
dos enums em `..common.enums`. O objetivo é preservar a surface pública
`training.domain.entities.<Nome>` usada por tests, policies, api/ e
infrastructure/ — zero-gap em relação ao módulo monolítico original.
"""
from __future__ import annotations

# Enums — facade de compatibilidade (SSOT em domain/common/enums.py).
from ..common.enums import (
    AttendanceSource,
    AttendanceStatus,
    ConversationOutcome,
    ExecutionType,
    IndividualizationMode,
    RecommendationActionType,
    RecommendationPriority,
    RecommendationStatus,
    SessionBlockIntensity,
    SessionBlockPhase,
    SessionObjectiveOrigin,
    TrainingSessionStatus,
)

# Entities — um módulo por agregado.
from .attendance import AttendanceRecord
from .blocks import SessionBlock
from .communication import AttentionQueueItem, FeedbackThread, Recommendation
from .eligibility import AthleteIneligibilityDeclaration
from .execution import ExecutionRecord
from .planning import Mesocycle, Microcycle
from .sessions import SessionObjective, TrainingSession
from .wellness import WellnessPost, WellnessPre

__all__ = [
    # Enums (facade)
    "AttendanceSource",
    "AttendanceStatus",
    "ConversationOutcome",
    "ExecutionType",
    "IndividualizationMode",
    "RecommendationActionType",
    "RecommendationPriority",
    "RecommendationStatus",
    "SessionBlockIntensity",
    "SessionBlockPhase",
    "SessionObjectiveOrigin",
    "TrainingSessionStatus",
    # Entities
    "AthleteIneligibilityDeclaration",
    "AttendanceRecord",
    "AttentionQueueItem",
    "ExecutionRecord",
    "FeedbackThread",
    "Mesocycle",
    "Microcycle",
    "Recommendation",
    "SessionBlock",
    "SessionObjective",
    "TrainingSession",
    "WellnessPost",
    "WellnessPre",
]
