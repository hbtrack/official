"""
Schemas para Analytics de Treino (Step 16).

Response models para endpoints de analytics.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class AnalyticsPeriod(BaseModel):
    """Período de análise."""
    start: str = Field(..., description="Data inicial (ISO format)")
    end: str = Field(..., description="Data final (ISO format)")


class AnalyticsMetrics(BaseModel):
    """Métricas agregadas de analytics."""
    
    # Contadores
    total_sessions: int = Field(..., description="Total de sessões")
    
    # Focos de treino (médias percentuais)
    avg_focus_attack_positional_pct: Optional[float] = Field(None, description="Média % ataque posicional")
    avg_focus_defense_positional_pct: Optional[float] = Field(None, description="Média % defesa posicional")
    avg_focus_transition_offense_pct: Optional[float] = Field(None, description="Média % transição ofensiva")
    avg_focus_transition_defense_pct: Optional[float] = Field(None, description="Média % transição defensiva")
    avg_focus_attack_technical_pct: Optional[float] = Field(None, description="Média % técnica ofensiva")
    avg_focus_defense_technical_pct: Optional[float] = Field(None, description="Média % técnica defensiva")
    avg_focus_physical_pct: Optional[float] = Field(None, description="Média % físico")
    
    # Carga de treino
    avg_rpe: Optional[float] = Field(None, description="Média RPE")
    avg_internal_load: Optional[float] = Field(None, description="Média carga interna")
    total_internal_load: Optional[float] = Field(None, description="Carga interna total acumulada")
    
    # Assiduidade
    attendance_rate: Optional[float] = Field(None, description="Taxa de assiduidade (%)")
    
    # Wellness
    wellness_response_rate_pre: Optional[float] = Field(None, description="Taxa resposta wellness pré (%)")
    wellness_response_rate_post: Optional[float] = Field(None, description="Taxa resposta wellness pós (%)")
    
    # Gamificação
    athletes_with_badges_count: Optional[int] = Field(None, description="Atletas com badges")
    
    # Desvios (threshold dinâmico)
    deviation_count: Optional[int] = Field(None, description="Sessões com desvio acima do threshold")
    threshold_mean: Optional[float] = Field(None, description="Média dos desvios calculados")
    threshold_stddev: Optional[float] = Field(None, description="Desvio padrão dos desvios")


class TeamSummaryResponse(BaseModel):
    """Resposta GET /analytics/team/{teamId}/summary"""
    team_id: str
    period: AnalyticsPeriod
    metrics: AnalyticsMetrics
    calculated_at: str = Field(..., description="Timestamp UTC do cálculo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "123e4567-e89b-12d3-a456-426614174000",
                "period": {
                    "start": "2024-01-01",
                    "end": "2024-01-31"
                },
                "metrics": {
                    "total_sessions": 12,
                    "avg_focus_attack_positional_pct": 35.5,
                    "avg_focus_defense_positional_pct": 25.0,
                    "avg_rpe": 6.5,
                    "total_internal_load": 7800.0,
                    "attendance_rate": 92.5,
                    "wellness_response_rate_pre": 85.0,
                    "deviation_count": 2
                },
                "calculated_at": "2024-01-31T14:30:00Z"
            }
        }


class WeeklyLoadItem(BaseModel):
    """Item de carga semanal."""
    week_start: str = Field(..., description="Início da semana (ISO)")
    week_end: str = Field(..., description="Fim da semana (ISO)")
    microcycle_id: str = Field(..., description="UUID do microciclo")
    total_sessions: int
    total_internal_load: float
    avg_rpe: float
    attendance_rate: float


class WeeklyLoadResponse(BaseModel):
    """Resposta GET /analytics/team/{teamId}/weekly-load"""
    team_id: str
    weeks: int = Field(..., description="Quantidade de semanas analisadas")
    data: list[WeeklyLoadItem]
    
    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "123e4567-e89b-12d3-a456-426614174000",
                "weeks": 4,
                "data": [
                    {
                        "week_start": "2024-01-22",
                        "week_end": "2024-01-28",
                        "microcycle_id": "abc123...",
                        "total_sessions": 3,
                        "total_internal_load": 1950.0,
                        "avg_rpe": 6.5,
                        "attendance_rate": 93.0
                    }
                ]
            }
        }


class DeviationItem(BaseModel):
    """Item de desvio detectado."""
    session_id: str
    session_at: str = Field(..., description="Data da sessão (ISO)")
    planned_rpe: float
    actual_rpe: float
    deviation: float = Field(..., description="Desvio calculado com threshold")
    exceeded_threshold: bool


class DeviationAnalysisResponse(BaseModel):
    """Resposta GET /analytics/team/{teamId}/deviation-analysis"""
    team_id: str
    threshold_multiplier: float = Field(..., description="Multiplicador configurado na equipe")
    period: AnalyticsPeriod
    total_sessions: int
    deviation_count: int = Field(..., description="Sessões que excederam threshold")
    deviations: list[DeviationItem]
    
    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "123e4567-e89b-12d3-a456-426614174000",
                "threshold_multiplier": 2.0,
                "period": {
                    "start": "2024-01-01",
                    "end": "2024-01-31"
                },
                "total_sessions": 12,
                "deviation_count": 2,
                "deviations": [
                    {
                        "session_id": "xyz789...",
                        "session_at": "2024-01-15",
                        "planned_rpe": 5.0,
                        "actual_rpe": 8.0,
                        "deviation": 6.0,
                        "exceeded_threshold": True
                    }
                ]
            }
        }
