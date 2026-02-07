"""
Pydantic schemas for Competitions and Competition Seasons.

Regras de negócio documentadas:
- R25/R26: Permissões por papel e escopo
- R29: Exclusão lógica obrigatória — não há DELETE físico
- R33: Regra de ouro (nada fora de vínculo, nada relevante apagado, histórico com rastro)
- R34: Clube único na V1; contexto organizacional implícito via token
- R42: Modo somente leitura sem vínculo ativo
- RF4: Criação de temporadas (referência para competition_seasons)

Campo kind (Competition):
- Texto livre na V1
- Exemplos: "official", "friendly", "training-game"
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# COMPETITION SCHEMAS
# =============================================================================


class CompetitionCreate(BaseModel):
    """
    Schema para criação de competição (POST).

    Campos obrigatórios:
    - name: Nome da competição

    Campo kind:
    Texto livre. Exemplos: "official", "friendly", "training-game"
    
    NOTA: organization_id é obtido automaticamente do contexto de autenticação (R34)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Campeonato Estadual Sub-17",
                "kind": "official",
            }
        }
    )

    name: str = Field(
        ...,
        min_length=1,
        description="Nome da competição (obrigatório)",
    )
    kind: Optional[str] = Field(
        default=None,
        description="Tipo da competição (texto livre). Ex: official, friendly, training-game",
    )


class CompetitionUpdate(BaseModel):
    """
    Schema para atualização de competição (PATCH).

    Campos editáveis:
    - name: Nome da competição
    - kind: Tipo da competição

    Campos NÃO editáveis (omitidos):
    - organization_id (imutável após criação)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Campeonato Estadual Sub-17 - Edição 2024",
                "kind": "official",
            }
        }
    )

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Nome da competição",
    )
    kind: Optional[str] = Field(
        default=None,
        description="Tipo da competição (texto livre)",
    )


class Competition(BaseModel):
    """
    Schema de resposta completo para competição.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "organization_id": "660e8400-e29b-41d4-a716-446655440001",
                "name": "Campeonato Estadual Sub-17",
                "kind": "official",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        }
    )

    id: UUID = Field(
        ...,
        description="ID único da competição",
    )
    organization_id: UUID = Field(
        ...,
        description="ID da organização",
    )
    name: str = Field(
        ...,
        description="Nome da competição",
    )
    kind: Optional[str] = Field(
        default=None,
        description="Tipo da competição (texto livre)",
    )
    created_at: datetime = Field(
        ...,
        description="Data/hora de criação",
    )
    updated_at: datetime = Field(
        ...,
        description="Data/hora da última atualização",
    )


class CompetitionPaginatedResponse(BaseModel):
    """
    Resposta paginada para listagem de competições.

    Envelope padrão: {items, page, limit, total}
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "organization_id": "660e8400-e29b-41d4-a716-446655440001",
                        "name": "Campeonato Estadual Sub-17",
                        "kind": "official",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z",
                    }
                ],
                "page": 1,
                "limit": 50,
                "total": 25,
            }
        }
    )

    items: list[Competition] = Field(
        ...,
        description="Lista de competições na página atual",
    )
    page: int = Field(
        ...,
        ge=1,
        description="Página atual",
    )
    limit: int = Field(
        ...,
        ge=1,
        le=100,
        description="Itens por página",
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total de itens (todas as páginas)",
    )


# =============================================================================
# COMPETITION SEASON SCHEMAS
# =============================================================================


class CompetitionSeasonCreate(BaseModel):
    """
    Schema para criação de vínculo competição ↔ temporada (POST).

    Campos obrigatórios:
    - season_id: UUID da temporada a vincular

    Constraint: UNIQUE (competition_id, season_id)
    - competition_id vem do path parameter
    - Violação retorna 409 conflict_unique
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "season_id": "880e8400-e29b-41d4-a716-446655440003",
                "name": "Fase Regional 2024",
            }
        }
    )

    season_id: UUID = Field(
        ...,
        description="ID da temporada a vincular (obrigatório)",
    )
    name: Optional[str] = Field(
        default=None,
        description="Nome/descrição do vínculo (opcional)",
    )


class CompetitionSeasonUpdate(BaseModel):
    """
    Schema para atualização de vínculo competição ↔ temporada (PATCH).

    Campos editáveis:
    - name: Nome/descrição do vínculo

    Campos NÃO editáveis (omitidos):
    - competition_id (imutável)
    - season_id (imutável)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Fase Regional 2024 - Atualizado",
            }
        }
    )

    name: Optional[str] = Field(
        default=None,
        description="Nome/descrição do vínculo",
    )


class CompetitionSeason(BaseModel):
    """
    Schema de resposta completo para vínculo competição ↔ temporada.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440002",
                "competition_id": "550e8400-e29b-41d4-a716-446655440000",
                "season_id": "880e8400-e29b-41d4-a716-446655440003",
                "name": "Fase Regional 2024",
                "created_at": "2024-01-20T09:00:00Z",
                "updated_at": "2024-01-20T09:00:00Z",
            }
        }
    )

    id: UUID = Field(
        ...,
        description="ID único do vínculo",
    )
    competition_id: UUID = Field(
        ...,
        description="ID da competição",
    )
    season_id: UUID = Field(
        ...,
        description="ID da temporada",
    )
    name: Optional[str] = Field(
        default=None,
        description="Nome/descrição do vínculo (ex. fase, edição)",
    )
    created_at: datetime = Field(
        ...,
        description="Data/hora de criação",
    )
    updated_at: datetime = Field(
        ...,
        description="Data/hora da última atualização",
    )


class CompetitionSeasonPaginatedResponse(BaseModel):
    """
    Resposta paginada para listagem de vínculos competição ↔ temporada.

    Envelope padrão: {items, page, limit, total}
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "770e8400-e29b-41d4-a716-446655440002",
                        "competition_id": "550e8400-e29b-41d4-a716-446655440000",
                        "season_id": "880e8400-e29b-41d4-a716-446655440003",
                        "name": "Fase Regional 2024",
                        "created_at": "2024-01-20T09:00:00Z",
                        "updated_at": "2024-01-20T09:00:00Z",
                    }
                ],
                "page": 1,
                "limit": 50,
                "total": 10,
            }
        }
    )

    items: list[CompetitionSeason] = Field(
        ...,
        description="Lista de vínculos na página atual",
    )
    page: int = Field(
        ...,
        ge=1,
        description="Página atual",
    )
    limit: int = Field(
        ...,
        ge=1,
        le=100,
        description="Itens por página",
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total de itens (todas as páginas)",
    )
