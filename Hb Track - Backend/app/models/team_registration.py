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

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END


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


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.team_registrations

    __table_args__ = (

        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_team_registrations_deleted_reason'),

        Index('idx_team_registrations_athlete_active', 'athlete_id', 'deleted_at', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),

        Index('idx_team_registrations_team_active', 'team_id', 'deleted_at', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),

        Index('ix_team_registrations_athlete_active', 'athlete_id', unique=False, postgresql_where=sa.text('((end_at IS NULL) AND (deleted_at IS NULL))')),

        Index('ix_team_registrations_athlete_id', 'athlete_id', unique=False),

        Index('ix_team_registrations_period', 'start_at', 'end_at', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),

        Index('ix_team_registrations_team_active', 'team_id', unique=False, postgresql_where=sa.text('((end_at IS NULL) AND (deleted_at IS NULL))')),

        Index('ix_team_registrations_team_athlete_active', 'team_id', 'athlete_id', unique=False, postgresql_where=sa.text('((end_at IS NULL) AND (deleted_at IS NULL))')),

        Index('ix_team_registrations_team_id', 'team_id', unique=False),

        Index('ux_team_registrations_active', 'athlete_id', 'team_id', unique=True, postgresql_where=sa.text('((end_at IS NULL) AND (deleted_at IS NULL))')),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    athlete_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('athletes.id', name='fk_team_registrations_athlete_id', ondelete='RESTRICT'), nullable=False)

    team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_team_registrations_team_id', ondelete='RESTRICT'), nullable=False)

    start_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    end_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    created_by_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_team_registrations_created_by_user'), nullable=True)

    # HB-AUTOGEN:END
    # PK

    # FKs (V1.2: apenas athlete_id e team_id)

    # Períodos de vínculo (RDB10)

    # Timestamps

    # Soft delete (RDB4)

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
