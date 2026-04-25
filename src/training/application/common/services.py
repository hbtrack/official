"""
TrainingServices — facade de factory de UseCases.

REGRA INQUEBRÁVEL: este módulo só expõe métodos (factories) e utilitários de teste.
Nunca deve ter atributos de repositório armazenados na instância.
Cada factory cria o UseCase (e seus repositórios) na chamada, garantindo
que não haja estado compartilhado entre requisições.

Injeção de mock para testes unitários
--------------------------------------
Use ``configure_for_testing`` + ``reset_testing_overrides`` para substituir factories
sem precisar de ``unittest.mock.patch`` no nível de módulo::

    mock_uc = MagicMock(spec=CreateTrainingSessionUseCase)
    TrainingServices.configure_for_testing(
        create_training_session_uc=lambda: mock_uc
    )
    try:
        svc = TrainingServices()
        assert svc.create_training_session_uc() is mock_uc
    finally:
        TrainingServices.reset_testing_overrides()

Verificado pelo teste: test_phase4_policy_guard_services.py::TestTrainingServicesFacade
"""
from __future__ import annotations

from typing import Any, Callable, ClassVar, TypeVar

_T = TypeVar("_T")

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
from ...infrastructure.repository.attendance import AttendanceRepository
from ...infrastructure.repository.blocks import SessionBlockRepository
from ...infrastructure.repository.communication import (
    AttentionQueueRepository,
    FeedbackThreadRepository,
    RecommendationRepository,
)
from ...infrastructure.repository.eligibility import AthleteIneligibilityDeclarationRepository
from ...infrastructure.repository.execution import ExecutionRecordRepository
from ...infrastructure.repository.planning import MesocycleRepository, MicrocycleRepository
from ...infrastructure.repository.sessions import SessionObjectiveRepository, TrainingSessionRepository
from ...infrastructure.repository.wellness import WellnessPostRepository, WellnessPreRepository


class TrainingServices:
    """
    Service locator de UseCases de Training.

    Cada método instancia o(s) repositório(s) necessário(s) e o UseCase,
    sem armazenar estado na instância.  Isso garante:
    - thread-safety por padrão (sem estado compartilhado)
    - ausência de vazamento de sessões de banco entre requests
    - facilidade de mock em testes (via configure_for_testing)

    Implementado como singleton via __new__: ``TrainingServices()`` retorna sempre
    a mesma instância, eliminando 48 alocações de objeto por request sem alterar
    a interface pública nem o comportamento dos handlers.

    Para injeção de mocks em testes, use ``configure_for_testing`` + ``reset_testing_overrides``.
    Ver docstring do módulo para exemplo completo.
    """

    _instance: ClassVar[TrainingServices | None] = None
    _test_overrides: ClassVar[dict[str, Callable[[], Any]]] = {}

    def __new__(cls) -> TrainingServices:
        """Singleton — evita 48 alocações de objeto por request."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------------------------------------------------------------
    # Testing support — mock injection
    # ------------------------------------------------------------------

    @classmethod
    def configure_for_testing(cls, **factory_overrides: Callable[[], Any]) -> None:
        """Injeta substituições de factory para testes unitários.

        Cada override deve ser um callable sem argumentos que retorna o objeto
        desejado (UseCase, repositório ou guard). Deve ser seguido de
        ``reset_testing_overrides()`` em teardown (ou use ``try/finally``).

        Exemplo::

            mock_uc = MagicMock(spec=CreateTrainingSessionUseCase)
            TrainingServices.configure_for_testing(
                create_training_session_uc=lambda: mock_uc
            )
            try:
                svc = TrainingServices()
                result = svc.create_training_session_uc()
                assert result is mock_uc
            finally:
                TrainingServices.reset_testing_overrides()
        """
        cls._test_overrides = dict(factory_overrides)

    @classmethod
    def reset_testing_overrides(cls) -> None:
        """Remove todas as substituições configuradas por ``configure_for_testing``."""
        cls._test_overrides = {}

    def _resolve(self, key: str, factory: Callable[[], _T]) -> _T:
        """Retorna override de teste para ``key`` se configurado, senão invoca factory.

        Método privado — não faz parte da API pública.
        """
        override = type(self)._test_overrides.get(key)
        return override() if override is not None else factory()

    # ------------------------------------------------------------------
    # Session guard
    # ------------------------------------------------------------------

    def session_guard(self) -> SessionGuard:
        return self._resolve("session_guard",
            lambda: SessionGuard(TrainingSessionRepository()))

    def session_block_repo(self) -> SessionBlockRepository:
        """Factory de SessionBlockRepository. Usado quando o handler precisa acesso
        direto ao repositório sem passar por um UseCase completo (ex: get_single_block)."""
        return self._resolve("session_block_repo",
            lambda: SessionBlockRepository())

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def list_training_sessions_uc(self, cursor_codec=None) -> ListTrainingSessionsUseCase:
        return self._resolve("list_training_sessions_uc",
            lambda: ListTrainingSessionsUseCase(TrainingSessionRepository(), cursor_codec=cursor_codec))

    def create_training_session_uc(self) -> CreateTrainingSessionUseCase:
        return self._resolve("create_training_session_uc",
            lambda: CreateTrainingSessionUseCase(TrainingSessionRepository()))

    def get_training_session_uc(self) -> GetTrainingSessionUseCase:
        return self._resolve("get_training_session_uc",
            lambda: GetTrainingSessionUseCase(TrainingSessionRepository()))

    def update_training_session_uc(self) -> UpdateTrainingSessionUseCase:
        return self._resolve("update_training_session_uc",
            lambda: UpdateTrainingSessionUseCase(TrainingSessionRepository()))

    def delete_training_session_uc(self) -> DeleteTrainingSessionUseCase:
        return self._resolve("delete_training_session_uc",
            lambda: DeleteTrainingSessionUseCase(TrainingSessionRepository()))

    def transition_training_session_uc(self) -> TransitionTrainingSessionUseCase:
        return self._resolve("transition_training_session_uc",
            lambda: TransitionTrainingSessionUseCase(TrainingSessionRepository()))

    # ------------------------------------------------------------------
    # Blocks
    # ------------------------------------------------------------------

    def list_session_blocks_uc(self) -> ListSessionBlocksUseCase:
        return self._resolve("list_session_blocks_uc",
            lambda: ListSessionBlocksUseCase(TrainingSessionRepository(), SessionBlockRepository()))

    def add_session_block_uc(self) -> AddSessionBlockUseCase:
        return self._resolve("add_session_block_uc",
            lambda: AddSessionBlockUseCase(TrainingSessionRepository(), SessionBlockRepository()))

    def update_session_block_uc(self) -> UpdateSessionBlockUseCase:
        return self._resolve("update_session_block_uc",
            lambda: UpdateSessionBlockUseCase(TrainingSessionRepository(), SessionBlockRepository()))

    def delete_session_block_uc(self) -> DeleteSessionBlockUseCase:
        return self._resolve("delete_session_block_uc",
            lambda: DeleteSessionBlockUseCase(TrainingSessionRepository(), SessionBlockRepository()))

    def reorder_session_blocks_uc(self) -> ReorderSessionBlocksUseCase:
        return self._resolve("reorder_session_blocks_uc",
            lambda: ReorderSessionBlocksUseCase(TrainingSessionRepository(), SessionBlockRepository()))

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def list_execution_records_uc(self) -> ListExecutionRecordsUseCase:
        return self._resolve("list_execution_records_uc",
            lambda: ListExecutionRecordsUseCase(TrainingSessionRepository(), ExecutionRecordRepository()))

    def create_execution_record_uc(self) -> CreateExecutionRecordUseCase:
        return self._resolve("create_execution_record_uc",
            lambda: CreateExecutionRecordUseCase(TrainingSessionRepository(), ExecutionRecordRepository()))

    def get_execution_record_uc(self) -> GetExecutionRecordUseCase:
        return self._resolve("get_execution_record_uc",
            lambda: GetExecutionRecordUseCase(TrainingSessionRepository(), ExecutionRecordRepository()))

    def list_session_objectives_uc(self) -> ListSessionObjectivesUseCase:
        return self._resolve("list_session_objectives_uc",
            lambda: ListSessionObjectivesUseCase(TrainingSessionRepository(), SessionObjectiveRepository()))

    def create_session_objective_uc(self) -> CreateSessionObjectiveUseCase:
        return self._resolve("create_session_objective_uc",
            lambda: CreateSessionObjectiveUseCase(TrainingSessionRepository(), SessionObjectiveRepository()))

    # ------------------------------------------------------------------
    # Wellness
    # ------------------------------------------------------------------

    def submit_wellness_pre_uc(self) -> SubmitWellnessPreUseCase:
        return self._resolve("submit_wellness_pre_uc",
            lambda: SubmitWellnessPreUseCase(TrainingSessionRepository(), WellnessPreRepository()))

    def get_wellness_pre_uc(self) -> GetWellnessPreUseCase:
        return self._resolve("get_wellness_pre_uc",
            lambda: GetWellnessPreUseCase(TrainingSessionRepository(), WellnessPreRepository()))

    def update_wellness_pre_uc(self) -> UpdateWellnessPreUseCase:
        return self._resolve("update_wellness_pre_uc",
            lambda: UpdateWellnessPreUseCase(TrainingSessionRepository(), WellnessPreRepository()))

    def submit_wellness_post_uc(self) -> SubmitWellnessPostUseCase:
        return self._resolve("submit_wellness_post_uc",
            lambda: SubmitWellnessPostUseCase(TrainingSessionRepository(), WellnessPostRepository()))

    def get_wellness_post_uc(self) -> GetWellnessPostUseCase:
        return self._resolve("get_wellness_post_uc",
            lambda: GetWellnessPostUseCase(TrainingSessionRepository(), WellnessPostRepository()))

    def update_wellness_post_uc(self) -> UpdateWellnessPostUseCase:
        return self._resolve("update_wellness_post_uc",
            lambda: UpdateWellnessPostUseCase(TrainingSessionRepository(), WellnessPostRepository()))

    # ------------------------------------------------------------------
    # Attendance
    # ------------------------------------------------------------------

    def list_session_attendance_uc(self) -> ListSessionAttendanceUseCase:
        return self._resolve("list_session_attendance_uc",
            lambda: ListSessionAttendanceUseCase(TrainingSessionRepository(), AttendanceRepository()))

    def record_session_attendance_uc(self) -> RecordSessionAttendanceUseCase:
        return self._resolve("record_session_attendance_uc",
            lambda: RecordSessionAttendanceUseCase(TrainingSessionRepository(), AttendanceRepository()))

    # ------------------------------------------------------------------
    # Feedback / Chat
    # ------------------------------------------------------------------

    def list_feedback_threads_uc(self) -> ListFeedbackThreadsUseCase:
        return self._resolve("list_feedback_threads_uc",
            lambda: ListFeedbackThreadsUseCase(TrainingSessionRepository(), FeedbackThreadRepository()))

    def create_feedback_thread_uc(self) -> CreateFeedbackThreadUseCase:
        return self._resolve("create_feedback_thread_uc",
            lambda: CreateFeedbackThreadUseCase(TrainingSessionRepository(), FeedbackThreadRepository()))

    def close_feedback_thread_uc(self) -> CloseFeedbackThreadUseCase:
        return self._resolve("close_feedback_thread_uc",
            lambda: CloseFeedbackThreadUseCase(TrainingSessionRepository(), FeedbackThreadRepository()))

    def list_chat_messages_uc(self) -> ListChatMessagesUseCase:
        return self._resolve("list_chat_messages_uc",
            lambda: ListChatMessagesUseCase(TrainingSessionRepository(), FeedbackThreadRepository()))

    def submit_training_suggestion_uc(self) -> SubmitTrainingSuggestionUseCase:
        return self._resolve("submit_training_suggestion_uc",
            lambda: SubmitTrainingSuggestionUseCase(TrainingSessionRepository(), FeedbackThreadRepository()))

    # ------------------------------------------------------------------
    # Eligibility
    # ------------------------------------------------------------------

    def get_ineligibility_status_uc(self) -> GetIneligibilityStatusUseCase:
        return self._resolve("get_ineligibility_status_uc",
            lambda: GetIneligibilityStatusUseCase(
                TrainingSessionRepository(), AthleteIneligibilityDeclarationRepository()))

    def submit_ineligibility_declaration_uc(self) -> SubmitIneligibilityDeclarationUseCase:
        return self._resolve("submit_ineligibility_declaration_uc",
            lambda: SubmitIneligibilityDeclarationUseCase(
                TrainingSessionRepository(), AthleteIneligibilityDeclarationRepository()))

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    def list_recommendations_uc(self) -> ListRecommendationsUseCase:
        return self._resolve("list_recommendations_uc",
            lambda: ListRecommendationsUseCase(TrainingSessionRepository(), RecommendationRepository()))

    def accept_recommendation_uc(self) -> AcceptRecommendationUseCase:
        return self._resolve("accept_recommendation_uc",
            lambda: AcceptRecommendationUseCase(TrainingSessionRepository(), RecommendationRepository()))

    def dismiss_recommendation_uc(self) -> DismissRecommendationUseCase:
        return self._resolve("dismiss_recommendation_uc",
            lambda: DismissRecommendationUseCase(TrainingSessionRepository(), RecommendationRepository()))

    # ------------------------------------------------------------------
    # Attention queue
    # ------------------------------------------------------------------

    def list_attention_queue_items_uc(self) -> ListAttentionQueueItemsUseCase:
        return self._resolve("list_attention_queue_items_uc",
            lambda: ListAttentionQueueItemsUseCase(TrainingSessionRepository(), AttentionQueueRepository()))

    def resolve_attention_queue_item_uc(self) -> ResolveAttentionQueueItemUseCase:
        return self._resolve("resolve_attention_queue_item_uc",
            lambda: ResolveAttentionQueueItemUseCase(TrainingSessionRepository(), AttentionQueueRepository()))

    def dismiss_attention_queue_item_uc(self) -> DismissAttentionQueueItemUseCase:
        return self._resolve("dismiss_attention_queue_item_uc",
            lambda: DismissAttentionQueueItemUseCase(TrainingSessionRepository(), AttentionQueueRepository()))

    def escalate_attention_queue_item_uc(self) -> EscalateAttentionQueueItemUseCase:
        return self._resolve("escalate_attention_queue_item_uc",
            lambda: EscalateAttentionQueueItemUseCase(TrainingSessionRepository(), AttentionQueueRepository()))

    # ------------------------------------------------------------------
    # Planning (mesocycles / microcycles)
    # ------------------------------------------------------------------

    def list_mesocycles_uc(self) -> ListMesocyclesUseCase:
        return self._resolve("list_mesocycles_uc",
            lambda: ListMesocyclesUseCase(MesocycleRepository()))

    def create_mesocycle_uc(self) -> CreateMesocycleUseCase:
        return self._resolve("create_mesocycle_uc",
            lambda: CreateMesocycleUseCase(MesocycleRepository()))

    def get_mesocycle_uc(self) -> GetMesocycleUseCase:
        return self._resolve("get_mesocycle_uc",
            lambda: GetMesocycleUseCase(MesocycleRepository()))

    def update_mesocycle_uc(self) -> UpdateMesocycleUseCase:
        return self._resolve("update_mesocycle_uc",
            lambda: UpdateMesocycleUseCase(MesocycleRepository()))

    def list_microcycles_uc(self) -> ListMicrocyclesUseCase:
        return self._resolve("list_microcycles_uc",
            lambda: ListMicrocyclesUseCase(MicrocycleRepository()))

    def create_microcycle_uc(self) -> CreateMicrocycleUseCase:
        return self._resolve("create_microcycle_uc",
            lambda: CreateMicrocycleUseCase(MicrocycleRepository()))

    def get_microcycle_uc(self) -> GetMicrocycleUseCase:
        return self._resolve("get_microcycle_uc",
            lambda: GetMicrocycleUseCase(MicrocycleRepository()))

    def update_microcycle_uc(self) -> UpdateMicrocycleUseCase:
        return self._resolve("update_microcycle_uc",
            lambda: UpdateMicrocycleUseCase(MicrocycleRepository()))

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_load_chart_uc(self) -> GetLoadChartUseCase:
        return self._resolve("get_load_chart_uc",
            lambda: GetLoadChartUseCase(TrainingSessionRepository(), ExecutionRecordRepository()))
