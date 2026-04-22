"""
ORM models package — decomposição por agregado (Fase 5.5).

Substitui o módulo monolítico `infrastructure/models.py` por submódulos
um por agregado. Re-exporta as 13 classes ORM para preservar:

- `from training.infrastructure.models import XModel` (repository + raiz
  `training/models.py` usada pela auto-descoberta do Django).
- Registro no app_registry do Django: cada submódulo mantém `class Meta:
  app_label = "training"`, e a importação em massa neste `__init__.py`
  garante que todos os modelos sejam carregados quando `training.models`
  (raiz) importa este pacote.

Nome do pacote preservado como `models/` (não `orm/`) para manter o
caminho `<app>.models` esperado por `makemigrations`/`migrate` e pelas
migrations já existentes (0001..0006).
"""
from __future__ import annotations

from .attendance import AttendanceRecordModel
from .blocks import SessionBlockModel
from .communication import (
    AttentionQueueItemModel,
    FeedbackThreadModel,
    RecommendationModel,
)
from .eligibility import AthleteIneligibilityDeclarationModel
from .execution import ExecutionRecordModel
from .planning import MesocycleModel, MicrocycleModel
from .sessions import SessionObjectiveModel, TrainingSessionModel
from .wellness import WellnessPostModel, WellnessPreModel

__all__ = [
    "AthleteIneligibilityDeclarationModel",
    "AttendanceRecordModel",
    "AttentionQueueItemModel",
    "ExecutionRecordModel",
    "FeedbackThreadModel",
    "MesocycleModel",
    "MicrocycleModel",
    "RecommendationModel",
    "SessionBlockModel",
    "SessionObjectiveModel",
    "TrainingSessionModel",
    "WellnessPostModel",
    "WellnessPreModel",
]
