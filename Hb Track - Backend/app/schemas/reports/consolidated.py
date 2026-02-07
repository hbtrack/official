"""
Schemas para relatórios consolidados.

Referências RAG:
- R17: Treinos são eventos operacionais
- R19: Estatísticas primárias vinculadas a jogo + equipe
- R20: Estatísticas agregadas derivadas
- R21: Métricas de treino (carga, PSE, assiduidade)
- RP5: Ausência = carga 0
- RP6: Participação = métricas obrigatórias
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional, List, Generic, TypeVar
from uuid import UUID


# =============================================================================
# PAGINAÇÃO
# =============================================================================

class PaginationMeta(BaseModel):
    """Metadados de paginação."""
    page: int = Field(..., description="Página atual")
    page_size: int = Field(..., description="Itens por página")
    total: int = Field(..., description="Total de itens")
    total_pages: int = Field(..., description="Total de páginas")


# =============================================================================
# ASSIDUIDADE
# =============================================================================

class AthleteAttendanceRecord(BaseModel):
    """Registro de assiduidade por atleta."""
    
    athlete_id: UUID
    athlete_name: str
    
    # Treinos
    total_training_sessions: int = Field(..., description="Total de treinos no período")
    training_sessions_present: int = Field(..., description="Treinos presentes")
    training_sessions_absent: int = Field(..., description="Treinos ausentes")
    training_attendance_rate: float = Field(..., ge=0, le=100, description="Taxa de presença em treinos (%)")
    
    # Jogos
    total_matches: int = Field(..., description="Total de jogos no período")
    matches_played: int = Field(..., description="Jogos jogados")
    matches_not_played: int = Field(..., description="Jogos não jogados (roster mas não jogou)")
    match_participation_rate: float = Field(..., ge=0, le=100, description="Taxa de participação em jogos (%)")
    
    # Combinado
    combined_attendance_rate: float = Field(..., ge=0, le=100, description="Taxa de assiduidade combinada (%)")
    
    model_config = ConfigDict(from_attributes=True)


class AttendanceReportResponse(BaseModel):
    """Resposta do relatório de assiduidade."""
    
    team_id: UUID
    team_name: str
    season_id: Optional[UUID] = None
    season_name: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    
    # Totais gerais
    total_training_sessions: int
    total_matches: int
    
    # Detalhamento por atleta (paginado)
    athletes: List[AthleteAttendanceRecord]
    
    # Paginação
    pagination: Optional[PaginationMeta] = None
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# MINUTOS POR ATLETA
# =============================================================================

class AthleteMinutesRecord(BaseModel):
    """Registro de minutos jogados por atleta."""
    
    athlete_id: UUID
    athlete_name: str
    
    # Minutos em jogos
    total_matches: int = Field(..., description="Total de jogos convocado")
    matches_played: int = Field(..., description="Jogos em que efetivamente jogou")
    matches_started: int = Field(..., description="Jogos em que foi titular")
    total_minutes_played: int = Field(..., description="Total de minutos jogados")
    avg_minutes_per_match: float = Field(..., description="Média de minutos por jogo jogado")
    
    # Minutos em treinos
    total_training_sessions: int = Field(..., description="Total de treinos presentes")
    total_training_minutes: int = Field(..., description="Minutos efetivos de treino")
    avg_training_minutes: float = Field(..., description="Média de minutos por treino")
    
    # Total combinado
    total_activity_minutes: int = Field(..., description="Total de minutos (jogo + treino)")
    
    model_config = ConfigDict(from_attributes=True)


class MinutesReportResponse(BaseModel):
    """Resposta do relatório de minutos."""
    
    team_id: UUID
    team_name: str
    season_id: Optional[UUID] = None
    season_name: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    
    # Detalhamento por atleta (paginado)
    athletes: List[AthleteMinutesRecord]
    
    # Paginação
    pagination: Optional[PaginationMeta] = None
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# CARGA POR PERÍODO
# =============================================================================

class AthleteLoadRecord(BaseModel):
    """Registro de carga por atleta."""
    
    athlete_id: UUID
    athlete_name: str
    
    # Carga de treino (RPE × minutos = carga interna)
    training_load_total: float = Field(..., description="Carga total de treinos (RPE × minutos)")
    training_sessions_count: int = Field(..., description="Número de treinos com carga registrada")
    training_load_avg: float = Field(..., description="Carga média por treino")
    
    # Carga de jogo (minutos jogados)
    match_load_total: float = Field(..., description="Carga total de jogos (minutos)")
    matches_count: int = Field(..., description="Número de jogos")
    match_load_avg: float = Field(..., description="Carga média por jogo")
    
    # Carga combinada
    total_load: float = Field(..., description="Carga total (treino + jogo)")
    avg_daily_load: float = Field(..., description="Carga média diária no período")
    
    # Flags de alerta
    is_overloaded: bool = Field(False, description="Acima do limiar de sobrecarga")
    load_trend: str = Field("stable", description="Tendência: increasing, decreasing, stable")
    
    model_config = ConfigDict(from_attributes=True)


class LoadReportResponse(BaseModel):
    """Resposta do relatório de carga."""
    
    team_id: UUID
    team_name: str
    season_id: Optional[UUID] = None
    season_name: Optional[str] = None
    period_start: date
    period_end: date
    period_days: int
    
    # Limiares configurados
    load_threshold_daily: float = Field(500, description="Limiar de carga diária para alerta")
    load_threshold_weekly: float = Field(3000, description="Limiar de carga semanal para alerta")
    
    # Estatísticas gerais
    team_avg_load: float
    team_total_load: float
    athletes_overloaded_count: int
    
    # Detalhamento por atleta (paginado)
    athletes: List[AthleteLoadRecord]
    
    # Paginação
    pagination: Optional[PaginationMeta] = None
    
    model_config = ConfigDict(from_attributes=True)
