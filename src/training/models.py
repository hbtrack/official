"""
models.py raiz — reexporta modelos ORM para descoberta pelo Django.
O Django requer este arquivo em <app>/models.py para registrar os models.
"""
from training.infrastructure.models import (  # noqa: F401
    AttentionQueueItemModel,
    AthleteIneligibilityDeclarationModel,
    AttendanceRecordModel,
    ExecutionRecordModel,
    FeedbackThreadModel,
    MesocycleModel,
    MicrocycleModel,
    RecommendationModel,
    SessionBlockModel,
    SessionObjectiveModel,
    TrainingSessionModel,
    WellnessPostModel,
    WellnessPreModel,
)
