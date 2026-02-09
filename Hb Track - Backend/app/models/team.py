"""
Model Team - Equipes esportivas.

Regras:
- RF6: Criação de equipe
- RDB4: Soft delete obrigatório

Estrutura REAL do banco (verificada via information_schema):
- id (uuid, PK)
- organization_id (uuid, FK, NOT NULL)
- name (varchar, NOT NULL)
- category_id (integer, FK, NOT NULL)
- gender (varchar, NOT NULL) - 'masculino', 'feminino', 'misto'
- is_our_team (boolean, NOT NULL)
- active_from (date, NULL)
- active_until (date, NULL)
- created_at (timestamptz, NOT NULL)
- updated_at (timestamptz, NOT NULL)
- created_by_user_id (uuid, NULL)
- deleted_at (timestamptz, NULL)
- deleted_reason (text, NULL)

NOTA: NÃO tem season_id, NÃO tem created_by_membership_id
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
from datetime import datetime, date, timezone
from typing import Optional, TYPE_CHECKING
from uuid import uuid4
from decimal import Decimal

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.team_registration import TeamRegistration
    from app.models.season import Season
    from app.models.org_membership import OrgMembership
    from app.models.competition import Competition


class Team(Base):
    """
    Model Team - Equipes por categoria.
    
    Regras aplicáveis:
    - RF6: Criação de equipe (dirigente/coordenador)
    - RF8: Encerramento de equipes (soft delete)
    - RDB4: Exclusão lógica obrigatória
    - R34: Contexto organizacional obrigatório
    """
    __tablename__ = "teams"
    

# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.teams
    __table_args__ = (
        CheckConstraint('active_from IS NULL OR active_until IS NULL OR active_from <= active_until', name='ck_teams_active_dates'),
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_teams_deleted_reason'),
        CheckConstraint("gender::text = ANY (ARRAY['masculino'::character varying, 'feminino'::character varying]::text[])", name='ck_teams_gender'),
        CheckConstraint('alert_threshold_multiplier >= 1.0 AND alert_threshold_multiplier <= 3.0', name='teams_alert_threshold_multiplier_check'),
        Index('ix_teams_category_id', 'category_id', unique=False),
        Index('ix_teams_coach_membership_id', 'coach_membership_id', unique=False),
        Index('ix_teams_created_by_membership_id', 'created_by_membership_id', unique=False),
        Index('ix_teams_name_trgm', 'name', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
        Index('ix_teams_organization_active', 'organization_id', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
        Index('ix_teams_organization_id', 'organization_id', unique=False),
        Index('ix_teams_season_id', 'season_id', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    organization_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('organizations.id', name='fk_teams_organization_id', ondelete='RESTRICT'), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(length=120), nullable=False)
    category_id: Mapped[int] = mapped_column(sa.Integer(), ForeignKey('categories.id', name='fk_teams_category_id', ondelete='RESTRICT'), nullable=False)
    gender: Mapped[str] = mapped_column(sa.String(length=16), nullable=False)
    is_our_team: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.text('true'))
    active_from: Mapped[Optional[date]] = mapped_column(sa.Date(), nullable=True)
    active_until: Mapped[Optional[date]] = mapped_column(sa.Date(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    created_by_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_teams_created_by_user_id', ondelete='SET NULL'), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    deleted_reason: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    season_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('seasons.id', name='fk_teams_season_id', ondelete='RESTRICT', use_alter=True), nullable=True)
    coach_membership_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('org_memberships.id', name='fk_teams_coach_membership_id', ondelete='SET NULL'), nullable=True)
    created_by_membership_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('org_memberships.id', name='fk_teams_created_by_membership_id', ondelete='SET NULL'), nullable=True)
    alert_threshold_multiplier: Mapped[Optional[object]] = mapped_column(sa.Numeric(3, 1), nullable=True, server_default=sa.text('2.0'))
    # HB-AUTOGEN:END
    # Campos estruturais são definidos exclusivamente no bloco HB-AUTOGEN acima.
    
    # ═══════════════════════════════════════════════════════════════════
    # Relationships
    # ═══════════════════════════════════════════════════════════════════
    
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="teams",
        lazy="selectin"
    )

    # Note: season relationship removed to avoid conflict with seasons
    # Use the @property season below instead

    seasons: Mapped[list["Season"]] = relationship(
        "Season",
        foreign_keys="Season.team_id",
        back_populates="team",
        lazy="selectin"
    )
    
    coach: Mapped[Optional["OrgMembership"]] = relationship(
        "OrgMembership",
        foreign_keys=[coach_membership_id],
        back_populates="coached_teams",
        lazy="selectin"
    )

    creator_membership: Mapped[Optional["OrgMembership"]] = relationship(
        "OrgMembership",
        foreign_keys=[created_by_membership_id],
        back_populates="created_teams",
        lazy="selectin"
    )
    
    # Inscrições de atletas nesta equipe (R38, RDB10)
    registrations: Mapped[list["TeamRegistration"]] = relationship(
        "TeamRegistration",
        back_populates="team",
        lazy="selectin"
    )

    # Competições relacionadas (V2)
    competitions: Mapped[list["Competition"]] = relationship(
        "Competition",
        foreign_keys="Competition.team_id",
        back_populates="team",
        lazy="selectin"
    )

    # Analytics cache (Step 16)
    analytics_cache: Mapped[list["TrainingAnalyticsCache"]] = relationship(
        "TrainingAnalyticsCache",
        back_populates="team",
        lazy="selectin"
    )

    # Alertas automáticos (Step 18)
    training_alerts: Mapped[list["TrainingAlert"]] = relationship(
        "TrainingAlert",
        back_populates="team",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    # Sugestões automáticas (Step 18)
    training_suggestions: Mapped[list["TrainingSuggestion"]] = relationship(
        "TrainingSuggestion",
        back_populates="team",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    # ═══════════════════════════════════════════════════════════════════
    # Métodos auxiliares
    # ═══════════════════════════════════════════════════════════════════

    @property
    def season(self) -> Optional["Season"]:
        """
        Retorna a temporada atual (primeira da lista).

        Note: This is a computed property to avoid conflicts with the seasons relationship.
        Código que usava team.season continuará funcionando.
        """
        return self.seasons[0] if self.seasons else None

    @property
    def is_deleted(self) -> bool:
        """Verifica se equipe foi soft-deleted (RDB4)."""
        return self.deleted_at is not None
    
    @property
    def is_active(self) -> bool:
        """Verifica se equipe está ativa baseado nas datas."""
        today = date.today()
        if self.is_deleted:
            return False
        if self.active_from and today < self.active_from:
            return False
        if self.active_until and today > self.active_until:
            return False
        return True
    
    def soft_delete(self, reason: str) -> None:
        """
        Executa soft delete da equipe (RDB4/RF8).
        
        Args:
            reason: Motivo obrigatório do soft delete
        """
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_reason = reason

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}', org={self.organization_id})>"
