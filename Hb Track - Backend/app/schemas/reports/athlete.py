"""
Schemas para relatórios individuais de atleta

Referências RAG:
- R12: Atleta permanente no histórico
- R13/R14: Estados e impactos
- RP4: Escopo de participação
- RP5: Ausência = carga 0
- RP6: Participação = métricas obrigatórias
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional
from uuid import UUID


class AthleteReadinessMetrics(BaseModel):
    """Métricas de prontidão (wellness pré-treino)"""

    avg_sleep_hours: Optional[float] = Field(None, description="Média de horas de sono")
    avg_sleep_quality: Optional[float] = Field(None, ge=1, le=5, description="Qualidade média de sono (1-5)")
    avg_fatigue_pre: Optional[float] = Field(None, ge=0, le=10, description="Fadiga média pré-treino (0-10)")
    avg_stress: Optional[float] = Field(None, ge=0, le=10, description="Estresse médio (0-10)")
    avg_muscle_soreness: Optional[float] = Field(None, ge=0, le=10, description="Dor muscular média (0-10)")

    last_sleep_hours: Optional[float] = None
    last_fatigue: Optional[float] = None


class AthleteTrainingLoadMetrics(BaseModel):
    """Métricas de carga de treino (RP6)"""

    avg_internal_load: Optional[float] = Field(None, description="Carga interna média (RPE × minutos)")
    avg_rpe: Optional[float] = Field(None, ge=0, le=10, description="RPE médio (0-10)")
    avg_minutes: Optional[float] = Field(None, description="Minutos médios por treino")

    load_7d: Optional[float] = Field(None, description="Carga acumulada (7 dias)")
    load_28d: Optional[float] = Field(None, description="Carga acumulada (28 dias)")

    last_internal_load: Optional[float] = None


class AthleteAttendanceMetrics(BaseModel):
    """Métricas de presença (RP5)"""

    total_sessions: int = Field(..., description="Total de treinos")
    sessions_presente: int = Field(..., description="Treinos presentes")
    sessions_ausente: int = Field(..., description="Treinos ausentes (RP5: carga = 0)")
    sessions_dm: int = Field(..., description="Treinos em DM")
    sessions_lesionada: int = Field(..., description="Treinos lesionada (R13)")
    attendance_rate: float = Field(..., description="Taxa de assiduidade (%)")


class AthleteWellnessMetrics(BaseModel):
    """Métricas de bem-estar pós-treino"""

    avg_fatigue_after: Optional[float] = Field(None, ge=0, le=10, description="Fadiga média pós-treino")
    avg_mood_after: Optional[float] = Field(None, ge=0, le=10, description="Humor médio pós-treino")


class AthleteIndividualReport(BaseModel):
    """Relatório individual completo de atleta (R12, R13, R14)"""

    # Identificação
    athlete_id: UUID
    person_id: UUID
    full_name: str
    nickname: Optional[str] = None
    birth_date: Optional[date] = None
    position: Optional[str] = None
    current_age: Optional[int] = None
    expected_category_code: Optional[str] = None

    # Contexto atual
    current_state: str = Field(..., description="Estado atual (R13: ativa, lesionada, dispensada)")
    current_season_id: Optional[UUID] = None
    current_team_id: Optional[UUID] = None
    organization_id: UUID

    # Métricas
    readiness: AthleteReadinessMetrics
    training_load: AthleteTrainingLoadMetrics
    attendance: AthleteAttendanceMetrics
    wellness: AthleteWellnessMetrics

    # Médico
    active_medical_cases: int = Field(..., description="Casos médicos ativos (R13)")

    # Última atividade
    last_session_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AthleteIndividualFilters(BaseModel):
    """Filtros para busca de relatórios individuais"""

    organization_id: UUID
    season_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    state: Optional[str] = Field(None, pattern="^(ativa|lesionada|dispensada)$")
    min_attendance_rate: Optional[float] = Field(None, ge=0, le=100)
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=500)