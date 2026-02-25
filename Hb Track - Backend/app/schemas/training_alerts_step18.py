"""
Training Suggestions Schemas - Step 18

Pydantic schemas para validação de API relacionadas a sugestões de treinamento (alertas automáticos).
"""

from datetime import datetime
from typing import Optional, Literal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class SuggestionType(str, Enum):
    """Tipos de sugestão."""
    COMPENSATION = "compensation"
    REDUCE_NEXT_WEEK = "reduce_next_week"


class SuggestionStatus(str, Enum):
    """Status da sugestão."""
    PENDING = "pending"
    APPLIED = "applied"
    DISMISSED = "dismissed"


class SuggestionCreate(BaseModel):
    """Schema para criação de sugestão."""
    team_id: UUID = Field(..., description="ID da equipe")
    type: SuggestionType = Field(..., description="Tipo de sugestão")
    origin_session_id: Optional[UUID] = Field(default=None, description="ID da sessão de origem")
    target_session_ids: list[UUID] = Field(..., min_length=1, description="IDs das sessões alvo")
    recommended_adjustment_pct: float = Field(..., ge=10, le=40, description="Ajuste recomendado em %")
    reason: str = Field(..., min_length=20, max_length=1000, description="Justificativa da sugestão")

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "550e8400-e29b-41d4-a716-446655440000",
                "type": "compensation",
                "origin_session_id": "550e8400-e29b-41d4-a716-446655440010",
                "target_session_ids": ["550e8400-e29b-41d4-a716-446655440011", "550e8400-e29b-41d4-a716-446655440012"],
                "recommended_adjustment_pct": 15.0,
                "reason": "Sessão #123 teve focus_pct=120%. Sugerindo compensação de -15% nas próximas 2 sessões não-locked."
            }
        }


class SuggestionApply(BaseModel):
    """Schema para aplicação de sugestão (ajuste final do usuário)."""
    adjustment_pct: float = Field(..., ge=10, le=40, description="Ajuste final escolhido pelo usuário (10-40%)")

    @field_validator('adjustment_pct')
    @classmethod
    def validate_adjustment(cls, v):
        """Valida range do ajuste."""
        if not (10 <= v <= 40):
            raise ValueError('adjustment_pct deve estar entre 10% e 40%')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "adjustment_pct": 20.0
            }
        }


class SuggestionDismiss(BaseModel):
    """Schema para dismissal de sugestão (com justificativa)."""
    dismissal_reason: str = Field(..., min_length=10, max_length=500, description="Motivo da rejeição")

    class Config:
        json_schema_extra = {
            "example": {
                "dismissal_reason": "Planejamento semanal já ajustado manualmente. Sugestão não aplicável."
            }
        }


class SuggestionResponse(BaseModel):
    """Schema de resposta de sugestão."""
    id: int
    team_id: int
    type: str
    origin_session_id: Optional[int]
    target_session_ids: list[int]
    recommended_adjustment_pct: float
    reason: str
    status: str
    created_at: datetime
    applied_at: Optional[datetime]
    dismissed_at: Optional[datetime]
    dismissal_reason: Optional[str]
    
    # Computed properties
    is_pending: bool
    is_applied: bool
    is_dismissed: bool
    target_count: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "team_id": 1,
                "type": "compensation",
                "origin_session_id": 123,
                "target_session_ids": [124, 125],
                "recommended_adjustment_pct": 15.0,
                "reason": "Sessão #123 teve focus_pct=120%. Compensação sugerida.",
                "status": "pending",
                "created_at": "2025-01-27T14:30:00",
                "applied_at": None,
                "dismissed_at": None,
                "dismissal_reason": None,
                "is_pending": True,
                "is_applied": False,
                "is_dismissed": False,
                "target_count": 2
            }
        }


class SuggestionListResponse(BaseModel):
    """Schema de resposta paginada de sugestões."""
    items: list[SuggestionResponse]
    total: int = Field(..., ge=0, description="Total de sugestões")
    page: int = Field(..., ge=1, description="Página atual")
    limit: int = Field(..., ge=1, le=100, description="Items por página")
    has_next: bool = Field(..., description="Tem próxima página")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 8,
                "page": 1,
                "limit": 10,
                "has_next": False
            }
        }


class SuggestionStatsResponse(BaseModel):
    """Schema de resposta de estatísticas de sugestões."""
    total: int = Field(..., ge=0, description="Total de sugestões")
    pending: int = Field(..., ge=0, description="Sugestões pendentes")
    applied: int = Field(..., ge=0, description="Sugestões aplicadas")
    dismissed: int = Field(..., ge=0, description="Sugestões dismissadas")
    acceptance_rate: float = Field(..., ge=0, le=100, description="Taxa de aceitação (%)")
    by_type: dict[str, int] = Field(default_factory=dict, description="Contagem por tipo")
    recent_suggestions: list[SuggestionResponse] = Field(default_factory=list, description="5 sugestões mais recentes")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 20,
                "pending": 3,
                "applied": 12,
                "dismissed": 5,
                "acceptance_rate": 70.59,
                "by_type": {
                    "compensation": 15,
                    "reduce_next_week": 5
                },
                "recent_suggestions": []
            }
        }


class SuggestionFilters(BaseModel):
    """Schema para filtros de listagem de sugestões."""
    type: Optional[SuggestionType] = Field(default=None, description="Filtrar por tipo")
    status: Optional[SuggestionStatus] = Field(default=None, description="Filtrar por status")
    origin_session_id: Optional[int] = Field(default=None, gt=0, description="Filtrar por sessão origem")
    start_date: Optional[datetime] = Field(default=None, description="Data início (created_at)")
    end_date: Optional[datetime] = Field(default=None, description="Data fim (created_at)")

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        """Valida que end_date >= start_date."""
        if v and info.data.get('start_date') and v < info.data['start_date']:
            raise ValueError('end_date deve ser maior ou igual a start_date')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "type": "compensation",
                "status": "pending",
                "start_date": "2025-01-01T00:00:00",
                "end_date": "2025-01-31T23:59:59"
            }
        }
