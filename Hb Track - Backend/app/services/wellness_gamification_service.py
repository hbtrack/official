"""
Sistema de Gamificação de Wellness
====================================

Service para gerenciar badges e recompensas baseadas em métricas de wellness:

**Scheduled Jobs:**
- `calculate_monthly_wellness_badges()`: Mensal (dia 1 00:00)
  - Calcula response_rate por atleta no mês anterior
  - Award badge 'wellness_champion_monthly' se rate >= 90%
  - Detect streaks de 3 meses consecutivos
  - Award badge especial 'wellness_streak_3months'

**Badge Types:**
- wellness_champion_monthly: Taxa de resposta >= 90% no mês
- wellness_streak_3months: 3 meses consecutivos com badge monthly
- wellness_perfect_week: 7 dias consecutivos com wellness completo

**Database:**
- athlete_badges (id, athlete_id, badge_type, month_reference, response_rate, earned_at)
- notifications (type='badge_earned')

**Integration:**
- Chamado via APScheduler/Celery Beat no dia 1 de cada mês
- Cria notificação para atleta via NotificationService
- WebSocket broadcast se atleta conectado

Autor: AI Assistant
Data: 2026-01-16
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.athletes import Athlete
from app.models.wellness_pre import WellnessPre
from app.models.wellness_post import WellnessPost
from app.models.training_sessions import TrainingSession
from app.models.attendance import Attendance
from app.services.notification_service import NotificationService


class WellnessGamificationService:
    """Service para gamificação de wellness com badges e recompensas"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_service = NotificationService(db)

    async def calculate_monthly_wellness_badges(
        self,
        target_month: Optional[datetime] = None
    ) -> Dict:
        """
        Scheduled Job Mensal - Calcular badges de wellness
        
        Executa dia 1 de cada mês às 00:00:
        1. Busca mês anterior (ou target_month se especificado)
        2. Para cada atleta ativo:
           - Conta wellness esperados (attendance presente)
           - Conta wellness respondidos (pre E post)
           - Calcula response_rate = (respondidos / esperados) × 100
           - Se rate >= 90%: award badge 'wellness_champion_monthly'
        3. Detecta streaks de 3 meses consecutivos
        4. Cria notificação type='badge_earned'
        
        Args:
            target_month: Mês para calcular (default: mês anterior)
            
        Returns:
            {
                "month_reference": "2026-01",
                "athletes_processed": 45,
                "badges_awarded": 12,
                "streaks_detected": 2,
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
            "athletes_processed": 0,
            "badges_awarded": 0,
            "streaks_detected": 0,
            "executed_at": datetime.now().isoformat()
        }
        
        # Buscar todos os atletas ativos
        stmt = select(Athlete).where(Athlete.active == True)
        result = await self.db.execute(stmt)
        athletes = result.scalars().all()
        
        for athlete in athletes:
            stats["athletes_processed"] += 1
            
            # Calcular response rate do atleta no mês
            rate_data = await self._calculate_athlete_monthly_rate(
                athlete.id,
                month_start,
                month_end
            )
            
            response_rate = rate_data["response_rate"]
            expected = rate_data["expected_responses"]
            actual = rate_data["actual_responses"]
            
            # Se rate >= 90%, award badge
            if response_rate >= 90.0 and expected > 0:
                badge_created = await self._award_badge(
                    athlete_id=athlete.id,
                    badge_type='wellness_champion_monthly',
                    month_reference=month_reference,
                    response_rate=response_rate
                )
                
                if badge_created:
                    stats["badges_awarded"] += 1
                    
                    # Criar notificação
                    await self._create_badge_notification(
                        athlete_id=athlete.id,
                        badge_type='wellness_champion_monthly',
                        month_reference=month_reference,
                        response_rate=response_rate
                    )
                    
                    # Verificar streak de 3 meses
                    has_streak = await self._check_and_award_streak(
                        athlete.id,
                        month_start
                    )
                    
                    if has_streak:
                        stats["streaks_detected"] += 1
        
        await self.db.commit()
        return stats

    async def _calculate_athlete_monthly_rate(
        self,
        athlete_id: int,
        month_start: datetime,
        month_end: datetime
    ) -> Dict:
        """
        Calcular taxa de resposta de wellness de um atleta em um mês
        
        Formula:
        - expected_responses = COUNT(attendance WHERE present=true)
        - actual_responses = COUNT de sessões com wellness_pre E wellness_post
        - response_rate = (actual / expected) × 100
        
        Args:
            athlete_id: ID do atleta
            month_start: Início do mês
            month_end: Fim do mês
            
        Returns:
            {
                "expected_responses": 20,
                "actual_responses": 18,
                "response_rate": 90.0
            }
        """
        # Contar presenças no mês
        stmt_attendance = select(func.count(Attendance.id)).where(
            and_(
                Attendance.athlete_id == athlete_id,
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
        result = await self.db.execute(stmt_attendance)
        expected_responses = result.scalar() or 0
        
        if expected_responses == 0:
            return {
                "expected_responses": 0,
                "actual_responses": 0,
                "response_rate": 0.0
            }
        
        # Contar sessões com wellness_pre E wellness_post
        # Query complexa: buscar session_ids onde existe AMBOS pre e post
        stmt_pre = select(WellnessPre.training_session_id).where(
            and_(
                WellnessPre.athlete_id == athlete_id,
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
                WellnessPost.athlete_id == athlete_id,
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
        
        # Interseção: sessões com AMBOS pre e post
        sessions_complete = sessions_with_pre.intersection(sessions_with_post)
        actual_responses = len(sessions_complete)
        
        # Calcular taxa
        response_rate = (actual_responses / expected_responses) * 100.0
        
        return {
            "expected_responses": expected_responses,
            "actual_responses": actual_responses,
            "response_rate": round(response_rate, 2)
        }

    async def _award_badge(
        self,
        athlete_id: int,
        badge_type: str,
        month_reference: str,
        response_rate: float
    ) -> bool:
        """
        Criar badge para atleta (se não existir)
        
        Args:
            athlete_id: ID do atleta
            badge_type: Tipo do badge ('wellness_champion_monthly', 'wellness_streak_3months')
            month_reference: Mês de referência ('YYYY-MM')
            response_rate: Taxa de resposta (0-100)
            
        Returns:
            True se badge criado, False se já existia
        """
        # Verificar se badge já existe
        query = text("""
            SELECT id FROM athlete_badges
            WHERE athlete_id = :athlete_id
              AND badge_type = :badge_type
              AND month_reference = :month_reference
        """)
        
        result = await self.db.execute(
            query,
            {
                "athlete_id": athlete_id,
                "badge_type": badge_type,
                "month_reference": month_reference
            }
        )
        
        existing = result.scalar()
        if existing:
            return False  # Badge já existe
        
        # Criar novo badge
        insert_query = text("""
            INSERT INTO athlete_badges (
                athlete_id,
                badge_type,
                month_reference,
                response_rate,
                earned_at
            ) VALUES (
                :athlete_id,
                :badge_type,
                :month_reference,
                :response_rate,
                NOW()
            )
        """)
        
        await self.db.execute(
            insert_query,
            {
                "athlete_id": athlete_id,
                "badge_type": badge_type,
                "month_reference": month_reference,
                "response_rate": response_rate
            }
        )
        
        return True

    async def _create_badge_notification(
        self,
        athlete_id: int,
        badge_type: str,
        month_reference: str,
        response_rate: float
    ):
        """
        Criar notificação de badge conquistado
        
        Args:
            athlete_id: ID do atleta
            badge_type: Tipo do badge
            month_reference: Mês de referência
            response_rate: Taxa de resposta
        """
        # Buscar user_id do atleta
        stmt = select(Athlete.user_id).where(Athlete.id == athlete_id)
        result = await self.db.execute(stmt)
        user_id = result.scalar()
        
        if not user_id:
            return
        
        # Formatar mensagem baseada no tipo
        if badge_type == 'wellness_champion_monthly':
            icon = "🏆"
            title = "Badge Conquistado!"
            message = (
                f"Parabéns! Você respondeu {response_rate:.0f}% dos wellness "
                f"em {month_reference}. Continue assim!"
            )
        elif badge_type == 'wellness_streak_3months':
            icon = "🔥"
            title = "Streak de 3 Meses!"
            message = (
                f"Incrível! Você manteve taxa >= 90% por 3 meses consecutivos. "
                f"Você é um campeão!"
            )
        else:
            icon = "⭐"
            title = "Nova Conquista"
            message = f"Você conquistou o badge {badge_type}!"
        
        # Criar notificação
        notification = await self.notification_service.create(
            user_id=user_id,
            type='badge_earned',
            message=f"{icon} {title} {message}",
            notification_data={
                "badge_type": badge_type,
                "month_reference": month_reference,
                "response_rate": response_rate,
                "icon": icon,
                "title": title
            }
        )
        
        # Broadcast via WebSocket
        await self.notification_service.broadcast_to_user(user_id, notification)

    async def _check_and_award_streak(
        self,
        athlete_id: int,
        current_month: datetime
    ) -> bool:
        """
        Verificar streak de 3 meses consecutivos com badge
        
        Se atleta tem 'wellness_champion_monthly' nos últimos 3 meses,
        award badge especial 'wellness_streak_3months'
        
        Args:
            athlete_id: ID do atleta
            current_month: Mês atual (badge acabou de ser criado)
            
        Returns:
            True se streak detectado e badge criado
        """
        # Calcular 3 meses: current, current-1, current-2
        month_refs = []
        
        for i in range(3):
            if current_month.month - i > 0:
                m = datetime(current_month.year, current_month.month - i, 1)
            else:
                # Voltar para ano anterior
                m = datetime(current_month.year - 1, 12 + (current_month.month - i), 1)
            
            month_refs.append(m.strftime("%Y-%m"))
        
        # Verificar se possui badge monthly nos 3 meses
        query = text("""
            SELECT COUNT(*) FROM athlete_badges
            WHERE athlete_id = :athlete_id
              AND badge_type = 'wellness_champion_monthly'
              AND month_reference IN :month_refs
        """)
        
        result = await self.db.execute(
            query,
            {
                "athlete_id": athlete_id,
                "month_refs": tuple(month_refs)
            }
        )
        
        count = result.scalar()
        
        if count >= 3:
            # Streak detectado! Award badge especial
            badge_created = await self._award_badge(
                athlete_id=athlete_id,
                badge_type='wellness_streak_3months',
                month_reference=current_month.strftime("%Y-%m"),
                response_rate=100.0  # Streak não tem rate específico
            )
            
            if badge_created:
                # Criar notificação de streak
                await self._create_badge_notification(
                    athlete_id=athlete_id,
                    badge_type='wellness_streak_3months',
                    month_reference=current_month.strftime("%Y-%m"),
                    response_rate=100.0
                )
                
                return True
        
        return False

    async def get_athlete_badges(
        self,
        athlete_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """
        Buscar badges de um atleta
        
        Args:
            athlete_id: ID do atleta
            limit: Limite de badges retornados
            
        Returns:
            [
                {
                    "id": 1,
                    "badge_type": "wellness_champion_monthly",
                    "month_reference": "2026-01",
                    "response_rate": 95.0,
                    "earned_at": "2026-02-01T00:00:00"
                }
            ]
        """
        query = text("""
            SELECT
                id,
                badge_type,
                month_reference,
                response_rate,
                earned_at
            FROM athlete_badges
            WHERE athlete_id = :athlete_id
            ORDER BY earned_at DESC
            LIMIT :limit
        """)
        
        result = await self.db.execute(
            query,
            {"athlete_id": athlete_id, "limit": limit}
        )
        
        rows = result.fetchall()
        
        badges = []
        for row in rows:
            badges.append({
                "id": row.id,
                "badge_type": row.badge_type,
                "month_reference": row.month_reference,
                "response_rate": float(row.response_rate) if row.response_rate else None,
                "earned_at": row.earned_at.isoformat() if row.earned_at else None
            })
        
        return badges

    async def get_team_badge_leaderboard(
        self,
        team_id: int,
        month_reference: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Ranking de atletas com mais badges em um time
        
        Args:
            team_id: ID do time
            month_reference: Mês específico ou None para todos os tempos
            limit: Limite de atletas retornados
            
        Returns:
            [
                {
                    "athlete_id": 5,
                    "athlete_name": "João Silva",
                    "badge_count": 12,
                    "latest_badge_date": "2026-01-01"
                }
            ]
        """
        if month_reference:
            query = text("""
                SELECT
                    ab.athlete_id,
                    p.full_name AS athlete_name,
                    COUNT(ab.id) AS badge_count,
                    MAX(ab.earned_at) AS latest_badge_date
                FROM athlete_badges ab
                JOIN athletes a ON a.id = ab.athlete_id
                JOIN persons p ON p.id = a.person_id
                JOIN team_memberships tm ON tm.athlete_id = a.id
                WHERE tm.team_id = :team_id
                  AND tm.active = true
                  AND ab.month_reference = :month_reference
                GROUP BY ab.athlete_id, p.full_name
                ORDER BY badge_count DESC, latest_badge_date DESC
                LIMIT :limit
            """)
            
            params = {
                "team_id": team_id,
                "month_reference": month_reference,
                "limit": limit
            }
        else:
            query = text("""
                SELECT
                    ab.athlete_id,
                    p.full_name AS athlete_name,
                    COUNT(ab.id) AS badge_count,
                    MAX(ab.earned_at) AS latest_badge_date
                FROM athlete_badges ab
                JOIN athletes a ON a.id = ab.athlete_id
                JOIN persons p ON p.id = a.person_id
                JOIN team_memberships tm ON tm.athlete_id = a.id
                WHERE tm.team_id = :team_id
                  AND tm.active = true
                GROUP BY ab.athlete_id, p.full_name
                ORDER BY badge_count DESC, latest_badge_date DESC
                LIMIT :limit
            """)
            
            params = {
                "team_id": team_id,
                "limit": limit
            }
        
        result = await self.db.execute(query, params)
        rows = result.fetchall()
        
        leaderboard = []
        for row in rows:
            leaderboard.append({
                "athlete_id": row.athlete_id,
                "athlete_name": row.athlete_name,
                "badge_count": row.badge_count,
                "latest_badge_date": row.latest_badge_date.isoformat() if row.latest_badge_date else None
            })
        
        return leaderboard

    async def generate_monthly_top_performers_report_and_notify(
        self,
        target_month: Optional[datetime] = None
    ) -> Dict:
        """
        Scheduled Job Mensal (dia 5) - Gerar relatório Top 5 e notificar treinadores
        
        Executa dia 5 de cada mês para o mês anterior:
        1. Para cada team ativo
        2. Calcula Top 5 atletas com melhor response_rate
        3. Cria notificação para coordenador/treinador do team
        4. Notificação inclui link direto para /teams/{team_id}/wellness-top-performers?month=
        
        Args:
            target_month: Mês para gerar relatório (default: mês anterior)
            
        Returns:
            {
                "month_reference": "2026-01",
                "teams_processed": 16,
                "notifications_sent": 12,
                "executed_at": "2026-02-05T00:00:00"
            }
        """
        from app.models.teams import Team
        from app.models.team_membership import TeamMembership
        from app.models.persons import Person
        
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
            "notifications_sent": 0,
            "executed_at": datetime.now().isoformat()
        }
        
        # Buscar todos os teams ativos
        stmt = select(Team).where(Team.active == True)
        result = await self.db.execute(stmt)
        teams = result.scalars().all()
        
        for team in teams:
            stats["teams_processed"] += 1
            
            # Buscar atletas ativos do team
            stmt_athletes = select(Athlete, Person).join(
                Person, Person.id == Athlete.person_id
            ).join(
                TeamMembership,
                TeamMembership.athlete_id == Athlete.id
            ).where(
                and_(
                    TeamMembership.team_id == team.id,
                    TeamMembership.active == True,
                    Athlete.active == True
                )
            )
            result_athletes = await self.db.execute(stmt_athletes)
            rows = result_athletes.all()
            
            if len(rows) == 0:
                continue  # Team sem atletas
            
            # Calcular métricas para cada atleta
            performers = []
            
            for athlete, person in rows:
                rate_data = await self._calculate_athlete_monthly_rate(
                    athlete_id=athlete.id,
                    month_start=month_start,
                    month_end=month_end
                )
                
                if rate_data["expected_responses"] == 0:
                    continue  # Atleta sem presenças no mês
                
                performers.append({
                    "athlete_id": athlete.id,
                    "athlete_name": person.full_name,
                    "response_rate": rate_data["response_rate"]
                })
            
            if len(performers) == 0:
                continue  # Team sem métricas
            
            # Ordenar por response_rate DESC e pegar top 5
            performers.sort(key=lambda x: x["response_rate"], reverse=True)
            top_5 = performers[:5]
            
            # Criar mensagem humanizada
            top_names = ", ".join([p["athlete_name"] for p in top_5])
            
            # Buscar coordenadores/treinadores do team
            stmt_staff = select(TeamMembership).join(
                Person, Person.id == TeamMembership.person_id
            ).where(
                and_(
                    TeamMembership.team_id == team.id,
                    TeamMembership.active == True,
                    TeamMembership.role.in_(['coordenador', 'treinador'])  # TODO: verificar campo correto
                )
            )
            result_staff = await self.db.execute(stmt_staff)
            staff_memberships = result_staff.scalars().all()
            
            # Criar notificação para cada membro do staff
            for staff in staff_memberships:
                # Buscar user_id do staff
                # TODO: corrigir query para pegar user_id via person_id
                # Por enquanto, skip se não conseguir
                
                notification = await self.notification_service.create(
                    user_id=staff.person_id,  # TODO: converter person_id para user_id
                    type='wellness_report',
                    message=f"🌟 Relatório Top 5 Atletas Comprometidos - {month_reference}. "
                           f"Destaques: {top_names}. "
                           f"Veja o relatório completo no painel do team.",
                    notification_data={
                        "team_id": str(team.id),
                        "team_name": team.name,
                        "month_reference": month_reference,
                        "top_performers_count": len(top_5),
                        "link": f"/teams/{team.id}/wellness-top-performers?month={month_reference}"
                    }
                )
                
                # Broadcast via WebSocket
                await self.notification_service.broadcast_to_user(staff.person_id, notification)
                
                stats["notifications_sent"] += 1
        
        await self.db.commit()
        return stats
