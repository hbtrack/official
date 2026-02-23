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

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END

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


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.competitions

    __table_args__ = (

        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_competitions_deleted_reason'),

        CheckConstraint("status IN ('draft', 'active', 'finished', 'cancelled')", name='ck_competitions_status'),

        CheckConstraint("modality IN ('masculino', 'feminino', 'misto')", name='ck_competitions_modality'),

        Index('ix_competitions_created_by', 'created_by', unique=False),

        Index('ix_competitions_organization_id', 'organization_id', unique=False),

        Index('ix_competitions_season', 'season', unique=False),

        Index('ix_competitions_status', 'status', unique=False),

        Index('ix_competitions_team_id', 'team_id', unique=False),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    organization_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('organizations.id', name='fk_competitions_organization_id', ondelete='RESTRICT'), nullable=False)

    name: Mapped[str] = mapped_column(sa.String(length=200), nullable=False)

    kind: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True)

    team_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_competitions_team_id', ondelete='SET NULL'), nullable=True)

    season: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True)

    modality: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True, server_default=sa.text("'masculino'::character varying"))

    competition_type: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True)

    format_details: Mapped[Optional[object]] = mapped_column(PG_JSONB(), nullable=True, server_default=sa.text("'{}'::jsonb"))

    tiebreaker_criteria: Mapped[Optional[object]] = mapped_column(PG_JSONB(), nullable=True, server_default=sa.text('\'["pontos", "saldo_gols", "gols_pro", "confronto_direto"]\'::jsonb'))

    points_per_win: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True, server_default=sa.text('2'))

    points_per_draw: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default=sa.text('1'))

    points_per_loss: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default=sa.text('0'))

    status: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True, server_default=sa.text("'draft'::character varying"))

    current_phase_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('competition_phases.id', name='fk_competitions_current_phase_id', ondelete='SET NULL'), nullable=True)

    regulation_file_url: Mapped[Optional[str]] = mapped_column(sa.String(length=500), nullable=True)

    regulation_notes: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    created_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_competitions_created_by', ondelete='SET NULL'), nullable=True)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    # HB-AUTOGEN:END
    # Primary key

    # Organization scope

    # Core fields


    # V2: Nossa equipe participante

    # V2: Temporada e modalidade


    # V2: Formato da competição


    # V2: Critérios de desempate

    # V2: Pontuação (padrão handebol: 2 pontos por vitória)

    # V2: Status


    # V2: Regulamento


    # V2: Auditoria

    # Timestamps


    # V2: Soft delete


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
