"""
Router FastAPI para Memberships (vínculos person↔organization+role) - V1.2.

FASE 5 - Implementação completa.

Regras RAG aplicadas:
- R6/R7: Vínculo organizacional (pessoa, papel, clube)
- RDB9: Exclusividade de vínculo ativo
- R25/R26: Permissões por papel e escopo
- R42: Usuários sem vínculo ativo não podem operar
- V1.2: org_memberships usa person_id, sem season_id, sem status (usa end_at)
"""

import logging
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_context, require_role
from app.core.context import ExecutionContext
from app.core.db import get_async_db
from app.core.exceptions import NotFoundError, ValidationError
from app.models.membership import OrgMembership
from app.schemas.error import ErrorResponse
from app.schemas.rbac import (
    Membership,
    MembershipCreate,
    MembershipOrderBy,
    MembershipPaginatedResponse,
    MembershipUpdate,
    OrderDirection,
    RoleCode,
)
from app.services.membership_service import MembershipService

logger = logging.getLogger(__name__)

# Router principal para /v1/memberships/{id}
router = APIRouter(
    prefix="/memberships",
    tags=["memberships"],
)

# Router secundário para /v1/organizations/{org_id}/memberships
org_memberships_router = APIRouter(
    prefix="/organizations",
    tags=["memberships"],
)

# Router para /v1/org-memberships (simplificado para frontend)
org_memberships_simple_router = APIRouter(
    prefix="/org-memberships",
    tags=["memberships"],
)


# =============================================================================
# GET /v1/organizations/{organization_id}/memberships - Listar vínculos por organização
# =============================================================================

@org_memberships_router.get(
    "/{organization_id}/memberships",
    response_model=MembershipPaginatedResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
    },
    summary="Listar vínculos por organização (paginado)",
    description="""
Lista paginada de vínculos (memberships) de uma organização.

**Regras aplicáveis:** R6/R7, RDB9, R25/R26
""",
)
async def list_memberships_by_organization(
    organization_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["dirigente", "coordenador"])),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    order_by: MembershipOrderBy = Query(
        MembershipOrderBy.CREATED_AT,
        description="Campo para ordenação"
    ),
    order_dir: OrderDirection = Query(
        OrderDirection.DESC,
        description="Direção da ordenação"
    ),
    is_active: Optional[bool] = Query(None, description="Filtrar por status ativo/inativo"),
    role_code: Optional[RoleCode] = Query(None, description="Filtrar por papel"),
):
    """
    Lista vínculos por organização (paginado).
    V1.2: usa active_only ao invés de status enum.
    Ref: R6/R7, RDB9, R25/R26
    """
    service = MembershipService(db)
    
    # Converter role_code para role_id
    role_id = None
    if role_code:
        role_map = {"dirigente": 1, "coordenador": 2, "treinador": 3, "atleta": 4}
        role_id = role_map.get(role_code.value)
    
    # V1.2: usa active_only (end_at IS NULL)
    active_only = is_active if is_active is not None else True
    
    memberships, total = await service.list_memberships(
        organization_id,
        role_id=role_id,
        active_only=active_only,
        page=page,
        limit=limit,
    )
    
    pages = (total + limit - 1) // limit if total > 0 else 0
    
    return MembershipPaginatedResponse(
        items=[Membership.model_validate(m) for m in memberships],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


# =============================================================================
# POST /v1/organizations/{organization_id}/memberships - Criar vínculo
# =============================================================================

@org_memberships_router.post(
    "/{organization_id}/memberships",
    response_model=Membership,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        409: {"model": ErrorResponse, "description": "Vínculo ativo duplicado (RDB9)"},
        422: {"model": ErrorResponse, "description": "Payload inválido"},
    },
    summary="Criar vínculo para organização",
    description="""
Cria um novo vínculo (membership) user↔organization+role.

**Regras aplicáveis:** R6/R7, RDB9 (exclusividade)
""",
)
async def create_membership_for_organization(
    organization_id: UUID,
    payload: MembershipCreate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["dirigente"])),
):
    """
    Cria vínculo para organização (V1.2).
    V1.2: usa person_id, sem season_id.
    Ref: R6/R7, RDB9
    """
    service = MembershipService(db)
    
    # Converter role_code para role_id
    role_map = {"dirigente": 1, "coordenador": 2, "treinador": 3, "atleta": 4}
    role_id = role_map.get(payload.role_code.value, 4)
    
    try:
        membership = await service.create(
            organization_id=organization_id,
            person_id=payload.person_id,  # V1.2: usa person_id
            role_id=role_id,
            start_at=payload.start_date,  # V1.2: start_at
        )
        await db.commit()
        await db.refresh(membership)
        
        logger.info(
            f"Created membership {membership.id} for person {payload.person_id} "
            f"in org {organization_id}"
        )
        
        return Membership.model_validate(membership)
        
    except ValueError as e:
        await db.rollback()
        if "conflict_membership_active" in str(e):
            raise ValidationError("Pessoa já possui vínculo ativo nesta organização (RDB9)")
        if "athlete_use_team_registrations" in str(e):
            raise ValidationError("Atletas usam team_registrations, não org_memberships (V1.2)")
        raise


# =============================================================================
# GET /v1/memberships/{membership_id} - Obter vínculo por ID
# =============================================================================

@router.get(
    "/{membership_id}",
    response_model=Membership,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        404: {"model": ErrorResponse, "description": "Vínculo não encontrado"},
    },
    summary="Obter vínculo por ID",
    description="""
Retorna os dados de um vínculo específico.

**Regras aplicáveis:** R25/R26 (permissões)
""",
)
async def get_membership_by_id(
    membership_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(get_current_context),
):
    """
    Obtém vínculo por ID.
    Ref: R6/R7
    """
    service = MembershipService(db)
    membership = await service.get_by_id(membership_id)
    
    if not membership:
        raise NotFoundError(f"Membership {membership_id} not found")
    
    return Membership.model_validate(membership)


# =============================================================================
# PATCH /v1/memberships/{membership_id} - Atualizar vínculo
# =============================================================================

@router.patch(
    "/{membership_id}",
    response_model=Membership,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        404: {"model": ErrorResponse, "description": "Vínculo não encontrado"},
        422: {"model": ErrorResponse, "description": "Payload inválido"},
    },
    summary="Atualizar vínculo",
    description="""
Atualiza role_code e/ou is_active de um vínculo existente.

**Regras aplicáveis:** R6/R7, RDB9, R25/R26
""",
)
async def update_membership(
    membership_id: UUID,
    payload: MembershipUpdate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["dirigente"])),
):
    """
    Atualiza vínculo (V1.2).
    V1.2: Não tem status, usa end_at para inativo.
    Ref: R6/R7, RDB9, R25/R26
    """
    service = MembershipService(db)
    membership = await service.get_by_id(membership_id)
    
    if not membership:
        raise NotFoundError(f"Membership {membership_id} not found")
    
    # Atualizar campos fornecidos
    if payload.role_code is not None:
        role_map = {"dirigente": 1, "coordenador": 2, "treinador": 3, "atleta": 4}
        membership.role_id = role_map.get(payload.role_code.value, membership.role_id)
    
    # V1.2: is_active controla end_at (não status)
    if payload.is_active is not None:
        if payload.is_active:
            membership.end_at = None  # Reativar
        else:
            membership.end_at = date.today()  # Desativar
    
    await db.commit()
    await db.refresh(membership)
    
    logger.info(f"Updated membership {membership_id}")
    
    return Membership.model_validate(membership)


@router.post(
    "/{membership_id}/end",
    response_model=Membership,
    summary="Encerrar vínculo",
    description="""
Encerra um vínculo ativo (soft delete via status=inativo).

**Regras aplicáveis:** R7 (encerramento de vínculo)
""",
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        404: {"model": ErrorResponse, "description": "Vínculo não encontrado"},
    },
)
async def end_membership(
    membership_id: UUID,
    end_date: Optional[date] = Query(None, description="Data de encerramento (default: hoje)"),
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["dirigente"])),
):
    """
    Encerra vínculo.
    Ref: R7
    """
    service = MembershipService(db)
    membership = await service.get_by_id(membership_id)
    
    if not membership:
        raise NotFoundError(f"Membership {membership_id} not found")
    
    membership = await service.end_membership(membership, end_date)
    await db.commit()
    await db.refresh(membership)
    
    logger.info(f"Ended membership {membership_id}")
    
    return Membership.model_validate(membership)

# =============================================================================
# GET /v1/org-memberships - Listar vínculos da organização do usuário
# =============================================================================

@org_memberships_simple_router.get(
    "",
    response_model=MembershipPaginatedResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
    },
    summary="Listar vínculos da organização do usuário",
    description="""
Lista paginada de vínculos (memberships) da organização do usuário logado.
Usa a organização do contexto de execução automaticamente.

**Regras aplicáveis:** R6/R7, RDB9, R25/R26
""",
)
async def list_org_memberships(
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(get_current_context),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    role_id: Optional[int] = Query(None, description="Filtrar por role_id (1=dirigente, 2=coordenador, 3=treinador)"),
    active_only: bool = Query(True, description="Apenas vínculos ativos"),
):
    """
    Lista vínculos da organização do usuário logado.
    Simplifica o frontend que não precisa passar organization_id.
    """
    if not context.organization_id:
        raise ValidationError("Usuário não possui organização associada")

    service = MembershipService(db)

    memberships, total = await service.list_memberships(
        context.organization_id,
        role_id=role_id,
        active_only=active_only,
        page=page,
        limit=limit,
    )

    pages = (total + limit - 1) // limit if total > 0 else 0

    return MembershipPaginatedResponse(
        items=[Membership.model_validate(m) for m in memberships],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


# NOTA: org_memberships_router e org_memberships_simple_router são exportados separadamente
