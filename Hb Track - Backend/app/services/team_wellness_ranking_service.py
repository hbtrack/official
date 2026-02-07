"""
Sistema de Ranking de Equipes por Taxa de Resposta de Wellness
================================================================

Service para gerenciar rankings mensais de equipes baseados em métricas de wellness:

**Scheduled Jobs:**
- `calculate_monthly_team_rankings()`: Mensal (dia 1 00:00)
  - Calcular response_rate_pre e response_rate_post por team
  - Calcular avg_rate = (pre + post) / 2
  - Contar athletes_90plus (atletas com response_rate >= 90%)
  - Ordenar teams por avg_rate DESC
  - Inserir em team_wellness_rankings com rank 1,2,3...

**Métricas:**
- response_rate_pre = (COUNT(wellness_pre) / COUNT(attendance present)) × 100
- response_rate_post = (COUNT(wellness_post) / COUNT(attendance present)) × 100
- avg_rate = (response_rate_pre + response_rate_post) / 2
- athletes_90plus = COUNT(DISTINCT athlete_id WHERE athlete_rate >= 90%)

**Database:**
- team_wellness_rankings (id, team_id, month_reference, response_rate_pre, response_rate_post, avg_rate, rank, athletes_90plus, calculated_at)

**Integration:**
- Chamado via APScheduler/Celery Beat no dia 1 de cada mês
- Pode ser executado manualmente via endpoint

Autor: AI Assistant
Data: 2026-01-16
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.models.athlete import Athlete
from app.models.wellness_pre import WellnessPre
from app.models.wellness_post import WellnessPost
from app.models.training_session import TrainingSession
from app.models.attendance import Attendance


class TeamWellnessRankingService:
    """Service para gerenciar rankings de equipes por wellness"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_monthly_team_rankings(
        self,
        target_month: Optional[datetime] = None,
        organization_id: Optional[int] = None,
        commit: bool = True,
    ) -> Dict:
        """
        Scheduled Job Mensal - Calcular rankings de equipes
        
        Executa dia 1 de cada mês às 00:00:
        1. Busca mês anterior (ou target_month se especificado)
        2. Para cada team ativo:
           - Calcula response_rate_pre = (COUNT(wellness_pre) / COUNT(attendance present)) × 100
           - Calcula response_rate_post similar
           - Calcula avg_rate = (pre + post) / 2
           - Conta athletes_90plus (atletas com rate >= 90%)
        3. Ordena teams por avg_rate DESC
        4. Atribui rank (1, 2, 3, ...)
        5. Insere/atualiza em team_wellness_rankings
        
        Args:
            target_month: Mês para calcular (default: mês anterior)
            organization_id: Filtrar por organização (opcional)
            
        Returns:
            {
                "month_reference": "2026-01",
                "teams_processed": 16,
                "rankings_created": 16,
                "top_team": {"id": 5, "name": "Sub-20", "avg_rate": 95.5},
                "executed_at": "2026-02-01T00:00:00"
            }
        """
        # Determinar mês de referência
        if target_month is None:
            today = datetime.now()
            # Mês anterior
            if today.month == 1:
                target_month = datetime(today.year - 1, 12, 1)
            else:
                target_month = datetime(today.year, today.month - 1, 1)
        
        month_start = target_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Último dia do mês
        if month_start.month == 12:
            month_end = datetime(month_start.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(month_start.year, month_start.month + 1, 1) - timedelta(seconds=1)
        
        month_reference = month_start.strftime("%Y-%m")
        
        stats = {
            "month_reference": month_reference,
            "teams_processed": 0,
            "rankings_created": 0,
            "top_team": None,
            "executed_at": datetime.now().isoformat()
        }
        
        # Buscar todos os teams ativos
        today = datetime.now().date()
        stmt = select(Team).where(
            Team.deleted_at.is_(None),
            Team.active_from.isnot(None),
            or_(
                Team.active_until.is_(None),
                Team.active_until >= today,
            ),
        )
        if organization_id:
            stmt = stmt.where(Team.organization_id == organization_id)
        
        result = await self.db.execute(stmt)
        teams = result.scalars().all()
        
        # Calcular métricas para cada team
        team_metrics = []
        
        for team in teams:
            stats["teams_processed"] += 1
            
            # Calcular taxas de resposta
            metrics = await self._calculate_team_monthly_rates(
                team_id=team.id,
                month_start=month_start,
                month_end=month_end
            )
            
            # Contar atletas 90%+
            athletes_90plus = await self._count_athletes_90plus(
                team_id=team.id,
                month_start=month_start,
                month_end=month_end
            )
            
            team_metrics.append({
                "team_id": team.id,
                "team_name": team.name,
                "response_rate_pre": metrics["response_rate_pre"],
                "response_rate_post": metrics["response_rate_post"],
                "avg_rate": metrics["avg_rate"],
                "athletes_90plus": athletes_90plus
            })
        
        # Ordenar por avg_rate DESC
        team_metrics.sort(key=lambda x: x["avg_rate"], reverse=True)
        
        # Atribuir ranks
        for idx, team_data in enumerate(team_metrics):
            rank = idx + 1
            
            # Inserir/atualizar ranking
            await self._upsert_ranking(
                team_id=team_data["team_id"],
                month_reference=month_reference,
                response_rate_pre=team_data["response_rate_pre"],
                response_rate_post=team_data["response_rate_post"],
                avg_rate=team_data["avg_rate"],
                rank=rank,
                athletes_90plus=team_data["athletes_90plus"]
            )
            
            stats["rankings_created"] += 1
            
            # Guardar top team
            if rank == 1:
                stats["top_team"] = {
                    "id": team_data["team_id"],
                    "name": team_data["team_name"],
                    "avg_rate": team_data["avg_rate"]
                }
        
        if commit:
            await self.db.commit()
        return stats

    async def _calculate_team_monthly_rates(
        self,
        team_id: int,
        month_start: datetime,
        month_end: datetime
    ) -> Dict:
        """
        Calcular taxas de resposta de wellness de um team em um mês
        
        Formula:
        - expected_responses = COUNT(attendance WHERE present=true AND team_id=X)
        - actual_responses_pre = COUNT de sessões com wellness_pre
        - actual_responses_post = COUNT de sessões com wellness_post
        - response_rate_pre = (actual_pre / expected) × 100
        - response_rate_post = (actual_post / expected) × 100
        - avg_rate = (rate_pre + rate_post) / 2
        
        Args:
            team_id: ID do team
            month_start: Início do mês
            month_end: Fim do mês
            
        Returns:
            {
                "response_rate_pre": 85.0,
                "response_rate_post": 75.0,
                "avg_rate": 80.0,
                "expected_responses": 100,
                "actual_responses_pre": 85,
                "actual_responses_post": 75
            }
        """
        # Contar presenças (expected responses) no mês para este team
        stmt_attendance = select(func.count(Attendance.id)).where(
            and_(
                Attendance.present == True,
                Attendance.training_session_id.in_(
                    select(TrainingSession.id).where(
                        and_(
                            TrainingSession.team_id == team_id,
                            TrainingSession.session_at >= month_start,
                            TrainingSession.session_at <= month_end
                        )
                    )
                )
            )
        )
        result = await self.db.execute(stmt_attendance)
        expected_responses = result.scalar() or 0
        
        if expected_responses == 0:
            return {
                "response_rate_pre": 0.0,
                "response_rate_post": 0.0,
                "avg_rate": 0.0,
                "expected_responses": 0,
                "actual_responses_pre": 0,
                "actual_responses_post": 0
            }
        
        # Contar wellness_pre respondidos
        # Query: COUNT(DISTINCT (session_id, athlete_id)) em wellness_pre
        stmt_pre = select(func.count(WellnessPre.id.distinct())).where(
            WellnessPre.training_session_id.in_(
                select(TrainingSession.id).where(
                    and_(
                        TrainingSession.team_id == team_id,
                        TrainingSession.session_at >= month_start,
                        TrainingSession.session_at <= month_end
                    )
                )
            )
        )
        result_pre = await self.db.execute(stmt_pre)
        actual_responses_pre = result_pre.scalar() or 0
        
        # Contar wellness_post respondidos
        stmt_post = select(func.count(WellnessPost.id.distinct())).where(
            WellnessPost.training_session_id.in_(
                select(TrainingSession.id).where(
                    and_(
                        TrainingSession.team_id == team_id,
                        TrainingSession.session_at >= month_start,
                        TrainingSession.session_at <= month_end
                    )
                )
            )
        )
        result_post = await self.db.execute(stmt_post)
        actual_responses_post = result_post.scalar() or 0
        
        # Calcular taxas
        response_rate_pre = (actual_responses_pre / expected_responses) * 100.0
        response_rate_post = (actual_responses_post / expected_responses) * 100.0
        avg_rate = (response_rate_pre + response_rate_post) / 2.0
        
        return {
            "response_rate_pre": round(response_rate_pre, 2),
            "response_rate_post": round(response_rate_post, 2),
            "avg_rate": round(avg_rate, 2),
            "expected_responses": expected_responses,
            "actual_responses_pre": actual_responses_pre,
            "actual_responses_post": actual_responses_post
        }

    async def _count_athletes_90plus(
        self,
        team_id: int,
        month_start: datetime,
        month_end: datetime
    ) -> int:
        """
        Contar atletas com response_rate >= 90% no mês
        
        Usa lógica similar ao WellnessGamificationService:
        - Para cada atleta ativo do team
        - Calcular response_rate individual
        - Contar quantos têm rate >= 90%
        
        Args:
            team_id: ID do team
            month_start: Início do mês
            month_end: Fim do mês
            
        Returns:
            Quantidade de atletas com rate >= 90%
        """
        # Buscar atletas ativos do team (via team_memberships)
        from app.models.team_membership import TeamMembership
        
        stmt = select(Athlete).join(
            TeamMembership,
            TeamMembership.athlete_id == Athlete.id
        ).where(
            and_(
                TeamMembership.team_id == team_id,
                TeamMembership.active == True,
                Athlete.active == True
            )
        )
        result = await self.db.execute(stmt)
        athletes = result.scalars().all()
        
        count_90plus = 0
        
        for athlete in athletes:
            # Calcular response rate do atleta
            # Contar presenças
            stmt_attendance = select(func.count(Attendance.id)).where(
                and_(
                    Attendance.athlete_id == athlete.id,
                    Attendance.present == True,
                    Attendance.training_session_id.in_(
                        select(TrainingSession.id).where(
                            and_(
                                TrainingSession.session_at >= month_start,
                                TrainingSession.session_at <= month_end
                            )
                        )
                    )
                )
            )
            result_att = await self.db.execute(stmt_attendance)
            expected = result_att.scalar() or 0
            
            if expected == 0:
                continue
            
            # Contar sessões com wellness_pre E wellness_post
            stmt_pre = select(WellnessPre.training_session_id).where(
                and_(
                    WellnessPre.athlete_id == athlete.id,
                    WellnessPre.training_session_id.in_(
                        select(TrainingSession.id).where(
                            and_(
                                TrainingSession.session_at >= month_start,
                                TrainingSession.session_at <= month_end
                            )
                        )
                    )
                )
            ).distinct()
            
            result_pre = await self.db.execute(stmt_pre)
            sessions_with_pre = set(result_pre.scalars().all())
            
            stmt_post = select(WellnessPost.training_session_id).where(
                and_(
                    WellnessPost.athlete_id == athlete.id,
                    WellnessPost.training_session_id.in_(
                        select(TrainingSession.id).where(
                            and_(
                                TrainingSession.session_at >= month_start,
                                TrainingSession.session_at <= month_end
                            )
                        )
                    )
                )
            ).distinct()
            
            result_post = await self.db.execute(stmt_post)
            sessions_with_post = set(result_post.scalars().all())
            
            # Interseção
            sessions_complete = sessions_with_pre.intersection(sessions_with_post)
            actual = len(sessions_complete)
            
            # Calcular taxa
            response_rate = (actual / expected) * 100.0
            
            if response_rate >= 90.0:
                count_90plus += 1
        
        return count_90plus

    async def _upsert_ranking(
        self,
        team_id: int,
        month_reference: str,
        response_rate_pre: float,
        response_rate_post: float,
        avg_rate: float,
        rank: int,
        athletes_90plus: int
    ):
        """
        Inserir ou atualizar ranking de team
        
        Usa INSERT ... ON CONFLICT UPDATE devido ao unique constraint
        (team_id, month_reference)
        
        Args:
            team_id: ID do team
            month_reference: Mês de referência ('YYYY-MM')
            response_rate_pre: Taxa de resposta Pre
            response_rate_post: Taxa de resposta Post
            avg_rate: Média (pre + post) / 2
            rank: Posição no ranking (1, 2, 3, ...)
            athletes_90plus: Quantidade de atletas com rate >= 90%
        """
        query = text("""
            INSERT INTO team_wellness_rankings (
                team_id,
                month_reference,
                response_rate_pre,
                response_rate_post,
                avg_rate,
                rank,
                athletes_90plus_count,
                calculated_at
            ) VALUES (
                :team_id,
                :month_reference,
                :response_rate_pre,
                :response_rate_post,
                :avg_rate,
                :rank,
                :athletes_90plus,
                NOW()
            )
            ON CONFLICT (team_id, month_reference)
            DO UPDATE SET
                response_rate_pre = EXCLUDED.response_rate_pre,
                response_rate_post = EXCLUDED.response_rate_post,
                avg_rate = EXCLUDED.avg_rate,
                rank = EXCLUDED.rank,
                athletes_90plus_count = EXCLUDED.athletes_90plus_count,
                calculated_at = NOW()
        """)
        
        await self.db.execute(
            query,
            {
                "team_id": team_id,
                "month_reference": month_reference,
                "response_rate_pre": response_rate_pre,
                "response_rate_post": response_rate_post,
                "avg_rate": avg_rate,
                "rank": rank,
                "athletes_90plus": athletes_90plus
            }
        )

    async def get_rankings(
        self,
        month_reference: Optional[str] = None,
        organization_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Buscar rankings de equipes
        
        Args:
            month_reference: Mês específico ('YYYY-MM') ou None para mês atual
            organization_id: Filtrar por organização (opcional)
            limit: Limite de resultados
            
        Returns:
            [
                {
                    "team_id": 5,
                    "team_name": "Sub-20",
                    "response_rate_pre": 85.5,
                    "response_rate_post": 75.2,
                    "avg_rate": 80.35,
                    "rank": 1,
                    "athletes_90plus": 12,
                    "calculated_at": "2026-02-01T00:00:00"
                }
            ]
        """
        # Se não especificado, usar mês anterior
        if month_reference is None:
            today = datetime.now()
            if today.month == 1:
                target = datetime(today.year - 1, 12, 1)
            else:
                target = datetime(today.year, today.month - 1, 1)
            month_reference = target.strftime("%Y-%m")
        
        # Montar query
        if organization_id:
            query = text("""
                SELECT
                    twr.team_id,
                    t.name AS team_name,
                    twr.response_rate_pre,
                    twr.response_rate_post,
                    twr.avg_rate,
                    twr.rank,
                    twr.athletes_90plus_count,
                    twr.calculated_at
                FROM team_wellness_rankings twr
                JOIN teams t ON t.id = twr.team_id
                WHERE twr.month_reference = :month_reference
                  AND t.organization_id = :organization_id
                ORDER BY twr.rank ASC
                LIMIT :limit
            """)
            
            params = {
                "month_reference": month_reference,
                "organization_id": organization_id,
                "limit": limit
            }
        else:
            query = text("""
                SELECT
                    twr.team_id,
                    t.name AS team_name,
                    twr.response_rate_pre,
                    twr.response_rate_post,
                    twr.avg_rate,
                    twr.rank,
                    twr.athletes_90plus_count,
                    twr.calculated_at
                FROM team_wellness_rankings twr
                JOIN teams t ON t.id = twr.team_id
                WHERE twr.month_reference = :month_reference
                ORDER BY twr.rank ASC
                LIMIT :limit
            """)
            
            params = {
                "month_reference": month_reference,
                "limit": limit
            }
        
        result = await self.db.execute(query, params)
        rows = result.fetchall()
        
        rankings = []
        for row in rows:
            rankings.append({
                "team_id": row.team_id,
                "team_name": row.team_name,
                "response_rate_pre": float(row.response_rate_pre) if row.response_rate_pre else 0.0,
                "response_rate_post": float(row.response_rate_post) if row.response_rate_post else 0.0,
                "avg_rate": float(row.avg_rate) if row.avg_rate else 0.0,
                "rank": row.rank,
                "athletes_90plus": row.athletes_90plus_count,
                "calculated_at": row.calculated_at.isoformat() if row.calculated_at else None
            })
        
        return rankings

    async def get_team_athletes_90plus(
        self,
        team_id: int,
        month_reference: str
    ) -> List[Dict]:
        """
        Buscar lista de atletas 90%+ de um team em um mês
        
        Drill-down para o ranking: mostra quais atletas atingiram >= 90%
        
        Args:
            team_id: ID do team
            month_reference: Mês de referência ('YYYY-MM')
            
        Returns:
            [
                {
                    "athlete_id": 10,
                    "athlete_name": "João Silva",
                    "response_rate": 95.5,
                    "badge_earned": true
                }
            ]
        """
        # Converter month_reference para datetime
        year, month = month_reference.split("-")
        month_start = datetime(int(year), int(month), 1)
        if int(month) == 12:
            month_end = datetime(int(year) + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(int(year), int(month) + 1, 1) - timedelta(seconds=1)
        
        # Buscar atletas ativos do team
        from app.models.team_membership import TeamMembership
        from app.models.persons import Person
        
        stmt = select(Athlete, Person).join(
            Person, Person.id == Athlete.person_id
        ).join(
            TeamMembership,
            TeamMembership.athlete_id == Athlete.id
        ).where(
            and_(
                TeamMembership.team_id == team_id,
                TeamMembership.active == True,
                Athlete.active == True
            )
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        
        athletes_90plus = []
        
        for athlete, person in rows:
            # Calcular response rate do atleta
            stmt_attendance = select(func.count(Attendance.id)).where(
                and_(
                    Attendance.athlete_id == athlete.id,
                    Attendance.present == True,
                    Attendance.training_session_id.in_(
                        select(TrainingSession.id).where(
                            and_(
                                TrainingSession.session_at >= month_start,
                                TrainingSession.session_at <= month_end
                            )
                        )
                    )
                )
            )
            result_att = await self.db.execute(stmt_attendance)
            expected = result_att.scalar() or 0
            
            if expected == 0:
                continue
            
            # Contar sessões completas (pre E post)
            stmt_pre = select(WellnessPre.training_session_id).where(
                and_(
                    WellnessPre.athlete_id == athlete.id,
                    WellnessPre.training_session_id.in_(
                        select(TrainingSession.id).where(
                            and_(
                                TrainingSession.session_at >= month_start,
                                TrainingSession.session_at <= month_end
                            )
                        )
                    )
                )
            ).distinct()
            
            result_pre = await self.db.execute(stmt_pre)
            sessions_with_pre = set(result_pre.scalars().all())
            
            stmt_post = select(WellnessPost.training_session_id).where(
                and_(
                    WellnessPost.athlete_id == athlete.id,
                    WellnessPost.training_session_id.in_(
                        select(TrainingSession.id).where(
                            and_(
                                TrainingSession.session_at >= month_start,
                                TrainingSession.session_at <= month_end
                            )
                        )
                    )
                )
            ).distinct()
            
            result_post = await self.db.execute(stmt_post)
            sessions_with_post = set(result_post.scalars().all())
            
            sessions_complete = sessions_with_pre.intersection(sessions_with_post)
            actual = len(sessions_complete)
            
            response_rate = (actual / expected) * 100.0
            
            if response_rate >= 90.0:
                # Verificar se tem badge no mês
                query_badge = text("""
                    SELECT COUNT(*) FROM athlete_badges
                    WHERE athlete_id = :athlete_id
                      AND badge_type = 'wellness_champion_monthly'
                      AND month_reference = :month_reference
                """)
                
                result_badge = await self.db.execute(
                    query_badge,
                    {
                        "athlete_id": athlete.id,
                        "month_reference": month_reference
                    }
                )
                
                has_badge = result_badge.scalar() > 0
                
                athletes_90plus.append({
                    "athlete_id": athlete.id,
                    "athlete_name": person.full_name,
                    "response_rate": round(response_rate, 2),
                    "badge_earned": has_badge
                })
        
        # Ordenar por response_rate DESC
        athletes_90plus.sort(key=lambda x: x["response_rate"], reverse=True)
        
        return athletes_90plus
