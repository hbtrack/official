"""
Training Alerts Schemas - Step 18

Pydantic schemas para validação de API relacionadas a alertas de treinamento.
"""

from datetime import datetime
from typing import Optional, Literal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class AlertType(str, Enum):
    """Tipos de alerta."""
    WEEKLY_OVERLOAD = "weekly_overload"
    LOW_WELLNESS_RESPONSE = "low_wellness_response"


class AlertSeverity(str, Enum):
    """Severidade do alerta."""
    WARNING = "warning"
    CRITICAL = "critical"


class AlertCreate(BaseModel):
    """Schema para criação de alerta."""
    team_id: UUID = Field(..., description="ID da equipe")
    alert_type: AlertType = Field(..., description="Tipo de alerta")
    severity: AlertSeverity = Field(..., description="Severidade do alerta")
    message: str = Field(..., min_length=10, max_length=500, description="Mensagem do alerta")
    alert_metadata: Optional[dict] = Field(default=None, description="Metadados adicionais (JSON)")

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "550e8400-e29b-41d4-a716-446655440000",
                "alert_type": "weekly_overload",
                "severity": "critical",
                "message": "Sobrecarga semanal detectada: 1850% (limite 1200%). Risco de overtraining.",
                "alert_metadata": {
                    "total_load": 1850,
                    "threshold": 1200,
                    "week_start": "2025-01-20",
                    "sessions_count": 5
                }
            }
        }


class AlertUpdate(BaseModel):
    """Schema para atualização de alerta (dismiss)."""
    dismissed_by_user_id: UUID = Field(..., description="ID do usuário que dismissou o alerta")

    class Config:
        json_schema_extra = {
            "example": {
                "dismissed_by_user_id": "550e8400-e29b-41d4-a716-446655440001"
            }
        }


class AlertResponse(BaseModel):
    """Schema de resposta de alerta."""
    id: int
    team_id: int
    alert_type: str
    severity: str
    message: str
    alert_metadata: Optional[dict]
    triggered_at: datetime
    dismissed_at: Optional[datetime]
    dismissed_by_user_id: Optional[int]
    
    # Computed properties
    is_active: bool
    is_dismissed: bool
    is_critical: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "team_id": 1,
                "alert_type": "weekly_overload",
                "severity": "critical",
                "message": "Sobrecarga semanal detectada: 1850% (limite 1200%)",
                "alert_metadata": {
                    "total_load": 1850,
                    "threshold": 1200,
                    "week_start": "2025-01-20"
                },
                "triggered_at": "2025-01-27T23:00:00",
                "dismissed_at": None,
                "dismissed_by_user_id": None,
                "is_active": True,
                "is_dismissed": False,
                "is_critical": True
            }
        }


class AlertListResponse(BaseModel):
    """Schema de resposta paginada de alertas."""
    items: list[AlertResponse]
    total: int = Field(..., ge=0, description="Total de alertas")
    page: int = Field(..., ge=1, description="Página atual")
    limit: int = Field(..., ge=1, le=100, description="Items por página")
    has_next: bool = Field(..., description="Tem próxima página")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 15,
                "page": 1,
                "limit": 10,
                "has_next": True
            }
        }


class AlertStatsResponse(BaseModel):
    """Schema de resposta de estatísticas de alertas."""
    total: int = Field(..., ge=0, description="Total de alertas")
    active: int = Field(..., ge=0, description="Alertas ativos")
    dismissed: int = Field(..., ge=0, description="Alertas dismissados")
    critical_count: int = Field(..., ge=0, description="Alertas críticos ativos")
    warning_count: int = Field(..., ge=0, description="Alertas de warning ativos")
    by_type: dict[str, int] = Field(default_factory=dict, description="Contagem por tipo")
    recent_alerts: list[AlertResponse] = Field(default_factory=list, description="5 alertas mais recentes")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 25,
                "active": 3,
                "dismissed": 22,
                "critical_count": 1,
                "warning_count": 2,
                "by_type": {
                    "weekly_overload": 15,
                    "low_wellness_response": 10
                },
                "recent_alerts": []
            }
        }


class AlertFilters(BaseModel):
    """Schema para filtros de listagem de alertas."""
    alert_type: Optional[AlertType] = Field(default=None, description="Filtrar por tipo")
    severity: Optional[AlertSeverity] = Field(default=None, description="Filtrar por severidade")
    is_active: Optional[bool] = Field(default=None, description="Filtrar por status ativo")
    start_date: Optional[datetime] = Field(default=None, description="Data início (triggered_at)")
    end_date: Optional[datetime] = Field(default=None, description="Data fim (triggered_at)")

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
                "alert_type": "weekly_overload",
                "severity": "critical",
                "is_active": True,
                "start_date": "2025-01-01T00:00:00",
                "end_date": "2025-01-31T23:59:59"
            }
        }
