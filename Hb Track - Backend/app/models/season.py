"""
Season model.

Regras implementadas:
- RF4: Criação de temporada
- RF5: Edição de temporada
- RF5.1: Cancelamento (canceled_at)
- RF5.2: Interrupção (interrupted_at)
- RDB3: created_at/updated_at automáticos
- RDB4: Soft delete (deleted_at/deleted_reason)

Estrutura REAL do banco (verificada via information_schema):
- id (uuid, PK)
- team_id (uuid, FK, NOT NULL) - FK para teams
- name (varchar, NOT NULL)
- year (integer, NOT NULL)
- competition_type (varchar, NULL)
- start_date (date, NOT NULL)
- end_date (date, NOT NULL)
- canceled_at (timestamptz, NULL)
- interrupted_at (timestamptz, NULL)
- created_at (timestamptz, NOT NULL)
- updated_at (timestamptz, NOT NULL)
- created_by_user_id (uuid, NULL)
- deleted_at (timestamptz, NULL)
- deleted_reason (text, NULL)

NOTA: NÃO tem organization_id, NÃO tem is_active, NÃO tem created_by_membership_id
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB
# HB-AUTOGEN-IMPORTS:END
from datetime import date, datetime, timezone
from typing import Optional, TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, Text, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property

from app.models.base import Base
from app.models.team import Team

if TYPE_CHECKING:
    from app.models.team import Team


class Season(Base):
    """
    Temporada esportiva por equipe.

    V1.2: Temporada pertence a uma equipe (team_id), não organização.
    Uma equipe pode ter múltiplas temporadas para diferentes competições.

    Status derivado (6.1.1):
    - planejada: start_date > hoje
    - ativa: start_date <= hoje <= end_date, sem canceled_at/interrupted_at
    - interrompida: interrupted_at preenchido
    - cancelada: canceled_at preenchido
    - encerrada: end_date < hoje, sem canceled_at/interrupted_at
    """

    __tablename__ = "seasons"


# HB-AUTOGEN:BEGIN

    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.

    # Table: public.seasons

    __table_args__ = (

        CheckConstraint('start_date < end_date', name='ck_seasons_dates'),

        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_seasons_deleted_reason'),

        Index('ix_seasons_team_id', 'team_id', unique=False),

        Index('ix_seasons_year', 'year', unique=False),

    )


    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID


    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))

    team_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('teams.id', name='fk_seasons_team_id', ondelete='RESTRICT', use_alter=True), nullable=False)

    name: Mapped[str] = mapped_column(sa.String(length=120), nullable=False)

    year: Mapped[int] = mapped_column(sa.Integer(), nullable=False)

    competition_type: Mapped[Optional[str]] = mapped_column(sa.String(length=32), nullable=True)

    start_date: Mapped[date] = mapped_column(sa.Date(), nullable=False)

    end_date: Mapped[date] = mapped_column(sa.Date(), nullable=False)

    canceled_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    interrupted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))

    created_by_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_seasons_created_by_user_id', ondelete='SET NULL'), nullable=True)

    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)

    # HB-AUTOGEN:END
    # Campos estruturais são definidos exclusivamente no bloco HB-AUTOGEN acima.

    # Column property to expose organization_id via team (no column on seasons table)
    # Derivado via FK team_id; evita autoconcorrência explicitando correlate_except
    organization_id: Mapped[Optional[PyUUID]] = column_property(
        select(Team.organization_id)
        .where(Team.id == team_id)
        .correlate_except(Team)
        .scalar_subquery()
    )

    # Relationships
    team: Mapped["Team"] = relationship(
        "Team",
        foreign_keys=[team_id],
        back_populates="seasons",
        lazy="selectin",
    )

    @property
    def status(self) -> str:
        """
        Status derivado conforme 6.1.1.

        Prioridade:
        1. cancelada (canceled_at preenchido)
        2. interrompida (interrupted_at preenchido)
        3. encerrada (end_date < hoje)
        4. ativa (start_date <= hoje <= end_date)
        5. planejada (start_date > hoje)
        """
        today = date.today()

        if self.canceled_at is not None:
            return "cancelada"
        if self.interrupted_at is not None:
            return "interrompida"
        if self.end_date < today:
            return "encerrada"
        if self.start_date <= today <= self.end_date:
            return "ativa"
        return "planejada"

    @property
    def is_deleted(self) -> bool:
        """Verifica se temporada foi soft-deleted (RDB4)."""
        return self.deleted_at is not None

    @property
    def is_active(self) -> bool:
        """True se status derivado estÇ¡ 'ativa'."""
        return self.status == "ativa"

    # Aliases legados para compatibilidade (código antigo usa starts_at/ends_at)
    @property
    def starts_at(self) -> date:
        return self.start_date

    @starts_at.setter
    def starts_at(self, value: date) -> None:
        self.start_date = value

    @property
    def ends_at(self) -> date:
        return self.end_date

    @ends_at.setter
    def ends_at(self, value: date) -> None:
        self.end_date = value

    def __repr__(self) -> str:
        return f"<Season(id={self.id}, year={self.year}, name={self.name!r}, status={self.status})>"
