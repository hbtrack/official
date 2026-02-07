"""
Schemas para relatórios de gerenciamento de lesões

Referências RAG:
- R13: Estados de atleta (lesionada)
- R14: Impacto de estados em participação
- RP7: Rastreamento de casos médicos
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional
from uuid import UUID


class MedicalCasesSummaryMetrics(BaseModel):
    """Métricas agregadas de casos médicos"""

    # Contadores
    total_cases: int = Field(..., description="Total de casos médicos")
    active_cases: int = Field(..., description="Casos ativos")
    resolved_cases: int = Field(..., description="Casos resolvidos")

    # Razões (top 5)
    top_reasons: dict[str, int] = Field(default_factory=dict, description="Razões mais comuns")

    # Atletas afetadas
    athletes_affected: int = Field(..., description="Atletas com casos ativos")
    athletes_with_history: int = Field(..., description="Atletas com histórico médico")

    # Duração média
    avg_duration_days: Optional[float] = Field(None, description="Duração média de casos resolvidos (dias)")
    median_duration_days: Optional[int] = Field(None, description="Mediana de duração (dias)")


class MedicalCasesReport(BaseModel):
    """Relatório de casos médicos (R13, R14, RP7)"""

    # Identificação
    organization_id: UUID
    season_id: Optional[UUID] = None
    team_id: Optional[UUID] = None

    # Período
    start_date: date
    end_date: date

    # Métricas
    metrics: MedicalCasesSummaryMetrics

    model_config = ConfigDict(from_attributes=True)


class MedicalCasesFilters(BaseModel):
    """Filtros para relatório de casos médicos"""

    organization_id: UUID
    season_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    start_date: Optional[date] = Field(None, description="Data inicial (inclusiva)")
    end_date: Optional[date] = Field(None, description="Data final (inclusiva)")
    status: Optional[str] = Field(None, pattern="^(ativo|resolvido)$", description="Status do caso")