"""
TeamRegistration model – Vínculo atleta↔equipe (V1.2).

Referência REGRAS.md V1.2:
- RDB10: team_registrations tem athlete_id, team_id, start_at, end_at
- R6: Atletas vinculam-se via team_registrations, não via organization_id
- R7: Múltiplos team_registrations ativos simultâneos permitidos
- RDB4: Soft delete obrigatório (deleted_at, deleted_reason)

Estrutura REAL do banco (verificada via information_schema):
- id (uuid, PK)
- athlete_id (uuid, FK, NOT NULL)
- team_id (uuid, FK, NOT NULL)
- start_at (timestamptz, NOT NULL)
- end_at (timestamptz, NULL)
- created_at (timestamptz, NOT NULL)
- updated_at (timestamptz, NOT NULL)
- deleted_at (timestamptz, NULL)
- deleted_reason (text, NULL)

NOTA: NÃO tem season_id, category_id, organization_id (V1.2)
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.athlete import Athlete
    from app.models.team import Team


class TeamRegistration(Base):
    """
    Vínculo de atleta com equipe (V1.2).

    Regras REGRAS.md V1.2:
    - RDB10: Apenas athlete_id, team_id, start_at, end_at
    - R7: Atleta pode ter múltiplos vínculos ativos simultâneos
    - RDB4: Soft delete obrigatório

    Campos:
    - id: UUID PK
    - athlete_id: FK → athletes
    - team_id: FK → teams
    - start_at: início do vínculo (NOT NULL)
    - end_at: fim do vínculo, NULL se ativo
    - created_at, updated_at: timestamps
    - deleted_at, deleted_reason: soft delete (RDB4)
    """

    __tablename__ = "team_registrations"

    # PK
    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # FKs (V1.2: apenas athlete_id e team_id)
    athlete_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("athletes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    team_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Períodos de vínculo (RDB10)
    start_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        comment="Data de início do vínculo (RDB10)",
    )
    end_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        comment="Data de término; NULL = ativo (RDB10)",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Soft delete (RDB4)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        comment="Soft delete timestamp (RDB4)",
    )
    deleted_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Motivo da exclusão (obrigatório se deleted_at NOT NULL)",
    )

    # Relationships
    athlete: Mapped["Athlete"] = relationship(
        "Athlete",
        back_populates="team_registrations",
        lazy="selectin",
    )
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="registrations",
        lazy="selectin",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "end_at IS NULL OR end_at >= start_at",
            name="ck_team_reg_date_order",
        ),
        Index("idx_team_reg_athlete", "athlete_id"),
        Index("idx_team_reg_team", "team_id"),
    )

    # Properties
    @property
    def is_active(self) -> bool:
        """
        Verifica se o vínculo está ativo (RDB10).
        
        Ativo se:
        - end_at é NULL
        - deleted_at é NULL
        """
        return self.end_at is None and self.deleted_at is None

    def __repr__(self) -> str:
        return (
            f"<TeamRegistration(id={self.id}, athlete_id={self.athlete_id}, "
            f"team_id={self.team_id}, active={self.is_active})>"
        )
