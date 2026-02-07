"""
Schemas Pydantic para Audit Logs.

Regras aplicadas:
- R31/R32: Ações críticas auditadas; log obrigatório com quem/quando/o quê/contexto.
- R33: Regra de ouro — nada relevante apagado; histórico com rastro.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ActorRoleCode(str, Enum):
    """Papel do ator no momento da ação auditada."""
    superadmin = "superadmin"
    dirigente = "dirigente"
    coordenador = "coordenador"
    treinador = "treinador"
    atleta = "atleta"


class AuditLogMetadata(BaseModel):
    """
    Metadata flexível para detalhes da ação auditada.
    
    Estrutura sugerida (não obrigatória):
    - old_values: valores anteriores (quando aplicável)
    - new_values: novos valores (quando aplicável)
    - reason: motivo da ação
    - context: informações adicionais
    """
    model_config = ConfigDict(extra="allow")
    
    old_values: Optional[dict[str, Any]] = Field(
        None,
        description="Valores anteriores à ação (quando aplicável)"
    )
    new_values: Optional[dict[str, Any]] = Field(
        None,
        description="Novos valores após a ação (quando aplicável)"
    )
    reason: Optional[str] = Field(
        None,
        description="Motivo/justificativa da ação"
    )


class AuditLog(BaseModel):
    """
    Log de auditoria de ação crítica.
    
    Referência: R31/R32 — log obrigatório com quem/quando/o quê/contexto.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="Identificador único do log"
    )
    organization_id: UUID = Field(
        ...,
        description="UUID da organização (R34 - clube único V1)"
    )
    season_id: Optional[UUID] = Field(
        None,
        description="UUID da temporada relacionada (quando aplicável)"
    )
    resource_type: str = Field(
        ...,
        description="Tipo do recurso auditado (ex: match, training_session, wellness_post)"
    )
    resource_id: UUID = Field(
        ...,
        description="UUID do recurso afetado"
    )
    action: str = Field(
        ...,
        description="Ação executada (ex: game_finalize, wellness_post_update)"
    )
    actor_membership_id: UUID = Field(
        ...,
        description="UUID do vínculo (membership) do ator"
    )
    actor_role_code: ActorRoleCode = Field(
        ...,
        description="Papel do ator no momento da ação"
    )
    occurred_at: datetime = Field(
        ...,
        description="Momento em que a ação ocorreu"
    )
    request_id: Optional[str] = Field(
        None,
        description="ID de correlação da requisição"
    )
    ip_address: Optional[str] = Field(
        None,
        description="Endereço IP do cliente"
    )
    metadata: Optional[dict[str, Any]] = Field(
        None,
        description="Detalhes adicionais (old_values, new_values, reason, etc.)"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp de criação do registro"
    )


class AuditLogPaginatedResponse(BaseModel):
    """Resposta paginada de logs de auditoria."""
    model_config = ConfigDict(from_attributes=True)

    items: list[AuditLog] = Field(
        ...,
        description="Lista de logs de auditoria"
    )
    page: int = Field(
        ...,
        ge=1,
        description="Página atual"
    )
    limit: int = Field(
        ...,
        ge=1,
        le=100,
        description="Itens por página"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total de registros"
    )
