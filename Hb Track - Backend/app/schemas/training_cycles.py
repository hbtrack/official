"""
Schemas Pydantic para ciclos de treinamento (Training Cycles).

Baseado em TRAINNIG.MD:
- Macrociclo: temporada completa ou fase longa
- Mesociclo: 4-6 semanas (pertence a um macrociclo)

Regras:
- start_date < end_date
- Macrociclo não pode ter parent_cycle_id
- Mesociclo deve ter parent_cycle_id
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict


class TrainingCycleBase(BaseModel):
    """Campos compartilhados de ciclo de treinamento."""
    team_id: UUID = Field(..., description="ID da equipe")
    type: str = Field(..., description="Tipo: 'macro' ou 'meso'", pattern="^(macro|meso)$")
    start_date: date = Field(..., description="Data de início do ciclo")
    end_date: date = Field(..., description="Data de término do ciclo")
    objective: Optional[str] = Field(None, description="Objetivo estratégico do ciclo")
    notes: Optional[str] = Field(None, description="Observações")
    status: str = Field(default='active', description="Status: active, completed, cancelled", pattern="^(active|completed|cancelled)$")
    parent_cycle_id: Optional[UUID] = Field(None, description="ID do macrociclo pai (apenas para mesociclos)")

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Valida que end_date seja posterior a start_date."""
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('end_date deve ser posterior a start_date')
        return v

    @field_validator('parent_cycle_id')
    @classmethod
    def validate_parent_cycle(cls, v, info):
        """Valida regras de parent_cycle_id por tipo."""
        cycle_type = info.data.get('type')

        if cycle_type == 'macro' and v is not None:
            raise ValueError('Macrociclo não pode ter parent_cycle_id')

        if cycle_type == 'meso' and v is None:
            raise ValueError('Mesociclo deve ter parent_cycle_id')

        return v


class TrainingCycleCreate(TrainingCycleBase):
    """Schema para criação de ciclo de treinamento."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "team_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "macro",
                "start_date": "2026-02-01",
                "end_date": "2026-06-30",
                "objective": "Preparação para o campeonato estadual",
                "status": "active"
            }
        }
    )


class TrainingCycleUpdate(BaseModel):
    """Schema para atualização de ciclo de treinamento."""
    objective: Optional[str] = Field(None, description="Objetivo estratégico do ciclo")
    notes: Optional[str] = Field(None, description="Observações")
    status: Optional[str] = Field(None, description="Status: active, completed, cancelled", pattern="^(active|completed|cancelled)$")


class TrainingCycleResponse(TrainingCycleBase):
    """Schema de resposta para ciclo de treinamento."""
    id: UUID
    organization_id: UUID
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TrainingCycleWithMicrocycles(TrainingCycleResponse):
    """Schema de resposta com microciclos incluídos."""
    microcycles: list["TrainingMicrocycleResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Import para referência circular
from app.schemas.training_microcycles import TrainingMicrocycleResponse

TrainingCycleWithMicrocycles.model_rebuild()
