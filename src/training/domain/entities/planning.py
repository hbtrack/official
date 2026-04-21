"""
Agregado: Mesocycle + Microcycle.

Periodização (blocos médio e semanal).
TRAIN-DEC-H04.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Mesocycle:
    """
    Bloco de periodização médio (4-6 semanas).
    TRAIN-DEC-H04.
    """
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    started_at: datetime
    ended_at: datetime
    created_at: datetime
    updated_at: datetime

    season_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    objective: Optional[str] = None
    notes: Optional[str] = None

    def validate_invariants(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("name é obrigatório para Mesocycle")
        if self.started_at >= self.ended_at:
            raise ValueError("startedAt deve ser anterior a endedAt")


@dataclass
class Microcycle:
    """
    Unidade semanal de periodização.
    TRAIN-DEC-H04.
    """
    id: uuid.UUID
    organization_id: uuid.UUID
    mesocycle_id: uuid.UUID
    week_number: int
    started_at: datetime
    ended_at: datetime
    created_at: datetime
    updated_at: datetime

    team_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    objective: Optional[str] = None
    planned_sessions_count: Optional[int] = None
    notes: Optional[str] = None

    def validate_invariants(self) -> None:
        if self.started_at >= self.ended_at:
            raise ValueError("startedAt deve ser anterior a endedAt")
        if self.week_number < 1:
            raise ValueError("weekNumber deve ser >= 1")
        if self.week_number > 32767:
            raise ValueError("weekNumber deve ser <= 32767 (SmallIntegerField)")


__all__ = ["Mesocycle", "Microcycle"]
