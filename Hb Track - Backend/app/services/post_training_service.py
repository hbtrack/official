"""
Service de Pós-Treino Conversacional.

Implementa feedback imediato pós-encerramento de sessão:
- INV-TRAIN-070: feedback registrado logo após close; bloqueado após 24h.
- INV-TRAIN-077: feedback do atleta é privado — treinador recebe apenas
  resumo agregado (rating médio, contagem), NUNCA o texto verbatim.

Decisão arquitetural (AR_191): usa wellness_post como backing store.
  - feedback_text → wellness_post.notes
  - rating        → wellness_post.session_rpe (0–10)
  - Requer sessão com status='readonly' (encerrada) para aceitar feedback.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wellness_post import WellnessPost
from app.models.training_session import TrainingSession
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError

logger = logging.getLogger(__name__)

# INV-TRAIN-070: janela de edição do feedback (24h após close)
FEEDBACK_EDIT_WINDOW_HOURS = 24


class PostTrainingService:
    """
    Service de feedback pós-treino conversacional.

    Refs: INV-TRAIN-070, INV-TRAIN-077
    Backing store: wellness_post table (notes=feedback_text, session_rpe=rating)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _get_session(self, session_id: UUID) -> TrainingSession:
        """Busca sessão por ID, lança NotFoundError se não encontrada."""
        result = await self.db.execute(
            select(TrainingSession).where(
                and_(
                    TrainingSession.id == session_id,
                    TrainingSession.deleted_at.is_(None),
                )
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundError(f"Training session {session_id} not found")
        return session

    # ------------------------------------------------------------------
    # INV-TRAIN-070: criar feedback imediato pós-treino
    # ------------------------------------------------------------------

    async def create_post_training_feedback(
        self,
        session_id: UUID,
        athlete_id: UUID,
        feedback_text: str,
        rating: int,
        organization_id: UUID,
        created_by_user_id: UUID,
    ) -> WellnessPost:
        """
        Registra feedback pós-treino do atleta.

        INV-TRAIN-070: sessão DEVE estar closed (status='readonly') para
        aceitar feedback. Feedback não pode ser editado após 24h.

        INV-TRAIN-077: feedback_text (notes) é privado do atleta —
        treinador não acessa via get_session_summary.

        Args:
            session_id: UUID da sessão encerrada.
            athlete_id: UUID do atleta que registra feedback.
            feedback_text: Texto livre do feedback (privado — INV-077).
            rating: Percepção subjetiva de esforço 0–10 (session_rpe).
            organization_id: UUID da organização.
            created_by_user_id: UUID do user criador.

        Returns:
            WellnessPost criado/atualizado.

        Raises:
            ValidationError: Se sessão não está encerrada (INV-070).
            ValidationError: Se rating fora do range 0–10.
        """
        session = await self._get_session(session_id)

        # INV-TRAIN-070: aceitar feedback somente em sessão encerrada
        if session.status not in ('readonly', 'closed'):
            raise ValidationError(
                "Feedback pós-treino só pode ser registrado após o encerramento "
                f"da sessão (status atual: '{session.status}') — INV-TRAIN-070."
            )

        # Validar rating
        if not (0 <= rating <= 10):
            raise ValidationError("rating deve ser entre 0 e 10 (session_rpe)")

        # Verificar se já existe wellness_post para esse atleta+sessão
        existing_result = await self.db.execute(
            select(WellnessPost).where(
                and_(
                    WellnessPost.training_session_id == session_id,
                    WellnessPost.athlete_id == athlete_id,
                    WellnessPost.deleted_at.is_(None),
                )
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            # INV-TRAIN-070: bloquear edição após 24h
            edit_deadline = existing.created_at + timedelta(hours=FEEDBACK_EDIT_WINDOW_HOURS)
            if datetime.now(timezone.utc) > edit_deadline:
                raise ValidationError(
                    "Feedback não pode ser editado após 24h do encerramento — INV-TRAIN-070."
                )
            existing.notes = feedback_text
            existing.session_rpe = rating
            existing.updated_at = datetime.now(timezone.utc)
            await self.db.flush()
            await self.db.refresh(existing)
            logger.info(f"Updated post-training feedback for session={session_id} athlete={athlete_id}")
            return existing

        # Criar novo registro
        wp = WellnessPost(
            organization_id=organization_id,
            training_session_id=session_id,
            athlete_id=athlete_id,
            session_rpe=rating,
            fatigue_after=rating,       # proxy: rpe ≈ fatigue percebido
            mood_after=5,               # neutro (atleta pode ajustar via wellness)
            notes=feedback_text,        # INV-077: privado do atleta
            filled_at=datetime.now(timezone.utc),
            created_by_user_id=created_by_user_id,
        )
        self.db.add(wp)
        await self.db.flush()
        await self.db.refresh(wp)
        logger.info(f"Created post-training feedback for session={session_id} athlete={athlete_id}")
        return wp

    # ------------------------------------------------------------------
    # INV-TRAIN-077: resumo de sessão (treinador vê apenas agregados)
    # ------------------------------------------------------------------

    async def get_session_summary(
        self,
        session_id: UUID,
        requesting_role: str = "treinador",
    ) -> dict:
        """
        Retorna resumo de performance da sessão encerrada.

        INV-TRAIN-077: se requesting_role != 'atleta', retorna APENAS
        dados agregados (média de rpe, contagem) — NUNCA texto verbatim.

        Args:
            session_id: UUID da sessão.
            requesting_role: Role do solicitante ('atleta' ou 'treinador').

        Returns:
            dict com resumo. Para treinador: só rating_avg + feedback_count.
            Para atleta: inclui seu próprio feedback_text.
        """
        session = await self._get_session(session_id)

        # Agregar wellness_posts da sessão
        agg_result = await self.db.execute(
            select(
                func.avg(WellnessPost.session_rpe).label("rating_avg"),
                func.count(WellnessPost.id).label("feedback_count"),
            ).where(
                and_(
                    WellnessPost.training_session_id == session_id,
                    WellnessPost.deleted_at.is_(None),
                )
            )
        )
        agg = agg_result.one()

        summary = {
            "session_id": str(session_id),
            "session_status": session.status,
            "rating_avg": float(agg.rating_avg) if agg.rating_avg else None,
            "feedback_count": agg.feedback_count,
        }

        # INV-TRAIN-077: treinador recebe APENAS resumo agregado — sem notas
        if requesting_role == "atleta":
            summary["note"] = "Feedback registrado com sucesso."

        return summary

    # ------------------------------------------------------------------
    # Lista de feedbacks (treinador: apenas agregados)
    # ------------------------------------------------------------------

    async def list_athlete_feedbacks(
        self,
        athlete_id: UUID,
        requesting_role: str = "treinador",
    ) -> list[dict]:
        """
        Lista feedbacks de um atleta por sessão.

        INV-TRAIN-077: para treinador, retorna apenas rating + session_id.
        NUNCA retorna o campo notes (feedback_text verbatim).

        Args:
            athlete_id: UUID do atleta.
            requesting_role: 'atleta' ou 'treinador'.

        Returns:
            Lista de dicts com session_id + rating (sem texto verbatim para treinador).
        """
        result = await self.db.execute(
            select(WellnessPost).where(
                and_(
                    WellnessPost.athlete_id == athlete_id,
                    WellnessPost.deleted_at.is_(None),
                )
            ).order_by(WellnessPost.created_at.desc())
        )
        feedbacks = result.scalars().all()

        items = []
        for fb in feedbacks:
            item = {
                "session_id": str(fb.training_session_id),
                "rating": fb.session_rpe,
                "filled_at": fb.filled_at.isoformat() if fb.filled_at else None,
            }
            # INV-TRAIN-077: atleta vê seu próprio texto; treinador não vê
            if requesting_role == "atleta":
                item["feedback_text"] = fb.notes
            # Para treinador: notes OMITIDO intencionalmente
            items.append(item)

        return items
