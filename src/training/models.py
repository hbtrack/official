"""
models.py raiz — reexporta modelos ORM para descoberta pelo Django.
O Django requer este arquivo em <app>/models.py para registrar os models.
Importa dos subm\u00f3dulos diretos (n\u00e3o do shim de compatibilidade).
"""
from training.infrastructure.models.attendance import AttendanceRecordModel  # noqa: F401
from training.infrastructure.models.blocks import SessionBlockModel  # noqa: F401
from training.infrastructure.models.communication import (  # noqa: F401
    AttentionQueueItemModel,
    FeedbackThreadModel,
    RecommendationModel,
)
from training.infrastructure.models.eligibility import AthleteIneligibilityDeclarationModel  # noqa: F401
from training.infrastructure.models.execution import ExecutionRecordModel  # noqa: F401
from training.infrastructure.models.planning import MesocycleModel, MicrocycleModel  # noqa: F401
from training.infrastructure.models.sessions import SessionObjectiveModel, TrainingSessionModel  # noqa: F401
from training.infrastructure.models.wellness import WellnessPostModel, WellnessPreModel  # noqa: F401

