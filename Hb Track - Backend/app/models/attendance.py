"""
Model: Attendance

Tabela attendance (schema real):
- id: UUID PK
- training_session_id: UUID NOT NULL FK(training_sessions)
- team_registration_id: UUID NOT NULL FK(team_registrations)
- athlete_id: UUID NOT NULL FK(athletes)
- presence_status: VARCHAR(32) NOT NULL CHECK ('present'|'absent')
- minutes_effective: smallint
- comment: text
- source: VARCHAR(32) NOT NULL DEFAULT 'manual' CHECK ('manual'|'import'|'correction')
- participation_type: VARCHAR(32) CHECK ('full'|'partial'|'adapted'|'did_not_train')
- reason_absence: VARCHAR(32) CHECK ('medico'|'escola'|'familiar'|'opcional'|'outro')
- is_medical_restriction: boolean DEFAULT false
- created_at, created_by_user_id, updated_at, deleted_at, deleted_reason

Regras:
- R22: Dados de treino são métricas operacionais
- R40: Limite temporal de edição (10min autor; até 24h superior; >24h readonly)
- RF10: Podem registrar presença: Dirigentes, Coordenadores e Treinadores
- 2.X.2: Ao criar treino, sistema gera lista de atletas como "presença a marcar"
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
# HB-AUTOGEN-IMPORTS:END

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Text, text, Boolean, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.training_session import TrainingSession
    from app.models.team_registration import TeamRegistration
    from app.models.athlete import Athlete
    from app.models.user import User


class Attendance(Base):
    """
    Registro de presença em sessão de treino.
    
    Regras:
    - RF10: Dirigentes, Coordenadores, Treinadores podem registrar
    - R40: Janela de edição limitada
    - 2.X.2: Atleta vinculada à equipe aparece na lista de presença
    """
    __tablename__ = "attendance"
    

# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.attendance
    __table_args__ = (
        CheckConstraint("source::text <> 'correction'::text OR source::text = 'correction'::text AND correction_by_user_id IS NOT NULL AND correction_at IS NOT NULL", name='ck_attendance_correction_fields'),
        CheckConstraint('deleted_at IS NULL AND deleted_reason IS NULL OR deleted_at IS NOT NULL AND deleted_reason IS NOT NULL', name='ck_attendance_deleted_reason'),
        CheckConstraint("participation_type IS NULL OR (participation_type::text = ANY (ARRAY['full'::character varying, 'partial'::character varying, 'adapted'::character varying, 'did_not_train'::character varying]::text[]))", name='ck_attendance_participation_type'),
        CheckConstraint("reason_absence IS NULL OR (reason_absence::text = ANY (ARRAY['medico'::character varying, 'escola'::character varying, 'familiar'::character varying, 'opcional'::character varying, 'outro'::character varying]::text[]))", name='ck_attendance_reason'),
        CheckConstraint("source::text = ANY (ARRAY['manual'::character varying, 'import'::character varying, 'correction'::character varying]::text[])", name='ck_attendance_source'),
        CheckConstraint("presence_status::text = ANY (ARRAY['present'::character varying, 'absent'::character varying]::text[])", name='ck_attendance_status'),
        Index('idx_attendance_corrections', 'correction_by_user_id', 'correction_at', unique=False, postgresql_where=sa.text("((source)::text = 'correction'::text)")),
        Index('idx_attendance_session', 'training_session_id', unique=False),
        Index('ix_attendance_athlete_id', 'athlete_id', unique=False),
        Index('ix_attendance_athlete_session_active', 'athlete_id', 'training_session_id', unique=False, postgresql_where=sa.text('(deleted_at IS NULL)')),
        Index('ix_attendance_training_session_id', 'training_session_id', unique=False),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    training_session_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('training_sessions.id', name='fk_attendance_training_session_id', ondelete='RESTRICT'), nullable=False)
    team_registration_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('team_registrations.id', name='fk_attendance_team_registration_id', ondelete='RESTRICT'), nullable=False)
    athlete_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('athletes.id', name='fk_attendance_athlete_id', ondelete='RESTRICT'), nullable=False)
    presence_status: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    minutes_effective: Mapped[int] = mapped_column(sa.SmallInteger())
    comment: Mapped[str] = mapped_column(sa.String())
    source: Mapped[str] = mapped_column(sa.String(32), nullable=False, server_default=sa.text("'manual'::character varying"))
    participation_type: Mapped[str] = mapped_column(sa.String(32))
    reason_absence: Mapped[str] = mapped_column(sa.String(32))
    is_medical_restriction: Mapped[bool] = mapped_column(sa.Boolean(), server_default=sa.text('false'))
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    created_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='fk_attendance_created_by_user_id', ondelete='RESTRICT'), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    deleted_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    deleted_reason: Mapped[str] = mapped_column(sa.String())
    correction_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='attendance_correction_by_user_id_fkey', ondelete='SET NULL'))
    correction_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    # HB-AUTOGEN:END
    # PK
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )
    
    # FK para sessão de treino
    training_session_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("training_sessions.id", name="fk_attendance_training_session_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # FK para team_registration (vínculo ativo no momento)
    team_registration_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("team_registrations.id", name="fk_attendance_team_registration_id", ondelete="RESTRICT"),
        nullable=False
    )
    
    # FK para atleta
    athlete_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("athletes.id", name="fk_attendance_athlete_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Status de presença: 'present' ou 'absent'
    presence_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False
    )
    
    # Minutos efetivos de participação
    minutes_effective: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True
    )
    
    # Comentário/observação
    comment: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Fonte do registro: 'manual', 'import', 'correction'
    source: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default='manual'
    )
    
    # Tipo de participação: 'full', 'partial', 'adapted', 'did_not_train'
    participation_type: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True
    )
    
    # Motivo de ausência: 'medico', 'escola', 'familiar', 'opcional', 'outro'
    reason_absence: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True
    )
    
    # Flag de restrição médica
    is_medical_restriction: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        default=False
    )
    
    # Auditoria
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    
    created_by_user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="fk_attendance_created_by_user_id", ondelete="RESTRICT"),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    
    # Campos de auditoria para correções (Step 5 - Plano Refatoração)
    # Quando source='correction', estes campos são preenchidos
    correction_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="attendance_correction_by_user_id_fkey", ondelete="SET NULL"),
        nullable=True,
        comment="ID do usuário que realizou a correção (quando source=correction)"
    )

    correction_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp da correção (quando source=correction)"
    )

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    deleted_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Relationships
    training_session: Mapped[Optional["TrainingSession"]] = relationship(
        "TrainingSession",
        foreign_keys=[training_session_id],
        lazy="selectin"
    )

    team_registration: Mapped[Optional["TeamRegistration"]] = relationship(
        "TeamRegistration",
        foreign_keys=[team_registration_id],
        lazy="selectin"
    )

    athlete: Mapped[Optional["Athlete"]] = relationship(
        "Athlete",
        foreign_keys=[athlete_id],
        lazy="selectin"
    )

    created_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="attendances_created",
        lazy="selectin"
    )

    correction_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[correction_by_user_id],
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Attendance {self.id} session={self.training_session_id} athlete={self.athlete_id}>"
