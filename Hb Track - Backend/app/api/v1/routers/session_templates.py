"""
Router para templates de sessão de treino (Session Templates).

Coaches criam templates customizados com distribuição de focos.
Limite 50 templates por org, favoritos, hard delete.
"""
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import permission_dep
from app.core.context import ExecutionContext
from app.core.db import get_async_db
from app.models.session_template import SessionTemplate
from app.schemas.session_template import (
    SessionTemplateCreate,
    SessionTemplateUpdate,
    SessionTemplateResponse,
    SessionTemplateListResponse,
)
from app.schemas.error import ErrorResponse, ErrorCode

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/session-templates",
    tags=["session-templates"],
)


@router.get(
    "",
    response_model=SessionTemplateListResponse,
    summary="List session templates",
    description="Lista templates de treino da organização (máx 50, favoritos primeiro)"
)
async def list_session_templates(
    active_only: bool = Query(True, description="Filtrar apenas templates ativos"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador", "preparador_fisico"])
    )
):
    """
    Lista templates da org do usuário.
    
    Ordenação: favoritos primeiro, depois alfabética.
    Limite: 50 templates por org.
    """
    ctx.requires("can_view_training")
    query = select(SessionTemplate).where(
        SessionTemplate.organization_id == ctx.organization_id
    )
    
    if active_only:
        query = query.where(SessionTemplate.is_active == True)
    
    # Order: favorites first, then alphabetical
    query = query.order_by(
        SessionTemplate.is_favorite.desc(),
        SessionTemplate.name
    )
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return SessionTemplateListResponse(
        templates=[SessionTemplateResponse.model_validate(t) for t in templates],
        total=len(templates),
        limit=50
    )


@router.post(
    "",
    response_model=SessionTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create session template",
    description="Cria template customizado (limite 50 por org)"
)
async def create_session_template(
    data: SessionTemplateCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador", "preparador_fisico"])
    )
):
    """
    Cria novo template de treino.
    
    Validações:
    - Limite 50 templates por org
    - Nome único por org
    - Soma focos ≤ 120%
    """
    ctx.requires("can_create_training")
    # Validate focus total
    try:
        data.validate_total_focus()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    
    # Check limit (50 templates per org)
    count_query = select(func.count()).select_from(SessionTemplate).where(
        SessionTemplate.organization_id == ctx.organization_id
    )
    result = await db.execute(count_query)
    count = result.scalar()
    
    if count >= 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": ErrorCode.VALIDATION_ERROR.value,
                "message": "Limite de 50 templates por organização atingido",
                "constraint": "session_templates_limit"
            }
        )
    
    # Check duplicate name
    check_query = select(SessionTemplate).where(
        and_(
            SessionTemplate.organization_id == ctx.organization_id,
            SessionTemplate.name == data.name
        )
    )
    result = await db.execute(check_query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": ErrorCode.RESOURCE_ALREADY_EXISTS.value,
                "message": f"Template '{data.name}' já existe nesta organização",
                "constraint": "uq_session_templates_org_name"
            }
        )
    
    # Create template
    template = SessionTemplate(
        organization_id=ctx.organization_id,
        created_by_membership_id=ctx.membership_id,
        **data.model_dump()
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    logger.info(
        f"Template created: {template.id} by {ctx.user_id} in org {ctx.organization_id}"
    )
    
    return SessionTemplateResponse.model_validate(template)


@router.get(
    "/{template_id}",
    response_model=SessionTemplateResponse,
    summary="Get session template",
    description="Retorna template específico"
)
async def get_session_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador", "preparador_fisico"])
    )
):
    """Retorna template por ID (org-scoped)."""
    ctx.requires("can_view_training")
    query = select(SessionTemplate).where(
        and_(
            SessionTemplate.id == template_id,
            SessionTemplate.organization_id == ctx.organization_id
        )
    )
    
    result = await db.execute(query)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.RESOURCE_NOT_FOUND.value,
                "message": "Template não encontrado"
            }
        )
    
    return SessionTemplateResponse.model_validate(template)


@router.patch(
    "/{template_id}",
    response_model=SessionTemplateResponse,
    summary="Update session template",
    description="Atualiza template (permite editar templates usados em treinos)"
)
async def update_session_template(
    template_id: UUID,
    data: SessionTemplateUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador", "preparador_fisico"])
    )
):
    """
    Atualiza template existente.
    
    Permite editar mesmo se template já usado em treinos (decisão usuário).
    Validações: nome único, soma focos ≤ 120%.
    """
    ctx.requires("can_edit_training")
    # Get template
    query = select(SessionTemplate).where(
        and_(
            SessionTemplate.id == template_id,
            SessionTemplate.organization_id == ctx.organization_id
        )
    )
    
    result = await db.execute(query)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.RESOURCE_NOT_FOUND.value,
                "message": "Template não encontrado"
            }
        )
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    
    # Check duplicate name if changing
    if 'name' in update_data and update_data['name'] != template.name:
        check_query = select(SessionTemplate).where(
            and_(
                SessionTemplate.organization_id == ctx.organization_id,
                SessionTemplate.name == update_data['name'],
                SessionTemplate.id != template_id
            )
        )
        result = await db.execute(check_query)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error_code": ErrorCode.RESOURCE_ALREADY_EXISTS.value,
                    "message": f"Template '{update_data['name']}' já existe nesta organização",
                    "constraint": "uq_session_templates_org_name"
                }
            )
    
    # Validate focus total if any focus field changed
    focus_fields = [
        'focus_attack_positional_pct', 'focus_defense_positional_pct',
        'focus_transition_offense_pct', 'focus_transition_defense_pct',
        'focus_attack_technical_pct', 'focus_defense_technical_pct',
        'focus_physical_pct'
    ]
    
    if any(f in update_data for f in focus_fields):
        # Calculate new total
        total = 0
        for field in focus_fields:
            if field in update_data:
                total += update_data[field]
            else:
                total += getattr(template, field)
        
        if total > 120:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": ErrorCode.VALIDATION_ERROR.value,
                    "message": f"Total de focos não pode exceder 120%. Atual: {total:.2f}%",
                    "constraint": "chk_session_templates_total_focus"
                }
            )
    
    # Apply updates
    for key, value in update_data.items():
        setattr(template, key, value)
    
    await db.commit()
    await db.refresh(template)
    
    logger.info(
        f"Template updated: {template.id} by {ctx.user_id}"
    )
    
    return SessionTemplateResponse.model_validate(template)


@router.patch(
    "/{template_id}/favorite",
    response_model=SessionTemplateResponse,
    summary="Toggle favorite",
    description="Alterna favorito do template (⭐)"
)
async def toggle_favorite_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador", "preparador_fisico"])
    )
):
    """Toggle template favorite status."""
    ctx.requires("can_edit_training")
    query = select(SessionTemplate).where(
        and_(
            SessionTemplate.id == template_id,
            SessionTemplate.organization_id == ctx.organization_id
        )
    )
    
    result = await db.execute(query)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.RESOURCE_NOT_FOUND.value,
                "message": "Template não encontrado"
            }
        )
    
    # Toggle favorite
    template.is_favorite = not template.is_favorite
    
    await db.commit()
    await db.refresh(template)
    
    logger.info(
        f"Template favorite toggled: {template.id} -> {template.is_favorite} by {ctx.user_id}"
    )
    
    return SessionTemplateResponse.model_validate(template)


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete session template",
    description="HARD DELETE - Remove template permanentemente e libera espaço no limite 50"
)
async def delete_session_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador", "preparador_fisico"])
    )
):
    """
    Hard delete template (físico, não soft delete).
    
    Remove permanentemente para liberar espaço no limite de 50 templates.
    """
    ctx.requires("can_delete_training")
    # Check template exists and belongs to org
    query = select(SessionTemplate).where(
        and_(
            SessionTemplate.id == template_id,
            SessionTemplate.organization_id == ctx.organization_id
        )
    )
    
    result = await db.execute(query)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.RESOURCE_NOT_FOUND.value,
                "message": "Template não encontrado"
            }
        )
    
    # Hard delete
    await db.delete(template)
    await db.commit()
    
    logger.info(
        f"Template HARD DELETED: {template_id} by {ctx.user_id} in org {ctx.organization_id}"
    )
    
    return None
