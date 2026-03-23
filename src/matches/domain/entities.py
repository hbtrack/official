from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


_VALID_STATUSES = {
    "SCHEDULED", "PRE_MATCH", "FIRST_HALF", "HALF_TIME",
    "SECOND_HALF", "OVERTIME_1", "OVERTIME_2", "PENALTIES",
    "COMPLETED", "CANCELLED",
}
_LINEUP_EDIT_STATUSES = {"SCHEDULED", "PRE_MATCH"}
_MAX_LINEUP_PER_TEAM = 16  # HBR-008


@dataclass
class Match:
    """
    Entidade principal — partida de handebol oficial.
    INV-MATCH-001: id, competition_id, home_team_id, away_team_id, scheduled_at obrigatórios.
    INV-MATCH-002: home_team_id != away_team_id.
    INV-MATCH-003: home_score/away_score >= 0 quando presentes.
    INV-MATCH-004: started_at <= ended_at quando ambos presentes.
    INV-MATCH-005: lineup_user_ids, official_incident_ids, referee_names sem duplicatas.
    DEC-MATCHES-001: CRUD simples — placar/súmula alimentados pelo operador pós-jogo.
    DEC-MATCHES-002: status_label = 10 fases HBR-013.
    """

    id: uuid.UUID
    competition_id: uuid.UUID
    home_team_id: uuid.UUID
    away_team_id: uuid.UUID
    scheduled_at: datetime
    status_label: str = "SCHEDULED"
    venue_label: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    referee_names: List[str] = field(default_factory=list)
    lineup_user_ids: List[uuid.UUID] = field(default_factory=list)
    official_incident_ids: List[uuid.UUID] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def validate_invariants(self) -> None:
        # INV-MATCH-001: campos obrigatórios
        if not self.competition_id:
            raise ValueError("INV-MATCH-001: competition_id é obrigatório.")
        if not self.home_team_id:
            raise ValueError("INV-MATCH-001: home_team_id é obrigatório.")
        if not self.away_team_id:
            raise ValueError("INV-MATCH-001: away_team_id é obrigatório.")
        if not self.scheduled_at:
            raise ValueError("INV-MATCH-001: scheduled_at é obrigatório.")

        # INV-MATCH-002: times distintos
        if self.home_team_id == self.away_team_id:
            raise ValueError("INV-MATCH-002: homeTeamId deve ser diferente de awayTeamId.")

        # INV-MATCH-003: scores >= 0
        if self.home_score is not None and self.home_score < 0:
            raise ValueError("INV-MATCH-003: homeScore deve ser >= 0.")
        if self.away_score is not None and self.away_score < 0:
            raise ValueError("INV-MATCH-003: awayScore deve ser >= 0.")

        # INV-MATCH-004: startedAt <= endedAt
        if self.started_at and self.ended_at and self.started_at > self.ended_at:
            raise ValueError("INV-MATCH-004: startedAt deve ser <= endedAt.")

        # INV-MATCH-005: sem duplicatas
        if len(self.lineup_user_ids) != len(set(self.lineup_user_ids)):
            raise ValueError("INV-MATCH-005: lineupUserIds não pode ter duplicatas.")
        if len(self.official_incident_ids) != len(set(self.official_incident_ids)):
            raise ValueError("INV-MATCH-005: officialIncidentIds não pode ter duplicatas.")
        if len(self.referee_names) != len(set(self.referee_names)):
            raise ValueError("INV-MATCH-005: refereeNames não pode ter duplicatas.")

        # status válido
        if self.status_label not in _VALID_STATUSES:
            raise ValueError(f"status_label inválido: {self.status_label}")

        # venue_label máx 200
        if self.venue_label and len(self.venue_label) > 200:
            raise ValueError("venue_label excede 200 caracteres.")
