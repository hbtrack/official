"""
Model: Competition (V2 - Módulo Competições com IA)

Estrutura da tabela competitions (atualizada):
- id (uuid, PK)
- organization_id (uuid, FK organizations, NOT NULL)
- name (varchar 200, NOT NULL)
- kind (varchar 50, NULL) - tipo legado: official, friendly, training-game
- team_id (uuid, FK teams, NULL) - nossa equipe que participa
- season (varchar 50, NULL) - temporada (ex: "2025", "2025/2026")
- modality (varchar 50, default 'masculino') - masculino, feminino, misto
- competition_type (varchar 50, NULL) - turno_unico, turno_returno, grupos, etc.
- format_details (jsonb, default {}) - detalhes específicos do formato
- tiebreaker_criteria (jsonb, default ["pontos", "saldo_gols", ...])
- points_per_win (int, default 2) - pontos por vitória (handebol = 2)
- status (varchar 50, default 'draft') - draft, active, finished, cancelled
- current_phase_id (uuid, FK competition_phases, NULL)
- regulation_file_url (varchar 500, NULL)
- regulation_notes (text, NULL)
- created_by (uuid, FK users, NULL)
- created_at, updated_at (timestamptz)
- deleted_at (timestamptz, NULL) - soft delete
- deleted_reason (text, NULL)

Regras:
- R25/R26: Permissões por papel e escopo
- R29: Exclusão lógica (soft delete)
- R34: Clube único na V1
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING, List, Any
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, Integer, Boolean, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.competition_season import CompetitionSeason
    from app.models.team import Team
    from app.models.user import User


class Competition(Base):
    """
    Competição esportiva (V2 - suporta importação via IA).
    
    Representa um torneio/campeonato com todas as informações necessárias
    para gerenciar tabela, jogos e classificação.
    
    Exemplo: "Copa Estadual Sub-17 Masculino 2025"
    """

    __tablename__ = "competitions"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        server_default=text("gen_random_uuid()"),
    )

    # Organization scope
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    # Core fields
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nome da competição",
    )

    kind: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Tipo legado: official, friendly, training-game",
    )

    # V2: Nossa equipe participante
    team_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Nossa equipe que participa desta competição",
    )

    # V2: Temporada e modalidade
    season: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Temporada (ex: 2025, 2025/2026)",
    )

    modality: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="masculino",
        comment="Modalidade: masculino, feminino, misto",
    )

    # V2: Formato da competição
    competition_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Tipo: turno_unico, turno_returno, grupos, grupos_mata_mata, mata_mata, triangular, quadrangular, custom",
    )

    format_details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default=text("'{}'::jsonb"),
        comment="Detalhes do formato (num_grupos, classificados_por_grupo, etc.)",
    )

    # V2: Critérios de desempate
    tiebreaker_criteria: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: ["pontos", "saldo_gols", "gols_pro", "confronto_direto"],
        server_default=text("'[\"pontos\", \"saldo_gols\", \"gols_pro\", \"confronto_direto\"]'::jsonb"),
        comment="Critérios de desempate em ordem de prioridade",
    )

    # V2: Pontuação (padrão handebol: 2 pontos por vitória)
    points_per_win: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=2,
        server_default=text("2"),
        comment="Pontos por vitória. Padrão handebol: 2. Algumas ligas usam 3.",
    )

    # V2: Status
    status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="draft",
        server_default=text("'draft'"),
        index=True,
        comment="Status: draft, active, finished, cancelled",
    )

    current_phase_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("competition_phases.id", ondelete="SET NULL", use_alter=True),
        nullable=True,
        comment="Fase atual da competição",
    )

    # V2: Regulamento
    regulation_file_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL do arquivo de regulamento (PDF)",
    )

    regulation_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Anotações sobre o regulamento",
    )

    # V2: Auditoria
    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Usuário que criou",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=text("now()"),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("now()"),
        nullable=False,
    )

    # V2: Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data de exclusão lógica",
    )

    deleted_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Motivo da exclusão",
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="competitions",
        lazy="selectin",
    )

    seasons: Mapped[List["CompetitionSeason"]] = relationship(
        "CompetitionSeason",
        back_populates="competition",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # V2: New relationships
    team: Mapped[Optional["Team"]] = relationship(
        "Team",
        foreign_keys=[team_id],
        back_populates="competitions",
        lazy="selectin",
    )

    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_competitions",
        lazy="selectin",
    )

    phases: Mapped[List["CompetitionPhase"]] = relationship(
        "CompetitionPhase",
        back_populates="competition",
        lazy="selectin",
        cascade="all, delete-orphan",
        foreign_keys="CompetitionPhase.competition_id",
    )

    opponent_teams: Mapped[List["CompetitionOpponentTeam"]] = relationship(
        "CompetitionOpponentTeam",
        back_populates="competition",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    matches: Mapped[List["CompetitionMatch"]] = relationship(
        "CompetitionMatch",
        back_populates="competition",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    standings: Mapped[List["CompetitionStanding"]] = relationship(
        "CompetitionStanding",
        back_populates="competition",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def is_deleted(self) -> bool:
        """Check if competition is soft deleted."""
        return self.deleted_at is not None

    def __repr__(self) -> str:
        return f"<Competition {self.id} name={self.name} status={self.status}>"


# Import at bottom to avoid circular imports
from app.models.competition_phase import CompetitionPhase
from app.models.competition_opponent_team import CompetitionOpponentTeam
from app.models.competition_match import CompetitionMatch
from app.models.competition_standing import CompetitionStanding
