"""
Router: Athlete Training Preview

AR_187 (AR-TRAIN-019)

Expõe pre-treino para o atleta autenticado com gate de wellness.

Invariantes:
- INV-TRAIN-068: atleta pode ver treino antes de iniciar
- INV-TRAIN-069: mídia acessível ao atleta
- INV-TRAIN-071: wellness missing bloqueia conteúdo completo (AccessGated)
- INV-TRAIN-076: wellness obrigatório
- INV-TRAIN-078: progresso exige compliance wellness

PROIBIDO: não alterar athlete_content_gate_service.py
"""

from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text as sa_text

from app.core.auth import get_current_user
from app.core.context import ExecutionContext
from app.core.db import AsyncSession, get_async_db
from app.core.exceptions import NotFoundError
from app.services.athlete_content_gate_service import (
    AccessGated,
    AthleteContentGateService,
)

router = APIRouter(tags=["athlete-training"])


@router.get(
    "/training-sessions/{session_id}/preview",
    summary="Pré-visualização do treino para atleta com gate de wellness (INV-TRAIN-071)",
    responses={
        200: {"description": "Dados de preview (conteúdo completo ou mínimo segundo wellness_blocked)"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente (apenas atleta da sessão)"},
        404: {"description": "Sessão ou atleta não encontrado"},
    },
)
async def get_training_preview(
    session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Retorna dados de pré-visualização do treino para o atleta.

    - Se wellness_blocked=True (AccessGated): retorna info mínima + flag
    - Se wellness_blocked=False (AccessGranted): retorna info completa com exercícios

    INV-TRAIN-071: conteúdo completo (exercícios + mídia) apenas se wellness em dia.
    """
    # ─── 1. Resolver athlete_id a partir do person_id do usuário autenticado ───
    athlete_row = await db.execute(
        sa_text(
            "SELECT id FROM athletes WHERE person_id = :pid AND deleted_at IS NULL LIMIT 1"
        ),
        {"pid": str(current_user.person_id)},
    )
    athlete = athlete_row.fetchone()
    if athlete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atleta não encontrado para o usuário autenticado",
        )
    athlete_id: UUID = athlete[0]

    # ─── 2. Carregar dados básicos da sessão ───
    session_row = await db.execute(
        sa_text(
            "SELECT id, name, scheduled_date, status "
            "FROM training_sessions "
            "WHERE id = :session_id AND deleted_at IS NULL LIMIT 1"
        ),
        {"session_id": str(session_id)},
    )
    session_data = session_row.fetchone()
    if session_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sessão de treino {session_id} não encontrada",
        )

    # ─── 3. Gate de wellness (INV-TRAIN-071) ───
    gate_service = AthleteContentGateService(db)
    access_result = await gate_service.check_content_access(athlete_id=athlete_id)
    wellness_blocked: bool = isinstance(access_result, AccessGated)

    # ─── 4. Montar response ───
    base_info: Dict[str, Any] = {
        "session_id": str(session_id),
        "name": session_data[1],
        "scheduled_date": str(session_data[2]) if session_data[2] else None,
        "status": session_data[3],
        "wellness_blocked": wellness_blocked,
    }

    if wellness_blocked:
        # INV-TRAIN-071: conteúdo completo bloqueado — retorna apenas info mínima
        return {
            **base_info,
            "message": (
                "Preencha o wellness do dia para acessar o conteúdo completo do treino."
            ),
            "exercises": [],
        }

    # Conteúdo completo: carregar exercícios da sessão
    exercises_rows = await db.execute(
        sa_text(
            "SELECT e.id, e.name, e.description, em.media_url "
            "FROM session_exercises se "
            "JOIN exercises e ON e.id = se.exercise_id "
            "LEFT JOIN exercise_media em ON em.exercise_id = e.id AND em.deleted_at IS NULL "
            "WHERE se.training_session_id = :session_id AND se.deleted_at IS NULL "
            "ORDER BY se.display_order ASC"
        ),
        {"session_id": str(session_id)},
    )
    exercises = [
        {
            "id": str(row[0]),
            "name": row[1],
            "description": row[2],
            "media_url": row[3],
        }
        for row in exercises_rows.fetchall()
    ]

    return {
        **base_info,
        "exercises": exercises,
    }


# =============================================================================
# AR_241 — AR-TRAIN-057 — CONTRACT-TRAIN-105
# GET /athlete/wellness-content-gate/{session_id}
# INV-TRAIN-071: sem wellness = conteúdo completo bloqueado
# INV-TRAIN-076: athlete_id inferido do token JWT — nunca de query param
# =============================================================================

@router.get(
    "/wellness-content-gate/{session_id}",
    summary="Gate de wellness do atleta para acesso a conteúdo (INV-TRAIN-071)",
    responses={
        200: {"description": "Estado do gate de wellness (has_wellness, can_see_full_content)"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente (apenas o próprio atleta)"},
        404: {"description": "Atleta não encontrado para o usuário autenticado"},
    },
)
async def get_wellness_content_gate(
    session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Verifica se o atleta autenticado tem wellness em dia e pode ver conteúdo completo.

    INV-TRAIN-071: sem wellness = conteúdo completo bloqueado.
    INV-TRAIN-076: athlete_id inferido do JWT — NUNCA de query param (self-only).

    Response:
    - has_wellness: bool — True se wellness diário completo
    - can_see_full_content: bool — True se acesso liberado
    - blocked_reason: str | null — razão do bloqueio quando has_wellness=False
    """
    # ─── 1. Resolver athlete_id a partir do person_id do token ───
    athlete_row = await db.execute(
        sa_text(
            "SELECT id FROM athletes WHERE person_id = :pid AND deleted_at IS NULL LIMIT 1"
        ),
        {"pid": str(current_user.person_id)},
    )
    athlete = athlete_row.fetchone()
    if athlete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atleta não encontrado para o usuário autenticado",
        )
    athlete_id: UUID = athlete[0]

    # ─── 2. Verificar gate de wellness (INV-TRAIN-071) ───
    gate_service = AthleteContentGateService(db)
    access_result = await gate_service.check_content_access(athlete_id=athlete_id)

    # ─── 3. Mapear AccessResult para response canônica ───
    if isinstance(access_result, AccessGated):
        return {
            "session_id": str(session_id),
            "has_wellness": False,
            "can_see_full_content": False,
            "blocked_reason": access_result.reason,
            "missing_items": access_result.missing_items,
        }

    return {
        "session_id": str(session_id),
        "has_wellness": True,
        "can_see_full_content": True,
        "blocked_reason": None,
        "missing_items": [],
    }
