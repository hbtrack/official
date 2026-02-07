"""
Schemas para análises de correlação treino → jogo (/statistics/teams).

Conforme especificação em eststisticas_equipes, estes schemas suportam o endpoint
/reports/team-training-game-correlation que responde à pergunta estratégica:

"O que do treino está (ou não) se traduzindo em performance de jogo?"

Referências RAG:
- Especificação: eststisticas_equipes (linhas 1780-1950)
- RAG/IMPLEMENTACAO_FOCOS_TREINO.md
"""

from datetime import date
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ============================================================================
# CONTEXT
# ============================================================================

class CorrelationContext(BaseModel):
    """Contexto da análise de correlação."""
    
    team_id: UUID = Field(..., description="ID da equipe analisada")
    team_name: str = Field(..., description="Nome da equipe")
    season_id: UUID = Field(..., description="ID da temporada")
    season_name: str = Field(..., description="Nome da temporada")
    competition_id: Optional[UUID] = Field(None, description="ID da competição (opcional)")
    competition_name: Optional[str] = Field(None, description="Nome da competição")
    period: str = Field(..., description="Período analisado (ex: 'últimos 5 jogos')")
    training_window_days: int = Field(..., description="Janela de treino pré-jogo (dias)")
    analysis_date: date = Field(..., description="Data da análise")


# ============================================================================
# SUMMARY
# ============================================================================

class CorrelationSummary(BaseModel):
    """Resumo executivo da correlação."""
    
    total_games: int = Field(..., description="Total de jogos analisados")
    total_training_sessions: int = Field(..., description="Total de treinos na janela")
    avg_training_load: float = Field(..., description="Carga média de treino (0-10)")
    avg_game_efficiency: float = Field(..., description="Eficiência média em jogos (%)")
    correlation_strength: str = Field(
        ...,
        description="Força da correlação: 'forte' | 'moderada' | 'fraca' | 'insuficiente'"
    )


# ============================================================================
# TRAINING FOCUS DISTRIBUTION (7 focos individuais)
# ============================================================================

class TrainingFocusDistribution(BaseModel):
    """Distribuição percentual dos 7 focos de treino."""
    
    attack_positional: float = Field(..., ge=0, le=100, description="% Ataque posicionado")
    defense_positional: float = Field(..., ge=0, le=100, description="% Defesa posicionada")
    transition_offense: float = Field(..., ge=0, le=100, description="% Transição ofensiva")
    transition_defense: float = Field(..., ge=0, le=100, description="% Transição defensiva")
    attack_technical: float = Field(..., ge=0, le=100, description="% Ataque técnico")
    defense_technical: float = Field(..., ge=0, le=100, description="% Defesa técnica")
    physical: float = Field(..., ge=0, le=100, description="% Preparação física")


# ============================================================================
# CONTENT TRANSLATION (macroblocks)
# ============================================================================

class FocusBreakdown(BaseModel):
    """Detalhamento de focos dentro de um macroblock."""
    
    attack_positional: Optional[float] = Field(None, description="% Ataque posicionado")
    attack_technical: Optional[float] = Field(None, description="% Ataque técnico")
    transition_offense: Optional[float] = Field(None, description="% Transição ofensiva")
    defense_positional: Optional[float] = Field(None, description="% Defesa posicionada")
    defense_technical: Optional[float] = Field(None, description="% Defesa técnica")
    transition_defense: Optional[float] = Field(None, description="% Transição defensiva")
    physical: Optional[float] = Field(None, description="% Preparação física")


class ContentTranslationMacro(BaseModel):
    """Mapeamento de foco de treino → eficiência de jogo para um macroblock."""
    
    training_focus_pct: float = Field(
        ...,
        ge=0,
        le=120,
        description="% total de foco no treino para este macroblock"
    )
    game_efficiency: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Eficiência de jogo neste macroblock (%)"
    )
    focus_breakdown: Optional[FocusBreakdown] = Field(
        None,
        description="Detalhamento dos focos que compõem este macroblock"
    )


# ============================================================================
# LOAD VS PERFORMANCE (scatter plot)
# ============================================================================

class LoadVsPerformancePoint(BaseModel):
    """Ponto no gráfico de dispersão carga × eficiência."""
    
    game_id: UUID = Field(..., description="ID do jogo")
    game_date: date = Field(..., description="Data do jogo")
    avg_training_load: float = Field(..., description="Carga média de treino (0-10)")
    game_efficiency: float = Field(..., description="Eficiência de jogo (%)")


class LoadVsPerformance(BaseModel):
    """Dados para gráfico de dispersão carga de treino × performance de jogo."""
    
    points: List[LoadVsPerformancePoint] = Field(
        default_factory=list,
        description="Pontos do scatter plot"
    )
    trend: Optional[str] = Field(
        None,
        description="Tendência: 'positiva' | 'negativa' | 'neutra'"
    )


# ============================================================================
# CONSISTENCY
# ============================================================================

class Consistency(BaseModel):
    """Métricas de consistência treino → jogo."""
    
    training_load_variability: float = Field(
        ...,
        description="Desvio padrão da carga de treino"
    )
    game_performance_variability: float = Field(
        ...,
        description="Desvio padrão da eficiência de jogo"
    )
    consistency_score: str = Field(
        ...,
        description="Score qualitativo: 'alta' | 'média' | 'baixa'"
    )


# ============================================================================
# INSIGHTS
# ============================================================================

class Insights(BaseModel):
    """Insights interpretativos gerados pelo backend."""
    
    works: List[str] = Field(
        default_factory=list,
        description="O que está funcionando (foco alto + eficiência alta)"
    )
    adjust: List[str] = Field(
        default_factory=list,
        description="O que precisa ajustar (foco médio ou eficiência média)"
    )
    avoid: List[str] = Field(
        default_factory=list,
        description="O que não está funcionando (foco baixo + eficiência baixa)"
    )


# ============================================================================
# MAIN RESPONSE
# ============================================================================

class TeamTrainingGameCorrelationResponse(BaseModel):
    """
    Resposta completa do endpoint /reports/team-training-game-correlation.
    
    Estrutura canônica conforme eststisticas_equipes (linhas 1785-1918).
    Backend entrega dados interpretados; frontend apenas renderiza.
    """
    
    context: CorrelationContext = Field(
        ...,
        description="Contexto da análise (equipe, temporada, período)"
    )
    summary: CorrelationSummary = Field(
        ...,
        description="Resumo executivo da correlação"
    )
    training_focus_distribution: TrainingFocusDistribution = Field(
        ...,
        description="Distribuição dos 7 focos de treino (%)"
    )
    content_translation: Dict[str, ContentTranslationMacro] = Field(
        ...,
        description="Mapeamento treino → jogo por macroblock (attack/defense/physical)"
    )
    load_vs_performance: LoadVsPerformance = Field(
        ...,
        description="Scatter plot carga × eficiência"
    )
    consistency: Consistency = Field(
        ...,
        description="Métricas de consistência"
    )
    insights: Insights = Field(
        ...,
        description="Insights interpretativos (works/adjust/avoid)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "context": {
                    "team_id": "123e4567-e89b-12d3-a456-426614174000",
                    "team_name": "Sub-16 Masculino",
                    "season_id": "223e4567-e89b-12d3-a456-426614174000",
                    "season_name": "2026",
                    "competition_id": "323e4567-e89b-12d3-a456-426614174000",
                    "competition_name": "Campeonato Estadual",
                    "period": "últimos 5 jogos",
                    "training_window_days": 7,
                    "analysis_date": "2026-01-04"
                },
                "summary": {
                    "total_games": 5,
                    "total_training_sessions": 18,
                    "avg_training_load": 7.2,
                    "avg_game_efficiency": 68.5,
                    "correlation_strength": "moderada"
                },
                "training_focus_distribution": {
                    "attack_positional": 25.5,
                    "defense_positional": 20.0,
                    "transition_offense": 15.3,
                    "transition_defense": 12.7,
                    "attack_technical": 10.0,
                    "defense_technical": 8.5,
                    "physical": 8.0
                },
                "content_translation": {
                    "attack": {
                        "training_focus_pct": 50.8,
                        "game_efficiency": 72.5,
                        "focus_breakdown": {
                            "attack_positional": 25.5,
                            "attack_technical": 10.0,
                            "transition_offense": 15.3
                        }
                    },
                    "defense": {
                        "training_focus_pct": 41.2,
                        "game_efficiency": 65.2,
                        "focus_breakdown": {
                            "defense_positional": 20.0,
                            "defense_technical": 8.5,
                            "transition_defense": 12.7
                        }
                    },
                    "physical": {
                        "training_focus_pct": 8.0,
                        "game_efficiency": None,
                        "focus_breakdown": {
                            "physical": 8.0
                        }
                    }
                },
                "load_vs_performance": {
                    "points": [
                        {
                            "game_id": "423e4567-e89b-12d3-a456-426614174000",
                            "game_date": "2025-12-15",
                            "avg_training_load": 7.5,
                            "game_efficiency": 75.2
                        }
                    ],
                    "trend": "positiva"
                },
                "consistency": {
                    "training_load_variability": 1.2,
                    "game_performance_variability": 8.5,
                    "consistency_score": "alta"
                },
                "insights": {
                    "works": [
                        "Ataque: foco alto (50.8%) com eficiência elevada (72.5%)"
                    ],
                    "adjust": [
                        "Defesa: considerar ajustar dedicação (foco 41.2%, eficiência 65.2%)"
                    ],
                    "avoid": []
                }
            }
        }
    }
