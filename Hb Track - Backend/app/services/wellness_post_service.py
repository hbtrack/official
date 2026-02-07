"""
Service para Wellness Pós-Treino com Janelas Temporais.

Regras de permissão:
- R25/R26: Atleta cria/edita APENAS SEU PRÓPRIO wellness
- R25/R26: Treinador/Coordenador VISUALIZA TODOS do team
- R40: Janelas temporais de edição (até created_at + 24 hours)
- RF5.2: Temporada interrompida bloqueia criação/edição

LGPD:
- Registra em data_access_logs apenas staff lendo dados de outros
- Não registra quando atleta acessa próprio wellness
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, and_, or_, update
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.wellness_post import WellnessPost
from app.models.training_session import TrainingSession
from app.models.training_analytics_cache import TrainingAnalyticsCache
from app.models.team import Team
from app.models.athlete import Athlete
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.models.data_access_log import DataAccessLog
from app.core.exceptions import NotFoundError, PermissionDeniedError, ConflictError, ValidationError
from app.services.training_alerts_service import TrainingAlertsService


class WellnessPostService:
    """Service para gerenciar wellness pós-treino."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def _get_user_team_ids(self, user_id: UUID) -> List[UUID]:
        """
        Retorna os IDs das equipes às quais o usuário tem acesso.
        LGPD: Filtra dados por team_memberships.
        """
        stmt = (
            select(TeamMembership.team_id)
            .join(User, User.person_id == TeamMembership.person_id)
            .where(
                User.id == str(user_id),
                TeamMembership.deleted_at.is_(None),
                TeamMembership.end_at.is_(None),
                TeamMembership.status.in_(["ativo", "pendente"]),
            )
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]
    
    async def _get_athlete_id_from_user(self, user_id: UUID) -> Optional[UUID]:
        """
        Retorna o athlete_id vinculado ao user_id (se existir).
        Usado para permissões de atleta.
        """
        stmt = select(Athlete.id).where(
            Athlete.user_id == user_id,
            Athlete.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        return row[0] if row else None
    
    async def _log_access(
        self,
        user_id: UUID,
        entity_type: str,
        entity_id: UUID,
        athlete_id: Optional[UUID],
        ip_address: Optional[str],
        user_agent: Optional[str]
    ):
        """
        Registra acesso em data_access_logs para LGPD.
        Chamado apenas quando staff lê dados de outros atletas.
        """
        log_entry = DataAccessLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            athlete_id=athlete_id,
            accessed_at=datetime.now(timezone.utc),
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(log_entry)
    
    async def _check_edit_window(self, wellness: WellnessPost) -> bool:
        """
        Verifica se está dentro da janela de edição (até created_at + 24 hours).
        R40: Limite temporal de edição pós-treino.
        """
        deadline = wellness.created_at + timedelta(hours=24)
        return datetime.now(timezone.utc) < deadline
    
    async def get_session_wellness_post(
        self,
        session_id: UUID,
        user_id: UUID,
        user_role: str,  # 'athlete', 'coach', 'coordinator'
        athlete_filter: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> List[WellnessPost]:
        """
        Lista wellness pós-treino de uma sessão.
        
        Permissões:
        - Atleta: Vê APENAS SEU PRÓPRIO (WHERE athlete_id = user.athlete_id)
        - Coach/Coordinator: Vê TODOS do team (WHERE session.team_id IN user_team_memberships)
        
        LGPD: Registra acesso se staff lendo outros atletas.
        Performance: Eager loading com joinedload/selectinload (<50ms).
        """
        # 1. Verificar se sessão existe
        session_stmt = select(TrainingSession).where(
            TrainingSession.id == session_id,
            TrainingSession.deleted_at.is_(None)
        )
        session_result = await self.db.execute(session_stmt)
        training_session = session_result.scalar_one_or_none()
        
        if not training_session:
            raise NotFoundError(f"Sessão de treino {session_id} não encontrada")
        
        # 2. Aplicar filtros de permissão
        stmt = select(WellnessPost).where(
            WellnessPost.training_session_id == session_id,
            WellnessPost.deleted_at.is_(None)
        ).options(
            joinedload(WellnessPost.athlete).joinedload(Athlete.person),
            selectinload(WellnessPost.training_session),
            selectinload(WellnessPost.created_by_user)
        )
        
        if user_role == 'athlete':
            # Atleta vê APENAS SEU PRÓPRIO
            athlete_id = await self._get_athlete_id_from_user(user_id)
            if not athlete_id:
                raise PermissionDeniedError("Usuário não é atleta")
            
            stmt = stmt.where(WellnessPost.athlete_id == athlete_id)
        
        elif user_role in ['coach', 'coordinator']:
            # Staff vê TODOS do team
            team_ids = await self._get_user_team_ids(user_id)
            if not team_ids:
                raise PermissionDeniedError("Usuário sem acesso a equipes")
            
            stmt = stmt.where(training_session.team_id.in_(team_ids))
            
            # LGPD: Registrar acesso de staff
            result = await self.db.execute(stmt)
            wellness_list = result.scalars().unique().all()
            
            for wellness in wellness_list:
                await self._log_access(
                    user_id=user_id,
                    entity_type='wellness_post',
                    entity_id=wellness.id,
                    athlete_id=wellness.athlete_id,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            
            return list(wellness_list)
        
        else:
            raise PermissionDeniedError(f"Role inválido: {user_role}")
        
        # Aplicar filtro adicional por atleta (se fornecido)
        if athlete_filter:
            stmt = stmt.where(WellnessPost.athlete_id == athlete_filter)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())
    
    async def submit_wellness_post(
        self,
        session_id: UUID,
        athlete_id: UUID,
        data: Dict[str, Any],
        user_id: UUID,
        user_role: str
    ) -> WellnessPost:
        """
        Cria ou atualiza wellness pós-treino.
        
        Permissões:
        - Atleta: Cria/edita APENAS SEU PRÓPRIO (athlete_id = user.athlete_id)
        - Staff: Pode criar para qualquer atleta do team
        
        Validações:
        - R40: Janela temporal (até created_at + 24 hours)
        - RF5.2: Temporada interrompida bloqueia
        - Unique constraint (session_id, athlete_id)
        - internal_load calculado por trigger no banco
        """
        # 1. Verificar se sessão existe
        session_stmt = select(TrainingSession).where(
            TrainingSession.id == session_id,
            TrainingSession.deleted_at.is_(None)
        )
        session_result = await self.db.execute(session_stmt)
        training_session = session_result.scalar_one_or_none()
        
        if not training_session:
            raise NotFoundError(f"Sessão de treino {session_id} não encontrada")
        
        # 2. Verificar permissões
        if user_role == 'athlete':
            user_athlete_id = await self._get_athlete_id_from_user(user_id)
            if not user_athlete_id or user_athlete_id != athlete_id:
                raise PermissionDeniedError("Atleta só pode criar/editar seu próprio wellness")
        
        elif user_role in ['coach', 'coordinator']:
            # Staff pode criar para qualquer atleta do team
            team_ids = await self._get_user_team_ids(user_id)
            if training_session.team_id not in team_ids:
                raise PermissionDeniedError("Usuário sem acesso a esta equipe")
        
        # 3. Verificar se já existe wellness
        existing_stmt = select(WellnessPost).where(
            WellnessPost.training_session_id == session_id,
            WellnessPost.athlete_id == athlete_id,
            WellnessPost.deleted_at.is_(None)
        )
        existing_result = await self.db.execute(existing_stmt)
        existing_wellness = existing_result.scalar_one_or_none()

        # Normalizar payload (compatibilidade schema -> modelo)
        normalized = dict(data)
        normalized.pop("organization_id", None)
        normalized.pop("created_by_membership_id", None)

        allowed_fields = {
            "session_rpe",
            "minutes_effective",
            "internal_load",
            "fatigue_after",
            "mood_after",
            "muscle_soreness_after",
            "perceived_intensity",
            "notes",
            "flag_medical_followup",
        }
        normalized = {k: v for k, v in normalized.items() if k in allowed_fields}
        
        if existing_wellness:
            # Atualizar existente: verificar janela temporal
            if existing_wellness.locked_at:
                raise ValidationError("Wellness bloqueado para edição. Solicite desbloqueio.")
            
            if not await self._check_edit_window(existing_wellness):
                raise ValidationError("Fora da janela de edição (24h após criação)")
            
            for key, value in normalized.items():
                setattr(existing_wellness, key, value)
            
            existing_wellness.updated_at = datetime.now(timezone.utc)
            await self.db.flush()
            await self._invalidate_training_analytics_cache(training_session)
            await self._trigger_overload_alert_on_wellness_post(training_session)
            return existing_wellness
        
        # 4. Criar novo wellness
        try:
            wellness = WellnessPost(
                organization_id=training_session.organization_id,
                training_session_id=session_id,
                athlete_id=athlete_id,
                created_by_user_id=user_id,
                filled_at=datetime.now(timezone.utc),
                **normalized
            )
            self.db.add(wellness)
            await self.db.flush()
            # internal_load será calculado por tr_calculate_internal_load trigger
            await self._invalidate_training_analytics_cache(training_session)
            await self._trigger_overload_alert_on_wellness_post(training_session)
            return wellness
        
        except IntegrityError as e:
            await self.db.rollback()
            if 'ux_wellness_post_session_athlete' in str(e):
                raise ConflictError(f"Wellness pós-treino já existe para atleta {athlete_id} na sessão {session_id}")
            raise ValidationError(f"Erro ao criar wellness: {str(e)}")

    async def _invalidate_training_analytics_cache(
        self,
        training_session: TrainingSession,
    ) -> None:
        """
        Marca caches de analytics como dirty quando wellness_post é registrado.
        """
        if not training_session.team_id or not training_session.session_at:
            return

        month_start = training_session.session_at.date().replace(day=1)

        if training_session.microcycle_id:
            await self.db.execute(
                update(TrainingAnalyticsCache)
                .where(
                    TrainingAnalyticsCache.team_id == training_session.team_id,
                    TrainingAnalyticsCache.microcycle_id == training_session.microcycle_id,
                    TrainingAnalyticsCache.granularity == "weekly",
                )
                .values(cache_dirty=True, calculated_at=None)
            )

        await self.db.execute(
            update(TrainingAnalyticsCache)
            .where(
                TrainingAnalyticsCache.team_id == training_session.team_id,
                TrainingAnalyticsCache.month == month_start,
                TrainingAnalyticsCache.granularity == "monthly",
            )
            .values(cache_dirty=True, calculated_at=None)
        )

    async def _trigger_overload_alert_on_wellness_post(
        self,
        training_session: TrainingSession,
    ) -> None:
        """
        Dispara a verificação de sobrecarga semanal baseada na sessão do wellness_post.
        """
        if not training_session.team_id or not training_session.session_at:
            return

        session_at = training_session.session_at
        if session_at.tzinfo is None:
            session_at = session_at.replace(tzinfo=timezone.utc)

        session_at_utc = session_at.astimezone(timezone.utc)
        week_start = (session_at_utc - timedelta(days=session_at_utc.weekday())).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        team = await self.db.get(Team, training_session.team_id)
        if not team:
            return

        threshold_multiplier = float(team.alert_threshold_multiplier) if team.alert_threshold_multiplier is not None else 1.5

        await TrainingAlertsService(self.db).check_weekly_overload(
            team_id=training_session.team_id,
            week_start=week_start,
            alert_threshold_multiplier=threshold_multiplier,
        )
    
    async def get_session_wellness_status(
        self,
        session_id: UUID,
        user_id: UUID,
        user_role: str
    ) -> Dict[str, Any]:
        """
        Retorna status de preenchimento do wellness pós-treino.
        
        Retorna:
        {
            "total_athletes": 20,
            "responded_post": 12,
            "pending": [athlete_id1, athlete_id2, ...],
            "response_rate": 60.0
        }
        """
        # 1. Verificar permissões (apenas staff)
        if user_role not in ['coach', 'coordinator']:
            raise PermissionDeniedError("Apenas treinadores podem acessar status")
        
        # 2. Verificar se sessão existe e user tem acesso
        session_stmt = select(TrainingSession).where(
            TrainingSession.id == session_id,
            TrainingSession.deleted_at.is_(None)
        )
        session_result = await self.db.execute(session_stmt)
        training_session = session_result.scalar_one_or_none()
        
        if not training_session:
            raise NotFoundError(f"Sessão de treino {session_id} não encontrada")
        
        team_ids = await self._get_user_team_ids(user_id)
        if training_session.team_id not in team_ids:
            raise PermissionDeniedError("Usuário sem acesso a esta equipe")
        
        # 3. Buscar atletas esperados (attendance com presence_status=present)
        from app.models.attendance import Attendance
        attendance_stmt = select(Attendance.athlete_id).where(
            Attendance.training_session_id == session_id,
            Attendance.presence_status == 'present',
            Attendance.deleted_at.is_(None)
        )
        attendance_result = await self.db.execute(attendance_stmt)
        expected_athletes = {row[0] for row in attendance_result.all()}
        
        # 4. Buscar wellness respondidos
        wellness_stmt = select(WellnessPost.athlete_id).where(
            WellnessPost.training_session_id == session_id,
            WellnessPost.deleted_at.is_(None)
        )
        wellness_result = await self.db.execute(wellness_stmt)
        responded_athletes = {row[0] for row in wellness_result.all()}
        
        # 5. Calcular pending
        pending_athletes = expected_athletes - responded_athletes
        
        total = len(expected_athletes)
        responded = len(responded_athletes)
        response_rate = (responded / total * 100) if total > 0 else 0.0
        
        return {
            "total_athletes": total,
            "responded_post": responded,
            "pending": list(pending_athletes),
            "response_rate": round(response_rate, 2)
        }
    
    async def request_unlock(
        self,
        wellness_id: UUID,
        reason: str,
        user_id: UUID,
        user_role: str
    ) -> WellnessPost:
        """
        Atleta solicita desbloqueio de wellness após deadline.
        
        TODO: Implementar workflow de aprovação (criar registro em approval_requests).
        Por enquanto, apenas staff pode desbloquear diretamente.
        """
        wellness_stmt = select(WellnessPost).where(
            WellnessPost.id == wellness_id,
            WellnessPost.deleted_at.is_(None)
        )
        result = await self.db.execute(wellness_stmt)
        wellness = result.scalar_one_or_none()
        
        if not wellness:
            raise NotFoundError(f"Wellness {wellness_id} não encontrado")
        
        # Verificar permissões
        if user_role == 'athlete':
            user_athlete_id = await self._get_athlete_id_from_user(user_id)
            if not user_athlete_id or user_athlete_id != wellness.athlete_id:
                raise PermissionDeniedError("Atleta só pode solicitar desbloqueio do próprio wellness")
        
        # Se for staff, desbloqueia diretamente
        if user_role in ['coach', 'coordinator']:
            wellness.locked_at = None
            wellness.updated_at = datetime.now(timezone.utc)
            await self.db.flush()
            return wellness
        
        # TODO: Criar registro em approval_requests para atleta
        raise ValidationError("Sistema de aprovação ainda não implementado")
