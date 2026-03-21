"""
Domain entities — módulo teams.
Contrato: contracts/schemas/teams/team.schema.json
Invariantes: docs/hbtrack/modulos/teams/INVARIANTS_TEAMS.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class TeamStatus(StrEnum):
    """
    Lifecycle status da Team.
    Transição canônica: DRAFT → ACTIVE → ARCHIVED (sem retorno de ARCHIVED).
    """
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


@dataclass
class Team:
    """
    Entidade central do módulo teams.
    teams é soberano do elenco, comissão esportiva, categoria competitiva
    e associação à temporada (DR-TEAM-001).

    Boundary: credenciais, sessão, prontuário clínico e ownership de perfil
    pessoal NUNCA pertencem a esta entidade (INV-TEAM-004).
    """
    id: UUID
    organization_id: UUID
    name: str
    category_label: str
    status_label: TeamStatus

    # Listas canônicas de vínculos explícitos (DR-TEAM-002, INV-TEAM-002)
    athlete_ids: list[UUID] = field(default_factory=list)
    staff_user_ids: list[UUID] = field(default_factory=list)

    # Contexto sazonal (DR-TEAM-004, INV-TEAM-003) — referência, não soberania
    season_id: UUID | None = None

    # Opcionais
    short_name: str | None = None
    roster_notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def validate_invariants(self) -> None:
        """
        Enforce invariantes conforme INVARIANTS_TEAMS.md.
        Chamar nos use cases, nunca diretamente no router.
        """
        # INV-TEAM-001: campos obrigatórios
        if not self.id:
            raise ValueError("INV-TEAM-001: id é obrigatório")
        if not self.organization_id:
            raise ValueError("INV-TEAM-001: organizationId é obrigatório")
        if not self.name or not self.name.strip():
            raise ValueError("INV-TEAM-001: name é obrigatório")
        if not self.category_label or not self.category_label.strip():
            raise ValueError("INV-TEAM-001: categoryLabel é obrigatório")

        # INV-TEAM-002: listas sem duplicidade
        if len(self.athlete_ids) != len(set(self.athlete_ids)):
            raise ValueError("INV-TEAM-002: athleteIds deve ter uniqueItems")
        if len(self.staff_user_ids) != len(set(self.staff_user_ids)):
            raise ValueError("INV-TEAM-002: staffUserIds deve ter uniqueItems")

        # Comprimentos do contrato
        if len(self.name) > 120:
            raise ValueError("INV-TEAM-001: name excede 120 caracteres")
        if len(self.category_label) > 80:
            raise ValueError("INV-TEAM-001: categoryLabel excede 80 caracteres")
