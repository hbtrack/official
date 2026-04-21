"""
SHIM — application/use_cases.py

Re-exporta todos os *UseCase e *Input/*Output dos subpacotes para manter
a surface pública inalterada. Os consumidores existentes (api/handlers/*)
continuam a importar de `.use_cases` sem precisar de atualização.

Fase 3 da refatoração training. Ver docs/rafatora_training.md.
"""
from __future__ import annotations

# sessions
from .sessions.commands import (  # noqa: F401
    CreateTrainingSessionUseCase,
    DeleteTrainingSessionUseCase,
    TransitionTrainingSessionUseCase,
    UpdateTrainingSessionUseCase,
)
from .sessions.dto import (  # noqa: F401
    CreateTrainingSessionInput,
    DeleteTrainingSessionInput,
    GetTrainingSessionInput,
    ListTrainingSessionsInput,
    ListTrainingSessionsOutput,
    TransitionTrainingSessionInput,
    UpdateTrainingSessionInput,
)
from .sessions.queries import (  # noqa: F401
    GetTrainingSessionUseCase,
    ListTrainingSessionsUseCase,
)

# blocks
from .blocks.commands import (  # noqa: F401
    AddSessionBlockUseCase,
    DeleteSessionBlockUseCase,
    ReorderSessionBlocksUseCase,
    UpdateSessionBlockUseCase,
)
from .blocks.dto import (  # noqa: F401
    AddSessionBlockInput,
    DeleteSessionBlockInput,
    GetSessionBlockInput,
    ListSessionBlocksInput,
    ReorderSessionBlocksInput,
    UpdateSessionBlockInput,
)
from .blocks.queries import (  # noqa: F401
    GetSessionBlockUseCase,
    ListSessionBlocksUseCase,
)

# wellness
from .wellness.commands import (  # noqa: F401
    SubmitWellnessPostUseCase,
    SubmitWellnessPreUseCase,
    UpdateWellnessPostUseCase,
    UpdateWellnessPreUseCase,
)
from .wellness.dto import (  # noqa: F401
    GetWellnessPostInput,
    GetWellnessPreInput,
    SubmitWellnessPostInput,
    SubmitWellnessPreInput,
    UpdateWellnessPostInput,
    UpdateWellnessPreInput,
)
from .wellness.queries import (  # noqa: F401
    GetWellnessPostUseCase,
    GetWellnessPreUseCase,
)

# attendance
from .attendance.commands import RecordSessionAttendanceUseCase  # noqa: F401
from .attendance.dto import (  # noqa: F401
    ListSessionAttendanceInput,
    RecordSessionAttendanceInput,
)
from .attendance.queries import ListSessionAttendanceUseCase  # noqa: F401

# execution
from .execution.commands import (  # noqa: F401
    CreateExecutionRecordUseCase,
    CreateSessionObjectiveUseCase,
)
from .execution.dto import (  # noqa: F401
    CreateExecutionRecordInput,
    CreateSessionObjectiveInput,
    GetExecutionRecordInput,
    ListExecutionRecordsInput,
    ListSessionObjectivesInput,
)
from .execution.queries import (  # noqa: F401
    GetExecutionRecordUseCase,
    ListExecutionRecordsUseCase,
    ListSessionObjectivesUseCase,
)

# planning
from .planning.commands import (  # noqa: F401
    CreateMesocycleUseCase,
    CreateMicrocycleUseCase,
    UpdateMesocycleUseCase,
    UpdateMicrocycleUseCase,
)
from .planning.dto import (  # noqa: F401
    CreateMesocycleInput,
    CreateMicrocycleInput,
    GetMesocycleInput,
    GetMicrocycleInput,
    ListMesocyclesInput,
    ListMicrocyclesInput,
    UpdateMesocycleInput,
    UpdateMicrocycleInput,
)
from .planning.queries import (  # noqa: F401
    GetMesocycleUseCase,
    GetMicrocycleUseCase,
    ListMesocyclesUseCase,
    ListMicrocyclesUseCase,
)

# communication
from .communication.commands import (  # noqa: F401
    AcceptRecommendationUseCase,
    CloseFeedbackThreadUseCase,
    CreateFeedbackThreadUseCase,
    DismissAttentionQueueItemUseCase,
    DismissRecommendationUseCase,
    EscalateAttentionQueueItemUseCase,
    ResolveAttentionQueueItemUseCase,
    SubmitTrainingSuggestionUseCase,
)
from .communication.dto import (  # noqa: F401
    AcceptRecommendationInput,
    CloseFeedbackThreadInput,
    CreateFeedbackThreadInput,
    DismissAttentionQueueItemInput,
    DismissRecommendationInput,
    EscalateAttentionQueueItemInput,
    ListAttentionQueueItemsInput,
    ListChatMessagesInput,
    ListFeedbackThreadsInput,
    ListRecommendationsInput,
    ResolveAttentionQueueItemInput,
    SubmitTrainingSuggestionInput,
)
from .communication.queries import (  # noqa: F401
    ListAttentionQueueItemsUseCase,
    ListChatMessagesUseCase,
    ListFeedbackThreadsUseCase,
    ListRecommendationsUseCase,
)

# eligibility
from .eligibility.commands import SubmitIneligibilityDeclarationUseCase  # noqa: F401
from .eligibility.dto import (  # noqa: F401
    GetIneligibilityStatusInput,
    SubmitIneligibilityDeclarationInput,
)
from .eligibility.queries import GetIneligibilityStatusUseCase  # noqa: F401

# analytics
from .analytics.dto import GetLoadChartInput, GetLoadChartResult  # noqa: F401
from .analytics.queries import GetLoadChartUseCase  # noqa: F401
