"""
Model: TrainingSessionAdjustment — AR_274 Ledger de Sessão

Append-only. Imutabilidade fisica garantida via trigger (migration 0071).
Ajustes sempre criam nova linha; nunca sobrescrevem o plan_data original.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TrainingSessionAdjustment(Base):
    """
    Ledger de ajustes aplicados a um plano de sessao.

    - Append-only: cada ajuste e uma nova linha (sequence_number incremental).
    - plan_id: FK para o plano original (imutavel).
    - session_id: referencia direta a sessao (para queries sem JOIN em plan).
    - Trigger trg_training_session_adjustments_immutable proibe UPDATE/DELETE.
    """

    __tablename__ = "training_session_adjustments"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    plan_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("training_session_plans.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("training_sessions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    adjustment_data: Mapped[dict] = mapped_column(
        PG_JSONB,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )
