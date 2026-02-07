"""
TrainingSuggestionService

Responsabilidades:
- Analisar padrões recorrentes de desvio (planejado vs executado)
- Gerar sugestões de ajuste de foco para novos microciclos
- Aprendizado baseado em histórico (últimos 3-5 microciclos similares)
- Sugestões por equipe e tipo de microciclo
- [Step 18] Sugestões automáticas de compensação e redução (alertas)

Conforme RAG/TRAINNIG.MD:
- Sugestão ≠ prescrição (sistema sugere, treinador decide)
- Recorrência mínima: 3 microciclos semelhantes
- Desvio significativo: ≥10pts em mesmo sentido
- Explicabilidade: sempre mostrar base da sugestão
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.training_microcycle import TrainingMicrocycle
from app.models.training_session import TrainingSession
from app.models.training_suggestion import TrainingSuggestion
from app.schemas.training_alerts_step18 import (
    SuggestionResponse,
    SuggestionStatsResponse,
    SuggestionFilters
)


class TrainingSuggestionService:
    """Serviço de sugestões inteligentes para planejamento."""

    # Configurações
    MIN_MICROCYCLES_FOR_SUGGESTION = 3  # Mínimo de microciclos para gerar sugestão
    MIN_DEVIATION_THRESHOLD = 10.0  # Desvio mínimo (pts) para considerar relevante
    LOOKBACK_DAYS = 90  # Analisar últimos 90 dias

    @staticmethod
    def get_suggestions_for_new_microcycle(
        db: Session,
        team_id: UUID,
        organization_id: UUID,
        microcycle_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gera sugestões para um novo microciclo com base no histórico.

        Args:
            db: Sessão do banco
            team_id: ID da equipe
            organization_id: ID da organização
            microcycle_type: Tipo de microciclo (carga_alta, recuperacao, etc.)

        Returns:
            Dict com sugestões e explicações
        """
        # Buscar microciclos recentes similares
        similar_microcycles = TrainingSuggestionService._get_similar_microcycles(
            db=db,
            team_id=team_id,
            organization_id=organization_id,
            microcycle_type=microcycle_type,
        )

        if len(similar_microcycles) < TrainingSuggestionService.MIN_MICROCYCLES_FOR_SUGGESTION:
            return {
                "has_suggestions": False,
                "reason": "insufficient_data",
                "message": f"São necessários pelo menos {TrainingSuggestionService.MIN_MICROCYCLES_FOR_SUGGESTION} microciclos similares para gerar sugestões.",
                "microcycles_analyzed": len(similar_microcycles),
            }

        # Analisar desvios recorrentes
        deviations = TrainingSuggestionService._analyze_recurrent_deviations(
            db=db,
            microcycles=similar_microcycles,
        )

        # Gerar sugestões baseadas em desvios
        suggestions = TrainingSuggestionService._generate_focus_suggestions(
            deviations=deviations,
            microcycles_analyzed=len(similar_microcycles),
        )

        if not suggestions:
            return {
                "has_suggestions": False,
                "reason": "no_significant_patterns",
                "message": "Não foram identificados padrões recorrentes significativos nos microciclos anteriores.",
                "microcycles_analyzed": len(similar_microcycles),
            }

        return {
            "has_suggestions": True,
            "microcycles_analyzed": len(similar_microcycles),
            "suggestions": suggestions,
            "context": {
                "period_analyzed": f"Últimos {TrainingSuggestionService.LOOKBACK_DAYS} dias",
                "microcycle_type": microcycle_type or "todos os tipos",
            },
        }

    @staticmethod
    def _get_similar_microcycles(
        db: Session,
        team_id: UUID,
        organization_id: UUID,
        microcycle_type: Optional[str],
    ) -> List[TrainingMicrocycle]:
        """
        Busca microciclos similares (mesma equipe, tipo, período recente).

        Returns:
            Lista de microciclos ordenados por mais recente
        """
        cutoff_date = datetime.utcnow() - timedelta(days=TrainingSuggestionService.LOOKBACK_DAYS)

        query = (
            select(TrainingMicrocycle)
            .where(
                and_(
                    TrainingMicrocycle.team_id == team_id,
                    TrainingMicrocycle.organization_id == organization_id,
                    TrainingMicrocycle.week_start >= cutoff_date,
                    TrainingMicrocycle.deleted_at.is_(None),
                )
            )
            .order_by(TrainingMicrocycle.week_start.desc())
        )

        # Filtrar por tipo se especificado
        if microcycle_type:
            query = query.where(TrainingMicrocycle.microcycle_type == microcycle_type)

        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def _analyze_recurrent_deviations(
        db: Session,
        microcycles: List[TrainingMicrocycle],
    ) -> Dict[str, Dict[str, float]]:
        """
        Analisa desvios recorrentes entre planejado e executado.

        Para cada foco:
        - Calcula média de desvio (executado - planejado)
        - Verifica consistência de direção (sempre + ou sempre -)
        - Considera apenas desvios ≥ MIN_DEVIATION_THRESHOLD

        Returns:
            Dict com desvios por foco:
            {
                "attack_positional": {
                    "avg_deviation": 12.5,  # média
                    "direction": "above",   # acima do planejado
                    "consistency": 0.8,     # 80% das vezes
                    "occurrences": 4,       # em 4 de 5 microciclos
                }
            }
        """
        focus_fields = [
            "attack_positional",
            "defense_positional",
            "transition_offense",
            "transition_defense",
            "attack_technical",
            "defense_technical",
            "physical",
        ]

        deviations_by_focus = {}

        for focus in focus_fields:
            planned_field = f"planned_focus_{focus}_pct"
            executed_field = f"focus_{focus}_pct"

            deviations = []

            for microcycle in microcycles:
                # Buscar sessões fechadas do microciclo
                sessions = (
                    db.query(TrainingSession)
                    .filter(
                        and_(
                            TrainingSession.microcycle_id == microcycle.id,
                            TrainingSession.status == "readonly",
                            TrainingSession.deleted_at.is_(None),
                        )
                    )
                    .all()
                )

                if not sessions:
                    continue

                # Calcular média executada das sessões
                planned_value = getattr(microcycle, planned_field) or 0
                executed_values = [getattr(s, executed_field) or 0 for s in sessions]
                avg_executed = sum(executed_values) / len(executed_values) if executed_values else 0

                deviation = avg_executed - planned_value

                # Considerar apenas desvios significativos
                if abs(deviation) >= TrainingSuggestionService.MIN_DEVIATION_THRESHOLD:
                    deviations.append(deviation)

            if len(deviations) < TrainingSuggestionService.MIN_MICROCYCLES_FOR_SUGGESTION:
                continue

            # Analisar consistência de direção
            positive_count = sum(1 for d in deviations if d > 0)
            negative_count = sum(1 for d in deviations if d < 0)
            total_count = len(deviations)

            # Verificar se há consistência (≥70% na mesma direção)
            consistency = max(positive_count, negative_count) / total_count

            if consistency < 0.7:
                continue  # Desvios inconsistentes, não gerar sugestão

            # Calcular média de desvio
            avg_deviation = sum(deviations) / len(deviations)

            deviations_by_focus[focus] = {
                "avg_deviation": round(avg_deviation, 1),
                "direction": "above" if avg_deviation > 0 else "below",
                "consistency": round(consistency, 2),
                "occurrences": total_count,
                "total_microcycles": len(microcycles),
            }

        return deviations_by_focus

    @staticmethod
    def _generate_focus_suggestions(
        deviations: Dict[str, Dict[str, float]],
        microcycles_analyzed: int,
    ) -> List[Dict[str, Any]]:
        """
        Gera sugestões de ajuste de foco baseadas em desvios recorrentes.

        Returns:
            Lista de sugestões com formato:
            [
                {
                    "focus_field": "attack_positional",
                    "focus_label": "Ataque Posicional",
                    "current_avg_planned": 25,  # (se houver)
                    "suggested_adjustment": +12,
                    "suggested_value": 37,
                    "reason": "Nos últimos 4 microciclos...",
                    "evidence": {...}
                }
            ]
        """
        focus_labels = {
            "attack_positional": "Ataque Posicional",
            "defense_positional": "Defesa Posicionada",
            "transition_offense": "Transição Ofensiva",
            "transition_defense": "Transição Defensiva",
            "attack_technical": "Técnico Ofensivo",
            "defense_technical": "Técnico Defensivo",
            "physical": "Físico",
        }

        suggestions = []

        for focus, data in deviations.items():
            adjustment = round(data["avg_deviation"])
            direction_word = "acima" if data["direction"] == "above" else "abaixo"

            suggestion = {
                "focus_field": focus,
                "focus_label": focus_labels[focus],
                "suggested_adjustment": adjustment,
                "reason": (
                    f"Nos últimos {data['occurrences']} microciclos semelhantes, "
                    f"o foco executado foi em média {abs(adjustment)}% {direction_word} do planejado. "
                    f"Consistência: {int(data['consistency'] * 100)}%."
                ),
                "evidence": {
                    "avg_deviation": data["avg_deviation"],
                    "direction": data["direction"],
                    "consistency": data["consistency"],
                    "occurrences": data["occurrences"],
                    "total_analyzed": microcycles_analyzed,
                },
                "type": "focus_adjustment",
                "confidence": "high" if data["consistency"] >= 0.8 else "medium",
            }

            suggestions.append(suggestion)

        # Ordenar por maior desvio absoluto
        suggestions.sort(key=lambda x: abs(x["suggested_adjustment"]), reverse=True)

        return suggestions

    @staticmethod
    def apply_suggestion_to_microcycle(
        db: Session,
        microcycle_id: UUID,
        suggestion: Dict[str, Any],
    ) -> TrainingMicrocycle:
        """
        Aplica uma sugestão a um microciclo (ajusta foco planejado).

        Args:
            db: Sessão do banco
            microcycle_id: ID do microciclo
            suggestion: Sugestão a aplicar

        Returns:
            Microciclo atualizado
        """
        microcycle = db.query(TrainingMicrocycle).filter(
            TrainingMicrocycle.id == microcycle_id
        ).first()

        if not microcycle:
            raise ValueError("Microciclo não encontrado")

        focus_field = f"planned_focus_{suggestion['focus_field']}_pct"
        current_value = getattr(microcycle, focus_field) or 0
        new_value = max(0, min(100, current_value + suggestion["suggested_adjustment"]))

        setattr(microcycle, focus_field, new_value)

        db.commit()
        db.refresh(microcycle)

        return microcycle

    # ======================================================================
    # STEP 18: Métodos para Alertas Automáticos e Sugestões
    # ======================================================================

    def __init__(self, db: AsyncSession):
        """Inicializa service com sessão async."""
        self.db = db

    async def generate_compensation_suggestion(
        self,
        session_id: int,
        adjustment_pct: Optional[float] = None
    ) -> Optional[SuggestionResponse]:
        """
        Gera sugestão de compensação quando sessão tem focus >100%.
        
        Args:
            session_id: ID da sessão com sobrecarga
            adjustment_pct: % de redução recomendada (default: auto-calcular)
        
        Returns:
            SuggestionResponse se criado, None caso contrário
        
        Lógica:
            - Se session.total_focus_pct > 100%: cria suggestion type='compensation'
            - Target: próximas 2-3 sessões não-locked da mesma equipe
            - recommended_adjustment_pct: (total - 100) / num_targets
            - Max adjustment: 40% por sessão
        """
        # Busca sessão origem
        origin_stmt = select(TrainingSession).where(TrainingSession.id == session_id)
        origin_result = await self.db.execute(origin_stmt)
        origin_session = origin_result.scalar_one_or_none()
        
        if not origin_session or not origin_session.total_focus_pct:
            return None
        
        # Verifica se há sobrecarga
        if origin_session.total_focus_pct <= 100:
            return None
        
        # Calcula ajuste necessário
        overload = origin_session.total_focus_pct - 100
        
        # Busca próximas sessões não-locked (2-3 sessões)
        next_sessions_stmt = select(TrainingSession).where(
            and_(
                TrainingSession.team_id == origin_session.team_id,
                TrainingSession.session_date > origin_session.session_date,
                TrainingSession.is_locked == False,
                TrainingSession.id != session_id
            )
        ).order_by(TrainingSession.session_date).limit(3)
        
        next_sessions_result = await self.db.execute(next_sessions_stmt)
        next_sessions = next_sessions_result.scalars().all()
        
        if not next_sessions:
            return None
        
        # Calcula ajuste por sessão
        if adjustment_pct is None:
            adjustment_pct = min(overload / len(next_sessions), 40.0)
            adjustment_pct = max(adjustment_pct, 10.0)  # Mínimo 10%
        
        # Cria sugestão
        suggestion = TrainingSuggestion(
            team_id=origin_session.team_id,
            type="compensation",
            origin_session_id=session_id,
            target_session_ids=[s.id for s in next_sessions],
            recommended_adjustment_pct=round(adjustment_pct, 1),
            reason=f"Sessão #{session_id} teve focus_pct={origin_session.total_focus_pct:.0f}% (sobrecarga de {overload:.0f}%). Sugerindo compensação de -{adjustment_pct:.0f}% nas próximas {len(next_sessions)} sessões não-locked.",
            status="pending",
            created_at=datetime.now()
        )
        
        self.db.add(suggestion)
        await self.db.commit()
        await self.db.refresh(suggestion)
        
        return self._to_response(suggestion)

    async def generate_reduction_suggestion(
        self,
        team_id: int,
        week: datetime,
        reduction_pct: float = 20.0
    ) -> Optional[SuggestionResponse]:
        """
        Gera sugestão de redução quando alerta critical de overload.
        
        Args:
            team_id: ID da equipe
            week: Semana de referência (usado para buscar próxima semana)
            reduction_pct: % de redução (default 20%)
        
        Returns:
            SuggestionResponse se criado, None caso contrário
        
        Lógica:
            - Busca sessões da próxima semana (não-locked)
            - Cria suggestion type='reduce_next_week'
            - Target: todas as sessões não-locked da próxima semana
        """
        # Calcula próxima semana
        next_week_start = week + timedelta(days=7)
        next_week_end = next_week_start + timedelta(days=7)
        
        # Busca sessões não-locked da próxima semana
        next_sessions_stmt = select(TrainingSession).where(
            and_(
                TrainingSession.team_id == team_id,
                TrainingSession.session_date >= next_week_start,
                TrainingSession.session_date < next_week_end,
                TrainingSession.is_locked == False
            )
        ).order_by(TrainingSession.session_date)
        
        next_sessions_result = await self.db.execute(next_sessions_stmt)
        next_sessions = next_sessions_result.scalars().all()
        
        if not next_sessions:
            return None
        
        # Verifica se já existe sugestão pendente similar
        existing_stmt = select(TrainingSuggestion).where(
            and_(
                TrainingSuggestion.team_id == team_id,
                TrainingSuggestion.type == "reduce_next_week",
                TrainingSuggestion.status == "pending",
                func.date_trunc('week', TrainingSuggestion.created_at) == next_week_start.date()
            )
        )
        existing_result = await self.db.execute(existing_stmt)
        if existing_result.scalar_one_or_none():
            return None  # Já existe sugestão para essa semana
        
        # Cria sugestão
        suggestion = TrainingSuggestion(
            team_id=team_id,
            type="reduce_next_week",
            target_session_ids=[s.id for s in next_sessions],
            recommended_adjustment_pct=reduction_pct,
            reason=f"Sobrecarga crítica detectada na semana {week.strftime('%Y-%m-%d')}. Sugerindo redução de {reduction_pct}% para próxima semana ({len(next_sessions)} sessões).",
            status="pending",
            created_at=datetime.now()
        )
        
        self.db.add(suggestion)
        await self.db.commit()
        await self.db.refresh(suggestion)
        
        return self._to_response(suggestion)

    async def apply_suggestion(
        self,
        suggestion_id: int,
        adjustment_pct: float
    ) -> Optional[SuggestionResponse]:
        """
        Aplica sugestão ajustando focus das sessões alvo.
        
        Args:
            suggestion_id: ID da sugestão
            adjustment_pct: % final escolhido pelo usuário (10-40%)
        
        Returns:
            SuggestionResponse atualizado
        
        Lógica:
            - Busca sessões target
            - Recalcula focus_pct mantendo proporções (total = 100%)
            - Marca suggestion como applied
            - Registra applied_at
        """
        # Busca sugestão
        stmt = select(TrainingSuggestion).where(TrainingSuggestion.id == suggestion_id)
        result = await self.db.execute(stmt)
        suggestion = result.scalar_one_or_none()
        
        if not suggestion or suggestion.status != "pending":
            return None
        
        # Busca sessões alvo
        target_sessions_stmt = select(TrainingSession).where(
            TrainingSession.id.in_(suggestion.target_session_ids)
        )
        target_sessions_result = await self.db.execute(target_sessions_stmt)
        target_sessions = target_sessions_result.scalars().all()
        
        if not target_sessions:
            return None
        
        # Aplica ajuste em cada sessão
        for session in target_sessions:
            if session.is_locked:
                continue  # Pula sessões locked
            
            # Reduz cada focus proporcionalmente
            reduction_factor = 1 - (adjustment_pct / 100)
            
            if session.attack_positional_pct:
                session.attack_positional_pct *= reduction_factor
            if session.defense_positional_pct:
                session.defense_positional_pct *= reduction_factor
            if session.transition_offense_pct:
                session.transition_offense_pct *= reduction_factor
            if session.transition_defense_pct:
                session.transition_defense_pct *= reduction_factor
            if session.attack_technical_pct:
                session.attack_technical_pct *= reduction_factor
            if session.defense_technical_pct:
                session.defense_technical_pct *= reduction_factor
            if session.physical_pct:
                session.physical_pct *= reduction_factor
            
            # Recalcula total
            session.total_focus_pct = sum([
                session.attack_positional_pct or 0,
                session.defense_positional_pct or 0,
                session.transition_offense_pct or 0,
                session.transition_defense_pct or 0,
                session.attack_technical_pct or 0,
                session.defense_technical_pct or 0,
                session.physical_pct or 0
            ])
        
        # Marca sugestão como aplicada
        suggestion.status = "applied"
        suggestion.applied_at = datetime.now()
        
        await self.db.commit()
        await self.db.refresh(suggestion)
        
        return self._to_response(suggestion)

    async def dismiss_suggestion(
        self,
        suggestion_id: int,
        dismissal_reason: str
    ) -> Optional[SuggestionResponse]:
        """
        Dismissal de sugestão com justificativa.
        
        Args:
            suggestion_id: ID da sugestão
            dismissal_reason: Motivo da rejeição (50-500 chars)
        
        Returns:
            SuggestionResponse atualizado
        """
        stmt = select(TrainingSuggestion).where(TrainingSuggestion.id == suggestion_id)
        result = await self.db.execute(stmt)
        suggestion = result.scalar_one_or_none()
        
        if not suggestion or suggestion.status != "pending":
            return None
        
        suggestion.status = "dismissed"
        suggestion.dismissed_at = datetime.now()
        suggestion.dismissal_reason = dismissal_reason
        
        await self.db.commit()
        await self.db.refresh(suggestion)
        
        return self._to_response(suggestion)

    async def get_pending_suggestions(
        self,
        team_id: int,
        limit: int = 10
    ) -> list[SuggestionResponse]:
        """Busca sugestões pendentes de uma equipe."""
        stmt = select(TrainingSuggestion).where(
            and_(
                TrainingSuggestion.team_id == team_id,
                TrainingSuggestion.status == "pending"
            )
        ).order_by(desc(TrainingSuggestion.created_at)).limit(limit)
        
        result = await self.db.execute(stmt)
        suggestions = result.scalars().all()
        
        return [self._to_response(s) for s in suggestions]

    async def get_suggestion_stats(
        self,
        team_id: int,
        filters: Optional[SuggestionFilters] = None
    ) -> SuggestionStatsResponse:
        """Calcula estatísticas de sugestões."""
        base_stmt = select(TrainingSuggestion).where(TrainingSuggestion.team_id == team_id)
        
        # Aplica filtros
        if filters:
            if filters.type:
                base_stmt = base_stmt.where(TrainingSuggestion.type == filters.type.value)
            if filters.status:
                base_stmt = base_stmt.where(TrainingSuggestion.status == filters.status.value)
            if filters.start_date:
                base_stmt = base_stmt.where(TrainingSuggestion.created_at >= filters.start_date)
            if filters.end_date:
                base_stmt = base_stmt.where(TrainingSuggestion.created_at <= filters.end_date)
        
        # Total
        total_result = await self.db.execute(select(func.count()).select_from(base_stmt.subquery()))
        total = total_result.scalar() or 0
        
        # Por status
        pending_stmt = base_stmt.where(TrainingSuggestion.status == "pending")
        pending_result = await self.db.execute(select(func.count()).select_from(pending_stmt.subquery()))
        pending = pending_result.scalar() or 0
        
        applied_stmt = base_stmt.where(TrainingSuggestion.status == "applied")
        applied_result = await self.db.execute(select(func.count()).select_from(applied_stmt.subquery()))
        applied = applied_result.scalar() or 0
        
        dismissed_stmt = base_stmt.where(TrainingSuggestion.status == "dismissed")
        dismissed_result = await self.db.execute(select(func.count()).select_from(dismissed_stmt.subquery()))
        dismissed = dismissed_result.scalar() or 0
        
        # Taxa de aceitação
        total_resolved = applied + dismissed
        acceptance_rate = (applied / total_resolved * 100) if total_resolved > 0 else 0.0
        
        # By type
        by_type_stmt = select(
            TrainingSuggestion.type,
            func.count(TrainingSuggestion.id).label("count")
        ).where(TrainingSuggestion.team_id == team_id).group_by(TrainingSuggestion.type)
        
        if filters:
            if filters.start_date:
                by_type_stmt = by_type_stmt.where(TrainingSuggestion.created_at >= filters.start_date)
            if filters.end_date:
                by_type_stmt = by_type_stmt.where(TrainingSuggestion.created_at <= filters.end_date)
        
        by_type_result = await self.db.execute(by_type_stmt)
        by_type = {row[0]: row[1] for row in by_type_result.all()}
        
        # Recent suggestions (5 mais recentes)
        recent_stmt = base_stmt.order_by(desc(TrainingSuggestion.created_at)).limit(5)
        recent_result = await self.db.execute(recent_stmt)
        recent_suggestions = [self._to_response(s) for s in recent_result.scalars().all()]
        
        return SuggestionStatsResponse(
            total=total,
            pending=pending,
            applied=applied,
            dismissed=dismissed,
            acceptance_rate=round(acceptance_rate, 2),
            by_type=by_type,
            recent_suggestions=recent_suggestions
        )

    def _to_response(self, suggestion: TrainingSuggestion) -> SuggestionResponse:
        """Converte TrainingSuggestion ORM para SuggestionResponse schema."""
        return SuggestionResponse(
            id=suggestion.id,
            team_id=suggestion.team_id,
            type=suggestion.type,
            origin_session_id=suggestion.origin_session_id,
            target_session_ids=suggestion.target_session_ids,
            recommended_adjustment_pct=suggestion.recommended_adjustment_pct,
            reason=suggestion.reason,
            status=suggestion.status,
            created_at=suggestion.created_at,
            applied_at=suggestion.applied_at,
            dismissed_at=suggestion.dismissed_at,
            dismissal_reason=suggestion.dismissal_reason,
            is_pending=suggestion.is_pending,
            is_applied=suggestion.is_applied,
            is_dismissed=suggestion.is_dismissed,
            target_count=suggestion.target_count
        )
