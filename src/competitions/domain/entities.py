"""
Entidades de domínio — módulo competitions.
Fonte: INVARIANTS_COMPETITIONS.md, DOMAIN_RULES_COMPETITIONS.md,
       contracts/openapi/paths/competitions.yaml
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import List, Optional


class CompetitionStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class Competition:
    """
    Entidade principal — Competition.
    INV-COMP-001: id, season_id, name, start_date obrigatórios.
    INV-COMP-002: start_date <= end_date quando end_date presente.
    INV-COMP-003: stage_labels e registration_team_ids sem duplicidade.
    DR-COMP-002: competição sem contexto temporal (season_id) é inválida.
    DR-COMP-003: registration_team_ids = inscrição formal, não inferida.
    DR-COMP-004: stage_labels = fases explícitas, não inferidas.
    DR-COMP-005: standings_summary é projeção resumida, não fonte primária.
    """

    id: uuid.UUID
    season_id: uuid.UUID
    name: str
    start_date: date

    organization_id: Optional[uuid.UUID] = None
    end_date: Optional[date] = None
    format_label: Optional[str] = None
    status_label: CompetitionStatus = CompetitionStatus.DRAFT
    stage_labels: List[str] = field(default_factory=list)
    registration_team_ids: List[uuid.UUID] = field(default_factory=list)
    standings_summary: Optional[str] = None

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def validate_invariants(self) -> None:
        # INV-COMP-001: campos obrigatórios (garantido por tipagem, mas defensivo)
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("INV-COMP-001: name é obrigatório e não pode ser vazio.")
        if len(self.name) > 140:
            raise ValueError("INV-COMP-001: name excede 140 caracteres.")

        # INV-COMP-002: startDate <= endDate
        if self.end_date is not None and self.start_date > self.end_date:
            raise ValueError(
                f"INV-COMP-002: start_date ({self.start_date}) deve ser "
                f"<= end_date ({self.end_date})."
            )

        # INV-COMP-003: unicidade de stage_labels
        if len(self.stage_labels) != len(set(self.stage_labels)):
            raise ValueError("INV-COMP-003: stage_labels contém duplicidades.")

        # INV-COMP-003: unicidade de registration_team_ids
        if len(self.registration_team_ids) != len(set(self.registration_team_ids)):
            raise ValueError("INV-COMP-003: registration_team_ids contém duplicidades.")

        # Validação de format_label
        if self.format_label is not None and len(self.format_label) > 80:
            raise ValueError("format_label excede 80 caracteres.")

        # standings_summary máx 500 chars (DR-COMP-005, contrato)
        if self.standings_summary is not None and len(self.standings_summary) > 500:
            raise ValueError("standings_summary excede 500 caracteres.")

        # stage_labels: cada item minLength=1, maxLength=80
        for label in self.stage_labels:
            if not label or len(label.strip()) == 0:
                raise ValueError("INV-COMP-003: stage_label não pode ser vazio.")
            if len(label) > 80:
                raise ValueError(f"INV-COMP-003: stage_label '{label}' excede 80 chars.")
