"""
Model: CompetitionPhase

Estrutura da tabela competition_phases:
- id (uuid, PK)
- competition_id (uuid, FK competitions, NOT NULL)
- name (varchar 100, NOT NULL)
- phase_type (varchar 50, NOT NULL) - group, knockout, round_robin, semifinal, final, etc.
- order_index (int, default 0)
- is_olympic_cross (bool, default false) - cruzamento olímpico (1ºA x 2ºB)
- config (jsonb, default {})
- status (varchar 50, default 'pending') - pending, in_progress, finished
- created_at, updated_at (timestamptz)

Regras:
- Uma competição pode ter múltiplas fases
- Fases são ordenadas por order_index
- Cada fase pode ter configuração específica em config
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

from sqlalchemy import DateTime, ForeignKey, String, Integer, Boolean, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.competition import Competition
    from app.models.competition_match import CompetitionMatch
    from app.models.competition_standing import CompetitionStanding


class CompetitionPhase(Base):
    """
    Fase de uma competição.
    
    Exemplos:
    - Fase de Grupos (phase_type='group')
    - Semifinal (phase_type='semifinal')
    - Final (phase_type='final')
    """

    __tablename__ = "competition_phases"


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.competition_phases

    __table_args__ = (

        Index('ix_competition_phases_competition_id', 'competition_id', unique=False),

        Index('ix_competition_phases_order', 'competition_id', 'order_index', unique=False),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    competition_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('competitions.id', name='fk_competition_phases_competition_id', ondelete='CASCADE'), nullable=False)

    name: Mapped[str] = mapped_column(sa.String(length=100), nullable=False)

    phase_type: Mapped[str] = mapped_column(sa.String(length=50), nullable=False)

    order_index: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default=sa.text('0'))

    is_olympic_cross: Mapped[Optional[bool]] = mapped_column(sa.Boolean(), nullable=True, server_default=sa.text('false'))

    config: Mapped[Optional[object]] = mapped_column(PG_JSONB(), nullable=True, server_default=sa.text("'{}'::jsonb"))

    status: Mapped[Optional[str]] = mapped_column(sa.String(length=50), nullable=True, server_default=sa.text("'pending'::character varying"))

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    # HB-AUTOGEN:END
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        server_default=text("gen_random_uuid()"),
    )

    # Competition FK

    # Core fields



    # Cruzamento olímpico

    # Configuração específica da fase

    # Status

    # Timestamps


    # Relationships
    competition: Mapped["Competition"] = relationship(
        "Competition",
        back_populates="phases",
        foreign_keys=[competition_id],
    )

    matches: Mapped[List["CompetitionMatch"]] = relationship(
        "CompetitionMatch",
        back_populates="phase",
        lazy="selectin",
    )

    standings: Mapped[List["CompetitionStanding"]] = relationship(
        "CompetitionStanding",
        back_populates="phase",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<CompetitionPhase {self.id} name={self.name} type={self.phase_type}>"
