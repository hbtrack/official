from __future__ import annotations

# CODEGEN CUTOVER — generated layer linked
from ..generated import schemas as _gen_schemas  # noqa: F401

from .sessions import (
    TrainingSessionOut,
    TrainingSessionListOut,
    CreateTrainingSessionIn,
    UpdateTrainingSessionIn,
    TransitionOut,
    ErrorOut,
)
from .blocks import (
    SessionBlockOut,
    SessionBlockListOut,
    AddSessionBlockIn,
    UpdateSessionBlockIn,
    ReorderSessionBlocksIn,
)
from .attendance import (
    AttendanceRecordOut,
    AttendanceListOut,
    RecordSessionAttendanceIn,
)
from .wellness import (
    WellnessPreOut,
    SubmitWellnessPreIn,
    UpdateWellnessPreIn,
    WellnessPostOut,
    SubmitWellnessPostIn,
    UpdateWellnessPostIn,
)
from .execution import (
    ExecutionRecordOut,
    ExecutionRecordListOut,
    CreateExecutionRecordIn,
    SessionObjectiveOut,
    SessionObjectiveListOut,
    CreateSessionObjectiveIn,
    LoadChartEntryOut,
    LoadChartOut,
)
from .planning import (
    MesocycleOut,
    MesocycleListOut,
    CreateMesocycleIn,
    UpdateMesocycleIn,
    MicrocycleOut,
    MicrocycleListOut,
    CreateMicrocycleIn,
    UpdateMicrocycleIn,
)
from .communication import (
    FeedbackThreadOut,
    FeedbackThreadListOut,
    CreateFeedbackThreadIn,
    CloseFeedbackThreadIn,
    AttentionQueueItemOut,
    AttentionQueueListOut,
    ResolveAttentionQueueItemIn,
    DismissAttentionQueueItemIn,
    EscalateAttentionQueueItemIn,
    RecommendationOut,
    RecommendationListOut,
    AcceptRecommendationIn,
    DismissRecommendationIn,
    SubmitTrainingSuggestionIn,
)
from .eligibility import (
    AthleteIneligibilityDeclarationOut,
    SubmitIneligibilityDeclarationIn,
)

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
