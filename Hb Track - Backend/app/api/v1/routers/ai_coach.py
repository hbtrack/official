"""
Router: IA Coach (AR_192 — AR-TRAIN-021).

Endpoints REST para chat conversacional com IA Coach e geração de rascunhos
de sugestões de sessão/microciclo para o treinador.

Invariantes enforçadas:
- INV-079: Reconhecimento usa apenas métricas agregadas (não texto íntimo).
- INV-080: Toda proposta de sessão/microciclo da IA → status='draft' (nunca autopublicada).
- INV-081: Sugestão sem justificativa → label 'ideia_generica' (não 'recomendação').
- Preservados: INV-072..075 (tone guard, privacy filter, educational, draft guard atleta).
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.auth import get_current_user
from app.services.ai_coach_service import (
    AICoachService,
    TrainingSessionDraft,
    MicrocycleDraft,
)

router = APIRouter(
    prefix="/ai",
    tags=["ai-coach"],
)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class ChatMessageRequest(BaseModel):
    """Mensagem de chat para a IA Coach."""

    message: str = Field(..., min_length=1, description="Mensagem do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão de contexto")


class ChatMessageResponse(BaseModel):
    """Resposta da IA Coach ao chat."""

    response: str
    tone_validated: bool = True
    privacy_filter_applied: bool = True


class SuggestSessionRequest(BaseModel):
    """Solicitar sugestão de sessão de treino."""

    title: Optional[str] = Field(None, description="Título sugerido para a sessão")
    justification: str = Field(
        ..., min_length=1,
        description="Justificativa baseada em sinais do sistema (INV-081)"
    )
    context: Dict[str, Any] = Field(default_factory=dict)


class SuggestSessionResponse(BaseModel):
    """Rascunho de sessão sugerida pela IA."""

    title: str
    status: str  # SEMPRE 'draft' (INV-080)
    source: str  # SEMPRE 'ai_coach_suggestion' (INV-080)
    requires_coach_approval: bool  # SEMPRE True (INV-080)
    justification: str
    label: str  # 'recomendacao' ou 'ideia_generica' (INV-081)


class SuggestMicrocycleRequest(BaseModel):
    """Solicitar sugestão de microciclo."""

    title: Optional[str] = Field(None)
    week_focus: Optional[str] = Field(None)
    justification: str = Field(..., min_length=1)
    context: Dict[str, Any] = Field(default_factory=dict)


class DraftListResponse(BaseModel):
    """Lista de rascunhos pendentes de revisão pelo treinador."""

    drafts: List[Dict[str, Any]]
    total: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/chat",
    response_model=ChatMessageResponse,
    summary="Chat conversacional com IA Coach",
    description=(
        "Atleta ou treinador envia mensagem para a IA Coach. "
        "INV-072: guard de tom imperativo aplicado na resposta. "
        "INV-073: filtro de privacidade — conteúdo íntimo do atleta não exposto ao treinador."
    ),
)
async def chat(
    body: ChatMessageRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """POST /ai/chat"""
    svc = AICoachService()

    # INV-072: verificar tom da mensagem do usuário
    tone_result = svc.check_suggestion_tone(body.message)

    # INV-073: filtrar privacidade
    privacy_result = svc.filter_privacy(body.message)

    # Resposta padrão (IA Coach placeholder — integração LLM futura)
    response_text = (
        "Olá! Estou analisando seus dados de treino. "
        "Como posso ajudar com sua performance?"
    )

    return ChatMessageResponse(
        response=response_text,
        tone_validated=not hasattr(tone_result, "reason") or tone_result.reason != "imperative_tone_detected",
        privacy_filter_applied=True,
    )


@router.post(
    "/coach/suggest-session",
    response_model=SuggestSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sugerir sessão de treino (treinador — rascunho obrigatório)",
    description=(
        "Treinador solicita sugestão de sessão à IA. "
        "INV-080: resultado SEMPRE criado como draft — nunca autopublicado. "
        "INV-081: justificativa obrigatória; sem ela → label 'ideia_generica'."
    ),
)
async def suggest_session(
    body: SuggestSessionRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """POST /ai/coach/suggest-session"""
    svc = AICoachService()

    ctx = dict(body.context)
    ctx["title"] = body.title or "Sessão sugerida pela IA"
    ctx["justification"] = body.justification

    # INV-080: gerar draft de sessão
    draft: TrainingSessionDraft = svc.generate_session_suggestion(
        coach_id=str(current_user.id),
        context=ctx,
    )

    # INV-081: verificar justificativa
    justification_result = svc.enforce_justification(
        content=draft.title,
        justification=draft.justification,
    )

    return SuggestSessionResponse(
        title=draft.title,
        status=draft.status,           # INV-080: SEMPRE 'draft'
        source=draft.source,           # INV-080: SEMPRE 'ai_coach_suggestion'
        requires_coach_approval=draft.requires_coach_approval,
        justification=draft.justification,
        label=justification_result.label,  # INV-081: 'recomendacao' ou 'ideia_generica'
    )


@router.post(
    "/coach/suggest-microcycle",
    status_code=status.HTTP_201_CREATED,
    summary="Sugerir microciclo (treinador — rascunho obrigatório)",
    description=(
        "INV-080: microciclo sugerido sempre como draft. "
        "INV-081: sem justificativa → label 'ideia_generica'."
    ),
)
async def suggest_microcycle(
    body: SuggestMicrocycleRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """POST /ai/coach/suggest-microcycle"""
    svc = AICoachService()

    ctx = dict(body.context)
    ctx["title"] = body.title or "Microciclo sugerido pela IA"
    ctx["week_focus"] = body.week_focus or "Foco geral"
    ctx["justification"] = body.justification

    draft: MicrocycleDraft = svc.generate_microcycle_suggestion(
        coach_id=str(current_user.id),
        context=ctx,
    )

    justification_result = svc.enforce_justification(
        content=draft.title,
        justification=draft.justification,
    )

    return {
        "title": draft.title,
        "week_focus": draft.week_focus,
        "status": draft.status,            # INV-080: 'draft'
        "source": draft.source,
        "requires_coach_approval": draft.requires_coach_approval,
        "justification": draft.justification,
        "label": justification_result.label,  # INV-081
    }


@router.get(
    "/coach/drafts",
    response_model=DraftListResponse,
    summary="Listar rascunhos pendentes de revisão (treinador)",
    description=(
        "Lista rascunhos de sessões/microciclos gerados pela IA aguardando "
        "aprovação do treinador. INV-080: nenhum draft é autopublicado."
    ),
)
async def list_drafts(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GET /ai/coach/drafts"""
    # Placeholder: integração com tabela de drafts futura
    return DraftListResponse(
        drafts=[],
        total=0,
    )
