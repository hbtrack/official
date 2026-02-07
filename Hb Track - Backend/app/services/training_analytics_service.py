"""
Service para cálculo e cache de analytics de treino (Step 16).

Funcionalidades:
- Calcula 17 métricas agregadas por equipe
- Suporta granularidade weekly (microciclo) e monthly (mês)
- Usa cache híbrido com invalidação automática via trigger
- Integra com team.alert_threshold_multiplier para cálculos de desvio

Métricas:
1. total_sessions
2-8. avg_focus_* (7 focos de treino)
9-11. avg_rpe, avg_internal_load, total_internal_load
12. attendance_rate
13-14. wellness_response_rate_pre/post
15. athletes_with_badges_count
16-18. deviation_count, threshold_mean, threshold_stddev
"""

import logging
from datetime import datetime, timezone, date, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.core.context import ExecutionContext
from app.core.exceptions import NotFoundError, ValidationError
from app.models.training_analytics_cache import TrainingAnalyticsCache
from app.models.training_session import TrainingSession
from app.models.training_microcycle import TrainingMicrocycle
from app.models.team import Team
from app.models.attendance import Attendance
from app.models.wellness_pre import WellnessPre
from app.models.wellness_post import WellnessPost
from app.models.athlete import Athlete

logger = logging.getLogger(__name__)


class TrainingAnalyticsService:
    """
    Service de Analytics de Treino com cache híbrido.
    Ref: Step 16
    """

    def __init__(self, db: AsyncSession, context: ExecutionContext):
        self.db = db
        self.context = context

    async def get_team_summary(
        self,
        team_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> dict:
        """
        Retorna sumário de analytics para uma equipe.
        
        Estratégia:
        - Mês corrente: usa cache weekly (por microciclo)
        - Meses anteriores: usa cache monthly
        - Recalcula automaticamente se cache_dirty=true
        
        Args:
            team_id: UUID da equipe
            start_date: Início do período (default: início do mês corrente)
            end_date: Fim do período (default: hoje)
        
        Returns:
            dict com métricas agregadas
        """
        # Validar acesso à equipe
        team = await self._get_team(team_id)
        
        # Definir período padrão (mês corrente)
        if not start_date:
            today = date.today()
            start_date = today.replace(day=1)
        if not end_date:
            end_date = date.today()
        
        # Buscar ou recalcular caches
        weekly_metrics = await self._get_weekly_metrics(team, start_date, end_date)
        monthly_metrics = await self._get_monthly_metrics(team, start_date, end_date)
        
        # Agregar resultados
        combined_metrics = self._combine_metrics(weekly_metrics, monthly_metrics)
        
        return {
            "team_id": str(team_id),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "metrics": combined_metrics,
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }

    async def get_weekly_load(
        self,
        team_id: UUID,
        weeks: int = 4
    ) -> list[dict]:
        """
        Retorna carga semanal das últimas N semanas.
        
        Args:
            team_id: UUID da equipe
            weeks: Quantidade de semanas (default: 4)
        
        Returns:
            Lista de dicts com métricas semanais
        """
        team = await self._get_team(team_id)
        
        # Buscar microciclos das últimas N semanas
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks)
        
        query = select(TrainingMicrocycle).where(
            and_(
                TrainingMicrocycle.team_id == team_id,
                TrainingMicrocycle.organization_id == self.context.organization_id,
                TrainingMicrocycle.week_start >= start_date,
                TrainingMicrocycle.week_end <= end_date,
                TrainingMicrocycle.deleted_at.is_(None)
            )
        ).order_by(TrainingMicrocycle.week_start.desc())
        
        result = await self.db.execute(query)
        microcycles = list(result.scalars().all())
        
        # Buscar ou calcular cache para cada microciclo
        weekly_data = []
        for micro in microcycles:
            cache = await self._get_or_calculate_weekly_cache(team, micro)
            weekly_data.append({
                "week_start": micro.week_start.isoformat(),
                "week_end": micro.week_end.isoformat(),
                "microcycle_id": str(micro.id),
                "total_sessions": cache.total_sessions or 0,
                "total_internal_load": float(cache.total_internal_load or 0),
                "avg_rpe": float(cache.avg_rpe or 0),
                "attendance_rate": float(cache.attendance_rate or 0),
            })
        
        return weekly_data

    async def get_deviation_analysis(
        self,
        team_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Análise de desvios usando alert_threshold_multiplier da equipe.
        
        Args:
            team_id: UUID da equipe
            start_date: Início do período
            end_date: Fim do período
        
        Returns:
            dict com análise de desvios
        """
        team = await self._get_team(team_id)
        
        if not start_date:
            start_date = date.today().replace(day=1)
        if not end_date:
            end_date = date.today()
        
        # Buscar sessões do período
        query = select(TrainingSession).where(
            and_(
                TrainingSession.team_id == team_id,
                TrainingSession.organization_id == self.context.organization_id,
                func.date(TrainingSession.session_at) >= start_date,
                func.date(TrainingSession.session_at) <= end_date,
                TrainingSession.deleted_at.is_(None)
            )
        )
        
        result = await self.db.execute(query)
        sessions = list(result.scalars().all())
        
        # Calcular desvios usando threshold do time
        threshold_multiplier = float(team.alert_threshold_multiplier)
        deviations = []
        
        for session in sessions:
            rpe_avg = getattr(session, "rpe_avg", None)
            planned_rpe = getattr(session, "planned_rpe", None)
            if rpe_avg is not None and planned_rpe is not None:
                # Cálculo simplificado: desvio = (real - planejado) × multiplier
                deviation = abs(float(rpe_avg) - float(planned_rpe)) * threshold_multiplier
                
                if deviation > threshold_multiplier:  # Threshold dinâmico
                    deviations.append({
                        "session_id": str(session.id),
                        "session_at": session.session_at.date().isoformat(),
                        "planned_rpe": float(planned_rpe),
                        "actual_rpe": float(rpe_avg),
                        "deviation": round(deviation, 2),
                        "exceeded_threshold": True
                    })
        
        return {
            "team_id": str(team_id),
            "threshold_multiplier": threshold_multiplier,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_sessions": len(sessions),
            "deviation_count": len(deviations),
            "deviations": deviations
        }

    # =========================================================================
    # MÉTODOS PRIVADOS - CACHE E CÁLCULO
    # =========================================================================

    async def _get_team(self, team_id: UUID) -> Team:
        """Valida e retorna equipe."""
        query = select(Team).where(
            and_(
                Team.id == team_id,
                Team.organization_id == self.context.organization_id,
                Team.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(query)
        team = result.scalar_one_or_none()
        
        if not team:
            raise NotFoundError(f"Team {team_id} not found")
        
        return team

    async def _get_weekly_metrics(
        self,
        team: Team,
        start_date: date,
        end_date: date
    ) -> list[TrainingAnalyticsCache]:
        """
        Busca métricas semanais (por microciclo) para o período.
        Recalcula se cache_dirty=true.
        """
        # Buscar microciclos no período
        query = select(TrainingMicrocycle).where(
            and_(
                TrainingMicrocycle.team_id == team.id,
                TrainingMicrocycle.organization_id == self.context.organization_id,
                or_(
                    and_(
                        TrainingMicrocycle.week_start >= start_date,
                        TrainingMicrocycle.week_start <= end_date
                    ),
                    and_(
                        TrainingMicrocycle.week_end >= start_date,
                        TrainingMicrocycle.week_end <= end_date
                    )
                ),
                TrainingMicrocycle.deleted_at.is_(None)
            )
        )
        
        result = await self.db.execute(query)
        microcycles = list(result.scalars().all())
        
        # Buscar ou calcular cache para cada microciclo
        metrics = []
        for micro in microcycles:
            cache = await self._get_or_calculate_weekly_cache(team, micro)
            metrics.append(cache)
        
        return metrics

    async def _get_monthly_metrics(
        self,
        team: Team,
        start_date: date,
        end_date: date
    ) -> list[TrainingAnalyticsCache]:
        """
        Busca métricas mensais (agregadas) para meses anteriores.
        Recalcula se cache_dirty=true.
        """
        # Identificar meses no período (excluindo mês corrente se start_date for início do mês)
        months = []
        current_month = start_date.replace(day=1)
        today = date.today()
        current_month_start = today.replace(day=1)
        
        while current_month <= end_date.replace(day=1):
            # Pular mês corrente (usa weekly)
            if current_month != current_month_start:
                months.append(current_month)
            current_month = (current_month + timedelta(days=32)).replace(day=1)
        
        # Buscar ou calcular cache para cada mês
        metrics = []
        for month_start in months:
            cache = await self._get_or_calculate_monthly_cache(team, month_start)
            metrics.append(cache)
        
        return metrics

    async def _get_or_calculate_weekly_cache(
        self,
        team: Team,
        microcycle: TrainingMicrocycle
    ) -> TrainingAnalyticsCache:
        """
        Busca cache weekly ou recalcula se necessário.
        """
        # Buscar cache existente
        query = select(TrainingAnalyticsCache).where(
            and_(
                TrainingAnalyticsCache.team_id == team.id,
                TrainingAnalyticsCache.microcycle_id == microcycle.id,
                TrainingAnalyticsCache.granularity == 'weekly'
            )
        )
        
        result = await self.db.execute(query)
        cache = result.scalar_one_or_none()
        
        # Se não existe ou está dirty, recalcular
        if not cache or cache.cache_dirty:
            cache = await self._calculate_weekly_metrics(team, microcycle, cache)
            await self.db.commit()
        
        return cache

    async def _get_or_calculate_monthly_cache(
        self,
        team: Team,
        month_start: date
    ) -> TrainingAnalyticsCache:
        """
        Busca cache monthly ou recalcula se necessário.
        """
        # Buscar cache existente
        query = select(TrainingAnalyticsCache).where(
            and_(
                TrainingAnalyticsCache.team_id == team.id,
                TrainingAnalyticsCache.month == month_start,
                TrainingAnalyticsCache.granularity == 'monthly'
            )
        )
        
        result = await self.db.execute(query)
        cache = result.scalar_one_or_none()
        
        # Se não existe ou está dirty, recalcular
        if not cache or cache.cache_dirty:
            cache = await self._calculate_monthly_metrics(team, month_start, cache)
            await self.db.commit()
        
        return cache

    async def _calculate_weekly_metrics(
        self,
        team: Team,
        microcycle: TrainingMicrocycle,
        existing_cache: Optional[TrainingAnalyticsCache] = None
    ) -> TrainingAnalyticsCache:
        """
        Calcula métricas semanais (por microciclo).
        """
        logger.info(f"Calculating weekly metrics for team {team.id}, microcycle {microcycle.id}")
        
        # Buscar sessões do microciclo
        query = select(TrainingSession).where(
            and_(
                TrainingSession.team_id == team.id,
                TrainingSession.microcycle_id == microcycle.id,
                TrainingSession.organization_id == self.context.organization_id,
                TrainingSession.deleted_at.is_(None)
            )
        )
        
        result = await self.db.execute(query)
        sessions = list(result.scalars().all())
        
        # Calcular métricas
        metrics = await self._aggregate_session_metrics(sessions, team)
        
        # Criar ou atualizar cache
        if existing_cache:
            cache = existing_cache
        else:
            cache = TrainingAnalyticsCache(
                team_id=team.id,
                microcycle_id=microcycle.id,
                granularity='weekly'
            )
            self.db.add(cache)
        
        # Popular métricas
        cache.total_sessions = metrics['total_sessions']
        cache.avg_focus_attack_positional_pct = metrics.get('avg_focus_attack_positional_pct')
        cache.avg_focus_defense_positional_pct = metrics.get('avg_focus_defense_positional_pct')
        cache.avg_focus_transition_offense_pct = metrics.get('avg_focus_transition_offense_pct')
        cache.avg_focus_transition_defense_pct = metrics.get('avg_focus_transition_defense_pct')
        cache.avg_focus_attack_technical_pct = metrics.get('avg_focus_attack_technical_pct')
        cache.avg_focus_defense_technical_pct = metrics.get('avg_focus_defense_technical_pct')
        cache.avg_focus_physical_pct = metrics.get('avg_focus_physical_pct')
        cache.avg_rpe = metrics.get('avg_rpe')
        cache.avg_internal_load = metrics.get('avg_internal_load')
        cache.total_internal_load = metrics.get('total_internal_load')
        cache.attendance_rate = metrics.get('attendance_rate')
        cache.wellness_response_rate_pre = metrics.get('wellness_response_rate_pre')
        cache.wellness_response_rate_post = metrics.get('wellness_response_rate_post')
        cache.athletes_with_badges_count = metrics.get('athletes_with_badges_count')
        cache.deviation_count = metrics.get('deviation_count')
        cache.threshold_mean = metrics.get('threshold_mean')
        cache.threshold_stddev = metrics.get('threshold_stddev')
        
        # Marcar como válido
        cache.cache_dirty = False
        cache.calculated_at = datetime.now(timezone.utc)
        
        await self.db.flush()
        return cache

    async def _calculate_monthly_metrics(
        self,
        team: Team,
        month_start: date,
        existing_cache: Optional[TrainingAnalyticsCache] = None
    ) -> TrainingAnalyticsCache:
        """
        Calcula métricas mensais (agregadas).
        """
        logger.info(f"Calculating monthly metrics for team {team.id}, month {month_start}")
        
        # Calcular último dia do mês
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
        
        # Buscar sessões do mês
        query = select(TrainingSession).where(
            and_(
                TrainingSession.team_id == team.id,
                TrainingSession.organization_id == self.context.organization_id,
                func.date(TrainingSession.session_at) >= month_start,
                func.date(TrainingSession.session_at) <= month_end,
                TrainingSession.deleted_at.is_(None)
            )
        )
        
        result = await self.db.execute(query)
        sessions = list(result.scalars().all())
        
        # Calcular métricas
        metrics = await self._aggregate_session_metrics(sessions, team)
        
        # Criar ou atualizar cache
        if existing_cache:
            cache = existing_cache
        else:
            cache = TrainingAnalyticsCache(
                team_id=team.id,
                month=month_start,
                granularity='monthly'
            )
            self.db.add(cache)
        
        # Popular métricas (mesmo código que weekly)
        cache.total_sessions = metrics['total_sessions']
        cache.avg_focus_attack_positional_pct = metrics.get('avg_focus_attack_positional_pct')
        cache.avg_focus_defense_positional_pct = metrics.get('avg_focus_defense_positional_pct')
        cache.avg_focus_transition_offense_pct = metrics.get('avg_focus_transition_offense_pct')
        cache.avg_focus_transition_defense_pct = metrics.get('avg_focus_transition_defense_pct')
        cache.avg_focus_attack_technical_pct = metrics.get('avg_focus_attack_technical_pct')
        cache.avg_focus_defense_technical_pct = metrics.get('avg_focus_defense_technical_pct')
        cache.avg_focus_physical_pct = metrics.get('avg_focus_physical_pct')
        cache.avg_rpe = metrics.get('avg_rpe')
        cache.avg_internal_load = metrics.get('avg_internal_load')
        cache.total_internal_load = metrics.get('total_internal_load')
        cache.attendance_rate = metrics.get('attendance_rate')
        cache.wellness_response_rate_pre = metrics.get('wellness_response_rate_pre')
        cache.wellness_response_rate_post = metrics.get('wellness_response_rate_post')
        cache.athletes_with_badges_count = metrics.get('athletes_with_badges_count')
        cache.deviation_count = metrics.get('deviation_count')
        cache.threshold_mean = metrics.get('threshold_mean')
        cache.threshold_stddev = metrics.get('threshold_stddev')
        
        # Marcar como válido
        cache.cache_dirty = False
        cache.calculated_at = datetime.now(timezone.utc)
        
        await self.db.flush()
        return cache

    async def _aggregate_session_metrics(
        self,
        sessions: list[TrainingSession],
        team: Team
    ) -> dict:
        """
        Agrega métricas de uma lista de sessões.
        Calcula todas as 17 métricas do cache.
        """
        if not sessions:
            return {'total_sessions': 0}
        
        total = len(sessions)
        
        # Inicializar acumuladores para médias
        focus_sums = {
            'attack_positional': 0.0,
            'defense_positional': 0.0,
            'transition_offense': 0.0,
            'transition_defense': 0.0,
            'attack_technical': 0.0,
            'defense_technical': 0.0,
            'physical': 0.0
        }
        focus_counts = {k: 0 for k in focus_sums.keys()}
        
        rpe_sum = 0.0
        rpe_count = 0
        
        internal_load_sum = 0.0
        internal_load_count = 0
        total_internal_load = 0.0
        
        # Processar cada sessão
        for session in sessions:
            # Focos
            if session.focus_attack_positional_pct is not None:
                focus_sums['attack_positional'] += float(session.focus_attack_positional_pct)
                focus_counts['attack_positional'] += 1
            if session.focus_defense_positional_pct is not None:
                focus_sums['defense_positional'] += float(session.focus_defense_positional_pct)
                focus_counts['defense_positional'] += 1
            if session.focus_transition_offense_pct is not None:
                focus_sums['transition_offense'] += float(session.focus_transition_offense_pct)
                focus_counts['transition_offense'] += 1
            if session.focus_transition_defense_pct is not None:
                focus_sums['transition_defense'] += float(session.focus_transition_defense_pct)
                focus_counts['transition_defense'] += 1
            if session.focus_attack_technical_pct is not None:
                focus_sums['attack_technical'] += float(session.focus_attack_technical_pct)
                focus_counts['attack_technical'] += 1
            if session.focus_defense_technical_pct is not None:
                focus_sums['defense_technical'] += float(session.focus_defense_technical_pct)
                focus_counts['defense_technical'] += 1
            if session.focus_physical_pct is not None:
                focus_sums['physical'] += float(session.focus_physical_pct)
                focus_counts['physical'] += 1
            
            # RPE
            rpe_avg = getattr(session, "rpe_avg", None)
            if rpe_avg is not None:
                rpe_sum += float(rpe_avg)
                rpe_count += 1
            
            # Carga interna
            internal_load_avg = getattr(session, "internal_load_avg", None)
            if internal_load_avg is not None:
                internal_load_sum += float(internal_load_avg)
                internal_load_count += 1
                total_internal_load += float(internal_load_avg)
        
        # Calcular médias de focos
        avg_focuses = {
            f'avg_focus_{key}_pct': round(focus_sums[key] / focus_counts[key], 2) if focus_counts[key] > 0 else None
            for key in focus_sums.keys()
        }
        
        # Calcular attendance rate
        attendance_rate = await self._calculate_attendance_rate(sessions)
        
        # Calcular wellness response rates
        wellness_rates = await self._calculate_wellness_rates(sessions)
        
        # Calcular badges count
        badges_count = await self._calculate_badges_count(team, sessions)
        
        # Calcular desvios
        deviation_metrics = self._calculate_deviation_metrics(sessions, team)
        
        return {
            'total_sessions': total,
            **avg_focuses,
            'avg_rpe': round(rpe_sum / rpe_count, 2) if rpe_count > 0 else None,
            'avg_internal_load': round(internal_load_sum / internal_load_count, 2) if internal_load_count > 0 else None,
            'total_internal_load': round(total_internal_load, 2),
            'attendance_rate': attendance_rate,
            **wellness_rates,
            'athletes_with_badges_count': badges_count,
            **deviation_metrics
        }

    async def _calculate_attendance_rate(self, sessions: list[TrainingSession]) -> Optional[float]:
        """Calcula taxa de assiduidade média das sessões."""
        if not sessions:
            return None
        
        rates = []
        for session in sessions:
            # Buscar attendance da sessão
            query = select(Attendance).where(
                Attendance.training_session_id == session.id
            )
            result = await self.db.execute(query)
            attendances = list(result.scalars().all())
            
            if attendances:
                present = sum(1 for a in attendances if a.present)
                rate = (present / len(attendances)) * 100
                rates.append(rate)
        
        return round(sum(rates) / len(rates), 2) if rates else None

    async def _calculate_wellness_rates(self, sessions: list[TrainingSession]) -> dict:
        """Calcula taxas de resposta wellness pré e pós treino."""
        if not sessions:
            return {
                'wellness_response_rate_pre': None,
                'wellness_response_rate_post': None
            }
        
        session_ids = [s.id for s in sessions]
        
        # Wellness pré
        query_pre = select(func.count(WellnessPre.id)).where(
            WellnessPre.training_session_id.in_(session_ids)
        )
        result_pre = await self.db.execute(query_pre)
        pre_count = result_pre.scalar_one_or_none() or 0
        
        # Wellness pós
        query_post = select(func.count(WellnessPost.id)).where(
            WellnessPost.training_session_id.in_(session_ids)
        )
        result_post = await self.db.execute(query_post)
        post_count = result_post.scalar_one_or_none() or 0
        
        # Total esperado (attendances)
        query_att = select(func.count(Attendance.id)).where(
            and_(
                Attendance.training_session_id.in_(session_ids),
                Attendance.present == True
            )
        )
        result_att = await self.db.execute(query_att)
        expected_count = result_att.scalar_one_or_none() or 0
        
        return {
            'wellness_response_rate_pre': round((pre_count / expected_count) * 100, 2) if expected_count > 0 else None,
            'wellness_response_rate_post': round((post_count / expected_count) * 100, 2) if expected_count > 0 else None
        }

    async def _calculate_badges_count(self, team: Team, sessions: list[TrainingSession]) -> Optional[int]:
        """Conta atletas com badges no período."""
        if not sessions:
            return None
        
        # Buscar atletas ativos da equipe com badges
        # NOTA: Implementação simplificada - assumindo que Athlete tem campo badge_count
        # Em produção, seria necessário verificar a tabela de badges real
        query = select(func.count(func.distinct(Athlete.id))).where(
            and_(
                Athlete.team_id == team.id,
                Athlete.deleted_at.is_(None)
                # Adicionar filtro de badges quando tabela estiver disponível
            )
        )
        
        result = await self.db.execute(query)
        count = result.scalar_one_or_none() or 0
        
        return count

    def _calculate_deviation_metrics(
        self,
        sessions: list[TrainingSession],
        team: Team
    ) -> dict:
        """
        Calcula métricas de desvio usando alert_threshold_multiplier.
        """
        if not sessions:
            return {
                'deviation_count': None,
                'threshold_mean': None,
                'threshold_stddev': None
            }
        
        threshold_multiplier = float(team.alert_threshold_multiplier)
        deviations = []
        
        for session in sessions:
            rpe_avg = getattr(session, "rpe_avg", None)
            planned_rpe = getattr(session, "planned_rpe", None)
            if rpe_avg is not None and planned_rpe is not None:
                # Desvio = |real - planejado| × multiplier
                deviation = abs(float(rpe_avg) - float(planned_rpe)) * threshold_multiplier
                deviations.append(deviation)
        
        if not deviations:
            return {
                'deviation_count': 0,
                'threshold_mean': None,
                'threshold_stddev': None
            }
        
        # Contar sessões que excederam threshold
        deviation_count = sum(1 for d in deviations if d > threshold_multiplier)
        
        # Calcular média e desvio padrão
        mean = sum(deviations) / len(deviations)
        variance = sum((d - mean) ** 2 for d in deviations) / len(deviations)
        stddev = variance ** 0.5
        
        return {
            'deviation_count': deviation_count,
            'threshold_mean': round(mean, 2),
            'threshold_stddev': round(stddev, 2)
        }

    def _combine_metrics(
        self,
        weekly_metrics: list[TrainingAnalyticsCache],
        monthly_metrics: list[TrainingAnalyticsCache]
    ) -> dict:
        """
        Combina métricas weekly e monthly em um único resultado agregado.
        """
        all_metrics = weekly_metrics + monthly_metrics
        
        if not all_metrics:
            return {}
        
        # Somar total_sessions
        total_sessions = sum(m.total_sessions or 0 for m in all_metrics)
        
        # Calcular médias ponderadas dos focos
        focus_fields = [
            'avg_focus_attack_positional_pct',
            'avg_focus_defense_positional_pct',
            'avg_focus_transition_offense_pct',
            'avg_focus_transition_defense_pct',
            'avg_focus_attack_technical_pct',
            'avg_focus_defense_technical_pct',
            'avg_focus_physical_pct'
        ]
        
        combined = {
            'total_sessions': total_sessions
        }
        
        # Para cada campo, calcular média ponderada pelo total_sessions
        for field in focus_fields:
            values = [(getattr(m, field), m.total_sessions) for m in all_metrics if getattr(m, field) is not None and m.total_sessions]
            if values:
                weighted_sum = sum(float(val) * sessions for val, sessions in values)
                total_weight = sum(sessions for _, sessions in values)
                combined[field] = round(weighted_sum / total_weight, 2)
            else:
                combined[field] = None
        
        # Métricas de carga
        combined['avg_rpe'] = self._weighted_avg(all_metrics, 'avg_rpe')
        combined['avg_internal_load'] = self._weighted_avg(all_metrics, 'avg_internal_load')
        combined['total_internal_load'] = round(sum(float(m.total_internal_load or 0) for m in all_metrics), 2)
        
        # Métricas percentuais (média simples)
        combined['attendance_rate'] = self._simple_avg(all_metrics, 'attendance_rate')
        combined['wellness_response_rate_pre'] = self._simple_avg(all_metrics, 'wellness_response_rate_pre')
        combined['wellness_response_rate_post'] = self._simple_avg(all_metrics, 'wellness_response_rate_post')
        
        # Badges (soma)
        combined['athletes_with_badges_count'] = sum(m.athletes_with_badges_count or 0 for m in all_metrics)
        
        # Desvios
        combined['deviation_count'] = sum(m.deviation_count or 0 for m in all_metrics)
        combined['threshold_mean'] = self._weighted_avg(all_metrics, 'threshold_mean')
        combined['threshold_stddev'] = self._weighted_avg(all_metrics, 'threshold_stddev')
        
        return combined

    def _weighted_avg(self, metrics: list[TrainingAnalyticsCache], field: str) -> Optional[float]:
        """Calcula média ponderada por total_sessions."""
        values = [(getattr(m, field), m.total_sessions) for m in metrics if getattr(m, field) is not None and m.total_sessions]
        if not values:
            return None
        weighted_sum = sum(float(val) * sessions for val, sessions in values)
        total_weight = sum(sessions for _, sessions in values)
        return round(weighted_sum / total_weight, 2)

    def _simple_avg(self, metrics: list[TrainingAnalyticsCache], field: str) -> Optional[float]:
        """Calcula média simples."""
        values = [getattr(m, field) for m in metrics if getattr(m, field) is not None]
        if not values:
            return None
        return round(sum(float(v) for v in values) / len(values), 2)
