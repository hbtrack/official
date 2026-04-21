"""
TrainingServices — facade de factory de UseCases.

REGRA INQUEBRÁVEL: este módulo só expõe métodos (factories).
Nunca deve ter atributos de repositório armazenados na instância.
Cada factory cria o UseCase (e seus repositórios) na chamada, garantindo
que não haja estado compartilhado entre requisições.

Verificado pelo teste: test_services_facade.py::test_training_services_exposes_only_factories
"""
from __future__ import annotations

from ..analytics.queries import GetLoadChartUseCase
from ..attendance.commands import RecordSessionAttendanceUseCase
from ..attendance.queries import ListSessionAttendanceUseCase
from ..blocks.commands import (
    AddSessionBlockUseCase,
    DeleteSessionBlockUseCase,
    ReorderSessionBlocksUseCase,
    UpdateSessionBlockUseCase,
)
from ..blocks.queries import ListSessionBlocksUseCase
from ..communication.commands import (
    AcceptRecommendationUseCase,
    CloseFeedbackThreadUseCase,
    CreateFeedbackThreadUseCase,
    DismissAttentionQueueItemUseCase,
    DismissRecommendationUseCase,
    EscalateAttentionQueueItemUseCase,
    ResolveAttentionQueueItemUseCase,
    SubmitTrainingSuggestionUseCase,
)
from ..communication.queries import (
    ListAttentionQueueItemsUseCase,
    ListChatMessagesUseCase,
    ListFeedbackThreadsUseCase,
    ListRecommendationsUseCase,
)
from ..eligibility.commands import SubmitIneligibilityDeclarationUseCase
from ..eligibility.queries import GetIneligibilityStatusUseCase
from ..execution.commands import CreateExecutionRecordUseCase, CreateSessionObjectiveUseCase
from ..execution.queries import (
    GetExecutionRecordUseCase,
    ListExecutionRecordsUseCase,
    ListSessionObjectivesUseCase,
)
from ..planning.commands import (
    CreateMesocycleUseCase,
    CreateMicrocycleUseCase,
    UpdateMesocycleUseCase,
    UpdateMicrocycleUseCase,
)
from ..planning.queries import (
    GetMesocycleUseCase,
    GetMicrocycleUseCase,
    ListMesocyclesUseCase,
    ListMicrocyclesUseCase,
)
from ..sessions.commands import (
    CreateTrainingSessionUseCase,
    DeleteTrainingSessionUseCase,
    TransitionTrainingSessionUseCase,
    UpdateTrainingSessionUseCase,
)
from ..sessions.queries import GetTrainingSessionUseCase, ListTrainingSessionsUseCase
from ..wellness.commands import (
    SubmitWellnessPostUseCase,
    SubmitWellnessPreUseCase,
    UpdateWellnessPostUseCase,
    UpdateWellnessPreUseCase,
)
from ..wellness.queries import GetWellnessPostUseCase, GetWellnessPreUseCase
from ...domain.policies.session_access import SessionGuard
from ...infrastructure.repository import (
    AttentionQueueRepository,
    AthleteIneligibilityDeclarationRepository,
    AttendanceRepository,
    ExecutionRecordRepository,
    FeedbackThreadRepository,
    MesocycleRepository,
    MicrocycleRepository,
    RecommendationRepository,
    SessionBlockRepository,
    SessionObjectiveRepository,
    TrainingSessionRepository,
    WellnessPostRepository,
    WellnessPreRepository,
)


class TrainingServices:
    """
    Service locator de UseCases de Training.

    Cada método instancia o(s) repositório(s) necessário(s) e o UseCase,
    sem armazenar estado na instância.  Isso garante:
    - thread-safety por padrão (sem estado compartilhado)
    - ausência de vazamento de sessões de banco entre requests
    - facilidade de mock em testes (substituição via injeção de guard/policy)
    """

    # ------------------------------------------------------------------
    # Session guard
    # ------------------------------------------------------------------

    def session_guard(self) -> SessionGuard:
        return SessionGuard(TrainingSessionRepository())

    def session_block_repo(self) -> SessionBlockRepository:
        """Factory de SessionBlockRepository. Usado quando o handler precisa acesso
        direto ao repositório sem passar por um UseCase completo (ex: get_single_block)."""
        return SessionBlockRepository()

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def list_training_sessions_uc(self, cursor_codec=None) -> ListTrainingSessionsUseCase:
        return ListTrainingSessionsUseCase(TrainingSessionRepository(), cursor_codec=cursor_codec)

    def create_training_session_uc(self) -> CreateTrainingSessionUseCase:
        return CreateTrainingSessionUseCase(TrainingSessionRepository())

    def get_training_session_uc(self) -> GetTrainingSessionUseCase:
        return GetTrainingSessionUseCase(TrainingSessionRepository())

    def update_training_session_uc(self) -> UpdateTrainingSessionUseCase:
        return UpdateTrainingSessionUseCase(TrainingSessionRepository())

    def delete_training_session_uc(self) -> DeleteTrainingSessionUseCase:
        return DeleteTrainingSessionUseCase(TrainingSessionRepository())

    def transition_training_session_uc(self) -> TransitionTrainingSessionUseCase:
        return TransitionTrainingSessionUseCase(TrainingSessionRepository())

    # ------------------------------------------------------------------
    # Blocks
    # ------------------------------------------------------------------

    def list_session_blocks_uc(self) -> ListSessionBlocksUseCase:
        return ListSessionBlocksUseCase(TrainingSessionRepository(), SessionBlockRepository())

    def add_session_block_uc(self) -> AddSessionBlockUseCase:
        return AddSessionBlockUseCase(TrainingSessionRepository(), SessionBlockRepository())

    def update_session_block_uc(self) -> UpdateSessionBlockUseCase:
        return UpdateSessionBlockUseCase(TrainingSessionRepository(), SessionBlockRepository())

    def delete_session_block_uc(self) -> DeleteSessionBlockUseCase:
        return DeleteSessionBlockUseCase(TrainingSessionRepository(), SessionBlockRepository())

    def reorder_session_blocks_uc(self) -> ReorderSessionBlocksUseCase:
        return ReorderSessionBlocksUseCase(TrainingSessionRepository(), SessionBlockRepository())

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def list_execution_records_uc(self) -> ListExecutionRecordsUseCase:
        return ListExecutionRecordsUseCase(TrainingSessionRepository(), ExecutionRecordRepository())

    def create_execution_record_uc(self) -> CreateExecutionRecordUseCase:
        return CreateExecutionRecordUseCase(TrainingSessionRepository(), ExecutionRecordRepository())

    def get_execution_record_uc(self) -> GetExecutionRecordUseCase:
        return GetExecutionRecordUseCase(TrainingSessionRepository(), ExecutionRecordRepository())

    def list_session_objectives_uc(self) -> ListSessionObjectivesUseCase:
        return ListSessionObjectivesUseCase(TrainingSessionRepository(), SessionObjectiveRepository())

    def create_session_objective_uc(self) -> CreateSessionObjectiveUseCase:
        return CreateSessionObjectiveUseCase(TrainingSessionRepository(), SessionObjectiveRepository())

    # ------------------------------------------------------------------
    # Wellness
    # ------------------------------------------------------------------

    def submit_wellness_pre_uc(self) -> SubmitWellnessPreUseCase:
        return SubmitWellnessPreUseCase(TrainingSessionRepository(), WellnessPreRepository())

    def get_wellness_pre_uc(self) -> GetWellnessPreUseCase:
        return GetWellnessPreUseCase(TrainingSessionRepository(), WellnessPreRepository())

    def update_wellness_pre_uc(self) -> UpdateWellnessPreUseCase:
        return UpdateWellnessPreUseCase(TrainingSessionRepository(), WellnessPreRepository())

    def submit_wellness_post_uc(self) -> SubmitWellnessPostUseCase:
        return SubmitWellnessPostUseCase(TrainingSessionRepository(), WellnessPostRepository())

    def get_wellness_post_uc(self) -> GetWellnessPostUseCase:
        return GetWellnessPostUseCase(TrainingSessionRepository(), WellnessPostRepository())

    def update_wellness_post_uc(self) -> UpdateWellnessPostUseCase:
        return UpdateWellnessPostUseCase(TrainingSessionRepository(), WellnessPostRepository())

    # ------------------------------------------------------------------
    # Attendance
    # ------------------------------------------------------------------

    def list_session_attendance_uc(self) -> ListSessionAttendanceUseCase:
        return ListSessionAttendanceUseCase(TrainingSessionRepository(), AttendanceRepository())

    def record_session_attendance_uc(self) -> RecordSessionAttendanceUseCase:
        return RecordSessionAttendanceUseCase(TrainingSessionRepository(), AttendanceRepository())

    # ------------------------------------------------------------------
    # Feedback / Chat
    # ------------------------------------------------------------------

    def list_feedback_threads_uc(self) -> ListFeedbackThreadsUseCase:
        return ListFeedbackThreadsUseCase(TrainingSessionRepository(), FeedbackThreadRepository())

    def create_feedback_thread_uc(self) -> CreateFeedbackThreadUseCase:
        return CreateFeedbackThreadUseCase(TrainingSessionRepository(), FeedbackThreadRepository())

    def close_feedback_thread_uc(self) -> CloseFeedbackThreadUseCase:
        return CloseFeedbackThreadUseCase(TrainingSessionRepository(), FeedbackThreadRepository())

    def list_chat_messages_uc(self) -> ListChatMessagesUseCase:
        return ListChatMessagesUseCase(TrainingSessionRepository(), FeedbackThreadRepository())

    def submit_training_suggestion_uc(self) -> SubmitTrainingSuggestionUseCase:
        return SubmitTrainingSuggestionUseCase(TrainingSessionRepository(), FeedbackThreadRepository())

    # ------------------------------------------------------------------
    # Eligibility
    # ------------------------------------------------------------------

    def get_ineligibility_status_uc(self) -> GetIneligibilityStatusUseCase:
        return GetIneligibilityStatusUseCase(
            TrainingSessionRepository(), AthleteIneligibilityDeclarationRepository()
        )

    def submit_ineligibility_declaration_uc(self) -> SubmitIneligibilityDeclarationUseCase:
        return SubmitIneligibilityDeclarationUseCase(
            TrainingSessionRepository(), AthleteIneligibilityDeclarationRepository()
        )

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    def list_recommendations_uc(self) -> ListRecommendationsUseCase:
        return ListRecommendationsUseCase(TrainingSessionRepository(), RecommendationRepository())

    def accept_recommendation_uc(self) -> AcceptRecommendationUseCase:
        return AcceptRecommendationUseCase(TrainingSessionRepository(), RecommendationRepository())

    def dismiss_recommendation_uc(self) -> DismissRecommendationUseCase:
        return DismissRecommendationUseCase(TrainingSessionRepository(), RecommendationRepository())

    # ------------------------------------------------------------------
    # Attention queue
    # ------------------------------------------------------------------

    def list_attention_queue_items_uc(self) -> ListAttentionQueueItemsUseCase:
        return ListAttentionQueueItemsUseCase(TrainingSessionRepository(), AttentionQueueRepository())

    def resolve_attention_queue_item_uc(self) -> ResolveAttentionQueueItemUseCase:
        return ResolveAttentionQueueItemUseCase(TrainingSessionRepository(), AttentionQueueRepository())

    def dismiss_attention_queue_item_uc(self) -> DismissAttentionQueueItemUseCase:
        return DismissAttentionQueueItemUseCase(TrainingSessionRepository(), AttentionQueueRepository())

    def escalate_attention_queue_item_uc(self) -> EscalateAttentionQueueItemUseCase:
        return EscalateAttentionQueueItemUseCase(TrainingSessionRepository(), AttentionQueueRepository())

    # ------------------------------------------------------------------
    # Planning (mesocycles / microcycles)
    # ------------------------------------------------------------------

    def list_mesocycles_uc(self) -> ListMesocyclesUseCase:
        return ListMesocyclesUseCase(MesocycleRepository())

    def create_mesocycle_uc(self) -> CreateMesocycleUseCase:
        return CreateMesocycleUseCase(MesocycleRepository())

    def get_mesocycle_uc(self) -> GetMesocycleUseCase:
        return GetMesocycleUseCase(MesocycleRepository())

    def update_mesocycle_uc(self) -> UpdateMesocycleUseCase:
        return UpdateMesocycleUseCase(MesocycleRepository())

    def list_microcycles_uc(self) -> ListMicrocyclesUseCase:
        return ListMicrocyclesUseCase(MicrocycleRepository())

    def create_microcycle_uc(self) -> CreateMicrocycleUseCase:
        return CreateMicrocycleUseCase(MicrocycleRepository())

    def get_microcycle_uc(self) -> GetMicrocycleUseCase:
        return GetMicrocycleUseCase(MicrocycleRepository())

    def update_microcycle_uc(self) -> UpdateMicrocycleUseCase:
        return UpdateMicrocycleUseCase(MicrocycleRepository())

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_load_chart_uc(self) -> GetLoadChartUseCase:
        return GetLoadChartUseCase(TrainingSessionRepository(), ExecutionRecordRepository())
