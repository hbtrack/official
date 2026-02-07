"""
Model: CompetitionSeason

Estrutura da tabela competition_seasons (do banco):
- id (uuid, PK)
- competition_id (uuid, FK competitions, NOT NULL)
- season_id (uuid, FK seasons, NOT NULL)
- name (text, NULL) - descrição/nome da edição
- created_at (timestamptz, NOT NULL)
- updated_at (timestamptz, NOT NULL)
- UNIQUE (competition_id, season_id)

Representa a vinculação entre uma competição e uma temporada específica.
Exemplo: "Campeonato Estadual Sub-17" + "Temporada 2025" = "Edição 2025"
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.competition import Competition
    from app.models.season import Season


class CompetitionSeason(Base):
    """
    Vínculo entre Competição e Temporada.
    
    Cada competição pode ter múltiplas edições vinculadas a diferentes temporadas.
    Constraint: UNIQUE (competition_id, season_id)
    """

    __tablename__ = "competition_seasons"

    __table_args__ = (
        UniqueConstraint(
            "competition_id",
            "season_id",
            name="uq_competition_seasons_competition_season"
        ),
    )

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        server_default=text("gen_random_uuid()"),
    )

    # Foreign keys
    competition_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("competitions.id"),
        nullable=False,
        index=True,
    )

    season_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("seasons.id"),
        nullable=False,
        index=True,
    )

    # Optional name/description
    name: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Nome/descrição da edição (ex: Fase Regional 2024)",
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

    # Relationships
    competition: Mapped["Competition"] = relationship(
        "Competition",
        back_populates="seasons",
        lazy="selectin",
    )

    season: Mapped["Season"] = relationship(
        "Season",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<CompetitionSeason {self.id} comp={self.competition_id} season={self.season_id}>"
