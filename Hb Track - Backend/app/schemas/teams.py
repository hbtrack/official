"""
Schemas para Team.
Ref: FASE 3 — Contrato Teams
Regras: RF6, RF7, RF8, RDB4
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TeamBase(BaseModel):
    """Response completo de equipe."""
    id: UUID
    organization_id: UUID
    organization_name: Optional[str] = None
    season_id: Optional[UUID] = None
    name: str
    category_id: Optional[int] = None
    gender: Optional[str] = None
    is_our_team: bool = True
    coach_membership_id: Optional[UUID] = None
    created_by_user_id: Optional[UUID] = None  # Quem criou a equipe (owner)
    created_by_membership_id: Optional[UUID] = None  # Membership do criador (auditoria)
    alert_threshold_multiplier: float = 2.0  # Step 15
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    deleted_reason: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class TeamCreate(BaseModel):
    """
    Payload para criação de equipe (RF6).
    
    Regras:
    - RF6: Equipe pertence a uma organização
    - UNIQUE(organization_id, category_id, name)
    """
    name: str = Field(..., min_length=1, max_length=100, description="Nome da equipe")
    category_id: int = Field(..., ge=1, description="ID da categoria (obrigatório)")
    gender: str = Field(..., description="Gênero: 'masculino' ou 'feminino'")
    is_our_team: bool = Field(True, description="Se é nossa equipe ou adversário")
    season_id: Optional[UUID] = Field(None, description="UUID da temporada (opcional)")
    coach_membership_id: Optional[UUID] = Field(
        None, 
        description="UUID do treinador responsável (opcional na criação, pode ser atribuído posteriormente)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "IDEC Cadete",
                "category_id": 1,
                "gender": "feminino",
                "is_our_team": True,
                "coach_membership_id": None
            }
        }
    )


class TeamUpdate(BaseModel):
    """
    Payload para atualização de equipe.
    
    Regras:
    - RF7: Pode alterar coach_membership_id
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category_id: Optional[int] = Field(None, ge=1)
    coach_membership_id: Optional[UUID] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "IDEC Atualizado",
            }
        }
    )


class TeamPaginatedResponse(BaseModel):
    """Response paginado para listagem de equipes."""
    items: list[TeamBase]
    page: int
    limit: int
    total: int


# Schemas auxiliares

class TeamStaffMember(BaseModel):
    """Membro da equipe (staff: dirigente, coordenador, treinador)."""
    id: UUID = Field(..., description="ID do team_membership")
    person_id: UUID
    full_name: str
    role: str = Field(..., description="Papel: dirigente, coordenador, treinador")
    status: str = Field(..., description="Status: ativo, pendente, inativo")
    start_at: datetime = Field(..., description="Data de início do vínculo")
    end_at: Optional[datetime] = Field(None, description="Data de término, NULL se ativo")
    invite_token: Optional[str] = Field(None, description="Token de convite se status=pendente")
    invited_at: Optional[datetime] = Field(None, description="Data do convite")
    resend_count: int = Field(0, description="Número de reenvios (máx 3)")
    can_resend_invite: bool = Field(False, description="Pode reenviar (48h após último envio E resend_count < 3)")

    model_config = ConfigDict(from_attributes=True)


class TeamCoachAssignment(BaseModel):
    """Payload para associação de treinador (RF7)."""
    coach_membership_id: UUID


class TeamCoachUpdate(BaseModel):
    """Payload para reatribuição de treinador (Step 18)."""
    new_coach_membership_id: UUID = Field(..., description="UUID do novo treinador")


class CoachHistoryItem(BaseModel):
    """Item de histórico de coaches (Step 19)."""
    id: UUID = Field(..., description="ID do team_membership")
    person_id: UUID = Field(..., description="ID da pessoa")
    person_name: str = Field(..., description="Nome completo do coach")
    start_at: datetime = Field(..., description="Data de início")
    end_at: Optional[datetime] = Field(None, description="Data de término (NULL se atual)")
    is_current: bool = Field(..., description="Se é o coach atual")
    
    model_config = ConfigDict(from_attributes=True)


class TeamCoachHistoryResponse(BaseModel):
    """Response de histórico de coaches (Step 19)."""
    items: list[CoachHistoryItem]
    total: int


class TeamSoftDelete(BaseModel):
    """Payload para soft delete (RF8/RDB4)."""
    reason: str = Field(..., min_length=1, max_length=500)


class TeamStaffMember(BaseModel):
    """Membro do staff de uma equipe."""
    id: UUID = Field(..., description="ID do org_membership")
    person_id: UUID = Field(..., description="ID da pessoa")
    full_name: str = Field(..., description="Nome completo")
    role: str = Field(..., description="Papel: treinador, etc")
    start_at: Optional[datetime] = Field(None, description="Início do vínculo")
    end_at: Optional[datetime] = Field(None, description="Fim do vínculo (null = ativo)")
    
    model_config = ConfigDict(from_attributes=True)


class TeamStaffResponse(BaseModel):
    """Response de staff de uma equipe."""
    items: list[TeamStaffMember]
    total: int


class TeamSettingsUpdate(BaseModel):
    """
    Payload para atualização de configurações da equipe (Step 15).
    
    Configura threshold de alertas automáticos para o sistema de wellness.
    """
    alert_threshold_multiplier: float = Field(
        ..., 
        ge=1.0, 
        le=3.0, 
        description="Multiplicador de threshold para alertas (1.0-3.0). Valores sugeridos: 1.5 (juvenis sensíveis), 2.0 (adultos padrão), 2.5 (adultos tolerantes)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "alert_threshold_multiplier": 2.0
            }
        }
    )
