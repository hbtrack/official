"""
Router: Pós-Treino Conversacional (AR_191 — AR-TRAIN-020).

Endpoints de feedback imediato pós-encerramento de sessão de treino.

INV-TRAIN-070: feedback somente após sessão encerrada (status=readonly).
INV-TRAIN-077: treinador acessa apenas resumo agregado — nunca texto verbatim.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.auth import get_current_user
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError
from app.services.post_training_service import PostTrainingService

router = APIRouter(
    prefix="/post-training",
    tags=["post-training"],
)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class PostTrainingFeedbackRequest(BaseModel):
    """Corpo da requisição para registrar feedback pós-treino."""

    feedback_text: str = Field(..., min_length=1, description="Texto do feedback (privado — INV-077)")
    rating: int = Field(..., ge=0, le=10, description="Percepção subjetiva de esforço 0–10")


class PostTrainingFeedbackResponse(BaseModel):
    """Resposta ao registrar feedback."""

    session_id: str
    athlete_id: str
    rating: int
    message: str = "Feedback registrado com sucesso."


class SessionSummaryResponse(BaseModel):
    """Resumo de sessão para treinador/atleta."""

    session_id: str
    session_status: str
    rating_avg: float | None = None
    feedback_count: int = 0
    note: str | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/sessions/{session_id}/feedback",
    response_model=PostTrainingFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar feedback pós-treino (atleta)",
    description=(
        "Atleta registra feedback imediato após encerramento da sessão. "
        "INV-TRAIN-070: somente aceito se sessão está encerrada. "
        "INV-TRAIN-077: texto é privado — treinador não acessa verbatim."
    ),
)
async def create_post_training_feedback(
    session_id: UUID,
    body: PostTrainingFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """POST /post-training/sessions/{session_id}/feedback"""
    svc = PostTrainingService(db)
    try:
        wp = await svc.create_post_training_feedback(
            session_id=session_id,
            athlete_id=current_user.athlete_id if hasattr(current_user, "athlete_id") else current_user.id,
            feedback_text=body.feedback_text,
            rating=body.rating,
            organization_id=current_user.organization_id,
            created_by_user_id=current_user.id,
        )
    except (NotFoundError, ValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return PostTrainingFeedbackResponse(
        session_id=str(session_id),
        athlete_id=str(wp.athlete_id),
        rating=wp.session_rpe,
    )


@router.get(
    "/sessions/{session_id}/summary",
    response_model=SessionSummaryResponse,
    summary="Resumo de sessão pós-treino (atleta e treinador)",
    description=(
        "Retorna resumo de performance da sessão encerrada. "
        "INV-TRAIN-077: treinador recebe apenas rating médio e contagem — "
        "NUNCA o texto verbatim do feedback do atleta."
    ),
)
async def get_session_summary(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """GET /post-training/sessions/{session_id}/summary"""
    svc = PostTrainingService(db)
    role = getattr(current_user, "role_name", "treinador")
    try:
        summary = await svc.get_session_summary(
            session_id=session_id,
            requesting_role=role,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return SessionSummaryResponse(**summary)


@router.get(
    "/athletes/{athlete_id}/feedbacks",
    summary="Listar feedbacks de atleta (treinador — apenas agregados)",
    description=(
        "Treinador lista feedbacks pós-treino de um atleta por sessão. "
        "INV-TRAIN-077: retorna somente rating por sessão — NUNCA texto verbatim."
    ),
)
async def list_athlete_feedbacks(
    athlete_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """GET /post-training/athletes/{athlete_id}/feedbacks"""
    svc = PostTrainingService(db)
    role = getattr(current_user, "role_name", "treinador")
    feedbacks = await svc.list_athlete_feedbacks(
        athlete_id=athlete_id,
        requesting_role=role,
    )
    return {"athlete_id": str(athlete_id), "feedbacks": feedbacks}
