"""
Router FastAPI para Roles (catálogo de papéis).

FASE 5 - Implementação completa.

Regras RAG aplicadas:
- R4: Papéis são fixos (catálogo)
- R25/R26: Permissões por papel e escopo
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_context
from app.core.context import ExecutionContext
from app.core.db import get_db, get_async_db
from app.schemas.error import ErrorResponse
from app.schemas.rbac import Role
from app.services.role_service import RoleService

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["roles"],
)


@router.get(
    "",
    response_model=List[Role],
    summary="Listar papéis disponíveis",
    description="""
Lista os papéis disponíveis no sistema (catálogo).

**Papéis V1:** dirigente, coordenador, treinador, atleta

**Regras aplicáveis:** R4 (papéis são catálogo fixo)

**Nota:** Endpoint público (não requer autenticação) pois é apenas um catálogo.
""",
)
def list_roles(
    db: Session = Depends(get_db),
):
    """
    Lista papéis (catálogo).
    Ref: R4 - Papéis são fixos no sistema
    Endpoint público - catálogo fixo não sensível.
    """
    from app.models.role import Role as RoleModel
    roles = db.query(RoleModel).all()
    
    return [Role.model_validate(r) for r in roles]


@router.get(
    "/{role_id}",
    response_model=Role,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        404: {"model": ErrorResponse, "description": "Papel não encontrado"},
    },
    summary="Obter papel por ID",
    description="""
Retorna os dados de um papel específico.

**Regras aplicáveis:** R4 (papéis são catálogo fixo)
""",
)
def get_role_by_id(
    role_id: int,
    db: Session = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
):
    """
    Obtém papel por ID.
    Ref: R4
    """
    service = RoleService(db, context)
    role = service.get_by_id(role_id)

    return Role.model_validate(role)


@router.get(
    "/by-name/{role_name}",
    response_model=Role,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        404: {"model": ErrorResponse, "description": "Papel não encontrado"},
    },
    summary="Obter papel por nome",
    description="""
Retorna os dados de um papel pelo nome (dirigente, coordenador, treinador, atleta).

**Regras aplicáveis:** R4 (papéis são catálogo fixo)
""",
)
def get_role_by_name(
    role_name: str,
    db: Session = Depends(get_db),
    context: ExecutionContext = Depends(get_current_context),
):
    """
    Obtém papel por nome.
    Ref: R4
    """
    service = RoleService(db, context)
    role = service.get_by_name(role_name)

    return Role.model_validate(role)
