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

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        server_default=text("gen_random_uuid()"),
    )

    # Competition FK
    competition_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Core fields
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nome da fase (ex: 'Fase de Grupos', 'Semifinal')",
    )

    phase_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Tipo: group, knockout, round_robin, semifinal, final, third_place, quarterfinal, round_of_16, custom",
    )

    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        comment="Ordem da fase na competição",
    )

    # Cruzamento olímpico
    is_olympic_cross: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
        server_default=text("false"),
        comment="Se é cruzamento olímpico (1ºA x 2ºB)",
    )

    # Configuração específica da fase
    config: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default=text("'{}'::jsonb"),
        comment="Configuração específica da fase",
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        default="pending",
        server_default=text("'pending'"),
        comment="Status: pending, in_progress, finished",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=text("now()"),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("now()"),
        nullable=True,
    )

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
