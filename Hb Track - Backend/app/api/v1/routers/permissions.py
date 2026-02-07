"""
Router FastAPI para Permissions (catálogo de permissões).

Conforme definido em:
- docs/openapi/rbac.yaml (OpenAPI 3.1)
- docs/fluxo-backend-oficial_Version12.md (Contrato de erros por regra)

Endpoints:
- GET    /v1/permissions                    - Listar permissões disponíveis
- GET    /v1/permissions/{permission_code}  - Obter permissão por código

Regras de negócio:
- R25/R26: Permissões por papel e escopo

Permissões V1 (catálogo inicial):
- read_athlete: Visualizar atletas
- edit_athlete: Editar atletas
- read_training: Visualizar treinos
- edit_training: Editar treinos
- read_match: Visualizar jogos
- edit_match: Editar jogos
- admin_memberships: Administrar vínculos
- admin_organization: Administrar organização

Erros mapeados (Contrato de erros por regra):
- 401 unauthorized: Token inválido ou ausente
- 403 permission_denied (R25/R26): Permissão insuficiente
- 404 not_found: Permissão não encontrada
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.error import ErrorResponse
from app.schemas.rbac import Permission, RoleCode

router = APIRouter(
    tags=["permissions"],
)


# =============================================================================
# GET /v1/permissions - Listar permissões disponíveis
# =============================================================================

@router.get(
    "",
    response_model=List[Permission],
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
    },
    summary="Listar permissões disponíveis",
    description="""
Lista as permissões disponíveis no sistema (catálogo).
Opcionalmente filtra por papel (role_code).

**Regras aplicáveis:** R25/R26 (permissões)
""",
)
async def list_permissions(
    db: Session = Depends(get_db),
    role_code: Optional[RoleCode] = Query(
        None,
        description="Filtrar permissões por papel"
    ),
):
    """
    Lista permissões (catálogo).
    
    Regras:
    - R25/R26: Verificar permissões do ator
    
    Erros:
    - 403 permission_denied: Ator sem permissão
    """
    # TODO: Implementar lógica de negócio
    # 1. Verificar permissões do ator (R25/R26)
    # 2. Filtrar por role_code se fornecido
    # 3. Retornar lista de permissões do catálogo
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint não implementado"
    )


# =============================================================================
# GET /v1/permissions/{permission_code} - Obter permissão por código
# =============================================================================

@router.get(
    "/{permission_code}",
    response_model=Permission,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        404: {"model": ErrorResponse, "description": "Permissão não encontrada"},
    },
    summary="Obter permissão por código",
    description="""
Retorna os dados de uma permissão específica.

**Regras aplicáveis:** R25/R26 (permissões)
""",
)
async def get_permission_by_code(
    permission_code: str,
    db: Session = Depends(get_db),
):
    """
    Obtém permissão por código.
    
    Regras:
    - R25/R26: Verificar permissões do ator
    
    Erros:
    - 403 permission_denied: Ator sem permissão
    - 404 not_found: Permissão não encontrada
    """
    # TODO: Implementar lógica de negócio
    # 1. Verificar permissões do ator (R25/R26)
    # 2. Buscar permissão por código
    # 3. Retornar Permission ou 404
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint não implementado"
    )
