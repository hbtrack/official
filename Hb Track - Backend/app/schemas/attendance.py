"""
Schemas Pydantic para presenças em sessões de treino (Attendance).

Campos baseados na tabela attendance (schema real):
- id: UUID PK
- training_session_id: UUID NOT NULL FK(training_sessions)
- team_registration_id: UUID NOT NULL FK(team_registrations)
- athlete_id: UUID NOT NULL FK(athletes)
- presence_status: VARCHAR(32) NOT NULL CHECK ('present'|'absent')
- minutes_effective: smallint
- comment: text
- source: VARCHAR(32) NOT NULL DEFAULT 'manual'
- participation_type: VARCHAR(32) CHECK ('full'|'partial'|'adapted'|'did_not_train')
- reason_absence: VARCHAR(32) CHECK ('medico'|'escola'|'familiar'|'opcional'|'outro')
- is_medical_restriction: boolean DEFAULT false
- created_at, created_by_user_id, updated_at, deleted_at, deleted_reason

Regras:
- RF10: Podem registrar presença: Dirigentes, Coordenadores e Treinadores
- R22: Dados de treino são métricas operacionais
- R40: Limite temporal de edição
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PresenceStatus(str, Enum):
    """Status de presença conforme banco."""
    PRESENT = "present"
    ABSENT = "absent"


class ParticipationType(str, Enum):
    """Tipo de participação conforme banco."""
    FULL = "full"
    PARTIAL = "partial"
    ADAPTED = "adapted"
    DID_NOT_TRAIN = "did_not_train"


class ReasonAbsence(str, Enum):
    """Motivo de ausência conforme banco."""
    MEDICO = "medico"
    ESCOLA = "escola"
    FAMILIAR = "familiar"
    OPCIONAL = "opcional"
    OUTRO = "outro"


class AttendanceCreate(BaseModel):
    """
    Payload para criação de registro de presença.
    Campos derivados automaticamente: training_session_id (path), team_registration_id (lookup)
    """
    athlete_id: UUID = Field(..., description="ID do atleta")
    team_registration_id: Optional[UUID] = Field(
        default=None,
        description="ID do vínculo ativo (opcional; validado pelo backend)"
    )
    presence_status: PresenceStatus = Field(
        default=PresenceStatus.PRESENT,
        description="Status: 'present' ou 'absent'"
    )
    minutes_effective: Optional[int] = Field(
        default=None,
        ge=0,
        le=180,
        description="Minutos efetivos de treino"
    )
    participation_type: Optional[ParticipationType] = Field(
        default=None,
        description="Tipo de participação"
    )
    reason_absence: Optional[ReasonAbsence] = Field(
        default=None,
        description="Motivo de ausência (se absent)"
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Comentário/observação"
    )
    is_medical_restriction: Optional[bool] = Field(
        default=False,
        description="Flag de restrição médica"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "athlete_id": "123e4567-e89b-12d3-a456-426614174010",
                "presence_status": "present",
                "minutes_effective": 90,
                "participation_type": "full",
                "comment": "Treino normal"
            }
        }
    )


class AttendanceCorrection(BaseModel):
    """
    Payload para correção administrativa de presença.

    Correções são permitidas apenas para:
    - Coordenadores com permissão attendance:correction_write
    - Após fechamento da sessão (R37: ação administrativa auditada)

    Campos correction_by_user_id e correction_at são preenchidos automaticamente.
    """
    presence_status: Optional[PresenceStatus] = Field(
        default=None,
        description="Status de presença corrigido"
    )
    minutes_effective: Optional[int] = Field(
        default=None,
        ge=0,
        le=180,
        description="Minutos efetivos corrigidos"
    )
    participation_type: Optional[ParticipationType] = Field(
        default=None,
        description="Tipo de participação corrigido"
    )
    reason_absence: Optional[ReasonAbsence] = Field(
        default=None,
        description="Motivo de ausência corrigido"
    )
    comment: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Motivo da correção (obrigatório para auditoria)"
    )
    is_medical_restriction: Optional[bool] = Field(
        default=None,
        description="Flag de restrição médica"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "presence_status": "present",
                "minutes_effective": 90,
                "comment": "Correção: atleta estava presente mas não foi registrado corretamente"
            }
        }
    )


class AttendanceUpdate(BaseModel):
    """Payload para atualização de registro de presença."""
    presence_status: Optional[PresenceStatus] = Field(
        default=None,
        description="Status de presença"
    )
    minutes_effective: Optional[int] = Field(
        default=None,
        ge=0,
        le=180,
        description="Minutos efetivos"
    )
    participation_type: Optional[ParticipationType] = Field(
        default=None,
        description="Tipo de participação"
    )
    reason_absence: Optional[ReasonAbsence] = Field(
        default=None,
        description="Motivo de ausência"
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Comentário"
    )
    is_medical_restriction: Optional[bool] = Field(
        default=None,
        description="Flag de restrição médica"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "presence_status": "present",
                "minutes_effective": 85,
                "comment": "Atualizado"
            }
        }
    )


# ============================================================================
# NESTED SCHEMAS (para eager loading response)
# ============================================================================

class AthleteNested(BaseModel):
    """Dados básicos do atleta para response nested."""
    id: UUID = Field(..., description="ID do atleta")
    athlete_name: str = Field(..., description="Nome do atleta")
    athlete_nickname: Optional[str] = Field(default=None, description="Apelido do atleta")
    shirt_number: Optional[int] = Field(default=None, description="Número da camisa")
    state: str = Field(default="ativa", description="Estado do atleta")

    model_config = ConfigDict(from_attributes=True)


class Attendance(BaseModel):
    """Resposta completa de registro de presença."""
    id: UUID = Field(..., description="ID do registro")
    training_session_id: UUID = Field(..., description="ID da sessão de treino")
    team_registration_id: UUID = Field(..., description="ID do team_registration")
    athlete_id: UUID = Field(..., description="ID do atleta")
    presence_status: str = Field(..., description="Status de presença")
    minutes_effective: Optional[int] = Field(default=None, description="Minutos efetivos")
    comment: Optional[str] = Field(default=None, description="Comentário")
    source: str = Field(default="manual", description="Fonte do registro")
    participation_type: Optional[str] = Field(default=None, description="Tipo de participação")
    reason_absence: Optional[str] = Field(default=None, description="Motivo de ausência")
    is_medical_restriction: Optional[bool] = Field(default=False, description="Restrição médica")
    created_at: datetime = Field(..., description="Data/hora de criação")
    created_by_user_id: UUID = Field(..., description="Usuário que criou")
    updated_at: datetime = Field(..., description="Data/hora de atualização")
    # Campos de auditoria para correções (Step 5)
    correction_by_user_id: Optional[UUID] = Field(default=None, description="Usuário que corrigiu")
    correction_at: Optional[datetime] = Field(default=None, description="Data/hora da correção")
    
    # Dados nested (eager loading)
    athlete: Optional[AthleteNested] = Field(default=None, description="Dados do atleta (nested)")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# CARGA / LOAD SCHEMAS
# ============================================================================

class AthleteLoadSummary(BaseModel):
    """Resumo de carga do atleta."""
    athlete_id: UUID
    total_trainings: int = Field(default=0, description="Total de treinos no período")
    total_minutes: int = Field(default=0, description="Total de minutos no período")
    total_presences: int = Field(default=0, description="Total de presenças")
    total_absences: int = Field(default=0, description="Total de ausências")
    attendance_rate: float = Field(default=0.0, description="Taxa de presença (%)")
    avg_minutes_per_session: float = Field(default=0.0, description="Média de minutos por sessão")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "athlete_id": "123e4567-e89b-12d3-a456-426614174010",
                "total_trainings": 20,
                "total_minutes": 1800,
                "total_presences": 18,
                "total_absences": 2,
                "attendance_rate": 90.0,
                "avg_minutes_per_session": 100.0
            }
        }
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174020",
                "session_id": "123e4567-e89b-12d3-a456-426614174002",
                "athlete_id": "123e4567-e89b-12d3-a456-426614174010",
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_by_membership_id": "123e4567-e89b-12d3-a456-426614174001",
                "status": "presente",
                "rpe": 7,
                "internal_load": 420,
                "notes": None,
                "created_at": "2025-01-20T10:00:00Z",
                "updated_at": "2025-01-20T12:00:00Z",
            }
        },
    )
