"""
Domain entities — módulo seasons.
Contrato: contracts/schemas/seasons/season.schema.json
Invariantes: docs/hbtrack/modulos/seasons/INVARIANTS_SEASONS.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from uuid import UUID


class SeasonStatus(StrEnum):
    """
    Lifecycle status da Season.
    Transição canônica: DRAFT → ACTIVE → ARCHIVED
    x-domain-enum-ref: entity_lifecycle_status
    """
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


@dataclass
class Season:
    """
    Entidade central do módulo seasons.
    Contêiner temporal do ciclo esportivo (DR-SEAS-001).
    seasons é soberano de ciclo, fases e associações canônicas.

    Boundary: scorekeeping, scout, semântica médica e autenticação
    NUNCA pertencem a esta entidade (INV-SEAS-004).
    """
    id: UUID
    name: str
    start_date: date
    end_date: date
    status_label: SeasonStatus

    # Listas canônicas (DR-SEAS-003, INV-SEAS-003)
    phase_labels: list[str] = field(default_factory=list)
    team_ids: list[UUID] = field(default_factory=list)
    competition_ids: list[UUID] = field(default_factory=list)

    # Opcionais
    organization_id: UUID | None = None
    sport_cycle_label: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def validate_invariants(self) -> None:
        """
        Enforce invariantes conforme INVARIANTS_SEASONS.md.
        Chamar nos use cases, nunca diretamente no router.
        """
        # INV-SEAS-001: campos obrigatórios
        if not self.id:
            raise ValueError("INV-SEAS-001: id é obrigatório")
        if not self.name or not self.name.strip():
            raise ValueError("INV-SEAS-001: name é obrigatório")
        if not self.start_date:
            raise ValueError("INV-SEAS-001: startDate é obrigatório")
        if not self.end_date:
            raise ValueError("INV-SEAS-001: endDate é obrigatório")

        # INV-SEAS-002: startDate <= endDate
        if self.start_date > self.end_date:
            raise ValueError("INV-SEAS-002: startDate deve ser <= endDate")

        # INV-SEAS-003: listas sem duplicidade
        if len(self.phase_labels) != len(set(self.phase_labels)):
            raise ValueError("INV-SEAS-003: phaseLabels deve ter uniqueItems")
        if len(self.team_ids) != len(set(self.team_ids)):
            raise ValueError("INV-SEAS-003: teamIds deve ter uniqueItems")
        if len(self.competition_ids) != len(set(self.competition_ids)):
            raise ValueError("INV-SEAS-003: competitionIds deve ter uniqueItems")

        # Name length: contrato maxLength 120
        if len(self.name) > 120:
            raise ValueError("INV-SEAS-001: name excede 120 caracteres")
