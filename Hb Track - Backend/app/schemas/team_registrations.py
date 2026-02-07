"""
Pydantic schemas for Team Registrations (inscrição atleta ↔ equipe na temporada).

Regras de negócio documentadas:
- RDB10: Períodos não sobrepostos por pessoa+equipe+temporada; reativação cria nova linha
- R16/RD1/RD2: Regra etária e categoria fixa na temporada
- R38: Atleta deve estar vinculada a pelo menos uma equipe
- R25/R26: Permissões e escopo por papel
- R13 (V1.1): Estado "dispensada" encerra participações vigentes
- R37/RF5.2: Temporada encerrada/interrompida bloqueia criação/edição

Nota de compatibilidade:
- Schema atual: UNIQUE (athlete_id, season_id, category_id)
- RDB10 prevê múltiplas linhas com start_at/end_at para histórico
- Migração futura ajustará unicidade
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TeamRegistrationBase(BaseModel):
    """
    Campos base compartilhados entre schemas de TeamRegistration.
    
    Nota: start_at/end_at usam format: date (não datetime) para consistência
    com membership.start_date/end_date.
    """
    
    season_id: UUID = Field(
        ...,
        description="ID da temporada"
    )
    category_id: int = Field(
        ...,
        description="ID da categoria (validar R16/RD1-RD2 - compatível com idade)"
    )
    team_id: UUID = Field(
        ...,
        description="ID da equipe"
    )
    organization_id: UUID = Field(
        ...,
        description="ID da organização"
    )
    created_by_membership_id: UUID = Field(
        ...,
        description="ID do membership que criou a inscrição"
    )
    role: Optional[str] = Field(
        default=None,
        description="Papel/posição na equipe (ex: goleira, pivo, armadora)"
    )
    start_at: date = Field(
        ...,
        description="Data de início da inscrição (RDB10)"
    )
    end_at: Optional[date] = Field(
        default=None,
        description="Data de término da inscrição; null se ativa (RDB10)"
    )


class TeamRegistrationCreate(BaseModel):
    """
    Schema para criação de inscrição (POST).
    
    Validações:
    - start_at obrigatório
    - end_at >= start_at (quando informado)
    - Backend valida R16/RD1-RD2 (categoria vs birth_date)
    - Backend valida RDB10 (não-sobreposição de período)
    - Backend valida RF5.2/R37 (temporada bloqueada)
    
    Campos obrigatórios: season_id, category_id, team_id, organization_id,
    created_by_membership_id, start_at
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "season_id": "770e8400-e29b-41d4-a716-446655440002",
                "category_id": 1,
                "team_id": "880e8400-e29b-41d4-a716-446655440003",
                "organization_id": "990e8400-e29b-41d4-a716-446655440004",
                "created_by_membership_id": "aa0e8400-e29b-41d4-a716-446655440005",
                "role": "pivo",
                "start_at": "2024-01-15"
            }
        }
    )
    
    season_id: UUID = Field(
        ...,
        description="ID da temporada (obrigatório)"
    )
    category_id: int = Field(
        ...,
        description="ID da categoria (obrigatório; validar R16)"
    )
    team_id: UUID = Field(
        ...,
        description="ID da equipe (obrigatório)"
    )
    organization_id: UUID = Field(
        ...,
        description="ID da organização (obrigatório)"
    )
    created_by_membership_id: UUID = Field(
        ...,
        description="ID do membership criador (obrigatório)"
    )
    role: Optional[str] = Field(
        default=None,
        description="Papel/posição na equipe (opcional)"
    )
    start_at: date = Field(
        ...,
        description="Data de início (obrigatório; RDB10)"
    )
    end_at: Optional[date] = Field(
        default=None,
        description="Data de término (opcional; >= start_at; RDB10)"
    )
    
    @model_validator(mode="after")
    def validate_date_range(self) -> "TeamRegistrationCreate":
        """Validar que end_at >= start_at quando informado."""
        if self.end_at is not None and self.end_at < self.start_at:
            raise ValueError("end_at deve ser >= start_at")
        return self


class TeamRegistrationUpdate(BaseModel):
    """
    Schema para atualização de inscrição (PATCH).
    
    Campos editáveis:
    - end_at: Data de término (para encerramento)
    - role: Papel/posição na equipe
    
    Campos NÃO editáveis (omitidos):
    - athlete_id, season_id, category_id, team_id, organization_id, created_by_membership_id
    
    Validações (backend):
    - Não reabrir período encerrado (RDB10)
    - end_at >= start_at
    - Sem sobreposição de período
    - Temporada não bloqueada (R37/RF5.2)
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "end_at": "2024-12-31",
                "role": "armadora"
            }
        }
    )
    
    end_at: Optional[date] = Field(
        default=None,
        description="Data de término (>= start_at; RDB10)"
    )
    role: Optional[str] = Field(
        default=None,
        description="Papel/posição na equipe"
    )


class TeamRegistrationMoveRequest(BaseModel):
    """
    Payload para mover atleta para outra equipe.

    - Encerra inscricoes ativas na temporada (RDB10)
    - Cria nova inscricao na equipe alvo
    """
    athlete_id: UUID = Field(..., description="ID do atleta")
    start_at: Optional[date] = Field(default=None, description="Data de inicio (default: hoje)")
    end_previous_at: Optional[date] = Field(default=None, description="Data de encerramento das inscricoes anteriores")
    role: Optional[str] = Field(default=None, description="Papel/posicao na equipe")


class AthleteNested(BaseModel):
    """Dados basicos do atleta para response nested."""
    id: UUID = Field(..., description="ID do atleta")
    athlete_name: str = Field(..., description="Nome do atleta")
    athlete_nickname: Optional[str] = Field(default=None, description="Apelido do atleta")
    shirt_number: Optional[int] = Field(default=None, description="Numero da camisa")
    state: str = Field(default="ativa", description="Estado do atleta")

    model_config = ConfigDict(from_attributes=True)


class TeamRegistration(BaseModel):
    """
    Schema de resposta completo para inscrição.
    
    Nota (RDB10): start_at/end_at garantem períodos não sobrepostos
    por pessoa+equipe+temporada. Reativação cria nova linha (novo UUID).
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "athlete_id": "660e8400-e29b-41d4-a716-446655440001",
                "season_id": "770e8400-e29b-41d4-a716-446655440002",
                "category_id": 1,
                "team_id": "880e8400-e29b-41d4-a716-446655440003",
                "organization_id": "990e8400-e29b-41d4-a716-446655440004",
                "created_by_membership_id": "aa0e8400-e29b-41d4-a716-446655440005",
                "role": "pivo",
                "start_at": "2024-01-15",
                "end_at": None,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    )
    
    id: UUID = Field(
        ...,
        description="ID único da inscrição"
    )
    athlete_id: UUID = Field(
        ...,
        description="ID do atleta"
    )
    season_id: Optional[UUID] = Field(
        default=None,
        description="ID da temporada (legado pode vir como None enquanto coluna não existir)"
    )
    category_id: Optional[int] = Field(
        default=None,
        description="ID da categoria (R16/RD1-RD2 - compatível com idade; legado pode ser None)"
    )
    team_id: UUID = Field(
        ...,
        description="ID da equipe"
    )
    organization_id: Optional[UUID] = Field(
        default=None,
        description="ID da organização (legado pode vir como None)"
    )
    created_by_membership_id: Optional[UUID] = Field(
        default=None,
        description="ID do membership que criou a inscrição (legado pode vir como None)"
    )
    role: Optional[str] = Field(
        default=None,
        description="Papel/posição na equipe (ex: goleira, pivo, armadora)"
    )
    start_at: date = Field(
        ...,
        description="Data de início da inscrição (RDB10)"
    )
    end_at: Optional[date] = Field(
        default=None,
        description="Data de término da inscrição; null se ativa (RDB10)"
    )
    created_at: datetime = Field(
        ...,
        description="Data/hora de criação"
    )
    updated_at: datetime = Field(
        ...,
        description="Data/hora da última atualização"
    )
    athlete: Optional[AthleteNested] = Field(default=None, description="Dados do atleta (nested)")


class TeamRegistrationPaginatedResponse(BaseModel):
    """
    Resposta paginada para listagem de inscrições.
    
    Envelope padrão: {items, page, limit, total}
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "athlete_id": "660e8400-e29b-41d4-a716-446655440001",
                        "season_id": "770e8400-e29b-41d4-a716-446655440002",
                        "category_id": 1,
                        "team_id": "880e8400-e29b-41d4-a716-446655440003",
                        "organization_id": "990e8400-e29b-41d4-a716-446655440004",
                        "created_by_membership_id": "aa0e8400-e29b-41d4-a716-446655440005",
                        "role": "pivo",
                        "start_at": "2024-01-15",
                        "end_at": None,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "page": 1,
                "limit": 50,
                "total": 125
            }
        }
    )
    
    items: list[TeamRegistration] = Field(
        ...,
        description="Lista de inscrições na página atual"
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
        description="Total de itens (todas as páginas)"
    )
