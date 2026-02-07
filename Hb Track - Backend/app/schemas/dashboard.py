"""
Schemas para o Dashboard Agregado

Endpoint único que retorna todos os dados necessários para o dashboard
em uma única requisição, reduzindo latência e carga no servidor.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID


# =============================================================================
# SEÇÃO: ATLETAS
# =============================================================================

class DashboardAthleteStats(BaseModel):
    """Estatísticas resumidas de atletas"""
    total: int = Field(..., description="Total de atletas registrados")
    ativas: int = Field(..., description="Atletas com estado 'ativa'")
    lesionadas: int = Field(..., description="Atletas com estado 'lesionada'")
    dispensadas: int = Field(..., description="Atletas com estado 'dispensada'")
    dm: int = Field(0, description="Atletas em DM")


# =============================================================================
# SEÇÃO: TREINOS
# =============================================================================

class DashboardTrainingSession(BaseModel):
    """Treino recente resumido"""
    session_id: UUID
    session_at: datetime
    main_objective: Optional[str] = None
    team_name: Optional[str] = None
    presentes: int = 0
    total_athletes: int = 0
    attendance_rate: float = 0.0
    avg_internal_load: Optional[float] = None


class DashboardTrainingStats(BaseModel):
    """Estatísticas agregadas de treinos"""
    total_sessions: int = Field(0, description="Total de sessões no período")
    avg_attendance_rate: float = Field(0.0, description="Taxa média de presença (%)")
    avg_internal_load: float = Field(0.0, description="Carga interna média")
    recent_sessions: list[DashboardTrainingSession] = Field(
        default_factory=list,
        description="Últimas sessões de treino"
    )


class DashboardTrainingTrend(BaseModel):
    """Tendência de treino por período"""
    period_start: date
    period_label: str  # "Sem 1", "Sem 2", etc
    sessions_count: int = 0
    avg_attendance: float = 0.0
    avg_load: float = 0.0


# =============================================================================
# SEÇÃO: JOGOS/PARTIDAS
# =============================================================================

class DashboardRecentMatch(BaseModel):
    """Jogo recente resumido"""
    match_id: UUID
    match_at: datetime
    opponent_name: Optional[str] = None
    is_home: bool = True
    our_score: Optional[int] = None
    opponent_score: Optional[int] = None
    result: Optional[str] = None  # "V", "E", "D"


class DashboardNextMatch(BaseModel):
    """Próximo jogo agendado"""
    match_id: UUID
    match_at: datetime
    opponent_name: Optional[str] = None
    location: Optional[str] = None
    is_home: bool = True


class DashboardMatchStats(BaseModel):
    """Estatísticas de jogos"""
    total_matches: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_scored: int = 0
    goals_conceded: int = 0
    recent_matches: list[DashboardRecentMatch] = Field(default_factory=list)
    next_match: Optional[DashboardNextMatch] = None


# =============================================================================
# SEÇÃO: WELLNESS/PRONTIDÃO
# =============================================================================

class DashboardWellnessStats(BaseModel):
    """Médias de wellness da equipe"""
    avg_sleep_quality: float = Field(0.0, ge=0, le=5)
    avg_fatigue: float = Field(0.0, ge=0, le=5)
    avg_stress: float = Field(0.0, ge=0, le=5)
    avg_mood: float = Field(0.0, ge=0, le=5)
    avg_soreness: float = Field(0.0, ge=0, le=5)
    readiness_score: float = Field(0.0, ge=0, le=100, description="Score de prontidão 0-100")
    athletes_reported: int = Field(0, description="Atletas que reportaram hoje")
    athletes_at_risk: int = Field(0, description="Atletas com indicadores preocupantes")


# =============================================================================
# SEÇÃO: MEDICAL/LESÕES
# =============================================================================

class DashboardMedicalStats(BaseModel):
    """Estatísticas médicas"""
    active_cases: int = Field(0, description="Casos médicos ativos")
    recovering: int = Field(0, description="Atletas em recuperação")
    cleared_this_week: int = Field(0, description="Liberados esta semana")
    avg_days_out: float = Field(0.0, description="Média de dias fora por lesão")


# =============================================================================
# SEÇÃO: ALERTAS
# =============================================================================

class DashboardAlert(BaseModel):
    """Alerta para o dashboard"""
    alert_id: UUID
    severity: str = Field(..., pattern="^(info|warning|critical)$")
    title: str
    message: str
    created_at: datetime
    athlete_id: Optional[UUID] = None
    athlete_name: Optional[str] = None


# =============================================================================
# SEÇÃO: PRÓXIMOS EVENTOS
# =============================================================================

class DashboardNextTraining(BaseModel):
    """Próximo treino agendado"""
    session_id: Optional[UUID] = None
    session_at: Optional[datetime] = None
    main_objective: Optional[str] = None
    team_name: Optional[str] = None


# =============================================================================
# RESPOSTA AGREGADA
# =============================================================================

class DashboardSummaryResponse(BaseModel):
    """
    Resposta completa do dashboard em uma única requisição.
    
    Cache: TTL 60-120s por team_id + season_id
    """
    # Metadados
    team_id: Optional[UUID] = None
    team_name: Optional[str] = None
    season_id: Optional[UUID] = None
    season_name: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    cache_ttl_seconds: int = Field(default=120)
    
    # Dados agregados
    athletes: DashboardAthleteStats
    training: DashboardTrainingStats
    training_trends: list[DashboardTrainingTrend] = Field(default_factory=list)
    matches: DashboardMatchStats
    wellness: DashboardWellnessStats
    medical: DashboardMedicalStats
    alerts: list[DashboardAlert] = Field(default_factory=list, max_length=10)
    
    # Próximos eventos
    next_training: Optional[DashboardNextTraining] = None
    next_match: Optional[DashboardNextMatch] = None

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "123e4567-e89b-12d3-a456-426614174000",
                "team_name": "Sub-15 Feminino",
                "generated_at": "2026-01-01T12:00:00Z",
                "cache_ttl_seconds": 120,
                "athletes": {
                    "total": 25,
                    "ativas": 22,
                    "lesionadas": 2,
                    "dispensadas": 1,
                    "dm": 0
                },
                "training": {
                    "total_sessions": 48,
                    "avg_attendance_rate": 87.5,
                    "avg_internal_load": 420.0,
                    "recent_sessions": []
                }
            }
        }
