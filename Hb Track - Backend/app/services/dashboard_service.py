"""
Dashboard Service - Serviço agregado para o dashboard

Otimizações aplicadas:
1. Query única com múltiplos CTEs
2. Cache por team_id + season_id com TTL 120s
3. Pré-agregações via materialized views
4. Evita joins desnecessários
"""
import logging
from datetime import datetime, date, timedelta
from typing import Optional
from uuid import UUID
from functools import lru_cache
import hashlib
import json

from sqlalchemy import text, select, func, and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.dashboard import (
    DashboardSummaryResponse,
    DashboardAthleteStats,
    DashboardTrainingStats,
    DashboardTrainingSession,
    DashboardTrainingTrend,
    DashboardMatchStats,
    DashboardRecentMatch,
    DashboardNextMatch,
    DashboardWellnessStats,
    DashboardMedicalStats,
    DashboardAlert,
    DashboardNextTraining,
)

logger = logging.getLogger(__name__)

# =============================================================================
# CACHE SIMPLES EM MEMÓRIA (produção: usar Redis)
# =============================================================================

_dashboard_cache: dict[str, tuple[datetime, DashboardSummaryResponse]] = {}
CACHE_TTL_SECONDS = 120


def _get_cache_key(organization_id: UUID, team_id: Optional[UUID], season_id: Optional[UUID]) -> str:
    """Gera chave de cache única"""
    key_data = f"{organization_id}:{team_id or 'all'}:{season_id or 'current'}"
    return hashlib.md5(key_data.encode()).hexdigest()


def _get_from_cache(cache_key: str) -> Optional[DashboardSummaryResponse]:
    """Busca do cache se ainda válido"""
    if cache_key in _dashboard_cache:
        cached_at, data = _dashboard_cache[cache_key]
        if (datetime.utcnow() - cached_at).total_seconds() < CACHE_TTL_SECONDS:
            logger.debug(f"Dashboard cache HIT: {cache_key}")
            return data
        else:
            del _dashboard_cache[cache_key]
    return None


def _set_cache(cache_key: str, data: DashboardSummaryResponse) -> None:
    """Salva no cache"""
    _dashboard_cache[cache_key] = (datetime.utcnow(), data)
    logger.debug(f"Dashboard cache SET: {cache_key}")


def invalidate_dashboard_cache(organization_id: UUID, team_id: Optional[UUID] = None) -> None:
    """
    Invalida cache do dashboard.
    Chamar após salvar treino, finalizar jogo, etc.
    """
    keys_to_remove = []
    for key in _dashboard_cache:
        if str(organization_id) in key:
            if team_id is None or str(team_id) in key:
                keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del _dashboard_cache[key]
    
    logger.info(f"Dashboard cache invalidated: {len(keys_to_remove)} entries")


# =============================================================================
# SERVICE
# =============================================================================

class DashboardService:
    """
    Serviço otimizado para dashboard.
    
    Princípios:
    - Uma query grande > várias queries pequenas
    - Cache agressivo (120s TTL)
    - Usar materialized views quando disponíveis
    - Retornar apenas campos essenciais
    """

    @staticmethod
    async def get_dashboard_summary(
        db: AsyncSession,
        organization_id: UUID,
        team_id: Optional[UUID] = None,
        season_id: Optional[UUID] = None,
        use_cache: bool = True
    ) -> DashboardSummaryResponse:
        """
        Retorna resumo completo do dashboard em UMA requisição.
        
        Args:
            db: Sessão do banco
            organization_id: ID da organização
            team_id: Filtrar por equipe (opcional)
            season_id: Filtrar por temporada (opcional)
            use_cache: Usar cache (default True)
            
        Returns:
            DashboardSummaryResponse com todos os dados agregados
        """
        # 1. Verificar cache
        cache_key = _get_cache_key(organization_id, team_id, season_id)
        if use_cache:
            cached = _get_from_cache(cache_key)
            if cached:
                return cached

        logger.info(f"Dashboard cache MISS, building fresh data for org={organization_id}")

        # 2. Buscar dados em uma query otimizada
        try:
            # Buscar estatísticas de atletas
            try:
                athlete_stats = await DashboardService._get_athlete_stats(db, organization_id, team_id, season_id)
            except Exception as e:
                logger.warning(f"Error getting athlete stats: {e}")
                await db.rollback()
                athlete_stats = DashboardAthleteStats(total=0, ativas=0, lesionadas=0, dispensadas=0, dm=0)
            
            # Buscar estatísticas de treino
            try:
                training_stats = await DashboardService._get_training_stats(db, organization_id, team_id, season_id)
            except Exception as e:
                logger.warning(f"Error getting training stats: {e}")
                await db.rollback()
                training_stats = DashboardTrainingStats()
            
            # Buscar tendências de treino
            try:
                training_trends = await DashboardService._get_training_trends(db, organization_id, team_id, season_id)
            except Exception as e:
                logger.warning(f"Error getting training trends: {e}")
                await db.rollback()
                training_trends = []
            
            # Buscar estatísticas de jogos
            try:
                match_stats = await DashboardService._get_match_stats(db, organization_id, team_id, season_id)
            except Exception as e:
                logger.warning(f"Error getting match stats: {e}")
                await db.rollback()
                match_stats = DashboardMatchStats()
            
            # Buscar wellness
            try:
                wellness_stats = await DashboardService._get_wellness_stats(db, organization_id, team_id, season_id)
            except Exception as e:
                logger.warning(f"Error getting wellness stats: {e}")
                await db.rollback()
                wellness_stats = DashboardWellnessStats()
            
            # Buscar medical
            try:
                medical_stats = await DashboardService._get_medical_stats(db, organization_id, team_id, season_id)
            except Exception as e:
                logger.warning(f"Error getting medical stats: {e}")
                await db.rollback()
                medical_stats = DashboardMedicalStats()
            
            # Buscar alertas
            try:
                alerts = await DashboardService._get_alerts(db, organization_id, team_id)
            except Exception as e:
                logger.warning(f"Error getting alerts: {e}")
                await db.rollback()
                alerts = []
            
            # Buscar próximos eventos
            try:
                next_training = await DashboardService._get_next_training(db, organization_id, team_id)
            except Exception as e:
                logger.warning(f"Error getting next training: {e}")
                await db.rollback()
                next_training = None
                
            try:
                next_match = await DashboardService._get_next_match(db, organization_id, team_id)
            except Exception as e:
                logger.warning(f"Error getting next match: {e}")
                await db.rollback()
                next_match = None
            
            # Buscar nome do time e temporada
            team_name = None
            season_name = None
            if team_id:
                try:
                    result = await db.execute(
                        text("SELECT name FROM teams WHERE id = :team_id AND deleted_at IS NULL"),
                        {"team_id": str(team_id)}
                    ).fetchone()
                    if result:
                        team_name = result[0]
                except Exception as e:
                    logger.warning(f"Error getting team name: {e}")
                    await db.rollback()
            
            if season_id:
                try:
                    result = await db.execute(
                        text("SELECT name FROM seasons WHERE id = :season_id"),
                        {"season_id": str(season_id)}
                    ).fetchone()
                    if result:
                        season_name = result[0]
                except Exception as e:
                    logger.warning(f"Error getting season name: {e}")
                    await db.rollback()

            # 3. Montar resposta
            response = DashboardSummaryResponse(
                team_id=team_id,
                team_name=team_name,
                season_id=season_id,
                season_name=season_name,
                generated_at=datetime.utcnow(),
                cache_ttl_seconds=CACHE_TTL_SECONDS,
                athletes=athlete_stats,
                training=training_stats,
                training_trends=training_trends,
                matches=match_stats,
                wellness=wellness_stats,
                medical=medical_stats,
                alerts=alerts,
                next_training=next_training,
                next_match=next_match,
            )

            # 4. Salvar no cache
            if use_cache:
                _set_cache(cache_key, response)

            return response

        except Exception as e:
            logger.error(f"Error building dashboard: {e}")
            raise

    @staticmethod
    async def _get_athlete_stats(
        db: AsyncSession,
        organization_id: UUID,
        team_id: Optional[UUID],
        season_id: Optional[UUID]
    ) -> DashboardAthleteStats:
        """Estatísticas de atletas usando query otimizada"""
        query = text("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE state = 'ativa') as ativas,
                COUNT(*) FILTER (WHERE state = 'lesionada') as lesionadas,
                COUNT(*) FILTER (WHERE state = 'dispensada') as dispensadas
            FROM athletes a
            WHERE a.organization_id = :org_id
              AND a.deleted_at IS NULL
              AND (:team_id IS NULL OR EXISTS (
                  SELECT 1 FROM team_registrations tr
                  WHERE tr.athlete_id = a.id
                    AND tr.team_id = :team_id
                    AND tr.deleted_at IS NULL
                    AND (tr.end_at IS NULL OR tr.end_at >= CURRENT_DATE)
              ))
        """)
        
        result = await db.execute(query, {
            "org_id": str(organization_id),
            "team_id": str(team_id) if team_id else None
        }).fetchone()
        
        if result:
            return DashboardAthleteStats(
                total=result.total or 0,
                ativas=result.ativas or 0,
                lesionadas=result.lesionadas or 0,
                dispensadas=result.dispensadas or 0,
                dm=0  # TODO: implementar quando houver estado DM
            )
        
        return DashboardAthleteStats(total=0, ativas=0, lesionadas=0, dispensadas=0, dm=0)

    @staticmethod
    async def _get_training_stats(
        db: AsyncSession,
        organization_id: UUID,
        team_id: Optional[UUID],
        season_id: Optional[UUID]
    ) -> DashboardTrainingStats:
        """Estatísticas de treino usando materialized view"""
        # Usar a MV se disponível
        query = text("""
            WITH recent_trainings AS (
                SELECT
                    session_id,
                    session_at,
                    main_objective,
                    team_id,
                    presentes,
                    total_athletes,
                    attendance_rate,
                    avg_internal_load
                FROM mv_training_performance
                WHERE organization_id = :org_id
                  AND (:team_id IS NULL OR team_id = :team_id)
                  AND (:season_id IS NULL OR season_id = :season_id)
                ORDER BY session_at DESC
                LIMIT 10
            ),
            stats AS (
                SELECT
                    COUNT(*) as total_sessions,
                    AVG(attendance_rate) as avg_attendance,
                    AVG(avg_internal_load) as avg_load
                FROM mv_training_performance
                WHERE organization_id = :org_id
                  AND (:team_id IS NULL OR team_id = :team_id)
                  AND (:season_id IS NULL OR season_id = :season_id)
                  AND session_at >= CURRENT_DATE - INTERVAL '30 days'
            )
            SELECT
                s.total_sessions,
                s.avg_attendance,
                s.avg_load,
                json_agg(
                    json_build_object(
                        'session_id', rt.session_id,
                        'session_at', rt.session_at,
                        'main_objective', rt.main_objective,
                        'presentes', rt.presentes,
                        'total_athletes', rt.total_athletes,
                        'attendance_rate', rt.attendance_rate,
                        'avg_internal_load', rt.avg_internal_load
                    ) ORDER BY rt.session_at DESC
                ) as recent_sessions
            FROM stats s
            LEFT JOIN recent_trainings rt ON TRUE
            GROUP BY s.total_sessions, s.avg_attendance, s.avg_load
        """)
        
        try:
            result = await db.execute(query, {
                "org_id": str(organization_id),
                "team_id": str(team_id) if team_id else None,
                "season_id": str(season_id) if season_id else None
            }).fetchone()
            
            if result:
                recent = []
                if result.recent_sessions and result.recent_sessions != [None]:
                    for s in result.recent_sessions:
                        # Ignorar registros incompletos (evita erro de validaÇõÇœ com UUID/datetime nulos)
                        if not s or not s.get('session_id') or not s.get('session_at'):
                            continue
                        recent.append(DashboardTrainingSession(
                            session_id=s.get('session_id'),
                            session_at=s.get('session_at'),
                            main_objective=s.get('main_objective'),
                                presentes=s.get('presentes') or 0,
                                total_athletes=s.get('total_athletes') or 0,
                                attendance_rate=s.get('attendance_rate') or 0.0,
                                avg_internal_load=s.get('avg_internal_load')
                            ))
                
                return DashboardTrainingStats(
                    total_sessions=result.total_sessions or 0,
                    avg_attendance_rate=float(result.avg_attendance or 0),
                    avg_internal_load=float(result.avg_load or 0),
                    recent_sessions=recent
                )
        except Exception as e:
            logger.warning(f"Error getting training stats (MV may not exist): {e}")
        
        return DashboardTrainingStats(
            total_sessions=0,
            avg_attendance_rate=0.0,
            avg_internal_load=0.0,
            recent_sessions=[]
        )

    @staticmethod
    async def _get_training_trends(
        db: AsyncSession,
        organization_id: UUID,
        team_id: Optional[UUID],
        season_id: Optional[UUID]
    ) -> list[DashboardTrainingTrend]:
        """Tendências de treino por semana"""
        query = text("""
            SELECT
                date_trunc('week', session_at)::date as period_start,
                'Sem ' || EXTRACT(WEEK FROM session_at)::text as period_label,
                COUNT(*) as sessions_count,
                AVG(attendance_rate) as avg_attendance,
                AVG(avg_internal_load) as avg_load
            FROM mv_training_performance
            WHERE organization_id = :org_id
              AND (:team_id IS NULL OR team_id = :team_id)
              AND (:season_id IS NULL OR season_id = :season_id)
              AND session_at >= CURRENT_DATE - INTERVAL '12 weeks'
            GROUP BY date_trunc('week', session_at), EXTRACT(WEEK FROM session_at)
            ORDER BY period_start DESC
            LIMIT 12
        """)
        
        try:
            results = await db.execute(query, {
                "org_id": str(organization_id),
                "team_id": str(team_id) if team_id else None,
                "season_id": str(season_id) if season_id else None
            }).fetchall()
            
            return [
                DashboardTrainingTrend(
                    period_start=r.period_start,
                    period_label=r.period_label,
                    sessions_count=r.sessions_count,
                    avg_attendance=float(r.avg_attendance or 0),
                    avg_load=float(r.avg_load or 0)
                )
                for r in results
            ]
        except Exception as e:
            logger.warning(f"Error getting training trends: {e}")
            return []

    @staticmethod
    async def _get_match_stats(
        db: AsyncSession,
        organization_id: UUID,
        team_id: Optional[UUID],
        season_id: Optional[UUID]
    ) -> DashboardMatchStats:
        """Estatísticas de jogos"""
        # Query corrigida para schema real: goals em matches.final_score_*, org via teams
        query = text("""
            SELECT
                COUNT(*) as total_matches,
                COUNT(*) FILTER (
                    WHERE (mt.is_home = true AND m.final_score_home > m.final_score_away)
                       OR (mt.is_home = false AND m.final_score_away > m.final_score_home)
                ) as wins,
                COUNT(*) FILTER (WHERE m.final_score_home = m.final_score_away) as draws,
                COUNT(*) FILTER (
                    WHERE (mt.is_home = true AND m.final_score_home < m.final_score_away)
                       OR (mt.is_home = false AND m.final_score_away < m.final_score_home)
                ) as losses,
                COALESCE(SUM(CASE WHEN mt.is_home THEN m.final_score_home ELSE m.final_score_away END), 0) as goals_scored,
                COALESCE(SUM(CASE WHEN mt.is_home THEN m.final_score_away ELSE m.final_score_home END), 0) as goals_conceded
            FROM matches m
            JOIN match_teams mt ON m.id = mt.match_id
            JOIN teams t ON mt.team_id = t.id
            WHERE t.organization_id = :org_id
              AND m.deleted_at IS NULL
              AND m.status = 'finished'
              AND mt.is_our_team = true
              AND (:team_id IS NULL OR mt.team_id = :team_id)
              AND (:season_id IS NULL OR m.season_id = :season_id)
        """)
        
        try:
            result = await db.execute(query, {
                "org_id": str(organization_id),
                "team_id": str(team_id) if team_id else None,
                "season_id": str(season_id) if season_id else None
            }).fetchone()
            
            if result:
                return DashboardMatchStats(
                    total_matches=result.total_matches or 0,
                    wins=result.wins or 0,
                    draws=result.draws or 0,
                    losses=result.losses or 0,
                    goals_scored=result.goals_scored or 0,
                    goals_conceded=result.goals_conceded or 0,
                    recent_matches=[],
                    next_match=None
                )
        except Exception as e:
            logger.warning(f"Error getting match stats: {e}")
        
        return DashboardMatchStats()

    @staticmethod
    async def _get_wellness_stats(
        db: AsyncSession,
        organization_id: UUID,
        team_id: Optional[UUID],
        season_id: Optional[UUID]
    ) -> DashboardWellnessStats:
        """Estatísticas de wellness (últimos 7 dias)"""
        query = text("""
            SELECT
                AVG(sleep_quality) as avg_sleep,
                AVG(fatigue_pre) as avg_fatigue,
                AVG(stress_level) as avg_stress,
                AVG(readiness_score) as avg_mood,
                AVG(muscle_soreness) as avg_soreness,
                COUNT(DISTINCT wp.athlete_id) as athletes_reported,
                COUNT(DISTINCT CASE WHEN fatigue_pre >= 4 OR stress_level >= 4 THEN wp.athlete_id END) as at_risk
            FROM wellness_pre wp
            JOIN athletes a ON wp.athlete_id = a.id
            WHERE a.organization_id = :org_id
              AND a.deleted_at IS NULL
              AND wp.deleted_at IS NULL
              AND wp.filled_at >= CURRENT_DATE - INTERVAL '7 days'
              AND (:team_id IS NULL OR EXISTS (
                  SELECT 1 FROM team_registrations tr
                  WHERE tr.athlete_id = a.id
                    AND tr.team_id = :team_id
                    AND tr.deleted_at IS NULL
              ))
        """)
        
        try:
            result = await db.execute(query, {
                "org_id": str(organization_id),
                "team_id": str(team_id) if team_id else None
            }).fetchone()
            
            if result:
                # Calcular readiness score (0-100)
                # Fórmula simples: ((5-fadiga) + (5-stress) + sleep + mood) / 20 * 100
                avg_fatigue = float(result.avg_fatigue or 2.5)
                avg_stress = float(result.avg_stress or 2.5)
                avg_sleep = float(result.avg_sleep or 2.5)
                avg_mood = float(result.avg_mood or 2.5)
                
                readiness = ((5 - avg_fatigue) + (5 - avg_stress) + avg_sleep + avg_mood) / 20 * 100
                
                return DashboardWellnessStats(
                    avg_sleep_quality=avg_sleep,
                    avg_fatigue=avg_fatigue,
                    avg_stress=avg_stress,
                    avg_mood=avg_mood,
                    avg_soreness=float(result.avg_soreness or 2.5),
                    readiness_score=min(100, max(0, readiness)),
                    athletes_reported=result.athletes_reported or 0,
                    athletes_at_risk=result.at_risk or 0
                )
        except Exception as e:
            logger.warning(f"Error getting wellness stats: {e}")
        
        return DashboardWellnessStats()

    @staticmethod
    async def _get_medical_stats(
        db: AsyncSession,
        organization_id: UUID,
        team_id: Optional[UUID],
        season_id: Optional[UUID]
    ) -> DashboardMedicalStats:
        """Estatísticas médicas baseadas no estado do atleta"""
        query = text("""
            SELECT
                COUNT(*) FILTER (WHERE injured = true) as active_cases,
                COUNT(*) FILTER (
                    WHERE injured = true
                    AND updated_at >= CURRENT_DATE - INTERVAL '30 days'
                ) as recovering,
                0 as cleared_this_week
            FROM athletes a
            WHERE a.organization_id = :org_id
              AND a.deleted_at IS NULL
              AND (:team_id IS NULL OR EXISTS (
                  SELECT 1 FROM team_registrations tr
                  WHERE tr.athlete_id = a.id
                    AND tr.team_id = :team_id
                    AND tr.deleted_at IS NULL
              ))
        """)
        
        try:
            result = await db.execute(query, {
                "org_id": str(organization_id),
                "team_id": str(team_id) if team_id else None
            }).fetchone()
            
            if result:
                return DashboardMedicalStats(
                    active_cases=result.active_cases or 0,
                    recovering=result.recovering or 0,
                    cleared_this_week=result.cleared_this_week or 0,
                    avg_days_out=0.0  # TODO: calcular média
                )
        except Exception as e:
            logger.warning(f"Error getting medical stats: {e}")
            await db.rollback()  # Rollback para evitar transação abortada
        
        return DashboardMedicalStats()

    @staticmethod
    async def _get_alerts(
        db: AsyncSession,
        organization_id: UUID,
        team_id: Optional[UUID]
    ) -> list[DashboardAlert]:
        """Busca alertas ativos"""
        query = text("""
            SELECT
                alert_id,
                severity,
                title,
                message,
                created_at,
                athlete_id
            FROM alerts
            WHERE organization_id = :org_id
              AND dismissed_at IS NULL
              AND (:team_id IS NULL OR team_id = :team_id)
            ORDER BY
                CASE severity
                    WHEN 'critical' THEN 1
                    WHEN 'warning' THEN 2
                    ELSE 3
                END,
                created_at DESC
            LIMIT 10
        """)
        
        try:
            results = await db.execute(query, {
                "org_id": str(organization_id),
                "team_id": str(team_id) if team_id else None
            }).fetchall()
            
            return [
                DashboardAlert(
                    alert_id=r.alert_id,
                    severity=r.severity,
                    title=r.title,
                    message=r.message,
                    created_at=r.created_at,
                    athlete_id=r.athlete_id
                )
                for r in results
            ]
        except Exception as e:
            logger.warning(f"Error getting alerts (table may not exist): {e}")
            await db.rollback()  # Rollback para evitar transação abortada
            return []

    @staticmethod
    async def _get_next_training(
        db: AsyncSession,
        organization_id: UUID,
        team_id: Optional[UUID]
    ) -> Optional[DashboardNextTraining]:
        """Próximo treino agendado"""
        query = text("""
            SELECT
                ts.id as session_id,
                ts.session_at,
                ts.main_objective,
                t.name as team_name
            FROM training_sessions ts
            LEFT JOIN teams t ON ts.team_id = t.id
            WHERE ts.organization_id = :org_id
              AND ts.deleted_at IS NULL
              AND ts.session_at > NOW()
              AND (:team_id IS NULL OR ts.team_id = :team_id)
            ORDER BY ts.session_at ASC
            LIMIT 1
        """)
        
        try:
            result = await db.execute(query, {
                "org_id": str(organization_id),
                "team_id": str(team_id) if team_id else None
            }).fetchone()
            
            if result:
                return DashboardNextTraining(
                    session_id=result.session_id,
                    session_at=result.session_at,
                    main_objective=result.main_objective,
                    team_name=result.team_name
                )
        except Exception as e:
            logger.warning(f"Error getting next training: {e}")
            await db.rollback()  # Rollback para evitar transação abortada
        
        return None

    @staticmethod
    async def _get_next_match(
        db: AsyncSession,
        organization_id: UUID,
        team_id: Optional[UUID]
    ) -> Optional[DashboardNextMatch]:
        """Próximo jogo agendado"""
        # Query corrigida: org via teams, opponent via home/away logic
        query = text("""
            SELECT
                m.id as match_id,
                m.match_date as match_at,
                CASE 
                    WHEN mt.is_home THEN t_away.name 
                    ELSE t_home.name 
                END as opponent_name,
                m.venue as location,
                mt.is_home
            FROM matches m
            JOIN match_teams mt ON m.id = mt.match_id AND mt.is_our_team = true
            JOIN teams t ON mt.team_id = t.id
            LEFT JOIN teams t_home ON m.home_team_id = t_home.id
            LEFT JOIN teams t_away ON m.away_team_id = t_away.id
            WHERE t.organization_id = :org_id
              AND m.deleted_at IS NULL
              AND m.status = 'scheduled'
              AND m.match_date > CURRENT_DATE
              AND (:team_id IS NULL OR mt.team_id = :team_id)
            ORDER BY m.match_date ASC
            LIMIT 1
        """)
        
        try:
            result = await db.execute(query, {
                "org_id": str(organization_id),
                "team_id": str(team_id) if team_id else None
            }).fetchone()
            
            if result:
                return DashboardNextMatch(
                    match_id=result.match_id,
                    match_at=result.match_at,
                    opponent_name=result.opponent_name,
                    location=result.location,
                    is_home=result.is_home or True
                )
        except Exception as e:
            logger.warning(f"Error getting next match: {e}")
            await db.rollback()  # Rollback para evitar transação abortada
        
        return None
