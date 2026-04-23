"""
Agregado: WellnessPre + WellnessPost.

Entradas de wellness do atleta (pré e pós treino).
INV-TRAIN-002 (janela submissão), INV-TRAIN-003 (janela edição),
INV-TRAIN-009/010 (unicidade por session/athlete).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class WellnessPre:
    """
    Wellness pré-treino por atleta.
    Contrato: contracts/openapi/components/schemas/training/wellness_pre.yaml
    INV-TRAIN-002: janela temporal de submissão (session_at - 2h).
    INV-TRAIN-009: máximo 1 ativo por (session_id, athlete_id).
    """
    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    readiness: Optional[int] = None
    sleep_quality: Optional[int] = None
    sleep_hours: Optional[float] = None
    mood: Optional[int] = None
    fatigue: Optional[int] = None
    muscle_soreness: Optional[int] = None
    notes: Optional[str] = None
    deleted_at: Optional[datetime] = None
    deleted_reason: Optional[str] = None

    def validate_invariants(self) -> None:
        for name, val in [
            ("readiness", self.readiness),
            ("sleepQuality", self.sleep_quality),
            ("mood", self.mood),
            ("fatigue", self.fatigue),
            ("muscleSoreness", self.muscle_soreness),
        ]:
            if val is not None and not (1 <= val <= 5):
                raise ValueError(f"{name} deve estar em [1..5]")
        if self.sleep_hours is not None and not (0 <= self.sleep_hours <= 24):
            raise ValueError("sleepHours deve estar em [0..24]")


@dataclass
class WellnessPost:
    """
    Wellness pós-treino por atleta.
    INV-TRAIN-003: janela de edição de 24h após criação.
    INV-TRAIN-010: máximo 1 ativo por (session_id, athlete_id).
    """
    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None
    deleted_at: Optional[datetime] = None
    deleted_reason: Optional[str] = None

    def validate_invariants(self) -> None:
        if self.perceived_exertion is not None and not (1 <= self.perceived_exertion <= 10):
            raise ValueError("perceivedExertion deve estar em [1..10]")
        for name, val in [
            ("enjoyment", self.enjoyment),
            ("technicalLearning", self.technical_learning),
        ]:
            if val is not None and not (1 <= val <= 5):
                raise ValueError(f"{name} deve estar em [1..5]")


__all__ = ["WellnessPre", "WellnessPost"]
