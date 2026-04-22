"""
Entities package — decomposição por agregado (Fase 5.3).  [DEPRECATED — remover em release N+2]

Re-exporta as 13 dataclasses em submódulos (sessions, blocks, wellness,
attendance, execution, communication, eligibility, planning) e o facade
dos enums em `..common.enums`. O objetivo é preservar a surface pública
`training.domain.entities.<Nome>` usada por tests, policies, api/ e
infrastructure/ — zero-gap em relação ao módulo monolítico original.

CAMINHOS NOVOS (use estes):
  training.domain.entities.sessions   → TrainingSession, SessionObjective
  training.domain.entities.blocks     → SessionBlock
  training.domain.entities.wellness   → WellnessPre, WellnessPost
  training.domain.entities.attendance → AttendanceRecord
  training.domain.entities.execution  → ExecutionRecord
  training.domain.entities.planning   → Mesocycle, Microcycle
  training.domain.entities.communication → FeedbackThread, Recommendation, AttentionQueueItem
  training.domain.entities.eligibility   → AthleteIneligibilityDeclaration
  training.domain.common.enums        → todos os StrEnums
"""
from __future__ import annotations

_DEPRECATED_EXPORTS: dict[str, str] = {
    # Entities
    "AttendanceRecord": "training.domain.entities.attendance",
    "SessionBlock": "training.domain.entities.blocks",
    "AttentionQueueItem": "training.domain.entities.communication",
    "FeedbackThread": "training.domain.entities.communication",
    "Recommendation": "training.domain.entities.communication",
    "AthleteIneligibilityDeclaration": "training.domain.entities.eligibility",
    "ExecutionRecord": "training.domain.entities.execution",
    "Mesocycle": "training.domain.entities.planning",
    "Microcycle": "training.domain.entities.planning",
    "SessionObjective": "training.domain.entities.sessions",
    "TrainingSession": "training.domain.entities.sessions",
    "WellnessPost": "training.domain.entities.wellness",
    "WellnessPre": "training.domain.entities.wellness",
    # Enums (facade — SSOT em training.domain.common.enums)
    "AttendanceSource": "training.domain.common.enums",
    "AttendanceStatus": "training.domain.common.enums",
    "ConversationOutcome": "training.domain.common.enums",
    "ExecutionType": "training.domain.common.enums",
    "IndividualizationMode": "training.domain.common.enums",
    "RecommendationActionType": "training.domain.common.enums",
    "RecommendationPriority": "training.domain.common.enums",
    "RecommendationStatus": "training.domain.common.enums",
    "SessionBlockIntensity": "training.domain.common.enums",
    "SessionBlockPhase": "training.domain.common.enums",
    "SessionObjectiveOrigin": "training.domain.common.enums",
    "TrainingSessionStatus": "training.domain.common.enums",
}

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


def __getattr__(name: str):
    if name in _DEPRECATED_EXPORTS:
        import importlib
        import warnings
        warnings.warn(
            f"Importar '{name}' de 'training.domain.entities' é depreciádo. "
            f"Use '{_DEPRECATED_EXPORTS[name]}' diretamente. "
            "Este shim será removido em release N+2.",
            DeprecationWarning,
            stacklevel=2,
        )
        mod = importlib.import_module(_DEPRECATED_EXPORTS[name])
        value = getattr(mod, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'training.domain.entities' has no attribute {name!r}")

