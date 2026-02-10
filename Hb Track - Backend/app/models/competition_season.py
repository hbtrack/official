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


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.competition_seasons

    __table_args__ = (

        UniqueConstraint('competition_id', 'season_id', name='uk_competition_seasons_competition_season'),

        Index('ix_competition_seasons_competition_id', 'competition_id', unique=False),

        Index('ix_competition_seasons_season_id', 'season_id', unique=False),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    competition_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('competitions.id', name='fk_competition_seasons_competition_id', ondelete='CASCADE'), nullable=False)

    season_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('seasons.id', name='fk_competition_seasons_season_id', ondelete='CASCADE'), nullable=False)

    name: Mapped[Optional[str]] = mapped_column(sa.String(length=100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    # HB-AUTOGEN:END
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


    # Optional name/description

    # Timestamps


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
