"""
Schemas para relatórios de treino

Referências RAG:
- R18: Treinos são eventos operacionais
- R22: Dados de treino são métricas operacionais
- RP5: Ausência gera carga = 0
- RP6: Participação gera métricas obrigatórias
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional
from uuid import UUID


class TrainingPerformanceMetrics(BaseModel):
    """Métricas agregadas de um treino (R22, RP6)"""

    # Presença (RP5)
    total_athletes: int = Field(..., description="Total de atletas registrados")
    presentes: int = Field(..., description="Atletas presentes")
    ausentes: int = Field(..., description="Atletas ausentes (RP5: carga = 0)")
    dm: int = Field(..., description="Atletas em DM (dispensados médico)")
    lesionadas: int = Field(..., description="Atletas lesionadas (R13)")
    attendance_rate: float = Field(..., description="Taxa de presença (%)")

    # Carga (R22, RP6)
    avg_minutes: Optional[float] = Field(None, description="Média de minutos (presentes)")
    avg_rpe: Optional[float] = Field(None, description="Média de RPE (presentes)")
    avg_internal_load: Optional[float] = Field(None, description="Média de carga interna (presentes)")
    stddev_internal_load: Optional[float] = Field(None, description="Desvio padrão de carga")

    # Completude de dados
    load_ok_count: int = Field(..., description="Atletas com carga registrada")
    data_completeness_pct: float = Field(..., description="% de dados completos")

    # Wellness pós-treino
    avg_fatigue_after: Optional[float] = Field(None, description="Fadiga média pós-treino (0-10)")
    avg_mood_after: Optional[float] = Field(None, description="Humor médio pós-treino (0-10)")


class TrainingPerformanceReport(BaseModel):
    """Relatório completo de performance de treino (R18, R22)"""

    # Identificação
    session_id: UUID
    organization_id: UUID
    season_id: Optional[UUID] = None
    team_id: Optional[UUID] = None

    # Dados do treino
    session_at: datetime
    main_objective: Optional[str] = None
    planned_load: Optional[int] = Field(None, ge=0, le=10, description="Carga planejada (0-10)")
    group_climate: Optional[int] = Field(None, ge=1, le=5, description="Clima do grupo (1-5)")

    # Métricas agregadas
    metrics: TrainingPerformanceMetrics

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrainingPerformanceFilters(BaseModel):
    """Filtros para relatório de performance de treinos"""

    organization_id: UUID
    season_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    start_date: Optional[date] = Field(None, description="Data inicial (inclusiva)")
    end_date: Optional[date] = Field(None, description="Data final (inclusiva)")
    min_attendance_rate: Optional[float] = Field(None, ge=0, le=100, description="Taxa mínima de presença (%)")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=500)


class TrainingPerformanceTrend(BaseModel):
    """Tendências de performance ao longo do tempo"""

    period: str = Field(..., description="Período (week, month)")
    period_start: date
    period_end: date
    sessions_count: int
    avg_attendance_rate: float
    avg_internal_load: Optional[float] = None
    avg_fatigue: Optional[float] = None
    avg_mood: Optional[float] = None