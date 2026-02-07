"""
Schemas para alertas do sistema.

Referências RAG:
- R13: Impacto dos estados e flags (injured, suspended_until, load_restricted)
- RP8: Alertas de sobrecarga e fadiga
- R21: Métricas de treino para cálculo de carga
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum


class AlertSeverity(str, Enum):
    """Severidade do alerta."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Tipo de alerta."""
    LOAD_EXCESS = "load_excess"
    INJURY_RETURN = "injury_return"
    FATIGUE_HIGH = "fatigue_high"
    READINESS_LOW = "readiness_low"
    ATTENDANCE_LOW = "attendance_low"


# =============================================================================
# ALERTA DE EXCESSO DE CARGA
# =============================================================================

class LoadExcessAlert(BaseModel):
    """Alerta de excesso de carga."""
    
    athlete_id: UUID
    athlete_name: str
    
    # Métricas de carga
    current_load_7d: float = Field(..., description="Carga dos últimos 7 dias")
    current_load_28d: float = Field(..., description="Carga dos últimos 28 dias")
    avg_load_28d: float = Field(..., description="Média de carga 28 dias")
    acwr: float = Field(..., description="Acute:Chronic Workload Ratio (7d/28d)")
    
    # Limiares
    threshold_load_7d: float = Field(3000, description="Limiar semanal")
    threshold_acwr_high: float = Field(1.5, description="ACWR máximo seguro")
    threshold_acwr_low: float = Field(0.8, description="ACWR mínimo para manutenção")
    
    # Severidade baseada em ACWR
    severity: AlertSeverity
    reason: str = Field(..., description="Motivo do alerta")
    recommendation: str = Field(..., description="Recomendação")
    
    # Flags atuais
    is_load_restricted: bool = Field(False, description="Flag load_restricted ativa")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)


class LoadExcessAlertResponse(BaseModel):
    """Resposta do endpoint de alertas de carga."""
    
    team_id: UUID
    team_name: str
    season_id: Optional[UUID] = None
    
    # Configuração
    threshold_load_7d: float = 3000
    threshold_acwr_high: float = 1.5
    threshold_acwr_low: float = 0.8
    
    # Resumo
    total_athletes: int
    athletes_at_risk: int
    athletes_overloaded: int
    athletes_underloaded: int
    
    # Detalhamento
    alerts: List[LoadExcessAlert]
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# ALERTA DE RETORNO DE LESÃO
# =============================================================================

class InjuryReturnAlert(BaseModel):
    """Alerta de atleta retornando de lesão com carga recente."""
    
    athlete_id: UUID
    athlete_name: str
    
    # Status de lesão
    injured: bool = Field(..., description="Flag injured atual")
    medical_restriction: bool = Field(..., description="Flag medical_restriction atual")
    
    # Informações da lesão
    injury_start_date: Optional[date] = None
    injury_duration_days: Optional[int] = None
    medical_case_reason: Optional[str] = None
    
    # Carga recente
    load_last_7d: float = Field(..., description="Carga últimos 7 dias")
    sessions_last_7d: int = Field(..., description="Sessões últimos 7 dias")
    
    # Análise de retorno
    is_returning: bool = Field(..., description="Está retornando de lesão")
    days_since_return: Optional[int] = None
    recommended_max_load: float = Field(..., description="Carga máxima recomendada no retorno")
    
    severity: AlertSeverity
    reason: str
    recommendation: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)


class InjuryReturnAlertResponse(BaseModel):
    """Resposta do endpoint de alertas de retorno de lesão."""
    
    team_id: UUID
    team_name: str
    season_id: Optional[UUID] = None
    
    # Resumo
    total_athletes: int
    athletes_injured: int
    athletes_returning: int
    athletes_with_restriction: int
    
    # Detalhamento
    alerts: List[InjuryReturnAlert]
    
    model_config = ConfigDict(from_attributes=True)
