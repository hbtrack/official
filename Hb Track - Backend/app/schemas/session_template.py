"""
Schemas para SessionTemplate
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from uuid import UUID

from app.schemas.base import BaseResponseSchema


class FocusValues(BaseModel):
    """Valores dos 7 focos de treino (0-100%)"""
    focus_attack_positional_pct: float = Field(0, ge=0, le=100, description="Ataque Posicional (%)")
    focus_defense_positional_pct: float = Field(0, ge=0, le=100, description="Defesa Posicional (%)")
    focus_transition_offense_pct: float = Field(0, ge=0, le=100, description="Transição Ofensiva (%)")
    focus_transition_defense_pct: float = Field(0, ge=0, le=100, description="Transição Defensiva (%)")
    focus_attack_technical_pct: float = Field(0, ge=0, le=100, description="Técnica Ofensiva (%)")
    focus_defense_technical_pct: float = Field(0, ge=0, le=100, description="Técnica Defensiva (%)")
    focus_physical_pct: float = Field(0, ge=0, le=100, description="Físico (%)")
    
    @field_validator(
        'focus_attack_positional_pct',
        'focus_defense_positional_pct',
        'focus_transition_offense_pct',
        'focus_transition_defense_pct',
        'focus_attack_technical_pct',
        'focus_defense_technical_pct',
        'focus_physical_pct'
    )
    @classmethod
    def round_two_decimals(cls, v: float) -> float:
        """Arredonda para 2 casas decimais"""
        return round(v, 2)


class SessionTemplateCreate(FocusValues):
    """Schema para criar template"""
    name: str = Field(..., min_length=1, max_length=100, description="Nome do template")
    description: Optional[str] = Field(None, max_length=500, description="Descrição do template")
    icon: str = Field("target", description="Ícone do template")
    is_favorite: bool = Field(False, description="Marcar como favorito")
    
    @field_validator('icon')
    @classmethod
    def validate_icon(cls, v: str) -> str:
        """Valida ícone permitido"""
        allowed = ['target', 'activity', 'bar-chart', 'shield', 'zap', 'flame']
        if v not in allowed:
            raise ValueError(f"Icon must be one of {allowed}")
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Valida nome (sem espaços duplicados)"""
        return ' '.join(v.split())
    
    def validate_total_focus(self) -> None:
        """Valida que soma dos focos ≤ 120%"""
        total = (
            self.focus_attack_positional_pct +
            self.focus_defense_positional_pct +
            self.focus_transition_offense_pct +
            self.focus_transition_defense_pct +
            self.focus_attack_technical_pct +
            self.focus_defense_technical_pct +
            self.focus_physical_pct
        )
        if total > 120:
            raise ValueError(f"Total focus cannot exceed 120%. Current: {total:.2f}%")


class SessionTemplateUpdate(BaseModel):
    """Schema para atualizar template (campos opcionais)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = None
    focus_attack_positional_pct: Optional[float] = Field(None, ge=0, le=100)
    focus_defense_positional_pct: Optional[float] = Field(None, ge=0, le=100)
    focus_transition_offense_pct: Optional[float] = Field(None, ge=0, le=100)
    focus_transition_defense_pct: Optional[float] = Field(None, ge=0, le=100)
    focus_attack_technical_pct: Optional[float] = Field(None, ge=0, le=100)
    focus_defense_technical_pct: Optional[float] = Field(None, ge=0, le=100)
    focus_physical_pct: Optional[float] = Field(None, ge=0, le=100)
    is_favorite: Optional[bool] = None
    is_active: Optional[bool] = None
    
    @field_validator('icon')
    @classmethod
    def validate_icon(cls, v: Optional[str]) -> Optional[str]:
        """Valida ícone permitido"""
        if v is not None:
            allowed = ['target', 'activity', 'bar-chart', 'shield', 'zap', 'flame']
            if v not in allowed:
                raise ValueError(f"Icon must be one of {allowed}")
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Valida nome (sem espaços duplicados)"""
        if v is not None:
            return ' '.join(v.split())
        return v


class SessionTemplateResponse(BaseResponseSchema, FocusValues):
    """Schema de resposta com todos os campos"""
    id: UUID
    organization_id: UUID = Field(..., alias="org_id")
    name: str
    description: Optional[str]
    icon: str
    is_favorite: bool
    is_active: bool
    created_by_membership_id: Optional[UUID]
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


class SessionTemplateListResponse(BaseModel):
    """Lista de templates com contador"""
    templates: list[SessionTemplateResponse]
    total: int
    limit: int = 50
    
    model_config = {"from_attributes": True}
