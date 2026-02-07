"""
Router para Audit Logs (Auditoria — somente leitura).

Logs de auditoria são IMUTÁVEIS. Não há endpoints POST/PATCH/DELETE públicos.
A criação ocorre internamente via triggers/serviços nas operações auditadas.

Regras aplicadas:
- R25/R26: Permissões por papel e escopo.
- R29: Sem DELETE físico de registros relevantes.
- R31/R32: Ações críticas auditadas; log obrigatório com quem/quando/o quê/contexto.
- R33: Regra de ouro — nada relevante apagado; histórico com rastro.
- R34: Clube único na V1 — contexto organizacional obrigatório.
- R42: Usuários sem vínculo ativo têm somente leitura restrita ou acesso negado.
"""

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.audit_logs import (
    AuditLog,
    AuditLogPaginatedResponse,
    ActorRoleCode,
)

router = APIRouter(
    tags=["audit-logs"],
)


@router.get(
    "",
    response_model=AuditLogPaginatedResponse,
    summary="Lista paginada de logs de auditoria",
    responses={
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente (R25/R26)"},
        422: {"description": "Parâmetros de consulta inválidos"},
    },
)
def list_audit_logs(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    order_by: str = Query("occurred_at", description="Campo para ordenação"),
    order_dir: str = Query("desc", description="Direção: asc ou desc"),
    resource_type: Optional[str] = Query(None, description="Tipo do recurso auditado"),
    resource_id: Optional[UUID] = Query(None, description="UUID do recurso"),
    action: Optional[str] = Query(None, description="Ação executada"),
    actor_membership_id: Optional[UUID] = Query(None, description="UUID do vínculo do ator"),
    actor_role_code: Optional[ActorRoleCode] = Query(None, description="Papel do ator"),
    season_id: Optional[UUID] = Query(None, description="UUID da temporada"),
    date_range_start: Optional[date] = Query(None, description="Data inicial"),
    date_range_end: Optional[date] = Query(None, description="Data final"),
):
    """
    Lista logs de auditoria com filtros por recurso, ação, ator e período.

    **x-rule-ids**: R25, R26, R29, R31, R32, R33, R42

    Filtros disponíveis:
    - resource_type: match, training_session, attendance, wellness_pre, wellness_post, etc.
    - action: game_finalize, game_reopen, wellness_post_update, membership_update, etc.
    - actor_membership_id: UUID do vínculo do ator
    - actor_role_code: superadmin, dirigente, coordenador, treinador, atleta
    - season_id: UUID da temporada
    - date_range_start/date_range_end: período de ocorrência

    Erros possíveis:
    - 401 unauthorized: Token inválido ou ausente
    - 403 permission_denied: Permissão insuficiente (R25/R26)
    - 422 validation_error: Parâmetros de consulta inválidos

    TODO (FASE 5/6):
    - Implementar lógica de busca no banco
    - Validar permissões R25/R26 (somente coordenador/dirigente/superadmin)
    - Aplicar filtro implícito por organization_id do token (R34)
    - Verificar vínculo ativo do requisitante (R42)
    """
    # TODO: Implementar lógica de negócio
    raise NotImplementedError("Endpoint não implementado — aguardando FASE 5/6")


@router.get(
    "/{audit_log_id}",
    response_model=AuditLog,
    summary="Obtém um log de auditoria por ID",
    responses={
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente (R25/R26)"},
        404: {"description": "Log de auditoria não encontrado"},
    },
)
def get_audit_log_by_id(
    audit_log_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retorna detalhes de um log de auditoria específico.

    **x-rule-ids**: R25, R26, R31, R32, R42

    Erros possíveis:
    - 401 unauthorized: Token inválido ou ausente
    - 403 permission_denied: Permissão insuficiente (R25/R26)
    - 404 not_found: Log de auditoria não encontrado

    TODO (FASE 5/6):
    - Implementar busca por ID
    - Validar permissões R25/R26 (somente coordenador/dirigente/superadmin)
    - Verificar se log pertence à organization do token (R34)
    - Verificar vínculo ativo do requisitante (R42)
    """
    # TODO: Implementar lógica de negócio
    raise NotImplementedError("Endpoint não implementado — aguardando FASE 5/6")
