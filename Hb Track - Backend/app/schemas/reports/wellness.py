"""
Schemas para relatórios de prontidão e bem-estar

Referências RAG:
- RP6: Wellness pré e pós-treino obrigatórios
- RP7: Escalas padronizadas (0-10, 1-5)
- RP8: Alertas de sobrecarga e fadiga
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional
from uuid import UUID


class WellnessSummaryMetrics(BaseModel):
    """Métricas agregadas de bem-estar"""

    # Pré-treino (prontidão)
    avg_sleep_hours: Optional[float] = Field(None, description="Média de horas de sono")
    avg_sleep_quality: Optional[float] = Field(None, ge=1, le=5, description="Qualidade média de sono (1-5)")
    avg_fatigue_pre: Optional[float] = Field(None, ge=0, le=10, description="Fadiga média pré-treino (0-10)")
    avg_stress: Optional[float] = Field(None, ge=0, le=10, description="Estresse médio (0-10)")
    avg_muscle_soreness: Optional[float] = Field(None, ge=0, le=10, description="Dor muscular média (0-10)")

    # Pós-treino (resposta)
    avg_fatigue_after: Optional[float] = Field(None, ge=0, le=10, description="Fadiga média pós-treino (0-10)")
    avg_mood_after: Optional[float] = Field(None, ge=0, le=10, description="Humor médio pós-treino (0-10)")

    # Alertas (RP8)
    athletes_high_fatigue: int = Field(0, description="Atletas com fadiga alta (> 7)")
    athletes_poor_sleep: int = Field(0, description="Atletas com sono ruim (< 6h ou qualidade < 3)")
    athletes_high_stress: int = Field(0, description="Atletas com estresse alto (> 7)")

    # Completude de dados
    total_athletes: int = Field(..., description="Total de atletas")
    athletes_with_wellness: int = Field(..., description="Atletas com dados de wellness")
    data_completeness_pct: float = Field(..., description="% de dados completos")


class WellnessSummaryReport(BaseModel):
    """Relatório de resumo de bem-estar (RP6, RP7, RP8)"""

    # Identificação
    organization_id: UUID
    season_id: Optional[UUID] = None
    team_id: Optional[UUID] = None

    # Período
    start_date: date
    end_date: date

    # Métricas
    metrics: WellnessSummaryMetrics

    model_config = ConfigDict(from_attributes=True)


class WellnessSummaryFilters(BaseModel):
    """Filtros para relatório de bem-estar"""

    organization_id: UUID
    season_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    start_date: Optional[date] = Field(None, description="Data inicial (inclusiva)")
    end_date: Optional[date] = Field(None, description="Data final (inclusiva)")