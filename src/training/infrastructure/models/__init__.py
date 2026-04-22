"""
ORM models package — decomposição por agregado (Fase 5.5).  [DEPRECATED — remover em release N+2]

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
migrations já existentes (0001..0007).

CAMINHOS NOVOS (use estes):
  training.infrastructure.models.sessions     → TrainingSessionModel, SessionObjectiveModel
  training.infrastructure.models.blocks       → SessionBlockModel
  training.infrastructure.models.wellness     → WellnessPreModel, WellnessPostModel
  training.infrastructure.models.attendance   → AttendanceRecordModel
  training.infrastructure.models.execution    → ExecutionRecordModel
  training.infrastructure.models.planning     → MesocycleModel, MicrocycleModel
  training.infrastructure.models.communication → AttentionQueueItemModel, FeedbackThreadModel, RecommendationModel
  training.infrastructure.models.eligibility  → AthleteIneligibilityDeclarationModel
"""
from __future__ import annotations

# Mapeamento: nome exportável → submódulo canônico
_DEPRECATED_EXPORTS: dict[str, str] = {
    "AttendanceRecordModel": "training.infrastructure.models.attendance",
    "SessionBlockModel": "training.infrastructure.models.blocks",
    "AttentionQueueItemModel": "training.infrastructure.models.communication",
    "FeedbackThreadModel": "training.infrastructure.models.communication",
    "RecommendationModel": "training.infrastructure.models.communication",
    "AthleteIneligibilityDeclarationModel": "training.infrastructure.models.eligibility",
    "ExecutionRecordModel": "training.infrastructure.models.execution",
    "MesocycleModel": "training.infrastructure.models.planning",
    "MicrocycleModel": "training.infrastructure.models.planning",
    "SessionObjectiveModel": "training.infrastructure.models.sessions",
    "TrainingSessionModel": "training.infrastructure.models.sessions",
    "WellnessPostModel": "training.infrastructure.models.wellness",
    "WellnessPreModel": "training.infrastructure.models.wellness",
}

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


def __getattr__(name: str):
    if name in _DEPRECATED_EXPORTS:
        import importlib
        import warnings
        warnings.warn(
            f"Importar '{name}' de 'training.infrastructure.models' é depreciádo. "
            f"Use '{_DEPRECATED_EXPORTS[name]}' diretamente. "
            "Este shim será removido em release N+2.",
            DeprecationWarning,
            stacklevel=2,
        )
        mod = importlib.import_module(_DEPRECATED_EXPORTS[name])
        value = getattr(mod, name)
        globals()[name] = value  # cache para evitar repeated warnings
        return value
    raise AttributeError(f"module 'training.infrastructure.models' has no attribute {name!r}")

