"""
Service para análises estatísticas de equipes.

Este service implementa as funções de agregação e correlação para o domínio
/statistics/teams, conforme especificação em eststisticas_equipes.

Referências RAG:
- Especificação: eststisticas_equipes (2,199 linhas)
- RAG/IMPLEMENTACAO_FOCOS_TREINO.md
- Pergunta estratégica: "O que do treino está (ou não) se traduzindo em jogo?"

Funções principais:
- aggregate_training_focus: Agrega focos de treino em janela temporal
- compute_content_translation: Mapeia focos → macroblocks (attack/defense/physical)
- compute_correlation_metrics: Calcula correlações treino → jogo
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_, func, text
from sqlalchemy.orm import Session

from app.models.training_session import TrainingSession
from app.models.match import Match

logger = logging.getLogger(__name__)


class TeamAnalyticsService:
    """
    Service de análise estatística para /statistics/teams.
    
    Implementa agregações e correlações conforme especificação canônica.
    Backend entrega dados interpretados; frontend apenas renderiza.
    """

    def __init__(self, db: Session):
        self.db = db

    def aggregate_training_focus(
        self,
        sessions: List[TrainingSession]
    ) -> Dict[str, float]:
        """
        Agrega percentuais de foco de treino em janela temporal.
        
        Retorna médias dos 7 focos individuais, tratando NULLs como 0.
        Usado pelo endpoint /reports/team-training-game-correlation.
        
        Args:
            sessions: Lista de TrainingSession na janela temporal
            
        Returns:
            Dict com 7 chaves:
            - attack_positional: média de focus_attack_positional_pct
            - defense_positional: média de focus_defense_positional_pct
            - transition_offense: média de focus_transition_offense_pct
            - transition_defense: média de focus_transition_defense_pct
            - attack_technical: média de focus_attack_technical_pct
            - defense_technical: média de focus_defense_technical_pct
            - physical: média de focus_physical_pct
            
        Exemplo:
            >>> sessions = [session1, session2, session3]
            >>> result = service.aggregate_training_focus(sessions)
            >>> result
            {
                'attack_positional': 25.5,
                'defense_positional': 20.0,
                'transition_offense': 15.3,
                'transition_defense': 12.7,
                'attack_technical': 10.0,
                'defense_technical': 8.5,
                'physical': 8.0
            }
        """
        if not sessions:
            return {
                "attack_positional": 0.0,
                "defense_positional": 0.0,
                "transition_offense": 0.0,
                "transition_defense": 0.0,
                "attack_technical": 0.0,
                "defense_technical": 0.0,
                "physical": 0.0,
            }

        totals = {
            "attack_positional": 0.0,
            "defense_positional": 0.0,
            "transition_offense": 0.0,
            "transition_defense": 0.0,
            "attack_technical": 0.0,
            "defense_technical": 0.0,
            "physical": 0.0,
        }

        for session in sessions:
            # COALESCE: trata NULL como 0
            totals["attack_positional"] += float(session.focus_attack_positional_pct or 0)
            totals["defense_positional"] += float(session.focus_defense_positional_pct or 0)
            totals["transition_offense"] += float(session.focus_transition_offense_pct or 0)
            totals["transition_defense"] += float(session.focus_transition_defense_pct or 0)
            totals["attack_technical"] += float(session.focus_attack_technical_pct or 0)
            totals["defense_technical"] += float(session.focus_defense_technical_pct or 0)
            totals["physical"] += float(session.focus_physical_pct or 0)

        count = len(sessions)
        
        # Retorna médias arredondadas para 1 casa decimal
        return {k: round(v / count, 1) for k, v in totals.items()}

    def compute_macroblock_aggregation(
        self,
        focus_distribution: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """
        Agrega focos individuais em macroblocks para content_translation.
        
        Macroblocks:
        - attack: attack_positional + attack_technical + transition_offense
        - defense: defense_positional + defense_technical + transition_defense
        - physical: physical (sem agregação)
        
        Args:
            focus_distribution: Dict retornado por aggregate_training_focus()
            
        Returns:
            Dict com estrutura:
            {
                'attack': {
                    'total_pct': 50.8,
                    'breakdown': {
                        'attack_positional': 25.5,
                        'attack_technical': 10.0,
                        'transition_offense': 15.3
                    }
                },
                'defense': {
                    'total_pct': 41.2,
                    'breakdown': {
                        'defense_positional': 20.0,
                        'defense_technical': 8.5,
                        'transition_defense': 12.7
                    }
                },
                'physical': {
                    'total_pct': 8.0,
                    'breakdown': {
                        'physical': 8.0
                    }
                }
            }
        """
        attack_total = (
            focus_distribution["attack_positional"]
            + focus_distribution["attack_technical"]
            + focus_distribution["transition_offense"]
        )
        
        defense_total = (
            focus_distribution["defense_positional"]
            + focus_distribution["defense_technical"]
            + focus_distribution["transition_defense"]
        )
        
        physical_total = focus_distribution["physical"]

        return {
            "attack": {
                "total_pct": round(attack_total, 1),
                "breakdown": {
                    "attack_positional": focus_distribution["attack_positional"],
                    "attack_technical": focus_distribution["attack_technical"],
                    "transition_offense": focus_distribution["transition_offense"],
                }
            },
            "defense": {
                "total_pct": round(defense_total, 1),
                "breakdown": {
                    "defense_positional": focus_distribution["defense_positional"],
                    "defense_technical": focus_distribution["defense_technical"],
                    "transition_defense": focus_distribution["transition_defense"],
                }
            },
            "physical": {
                "total_pct": round(physical_total, 1),
                "breakdown": {
                    "physical": physical_total,
                }
            }
        }

    def fetch_training_sessions_in_window(
        self,
        team_id: UUID,
        season_id: UUID,
        start_date: date,
        end_date: date,
        organization_id: Optional[UUID] = None
    ) -> List[TrainingSession]:
        """
        Busca sessões de treino em janela temporal para análise de correlação.
        
        Args:
            team_id: UUID da equipe
            season_id: UUID da temporada
            start_date: Data inicial da janela (inclusive)
            end_date: Data final da janela (inclusive)
            organization_id: UUID da organização (opcional, para scoped queries)
            
        Returns:
            Lista de TrainingSession ordenadas por session_at ASC
        """
        stmt = (
            select(TrainingSession)
            .where(
                and_(
                    TrainingSession.team_id == team_id,
                    TrainingSession.season_id == season_id,
                    TrainingSession.session_at >= datetime.combine(start_date, datetime.min.time()),
                    TrainingSession.session_at <= datetime.combine(end_date, datetime.max.time()),
                    TrainingSession.deleted_at.is_(None)  # Ignora soft deleted
                )
            )
            .order_by(TrainingSession.session_at.asc())
        )

        if organization_id:
            stmt = stmt.where(TrainingSession.organization_id == organization_id)

        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def compute_avg_training_load_from_sessions(
        self,
        sessions: List[TrainingSession]
    ) -> float:
        """
        Calcula média de carga de treino a partir de sessões.
        
        Usa actual_load_avg se disponível, caso contrário usa planned_load.
        
        Args:
            sessions: Lista de TrainingSession
            
        Returns:
            Média de carga (0-10), ou 0.0 se não houver sessões
        """
        if not sessions:
            return 0.0

        total_load = 0.0
        count = 0

        for session in sessions:
            # Prioriza actual_load_avg (carga realizada)
            load = session.actual_load_avg if session.actual_load_avg is not None else session.planned_load
            if load is not None:
                total_load += float(load)
                count += 1

        return round(total_load / count, 1) if count > 0 else 0.0

    def compute_training_load_variability(
        self,
        sessions: List[TrainingSession]
    ) -> float:
        """
        Calcula variabilidade (desvio padrão) da carga de treino.
        
        Usado no bloco 'consistency' da resposta de correlação.
        
        Args:
            sessions: Lista de TrainingSession
            
        Returns:
            Desvio padrão da carga de treino, ou 0.0 se não houver sessões
        """
        if not sessions or len(sessions) < 2:
            return 0.0

        loads = []
        for session in sessions:
            load = session.actual_load_avg if session.actual_load_avg is not None else session.planned_load
            if load is not None:
                loads.append(float(load))

        if len(loads) < 2:
            return 0.0

        # Cálculo manual de desvio padrão
        mean = sum(loads) / len(loads)
        variance = sum((x - mean) ** 2 for x in loads) / len(loads)
        std_dev = variance ** 0.5

        return round(std_dev, 2)

    def generate_insights_from_correlation(
        self,
        macroblock_data: Dict[str, Dict[str, float]],
        game_efficiency: Dict[str, float],
        consistency: Dict[str, float]
    ) -> Dict[str, List[str]]:
        """
        Gera insights interpretativos (works/adjust/avoid) baseados em correlações.
        
        Lógica simples de thresholds para MVP:
        - works: foco alto (>30%) + eficiência alta (>70%)
        - adjust: foco médio (15-30%) + eficiência média (50-70%)
        - avoid: foco baixo (<15%) + eficiência baixa (<50%)
        
        Args:
            macroblock_data: Dict retornado por compute_macroblock_aggregation()
            game_efficiency: Dict com eficiências de jogo {'attack': 75.5, 'defense': 68.2}
            consistency: Dict com métricas de consistência
            
        Returns:
            Dict com 3 arrays:
            {
                'works': ['Ataque posicionado: foco alto e eficiência alta', ...],
                'adjust': ['Defesa: aumentar dedicação', ...],
                'avoid': ['Transições: baixo investimento sem retorno', ...]
            }
        """
        insights = {
            "works": [],
            "adjust": [],
            "avoid": []
        }

        # Análise de ataque
        attack_pct = macroblock_data["attack"]["total_pct"]
        attack_eff = game_efficiency.get("attack", 0)
        
        if attack_pct > 30 and attack_eff > 70:
            insights["works"].append(
                f"Ataque: foco alto ({attack_pct:.1f}%) com eficiência elevada ({attack_eff:.1f}%)"
            )
        elif attack_pct < 15 and attack_eff < 50:
            insights["avoid"].append(
                f"Ataque: baixo investimento ({attack_pct:.1f}%) e eficiência insuficiente ({attack_eff:.1f}%)"
            )
        elif 15 <= attack_pct <= 30 or 50 <= attack_eff <= 70:
            insights["adjust"].append(
                f"Ataque: considerar ajustar dedicação (foco {attack_pct:.1f}%, eficiência {attack_eff:.1f}%)"
            )

        # Análise de defesa
        defense_pct = macroblock_data["defense"]["total_pct"]
        defense_eff = game_efficiency.get("defense", 0)
        
        if defense_pct > 30 and defense_eff > 70:
            insights["works"].append(
                f"Defesa: foco alto ({defense_pct:.1f}%) com eficiência elevada ({defense_eff:.1f}%)"
            )
        elif defense_pct < 15 and defense_eff < 50:
            insights["avoid"].append(
                f"Defesa: baixo investimento ({defense_pct:.1f}%) e eficiência insuficiente ({defense_eff:.1f}%)"
            )
        elif 15 <= defense_pct <= 30 or 50 <= defense_eff <= 70:
            insights["adjust"].append(
                f"Defesa: considerar ajustar dedicação (foco {defense_pct:.1f}%, eficiência {defense_eff:.1f}%)"
            )

        # Análise de físico
        physical_pct = macroblock_data["physical"]["total_pct"]
        if physical_pct > 20:
            insights["works"].append(
                f"Preparação física: dedicação significativa ({physical_pct:.1f}%)"
            )
        elif physical_pct < 5:
            insights["adjust"].append(
                f"Preparação física: dedicação muito baixa ({physical_pct:.1f}%)"
            )

        # Análise de consistência
        load_variability = consistency.get("training_load_variability", 0)
        if load_variability > 2.5:
            insights["adjust"].append(
                f"Carga de treino: variabilidade elevada (σ={load_variability:.1f}), considerar maior consistência"
            )
        elif load_variability < 1.0:
            insights["works"].append(
                f"Carga de treino: consistência elevada (σ={load_variability:.1f})"
            )

        return insights
