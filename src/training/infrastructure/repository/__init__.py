"""
Repository package — decomposição por agregado (Fase 5.4).

Substitui o módulo monolítico `infrastructure/repository.py` por submódulos
um por agregado. Re-exporta a surface pública (13 Repository classes) para
preservar `from training.infrastructure.repository import XRepository` sem
mudanças em application/, api/ ou testes.
"""
from __future__ import annotations

from .attendance import AttendanceRepository
from .blocks import SessionBlockRepository
from .communication import (
    AttentionQueueRepository,
    FeedbackThreadRepository,
    RecommendationRepository,
)
from .eligibility import AthleteIneligibilityDeclarationRepository
from .execution import ExecutionRecordRepository
from .planning import MesocycleRepository, MicrocycleRepository
from .sessions import SessionObjectiveRepository, TrainingSessionRepository
from .wellness import WellnessPostRepository, WellnessPreRepository

__all__ = [
    "AthleteIneligibilityDeclarationRepository",
    "AttendanceRepository",
    "AttentionQueueRepository",
    "ExecutionRecordRepository",
    "FeedbackThreadRepository",
    "MesocycleRepository",
    "MicrocycleRepository",
    "RecommendationRepository",
    "SessionBlockRepository",
    "SessionObjectiveRepository",
    "TrainingSessionRepository",
    "WellnessPostRepository",
    "WellnessPreRepository",
]
