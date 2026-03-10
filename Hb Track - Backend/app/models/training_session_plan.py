"""
Model: TrainingSessionPlan — AR_274 Ledger de Sessão

Append-only. Imutabilidade fisica garantida via trigger (migration 0071).
Nenhum metodo de update deve ser adicionado a este model.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TrainingSessionPlan(Base):
    """
    Ledger imutavel de planos de sessao gerados pela IA.

    - Append-only: nao permite UPDATE ou DELETE (trigger trg_training_session_plans_immutable).
    - draft_id: rastreabilidade do draft de IA de origem.
    - plan_data: conteudo do plano no momento da aplicacao.
    """

    __tablename__ = "training_session_plans"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("training_sessions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    draft_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="Referencia ao draft de IA de origem (rastreabilidade)",
    )
    plan_data: Mapped[dict] = mapped_column(
        PG_JSONB,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )
