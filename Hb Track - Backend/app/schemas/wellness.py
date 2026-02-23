"""
Schemas Pydantic para wellness pré e pós-treino.

## Wellness Pré-Treino (wellness_pre)
Campos baseados na tabela wellness_pre:
- id: UUID PK
- session_id: UUID NOT NULL (FK → training_sessions)
- athlete_id: UUID NOT NULL (FK → athletes)
- organization_id: UUID NOT NULL
- created_by_membership_id: UUID NOT NULL
- sleep_hours: numeric(4,1) CHECK 0-24
- sleep_quality: int CHECK 1-5
- fatigue_pre (payload alias: fatigue): int CHECK 0-10
- stress_level (payload alias: stress/humor): int CHECK 0-10 (semântica inversa: 0=ótimo, 10=pior)
- muscle_soreness: int CHECK 0-10
- pain: boolean DEFAULT false
- pain_level: int CHECK 0-10
- pain_location: text
- notes: text
- created_at/updated_at: timestamptz

Constraint: UNIQUE (session_id, athlete_id)

## Wellness Pós-Treino (wellness_post)
Campos baseados na tabela wellness_post:
- id: UUID PK
- session_id: UUID NOT NULL (FK → training_sessions)
- athlete_id: UUID NOT NULL (FK → athletes)
- organization_id: UUID NOT NULL
- created_by_membership_id: UUID NOT NULL
- session_rpe: int CHECK 0-10 (Rating of Perceived Exertion)
- minutes_effective: int CHECK 0-300
- internal_load: numeric(10,2) CHECK >= 0 (calculado por trigger: minutes_effective × session_rpe)
- fatigue_after: int CHECK 0-10
- mood_after: int CHECK 0-10
- notes: text
- created_at/updated_at: timestamptz

Constraint: UNIQUE (session_id, athlete_id)
"""

# DECISÃO AR_050 (2026-02-22): Manter escala 0-10 para fatigue_pre, stress_level,
# muscle_soreness, pain_level. sleep_quality permanece 1-5 (alinhado PRD).
# PRD Seção 7 US-002 deve ser atualizado em próximo ciclo de PRD sync.
# Ref: docs/hbtrack/ars/drafts/AR_050_wellness_*.md

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


# ==============================================================================
# WELLNESS PRE
# ==============================================================================


class WellnessPreBase(BaseModel):
    """Campos compartilhados de wellness pré-treino."""

    athlete_id: UUID = Field(..., description="ID do atleta")
    organization_id: UUID = Field(..., description="ID da organização")
    created_by_membership_id: Optional[UUID] = Field(
        None, description="ID do membership que criou"
    )
    sleep_hours: Optional[float] = Field(None, ge=0, le=24, description="Horas de sono")
    sleep_quality: Optional[int] = Field(None, ge=1, le=5, description="Qualidade do sono (1-5). 1=péssimo, 5=excelente.")
    fatigue: Optional[int] = Field(
        None,
        ge=0,
        le=10,
        validation_alias=AliasChoices("fatigue", "fatigue_pre"),
        description="Fadiga pré-treino (0-10). 0=sem fadiga, 10=exausto. Campo de banco: fatigue_pre.",
    )
    stress: Optional[int] = Field(
        None,
        ge=0,
        le=10,
        validation_alias=AliasChoices("stress", "stress_level", "humor"),
        description=(
            "Humor/Disposição (proxy stress_level) em escala 0-10, semântica inversa: "
            "0 = muito bem, 10 = muito estressado."
        ),
        json_schema_extra={"x-accepted-aliases": ["stress_level", "humor"]},
    )
    muscle_soreness: Optional[int] = Field(None, ge=0, le=10, description="Dor muscular (0-10). 0=sem dor, 10=dor intensa.")
    pain: bool = Field(False, description="Indica presença de dor")
    pain_level: Optional[int] = Field(None, ge=0, le=10, description="Nível de dor (0-10)")
    pain_location: Optional[str] = Field(None, description="Localização da dor")
    notes: Optional[str] = Field(None, description="Observações")


class WellnessPreCreate(BaseModel):
    """Payload para criação de wellness pré-treino."""

    athlete_id: UUID = Field(..., description="ID do atleta")
    organization_id: UUID = Field(..., description="ID da organização")
    created_by_membership_id: UUID = Field(..., description="ID do membership que criou")
    sleep_hours: Optional[float] = Field(None, ge=0, le=24, description="Horas de sono")
    sleep_quality: Optional[int] = Field(None, ge=1, le=5, description="Qualidade do sono (1-5). 1=péssimo, 5=excelente.")
    fatigue: Optional[int] = Field(
        None,
        ge=0,
        le=10,
        validation_alias=AliasChoices("fatigue", "fatigue_pre"),
        description="Fadiga pré-treino (0-10). 0=sem fadiga, 10=exausto. Campo de banco: fatigue_pre.",
    )
    stress: Optional[int] = Field(
        None,
        ge=0,
        le=10,
        validation_alias=AliasChoices("stress", "stress_level", "humor"),
        description=(
            "Humor/Disposição (proxy stress_level) em escala 0-10, semântica inversa: "
            "0 = muito bem, 10 = muito estressado."
        ),
        json_schema_extra={"x-accepted-aliases": ["stress_level", "humor"]},
    )
    muscle_soreness: Optional[int] = Field(None, ge=0, le=10, description="Dor muscular (0-10). 0=sem dor, 10=dor intensa.")
    pain: bool = Field(False, description="Indica presença de dor")
    pain_level: Optional[int] = Field(None, ge=0, le=10, description="Nível de dor (0-10)")
    pain_location: Optional[str] = Field(None, description="Localização da dor")
    notes: Optional[str] = Field(None, description="Observações")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "athlete_id": "123e4567-e89b-12d3-a456-426614174010",
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_by_membership_id": "123e4567-e89b-12d3-a456-426614174001",
                "sleep_hours": 7.5,
                "sleep_quality": 4,
                "fatigue": 3,
                "stress": 2,
                "muscle_soreness": 4,
                "pain": False,
            }
        }
    )


class WellnessPreUpdate(BaseModel):
    """Payload para atualização de wellness pré-treino."""

    sleep_hours: Optional[float] = Field(None, ge=0, le=24, description="Horas de sono")
    sleep_quality: Optional[int] = Field(None, ge=1, le=5, description="Qualidade do sono (1-5). 1=péssimo, 5=excelente.")
    fatigue: Optional[int] = Field(
        None,
        ge=0,
        le=10,
        validation_alias=AliasChoices("fatigue", "fatigue_pre"),
        description="Fadiga pré-treino (0-10). 0=sem fadiga, 10=exausto. Campo de banco: fatigue_pre.",
    )
    stress: Optional[int] = Field(
        None,
        ge=0,
        le=10,
        validation_alias=AliasChoices("stress", "stress_level", "humor"),
        description=(
            "Humor/Disposição (proxy stress_level) em escala 0-10, semântica inversa: "
            "0 = muito bem, 10 = muito estressado."
        ),
        json_schema_extra={"x-accepted-aliases": ["stress_level", "humor"]},
    )
    muscle_soreness: Optional[int] = Field(None, ge=0, le=10, description="Dor muscular (0-10). 0=sem dor, 10=dor intensa.")
    pain: Optional[bool] = Field(None, description="Indica presença de dor")
    pain_level: Optional[int] = Field(None, ge=0, le=10, description="Nível de dor (0-10)")
    pain_location: Optional[str] = Field(None, description="Localização da dor")
    notes: Optional[str] = Field(None, description="Observações")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fatigue": 4,
                "stress": 3,
                "notes": "Ajustado após revisão",
            }
        }
    )


class WellnessPre(WellnessPreBase):
    """Resposta completa de wellness pré-treino."""

    id: UUID = Field(..., description="ID do registro de wellness pré-treino")
    session_id: UUID = Field(..., description="ID da sessão de treino")
    created_at: datetime = Field(..., description="Data/hora de criação")
    updated_at: datetime = Field(..., description="Data/hora da última atualização")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174030",
                "session_id": "123e4567-e89b-12d3-a456-426614174002",
                "athlete_id": "123e4567-e89b-12d3-a456-426614174010",
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_by_membership_id": "123e4567-e89b-12d3-a456-426614174001",
                "sleep_hours": 7.5,
                "sleep_quality": 4,
                "fatigue": 3,
                "stress": 2,
                "muscle_soreness": 4,
                "pain": False,
                "pain_level": None,
                "pain_location": None,
                "notes": None,
                "created_at": "2025-01-20T09:30:00Z",
                "updated_at": "2025-01-20T09:30:00Z",
            }
        },
    )


# ==============================================================================
# WELLNESS POST
# ==============================================================================


class WellnessPostBase(BaseModel):
    """Campos compartilhados de wellness pós-treino."""

    athlete_id: UUID = Field(..., description="ID do atleta")
    organization_id: UUID = Field(..., description="ID da organização")
    created_by_membership_id: Optional[UUID] = Field(
        None, description="ID do membership que criou"
    )
    session_rpe: Optional[int] = Field(None, ge=0, le=10, description="RPE (Rating of Perceived Exertion) - escala 0-10")
    minutes_effective: Optional[int] = Field(None, ge=0, le=300, description="Duração efetiva do treino em minutos")
    internal_load: Optional[float] = Field(
        None, ge=0, description="Carga interna (minutes_effective × session_rpe) - calculada por trigger"
    )
    fatigue_after: Optional[int] = Field(None, ge=0, le=10, description="Fadiga após treino (0-10)")
    mood_after: Optional[int] = Field(None, ge=0, le=10, description="Humor após treino (0-10)")
    notes: Optional[str] = Field(None, description="Observações")


class WellnessPostCreate(BaseModel):
    """Payload para criação de wellness pós-treino."""

    athlete_id: UUID = Field(..., description="ID do atleta")
    organization_id: UUID = Field(..., description="ID da organização")
    created_by_membership_id: UUID = Field(..., description="ID do membership que criou")
    session_rpe: Optional[int] = Field(None, ge=0, le=10, description="RPE (Rating of Perceived Exertion) - escala 0-10")
    minutes_effective: Optional[int] = Field(None, ge=0, le=300, description="Duração efetiva do treino em minutos")
    internal_load: Optional[float] = Field(
        None, ge=0, description="Opcional - será recalculado se minutes_effective e session_rpe presentes"
    )
    fatigue_after: Optional[int] = Field(None, ge=0, le=10, description="Fadiga após treino (0-10)")
    mood_after: Optional[int] = Field(None, ge=0, le=10, description="Humor após treino (0-10)")
    notes: Optional[str] = Field(None, description="Observações")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "athlete_id": "123e4567-e89b-12d3-a456-426614174010",
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_by_membership_id": "123e4567-e89b-12d3-a456-426614174001",
                "session_rpe": 7,
                "minutes_effective": 60,
                "fatigue_after": 6,
                "mood_after": 7,
            }
        }
    )


class WellnessPostUpdate(BaseModel):
    """Payload para atualização de wellness pós-treino."""

    session_rpe: Optional[int] = Field(None, ge=0, le=10, description="RPE (Rating of Perceived Exertion) - escala 0-10")
    minutes_effective: Optional[int] = Field(None, ge=0, le=300, description="Duração efetiva do treino em minutos")
    internal_load: Optional[float] = Field(
        None, ge=0, description="Recalculado automaticamente quando minutes_effective/session_rpe são alterados"
    )
    fatigue_after: Optional[int] = Field(None, ge=0, le=10, description="Fadiga após treino (0-10)")
    mood_after: Optional[int] = Field(None, ge=0, le=10, description="Humor após treino (0-10)")
    notes: Optional[str] = Field(None, description="Observações")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_rpe": 8,
                "minutes_effective": 75,
                "notes": "Treino estendido",
            }
        }
    )


class WellnessPost(WellnessPostBase):
    """Resposta completa de wellness pós-treino."""

    id: UUID = Field(..., description="ID do registro de wellness pós-treino")
    session_id: UUID = Field(..., description="ID da sessão de treino")
    created_at: datetime = Field(..., description="Data/hora de criação")
    updated_at: datetime = Field(..., description="Data/hora da última atualização")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174040",
                "session_id": "123e4567-e89b-12d3-a456-426614174002",
                "athlete_id": "123e4567-e89b-12d3-a456-426614174010",
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_by_membership_id": "123e4567-e89b-12d3-a456-426614174001",
                "session_rpe": 7,
                "minutes_effective": 60,
                "internal_load": 420.0,
                "fatigue_after": 6,
                "mood_after": 7,
                "notes": None,
                "created_at": "2025-01-20T12:00:00Z",
                "updated_at": "2025-01-20T12:00:00Z",
            }
        },
    )


# ==============================================================================
# WELLNESS STATUS DASHBOARD (para frontend WellnessStatusDashboard)
# ==============================================================================


class WellnessPreData(BaseModel):
    """Dados resumidos do wellness pré-treino para exibição no dashboard."""
    fatigue_level: int = Field(..., description="Nível de fadiga (0-10)")
    stress_level: int = Field(..., description="Nível de estresse (0-10)")
    readiness: Optional[int] = Field(None, description="Prontidão (0-10)")
    filled_at: datetime = Field(..., description="Data/hora do preenchimento")


class WellnessPostData(BaseModel):
    """Dados resumidos do wellness pós-treino para exibição no dashboard."""
    session_rpe: int = Field(..., description="RPE da sessão (0-10)")
    internal_load: Optional[float] = Field(None, description="Carga interna calculada")
    fatigue_after: int = Field(..., description="Fadiga após treino (0-10)")
    filled_at: datetime = Field(..., description="Data/hora do preenchimento")


class WellnessAthleteData(BaseModel):
    """Dados de um atleta no dashboard de wellness."""
    athlete_id: UUID = Field(..., description="ID do atleta")
    athlete_name: str = Field(..., description="Nome do atleta")
    athlete_nickname: Optional[str] = Field(None, description="Apelido do atleta")
    position: Optional[str] = Field(None, description="Posição do atleta")

    status: str = Field(..., description="Status: complete, partial, none, absent")
    has_wellness_pre: bool = Field(..., description="Preencheu wellness pré")
    has_wellness_post: bool = Field(..., description="Preencheu wellness pós")
    is_absent: bool = Field(..., description="Atleta ausente na sessão")

    monthly_response_rate: float = Field(0.0, description="Taxa de resposta mensal (%)")
    has_monthly_badge: bool = Field(False, description="Badge de comprometimento (≥90%)")
    reminders_sent_count: int = Field(0, description="Lembretes enviados no mês")

    wellness_pre: Optional[WellnessPreData] = Field(None, description="Dados do wellness pré")
    wellness_post: Optional[WellnessPostData] = Field(None, description="Dados do wellness pós")


class WellnessSessionStats(BaseModel):
    """Estatísticas agregadas de wellness da sessão."""
    total_athletes: int = Field(..., description="Total de atletas presentes")
    responded_pre: int = Field(..., description="Responderam wellness pré")
    responded_post: int = Field(..., description="Responderam wellness pós")
    response_rate_pre: float = Field(..., description="Taxa de resposta pré (%)")
    response_rate_post: float = Field(..., description="Taxa de resposta pós (%)")

    avg_fatigue_pre: float = Field(0.0, description="Média fadiga pré")
    avg_stress_pre: float = Field(0.0, description="Média stress pré")
    avg_readiness_pre: float = Field(0.0, description="Média prontidão pré")
    avg_rpe_post: float = Field(0.0, description="Média RPE pós")
    avg_internal_load_post: float = Field(0.0, description="Média carga interna pós")

    has_high_fatigue_alert: bool = Field(False, description="Alerta fadiga alta (≥7)")
    has_high_stress_alert: bool = Field(False, description="Alerta stress alto (≥7)")
    has_low_readiness_alert: bool = Field(False, description="Alerta prontidão baixa (≤4)")
    has_high_rpe_alert: bool = Field(False, description="Alerta RPE alto (≥8)")


class WellnessStatusResponse(BaseModel):
    """Resposta completa do endpoint wellness-status."""
    athletes: list[WellnessAthleteData] = Field(..., description="Lista de atletas com status")
    stats: WellnessSessionStats = Field(..., description="Estatísticas agregadas")
