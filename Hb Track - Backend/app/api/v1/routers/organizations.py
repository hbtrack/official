"""
Router FastAPI para Organizations.

Conforme definido em:
- docs/openapi/rbac.yaml (OpenAPI 3.1)
- docs/fluxo-backend-oficial_Version12.md (Contrato de erros por regra)

Endpoints:
- GET    /v1/organizations                    - Listar organizações (paginado)
- POST   /v1/organizations                    - Criar organização
- GET    /v1/organizations/{organization_id}  - Obter organização por ID
- PATCH  /v1/organizations/{organization_id}  - Atualizar organização

Regras de negócio:
- R25/R26: Permissões por papel e escopo
- R29/R33: Exclusão lógica e histórico com rastro (sem DELETE físico)
- R31/R32: Ações críticas auditadas
- R34: Clube único na V1 (contexto organizacional obrigatório)

Erros mapeados (Contrato de erros por regra):
- 401 unauthorized: Token inválido ou ausente
- 403 permission_denied (R25/R26): Permissão insuficiente
- 404 not_found: Organização não encontrada
- 409 conflict_unique: Code/name já cadastrado
- 422 validation_error: Payload inválido
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import permission_dep
from app.core.context import ExecutionContext
from app.core.db import get_async_db
from app.schemas.error import ErrorResponse
from app.schemas.rbac import (
    Organization,
    OrganizationCreate,
    OrganizationOrderBy,
    OrganizationPaginatedResponse,
    OrganizationUpdate,
    OrderDirection,
)
from app.services.organization_service import OrganizationService

router = APIRouter(
    tags=["organizations"],
)


# =============================================================================
# GET /v1/organizations - Listar organizações (paginado)
# =============================================================================

@router.get(
    "",
    response_model=OrganizationPaginatedResponse,
    summary="Listar organizações (paginado)",
    description="""
Lista paginada de organizações/clubes.

**Nota V1:** Clube único (R34) — contexto organizacional implícito no token.

**Endpoint público:** Necessário para formulário de cadastro.
""",
)
async def list_organizations(
    db: AsyncSession = Depends(get_async_db),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    order_by: OrganizationOrderBy = Query(
        OrganizationOrderBy.CREATED_AT,
        description="Campo para ordenação"
    ),
    order_dir: OrderDirection = Query(
        OrderDirection.DESC,
        description="Direção da ordenação"
    ),
    search: Optional[str] = Query(None, description="Busca por name ou code"),
):
    """
    Lista organizações (paginado).
    
    Endpoint público para uso em formulários de cadastro.
    """
    service = OrganizationService(db)
    items, total = await service.list_organizations(page=page, limit=limit)
    
    return OrganizationPaginatedResponse(
        items=[Organization.model_validate(o) for o in items],
        page=page,
        limit=limit,
        total=total,
    )


# =============================================================================
# POST /v1/organizations - Criar organização
# =============================================================================

@router.post(
    "",
    response_model=Organization,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        409: {"model": ErrorResponse, "description": "Code/name já cadastrado"},
        422: {"model": ErrorResponse, "description": "Payload inválido"},
    },
    summary="Criar organização",
    description="""
Cria uma nova organização/clube.

**Regras aplicáveis:** R25/R26 (permissões), R29 (exclusão lógica), R31/R32 (auditoria)

**Comportamento:**
- Valida unicidade de code e name
- Registra auditoria da criação (R31/R32)
""",
)
async def create_organization(
    payload: OrganizationCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador"], require_org=True)
    ),
):
    """
    Cria organização.
    
    Regras:
    - R25/R26: Verificar permissões do ator (somente superadmin)
    - R29: Exclusão lógica (preparar para soft delete)
    - R31/R32: Registrar auditoria
    """
    service = OrganizationService(db)
    
    # Verificar nome único
    existing = await service.get_by_name(payload.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "name_already_exists", "message": "Nome já existe"}
        )
    
    # ctx.user_id já é UUID, não precisa converter novamente
    owner_id = ctx.user_id if isinstance(ctx.user_id, UUID) else UUID(ctx.user_id)
    org = await service.create(payload, owner_user_id=owner_id)
    await db.commit()
    return Organization.model_validate(org)


# =============================================================================
# GET /v1/organizations/{organization_id} - Obter organização por ID
# =============================================================================

@router.get(
    "/{organization_id}",
    response_model=Organization,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        404: {"model": ErrorResponse, "description": "Organização não encontrada"},
    },
    summary="Obter organização por ID",
    description="""
Retorna os dados de uma organização específica.

**Regras aplicáveis:** R25/R26 (permissões)
""",
)
async def get_organization_by_id(
    organization_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador"], require_org=True)
    ),
):
    """
    Obtém organização por ID.
    
    Regras:
    - R25/R26: Verificar permissões do ator
    """
    service = OrganizationService(db)
    org = await service.get_by_id(organization_id)
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Organização não encontrada"}
        )
    
    return Organization.model_validate(org)


# =============================================================================
# PATCH /v1/organizations/{organization_id} - Atualizar organização
# =============================================================================

@router.patch(
    "/{organization_id}",
    response_model=Organization,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        409: {"model": ErrorResponse, "description": "Code/name já cadastrado"},
        422: {"model": ErrorResponse, "description": "Payload inválido"},
    },
    summary="Atualizar organização",
    description="""
Atualiza dados de uma organização existente.

**Regras aplicáveis:** R25/R26 (permissões), R31/R32 (auditoria)

**Comportamento:**
- Valida unicidade de code e name (se alterados)
- Registra auditoria da alteração (R31/R32)
""",
)
async def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador"], require_org=True)
    ),
):
    """
    Atualiza organização.
    
    Regras:
    - R25/R26: Verificar permissões do ator
    - R31/R32: Registrar auditoria
    """
    service = OrganizationService(db)
    org = await service.get_by_id(organization_id)
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Organização não encontrada"}
        )
    
    # Verificar unicidade do nome se estiver sendo alterado
    if payload.name and payload.name != org.name:
        existing = await service.get_by_name(payload.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "name_already_exists", "message": "Nome já existe"}
            )
    
    try:
        updated = await service.update(org, payload)
        await db.commit()
        return Organization.model_validate(updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": str(e), "message": str(e)}
        )
