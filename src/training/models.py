"""
models.py raiz — reexporta modelos ORM para descoberta pelo Django.
O Django requer este arquivo em <app>/models.py para registrar os models.
"""
from training.infrastructure.models import (  # noqa: F401
    AttentionQueueItemModel,
    ExecutionRecordModel,
    FeedbackThreadModel,
    MesocycleModel,
    MicrocycleModel,
    SessionBlockModel,
    SessionObjectiveModel,
    TrainingSessionModel,
    WellnessPostModel,
    WellnessPreModel,
)
