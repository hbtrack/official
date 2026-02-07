"""
Schemas Pydantic para microciclos de treinamento (Training Microcycles).

Baseado em TRAINNIG.MD:
- Microciclo: planejamento semanal de treinos
- Armazena focos planejados (intenção)
- Base para cálculo de desvios (planejado vs executado)

Regras:
- week_start < week_end
- Soma dos focos planejados ≤ 120
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict


class TrainingMicrocycleBase(BaseModel):
    """Campos compartilhados de microciclo de treinamento."""
    team_id: UUID = Field(..., description="ID da equipe")
    week_start: date = Field(..., description="Início da semana (segunda)")
    week_end: date = Field(..., description="Fim da semana (domingo)")
    cycle_id: Optional[UUID] = Field(None, description="ID do mesociclo (opcional)")

    # Focos planejados (percentuais 0-100)
    planned_focus_attack_positional_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual planejado de foco em ataque posicionado (0-100)"
    )
    planned_focus_defense_positional_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual planejado de foco em defesa posicionada (0-100)"
    )
    planned_focus_transition_offense_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual planejado de foco em transição ofensiva (0-100)"
    )
    planned_focus_transition_defense_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual planejado de foco em transição defensiva (0-100)"
    )
    planned_focus_attack_technical_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual planejado de foco em ataque técnico (0-100)"
    )
    planned_focus_defense_technical_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual planejado de foco em defesa técnica (0-100)"
    )
    planned_focus_physical_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual planejado de foco em treino físico (0-100)"
    )

    planned_weekly_load: Optional[int] = Field(
        None, gt=0,
        description="Carga planejada da semana (RPE × minutos estimado)"
    )
    microcycle_type: Optional[str] = Field(
        None,
        description="Tipo de microciclo: carga_alta, recuperacao, pre_jogo, etc."
    )
    notes: Optional[str] = Field(None, description="Observações do planejamento")

    @field_validator('week_end')
    @classmethod
    def validate_dates(cls, v, info):
        """Valida que week_end seja posterior a week_start."""
        if 'week_start' in info.data and v <= info.data['week_start']:
            raise ValueError('week_end deve ser posterior a week_start')
        return v

    def _get_focus_total(self, info) -> float:
        """Calcula soma total dos focos planejados."""
        total = 0.0
        focus_fields = [
            'planned_focus_attack_positional_pct',
            'planned_focus_defense_positional_pct',
            'planned_focus_transition_offense_pct',
            'planned_focus_transition_defense_pct',
            'planned_focus_attack_technical_pct',
            'planned_focus_defense_technical_pct',
            'planned_focus_physical_pct',
        ]

        for field in focus_fields:
            val = info.data.get(field)
            if val is not None:
                total += float(val)

        return total

    @field_validator('planned_focus_physical_pct')
    @classmethod
    def validate_focus_total(cls, v, info):
        """Valida que soma dos focos não ultrapasse 120."""
        # Calcula total incluindo todos os campos
        total = 0.0
        focus_fields = [
            'planned_focus_attack_positional_pct',
            'planned_focus_defense_positional_pct',
            'planned_focus_transition_offense_pct',
            'planned_focus_transition_defense_pct',
            'planned_focus_attack_technical_pct',
            'planned_focus_defense_technical_pct',
        ]

        for field in focus_fields:
            val_field = info.data.get(field)
            if val_field is not None:
                total += float(val_field)

        if v is not None:
            total += float(v)

        if total > 120:
            raise ValueError(f'Soma dos focos não pode ultrapassar 120 (total: {total:.2f})')

        return v


class TrainingMicrocycleCreate(TrainingMicrocycleBase):
    """Schema para criação de microciclo de treinamento."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "team_id": "123e4567-e89b-12d3-a456-426614174000",
                "week_start": "2026-02-03",
                "week_end": "2026-02-09",
                "cycle_id": "123e4567-e89b-12d3-a456-426614174001",
                "planned_focus_attack_positional_pct": 30,
                "planned_focus_defense_positional_pct": 25,
                "planned_focus_transition_offense_pct": 15,
                "planned_focus_transition_defense_pct": 15,
                "planned_focus_attack_technical_pct": 5,
                "planned_focus_defense_technical_pct": 5,
                "planned_focus_physical_pct": 5,
                "planned_weekly_load": 2500,
                "microcycle_type": "carga_alta"
            }
        }
    )


class TrainingMicrocycleUpdate(BaseModel):
    """Schema para atualização de microciclo de treinamento."""
    planned_focus_attack_positional_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    planned_focus_defense_positional_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    planned_focus_transition_offense_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    planned_focus_transition_defense_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    planned_focus_attack_technical_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    planned_focus_defense_technical_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    planned_focus_physical_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    planned_weekly_load: Optional[int] = Field(None, gt=0)
    microcycle_type: Optional[str] = None
    notes: Optional[str] = None


class TrainingMicrocycleResponse(TrainingMicrocycleBase):
    """Schema de resposta para microciclo de treinamento."""
    id: UUID
    organization_id: UUID
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TrainingMicrocycleWithSessions(TrainingMicrocycleResponse):
    """Schema de resposta com sessões incluídas."""
    sessions: list["TrainingSessionResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Import para referência circular
from app.schemas.training_sessions import TrainingSessionResponse

TrainingMicrocycleWithSessions.model_rebuild()
