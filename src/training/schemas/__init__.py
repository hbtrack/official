"""
Schemas package — decomposição por agregado (Fase 5.6).  [DEPRECATED — remover em release N+2]

Re-exporta os schemas Pydantic de todos os submódulos para preservar
`from training.schemas import XOut/XIn` sem alterações em api/.

CAMINHOS NOVOS (use estes):
  training.schemas.sessions     → TrainingSessionOut, TrainingSessionListOut, CreateTrainingSessionIn, ...
  training.schemas.blocks       → SessionBlockOut, SessionBlockListOut, AddSessionBlockIn, ...
  training.schemas.wellness     → WellnessPreOut, SubmitWellnessPreIn, ...
  training.schemas.attendance   → AttendanceRecordOut, AttendanceListOut, ...
  training.schemas.execution    → ExecutionRecordOut, CreateExecutionRecordIn, ...
  training.schemas.planning     → MesocycleOut, CreateMesocycleIn, ...
  training.schemas.communication → FeedbackThreadOut, CreateFeedbackThreadIn, ...
  training.schemas.eligibility  → IneligibilityOut, SubmitIneligibilityDeclarationIn, ...
"""
from __future__ import annotations

# CODEGEN CUTOVER — generated layer linked (não depreciado)
from ..generated import schemas as _gen_schemas  # noqa: F401

_DEPRECATED_EXPORTS: dict[str, str] = {
    # sessions
    "TrainingSessionOut": "training.schemas.sessions",
    "TrainingSessionListOut": "training.schemas.sessions",
    "CreateTrainingSessionIn": "training.schemas.sessions",
    "UpdateTrainingSessionIn": "training.schemas.sessions",
    "TransitionOut": "training.schemas.sessions",
    "ErrorOut": "training.schemas.sessions",
    # blocks
    "SessionBlockOut": "training.schemas.blocks",
    "SessionBlockListOut": "training.schemas.blocks",
    "AddSessionBlockIn": "training.schemas.blocks",
    "UpdateSessionBlockIn": "training.schemas.blocks",
    "ReorderSessionBlocksIn": "training.schemas.blocks",
    # attendance
    "AttendanceRecordOut": "training.schemas.attendance",
    "AttendanceListOut": "training.schemas.attendance",
    "RecordSessionAttendanceIn": "training.schemas.attendance",
    # wellness
    "WellnessPreOut": "training.schemas.wellness",
    "SubmitWellnessPreIn": "training.schemas.wellness",
    "UpdateWellnessPreIn": "training.schemas.wellness",
    "WellnessPostOut": "training.schemas.wellness",
    "SubmitWellnessPostIn": "training.schemas.wellness",
    "UpdateWellnessPostIn": "training.schemas.wellness",
    # execution
    "ExecutionRecordOut": "training.schemas.execution",
    "ExecutionRecordListOut": "training.schemas.execution",
    "CreateExecutionRecordIn": "training.schemas.execution",
    "SessionObjectiveOut": "training.schemas.execution",
    "SessionObjectiveListOut": "training.schemas.execution",
    "CreateSessionObjectiveIn": "training.schemas.execution",
    "LoadChartEntryOut": "training.schemas.execution",
    "LoadChartOut": "training.schemas.execution",
    # planning
    "MesocycleOut": "training.schemas.planning",
    "MesocycleListOut": "training.schemas.planning",
    "CreateMesocycleIn": "training.schemas.planning",
    "UpdateMesocycleIn": "training.schemas.planning",
    "MicrocycleOut": "training.schemas.planning",
    "MicrocycleListOut": "training.schemas.planning",
    "CreateMicrocycleIn": "training.schemas.planning",
    "UpdateMicrocycleIn": "training.schemas.planning",
    # communication
    "FeedbackThreadOut": "training.schemas.communication",
    "FeedbackThreadListOut": "training.schemas.communication",
    "CreateFeedbackThreadIn": "training.schemas.communication",
    "CloseFeedbackThreadIn": "training.schemas.communication",
    "AttentionQueueItemOut": "training.schemas.communication",
    "AttentionQueueListOut": "training.schemas.communication",
    "ResolveAttentionQueueItemIn": "training.schemas.communication",
    "DismissAttentionQueueItemIn": "training.schemas.communication",
    "EscalateAttentionQueueItemIn": "training.schemas.communication",
    "RecommendationOut": "training.schemas.communication",
    "RecommendationListOut": "training.schemas.communication",
    "AcceptRecommendationIn": "training.schemas.communication",
    "DismissRecommendationIn": "training.schemas.communication",
    "SubmitTrainingSuggestionIn": "training.schemas.communication",
    # eligibility
    "AthleteIneligibilityDeclarationOut": "training.schemas.eligibility",
    "SubmitIneligibilityDeclarationIn": "training.schemas.eligibility",
}

__all__ = [
    # sessions
    "TrainingSessionOut",
    "TrainingSessionListOut",
    "CreateTrainingSessionIn",
    "UpdateTrainingSessionIn",
    "TransitionOut",
    "ErrorOut",
    # blocks
    "SessionBlockOut",
    "SessionBlockListOut",
    "AddSessionBlockIn",
    "UpdateSessionBlockIn",
    "ReorderSessionBlocksIn",
    # attendance
    "AttendanceRecordOut",
    "AttendanceListOut",
    "RecordSessionAttendanceIn",
    # wellness
    "WellnessPreOut",
    "SubmitWellnessPreIn",
    "UpdateWellnessPreIn",
    "WellnessPostOut",
    "SubmitWellnessPostIn",
    "UpdateWellnessPostIn",
    # execution
    "ExecutionRecordOut",
    "ExecutionRecordListOut",
    "CreateExecutionRecordIn",
    "SessionObjectiveOut",
    "SessionObjectiveListOut",
    "CreateSessionObjectiveIn",
    "LoadChartEntryOut",
    "LoadChartOut",
    # planning
    "MesocycleOut",
    "MesocycleListOut",
    "CreateMesocycleIn",
    "UpdateMesocycleIn",
    "MicrocycleOut",
    "MicrocycleListOut",
    "CreateMicrocycleIn",
    "UpdateMicrocycleIn",
    # communication
    "FeedbackThreadOut",
    "FeedbackThreadListOut",
    "CreateFeedbackThreadIn",
    "CloseFeedbackThreadIn",
    "AttentionQueueItemOut",
    "AttentionQueueListOut",
    "ResolveAttentionQueueItemIn",
    "DismissAttentionQueueItemIn",
    "EscalateAttentionQueueItemIn",
    "RecommendationOut",
    "RecommendationListOut",
    "AcceptRecommendationIn",
    "DismissRecommendationIn",
    "SubmitTrainingSuggestionIn",
    # eligibility
    "AthleteIneligibilityDeclarationOut",
    "SubmitIneligibilityDeclarationIn",
]


def __getattr__(name: str):
    if name in _DEPRECATED_EXPORTS:
        import importlib
        import warnings
        warnings.warn(
            f"Importar '{name}' de 'training.schemas' é depreciado. "
            f"Use '{_DEPRECATED_EXPORTS[name]}' diretamente. "
            "Este shim será removido em release N+2.",
            DeprecationWarning,
            stacklevel=2,
        )
        mod = importlib.import_module(_DEPRECATED_EXPORTS[name])
        value = getattr(mod, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'training.schemas' has no attribute {name!r}")

