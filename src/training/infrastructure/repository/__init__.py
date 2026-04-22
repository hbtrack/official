"""
Repository package — decomposição por agregado (Fase 5.4).  [DEPRECATED — remover em release N+2]

Substitui o módulo monolítico `infrastructure/repository.py` por submódulos
um por agregado. Re-exporta a surface pública (13 Repository classes) para
preservar `from training.infrastructure.repository import XRepository` sem
mudanças em application/, api/ ou testes.

CAMINHOS NOVOS (use estes):
  training.infrastructure.repository.sessions     → TrainingSessionRepository, SessionObjectiveRepository
  training.infrastructure.repository.blocks       → SessionBlockRepository
  training.infrastructure.repository.wellness     → WellnessPreRepository, WellnessPostRepository
  training.infrastructure.repository.attendance   → AttendanceRepository
  training.infrastructure.repository.execution    → ExecutionRecordRepository
  training.infrastructure.repository.planning     → MesocycleRepository, MicrocycleRepository
  training.infrastructure.repository.communication → AttentionQueueRepository, FeedbackThreadRepository, RecommendationRepository
  training.infrastructure.repository.eligibility  → AthleteIneligibilityDeclarationRepository
"""
from __future__ import annotations

_DEPRECATED_EXPORTS: dict[str, str] = {
    "AthleteIneligibilityDeclarationRepository": "training.infrastructure.repository.eligibility",
    "AttendanceRepository": "training.infrastructure.repository.attendance",
    "AttentionQueueRepository": "training.infrastructure.repository.communication",
    "ExecutionRecordRepository": "training.infrastructure.repository.execution",
    "FeedbackThreadRepository": "training.infrastructure.repository.communication",
    "MesocycleRepository": "training.infrastructure.repository.planning",
    "MicrocycleRepository": "training.infrastructure.repository.planning",
    "RecommendationRepository": "training.infrastructure.repository.communication",
    "SessionBlockRepository": "training.infrastructure.repository.blocks",
    "SessionObjectiveRepository": "training.infrastructure.repository.sessions",
    "TrainingSessionRepository": "training.infrastructure.repository.sessions",
    "WellnessPostRepository": "training.infrastructure.repository.wellness",
    "WellnessPreRepository": "training.infrastructure.repository.wellness",
}

__all__ = [
    "AthleteIneligibilityDeclarationRepository",
    "AttendanceRepository",
    "AttentionQueueRepository",
    "ExecutionRecordRepository",
    "FeedbackThreadRepository",
    "MesocycleRepository",
    "MicrocycleRepository",
    "RecommendationRepository",
    "SessionBlockRepository",
    "SessionObjectiveRepository",
    "TrainingSessionRepository",
    "WellnessPostRepository",
    "WellnessPreRepository",
]


def __getattr__(name: str):
    if name in _DEPRECATED_EXPORTS:
        import importlib
        import warnings
        warnings.warn(
            f"Importar '{name}' de 'training.infrastructure.repository' é depreciádo. "
            f"Use '{_DEPRECATED_EXPORTS[name]}' diretamente. "
            "Este shim será removido em release N+2.",
            DeprecationWarning,
            stacklevel=2,
        )
        mod = importlib.import_module(_DEPRECATED_EXPORTS[name])
        value = getattr(mod, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'training.infrastructure.repository' has no attribute {name!r}")

