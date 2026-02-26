"""
Service para gerenciamento de Sessões de Treino (Training Sessions).

Regras RAG aplicadas:
- R18: Estrutura de sessão de treino
- R40: Janelas de edição (10 min autor, 24h superior, admin com nota)
- RDB3: Soft delete
- RDB14: Paginação padrão
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context import ExecutionContext
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    ForbiddenError,
    SessionOutsideMicrocycleWeekError,
)
from app.models.training_session import TrainingSession
from app.models.training_microcycle import TrainingMicrocycle
from app.models.team import Team
from app.models.season import Season
from app.models.team_registration import TeamRegistration
from app.models.attendance import Attendance
from app.models.session_exercise import SessionExercise
from app.models.athlete import Athlete
from app.models.person import Person
from app.schemas.training_sessions import (
    TrainingSessionCreate,
    TrainingSessionUpdate,
    SessionClosureFieldErrors,
    SessionClosureValidationResult,
    SessionClosureResponse,
    AthleteWithoutPresence,
)
from app.services.training_suggestion_service import TrainingSuggestionService

logger = logging.getLogger(__name__)


class TrainingSessionService:
    """
    Service de Sessões de Treino.
    Ref: R18, R40, RDB3, RDB14
    """

    # R40: Janelas de edição
    AUTHOR_EDIT_WINDOW_MINUTES = 10
    SUPERIOR_EDIT_WINDOW_HOURS = 24
    
    # Step 15: Imutabilidade - sessões >60 dias são somente leitura
    IMMUTABILITY_DAYS = 60

    def __init__(self, db: AsyncSession, context: ExecutionContext):
        self.db = db
        self.context = context

    async def get_all(
        self,
        *,
        team_id: Optional[UUID] = None,
        season_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_deleted: bool = False,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[TrainingSession], int]:
        """
        Lista sessões de treino com filtros.
        Ref: RDB14 - Paginação padrão
        """
        query = select(TrainingSession).where(
            TrainingSession.organization_id == self.context.organization_id
        )

        if not include_deleted:
            query = query.where(TrainingSession.deleted_at.is_(None))

        if team_id:
            query = query.where(TrainingSession.team_id == team_id)

        if season_id:
            query = query.where(TrainingSession.season_id == season_id)

        if start_date:
            query = query.where(TrainingSession.session_at >= start_date)

        if end_date:
            query = query.where(TrainingSession.session_at <= end_date)

        # Count total - usar with_only_columns para evitar produto cartesiano
        count_query = query.with_only_columns(func.count()).order_by(None)
        result_count = await self.db.execute(count_query)
        total = result_count.scalar_one_or_none() or 0

        # Paginate
        query = query.order_by(TrainingSession.session_at.desc())
        query = query.offset((page - 1) * size).limit(size)

        result = await self.db.execute(query)
        sessions = list(result.scalars().all())

        if sessions:
            session_ids = [session.id for session in sessions]

            exercises_result = await self.db.execute(
                select(SessionExercise.session_id, func.count(SessionExercise.id))
                .where(
                    SessionExercise.session_id.in_(session_ids),
                    SessionExercise.deleted_at.is_(None),
                )
                .group_by(SessionExercise.session_id)
            )
            exercises_counts = {row[0]: row[1] for row in exercises_result.all()}

            attendance_result = await self.db.execute(
                select(
                    Attendance.training_session_id,
                    func.count(Attendance.id).filter(Attendance.presence_status == "present"),
                )
                .where(
                    Attendance.training_session_id.in_(session_ids),
                    Attendance.deleted_at.is_(None),
                )
                .group_by(Attendance.training_session_id)
            )
            attendance_counts = {row[0]: row[1] for row in attendance_result.all()}

            roster_result = await self.db.execute(
                select(
                    TrainingSession.id,
                    func.count(TeamRegistration.id),
                )
                .select_from(TrainingSession)
                .join(
                    TeamRegistration,
                    and_(
                        TeamRegistration.team_id == TrainingSession.team_id,
                        TeamRegistration.deleted_at.is_(None),
                        TeamRegistration.start_at <= TrainingSession.session_at,
                        or_(
                            TeamRegistration.end_at.is_(None),
                            TeamRegistration.end_at >= TrainingSession.session_at,
                        ),
                    ),
                )
                .where(TrainingSession.id.in_(session_ids))
                .group_by(TrainingSession.id)
            )
            roster_counts = {row[0]: row[1] for row in roster_result.all()}

            for session in sessions:
                setattr(session, "exercises_count", exercises_counts.get(session.id, 0))
                setattr(session, "attendance_present_count", attendance_counts.get(session.id, 0))
                setattr(session, "attendance_total_count", roster_counts.get(session.id, 0))

        logger.info(
            f"Listed {len(sessions)} training sessions for org {self.context.organization_id}"
        )
        return sessions, total

    async def get_by_id(
        self,
        session_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> TrainingSession:
        """
        Busca sessão de treino por ID.
        """
        query = select(TrainingSession).where(
            and_(
                TrainingSession.id == session_id,
                TrainingSession.organization_id == self.context.organization_id,
            )
        )

        if not include_deleted:
            query = query.where(TrainingSession.deleted_at.is_(None))

        result = await self.db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            raise NotFoundError(f"Training session {session_id} not found")

        return session

    async def create(self, data: TrainingSessionCreate) -> TrainingSession:
        """
        Cria nova sessão de treino.
        Ref: R18 - Sessão vinculada a team -> season -> organization
        """
        # Buscar team para obter organization_id
        team_query = select(Team).where(Team.id == data.team_id)
        team_result = await self.db.execute(team_query)
        team = team_result.scalar_one_or_none()

        if not team:
            raise NotFoundError(f"Team {data.team_id} not found")

        if team.organization_id != self.context.organization_id:
            raise ForbiddenError("Team belongs to another organization")

        # TASK-TRN-052/INV-TRN-008: Bloqueia criação se temporada estiver interrompida (RF5.2)
        if data.season_id:
            await self._check_season_locked(data.season_id)

        # INV-TRAIN-054: standalone = True se sem microciclo, False caso contrário
        standalone = data.microcycle_id is None
        
        # INV-TRAIN-057: validar que sessão está dentro da semana do microciclo
        if data.microcycle_id:
            microcycle_query = select(TrainingMicrocycle).where(
                TrainingMicrocycle.id == data.microcycle_id,
                TrainingMicrocycle.deleted_at.is_(None),
            )
            microcycle_result = await self.db.execute(microcycle_query)
            microcycle = microcycle_result.scalar_one_or_none()
            
            if not microcycle:
                raise NotFoundError(f"Microcycle {data.microcycle_id} not found")
            
            # Validar que session_at está dentro de [week_start, week_end]
            session_date = data.session_at.date()
            if not (microcycle.week_start <= session_date <= microcycle.week_end):
                raise SessionOutsideMicrocycleWeekError(
                    f"Sessão ({session_date}) fora da semana do microciclo "
                    f"[{microcycle.week_start} - {microcycle.week_end}]"
                )

        # season_id é opcional - Team não tem season_id
        session = TrainingSession(
            organization_id=team.organization_id,
            season_id=data.season_id,  # Pode ser None
            team_id=team.id,
            session_at=data.session_at,
            duration_planned_minutes=data.duration_planned_minutes,
            session_type=data.session_type,
            location=data.location,
            notes=data.notes,
            main_objective=data.main_objective,
            planned_load=data.planned_load,
            group_climate=data.group_climate,
            created_by_user_id=self.context.user_id,
            # Campos de foco e microciclo
            microcycle_id=data.microcycle_id,
            standalone=standalone,  # INV-TRAIN-054
            focus_attack_positional_pct=data.focus_attack_positional_pct,
            focus_defense_positional_pct=data.focus_defense_positional_pct,
            focus_transition_offense_pct=data.focus_transition_offense_pct,
            focus_transition_defense_pct=data.focus_transition_defense_pct,
            focus_attack_technical_pct=data.focus_attack_technical_pct,
            focus_defense_technical_pct=data.focus_defense_technical_pct,
            focus_physical_pct=data.focus_physical_pct,
            deviation_justification=data.deviation_justification,
        )

        if data.microcycle_id:
            errors = self.validate_session_publish(session)
            session.status = "scheduled" if not errors else "draft"

        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)

        await self._audit_session_action(
            session,
            action="create",
            context={
                "status": session.status,
                "team_id": str(session.team_id),
                "session_at": session.session_at.isoformat(),
            },
            new_value={"status": session.status},
        )

        logger.info(
            f"Created training session {session.id} for team {team.id} "
            f"by user {self.context.user_id}"
        )
        
        # Step 18: Auto-gerar sugestão de compensação se focus > 100%
        await self._check_and_generate_compensation_suggestion(session)
        
        return session

    async def update(
        self,
        session_id: UUID,
        data: TrainingSessionUpdate,
    ) -> TrainingSession:
        """
        Atualiza sessão de treino.
        Ref: R40 - Janelas de edição
        """
        session = await self.get_by_id(session_id)

        # R40: Verificar janela de edição
        self._validate_edit_permission(session, data)

        # Atualizar campos fornecidos
        update_data = data.model_dump(exclude_unset=True)

        # Normaliza regras de outcome para evitar violação de CHECKs
        if "execution_outcome" in update_data:
            outcome = update_data.get("execution_outcome")
            delay_minutes = update_data.get("delay_minutes", session.delay_minutes)
            duration_actual = update_data.get("duration_actual_minutes", session.duration_actual_minutes)
            cancellation_reason = update_data.get("cancellation_reason", session.cancellation_reason)

            if outcome == "on_time":
                update_data["delay_minutes"] = None
                update_data["duration_actual_minutes"] = None
                update_data["cancellation_reason"] = None
                update_data["deviation_justification"] = None
                update_data["planning_deviation_flag"] = False
            elif outcome == "delayed":
                if not delay_minutes or delay_minutes <= 0:
                    raise ValidationError("Informe o atraso em minutos")
                update_data["duration_actual_minutes"] = None
                update_data["cancellation_reason"] = None
                update_data["planning_deviation_flag"] = True
            elif outcome == "canceled":
                if not cancellation_reason or not cancellation_reason.strip():
                    raise ValidationError("Informe o motivo do cancelamento")
                update_data["delay_minutes"] = None
                update_data["duration_actual_minutes"] = None
                update_data["planning_deviation_flag"] = True
            elif outcome in ("shortened", "extended"):
                if not duration_actual or duration_actual <= 0:
                    raise ValidationError("Informe a duração real em minutos")
                update_data["delay_minutes"] = None
                update_data["cancellation_reason"] = None
                update_data["planning_deviation_flag"] = True

            if outcome and outcome != "on_time":
                justification = update_data.get("deviation_justification", session.deviation_justification)
                if not justification or len(justification.strip()) < self.MIN_JUSTIFICATION_LENGTH:
                    raise ValidationError(
                        f"Justificativa obrigatória (mínimo {self.MIN_JUSTIFICATION_LENGTH} caracteres)"
                    )
        for field, value in update_data.items():
            setattr(session, field, value)

        # Ajustar ended_at quando duração real é informada na revisão
        if "duration_actual_minutes" in update_data and update_data.get("duration_actual_minutes"):
            if session.started_at is None:
                session.started_at = session.session_at
            session.ended_at = session.started_at + timedelta(
                minutes=int(update_data["duration_actual_minutes"])
            )


        await self.db.flush()
        await self.db.refresh(session)

        logger.info(
            f"Updated training session {session_id} by user {self.context.user_id}"
        )

        await self._audit_session_action(
            session,
            action="update",
            context={
                "status": session.status,
                "fields": list(update_data.keys()),
            },
        )
        
        # Step 18: Auto-gerar sugestão de compensação se focus > 100%
        await self._check_and_generate_compensation_suggestion(session)
        
        return session

    def validate_session_publish(self, session: TrainingSession) -> dict:
        """
        Valida se a sessão possui dados mínimos para publicação (draft -> scheduled).
        """
        errors: dict[str, str] = {}

        if not session.session_at:
            errors["session_at"] = "Data/hora é obrigatória para agendar"
        if not session.duration_planned_minutes or session.duration_planned_minutes <= 0:
            errors["duration_planned_minutes"] = "Duração planejada é obrigatória"
        if not session.location or not session.location.strip():
            errors["location"] = "Local do treino é obrigatório"
        if not session.session_type:
            errors["session_type"] = "Tipo de sessão é obrigatório"
        if not session.main_objective or not session.main_objective.strip():
            errors["main_objective"] = "Objetivo principal é obrigatório"

        return errors

    async def publish_session(self, session_id: UUID) -> tuple[TrainingSession, dict]:
        """
        Publica um rascunho completo (draft -> scheduled).
        """
        session = await self.get_by_id(session_id)

        if session.status != "draft":
            raise ValidationError("Sessão não está em rascunho")

        errors = self.validate_session_publish(session)
        if errors:
            return session, errors

        previous_status = session.status
        session.status = "scheduled"

        await self.db.flush()
        await self.db.refresh(session)

        await self._audit_session_action(
            session,
            action="publish",
            context={"status": session.status},
            old_value={"status": previous_status},
            new_value={"status": session.status},
        )

        logger.info(
            f"Sessão {session_id} publicada por {self.context.user_id}"
        )

        return session, {}

    def _validate_edit_permission(
        self,
        session: TrainingSession,
        data: TrainingSessionUpdate,
    ) -> None:
        """
        Valida permissão de edição de sessão.

        Regras (INV-TRAIN-004 + INV-TRAIN-029):
        - Autor (treinador): pode editar sessão scheduled até 10min antes de session_at
        - Superior (coordenador/dirigente): pode editar pending_review até 24h após ended_at
        - Sessões > 60 dias são somente leitura (exceto soft delete)
        - Atletas não podem editar
        """
        now = datetime.now(timezone.utc)
        session_at = session.session_at

        # Step 15: Validar imutabilidade de sessões antigas (>60 dias)
        immutability_threshold = now - timedelta(days=self.IMMUTABILITY_DAYS)
        if session_at < immutability_threshold:
            raise ForbiddenError(
                f"Training session is older than {self.IMMUTABILITY_DAYS} days and is read-only. "
                "Only soft delete with reason is permitted for archived sessions."
            )

        # Dirigentes, Coordenadores e Treinadores podem editar
        allowed_roles = ["dirigente", "coordenador", "treinador"]
        if not (self.context.is_superadmin or self.context.role_code in allowed_roles):
            raise ForbiddenError(
                "Apenas dirigentes, coordenadores e treinadores podem editar sessões de treino."
            )

        # INV-TRAIN-004: Janelas de edição por autoria/hierarquia
        superior_roles = ["dirigente", "coordenador"]
        is_superior = self.context.is_superadmin or self.context.role_code in superior_roles

        # Para sessão scheduled: treinador pode editar até 10min antes de session_at
        if session.status == "scheduled" and not is_superior:
            author_deadline = session_at - timedelta(minutes=self.AUTHOR_EDIT_WINDOW_MINUTES)
            if now > author_deadline:
                raise ForbiddenError(
                    f"Prazo de edição do autor expirado. "
                    f"Treinadores podem editar até {self.AUTHOR_EDIT_WINDOW_MINUTES} minutos antes do início."
                )

        # Para sessão pending_review: superior pode editar até 24h após ended_at
        if session.status == "pending_review" and session.ended_at:
            superior_deadline = session.ended_at + timedelta(hours=self.SUPERIOR_EDIT_WINDOW_HOURS)
            if now > superior_deadline:
                raise ForbiddenError(
                    f"Prazo de edição do superior expirado. "
                    f"Edição permitida até {self.SUPERIOR_EDIT_WINDOW_HOURS} horas após o término da sessão."
                )

        # Restrições por estado
        update_fields = set(data.model_dump(exclude_unset=True).keys())

        if session.status == "readonly":
            raise ForbiddenError("Sessão congelada. Revisão já concluída.")

        if session.status == "in_progress":
            raise ForbiddenError("Sessão em andamento não pode ser editada. Aguarde a revisão.")

        if session.status == "pending_review":
            allowed_fields = {
                "execution_outcome",
                "delay_minutes",
                "cancellation_reason",
                "duration_actual_minutes",
                "deviation_justification",
            }
            if not update_fields.issubset(allowed_fields):
                raise ForbiddenError(
                    "Somente campos da revisão operacional podem ser editados neste estado."
                )

        if session.status == "scheduled":
            allowed_fields = {
                "secondary_objective",
                "notes",
                "planned_load",
                "intensity_target",
                "group_climate",
                "highlight",
                "next_corrections",
                "focus_attack_positional_pct",
                "focus_defense_positional_pct",
                "focus_transition_offense_pct",
                "focus_transition_defense_pct",
                "focus_attack_technical_pct",
                "focus_defense_technical_pct",
                "focus_physical_pct",
                "deviation_justification",
            }
            if not update_fields.issubset(allowed_fields):
                raise ForbiddenError(
                    "Sessão agendada: apenas focos, notas e campos complementares podem ser editados."
                )

    async def soft_delete(
        self,
        session_id: UUID,
        reason: str,
    ) -> TrainingSession:
        """
        Soft delete de sessão de treino.
        Ref: RDB3 - Soft delete
        
        Step 15: Permitido mesmo para sessões >60 dias (apenas operação permitida),
        mas reason é obrigatório.
        """
        session = await self.get_by_id(session_id)
        
        # Step 15: Validar que reason está presente para sessões antigas
        if not reason or not reason.strip():
            raise ValidationError("Deletion reason is required")

        session.deleted_at = datetime.now(timezone.utc)
        session.deleted_reason = reason

        await self.db.flush()
        await self.db.refresh(session)

        logger.info(
            f"Soft deleted training session {session_id} by user {self.context.user_id}: {reason}"
        )
        return session

    async def restore(self, session_id: UUID) -> TrainingSession:
        """
        Restaura sessão de treino deletada.
        Ref: RDB3 - Restore
        """
        session = await self.get_by_id(session_id, include_deleted=True)

        if session.deleted_at is None:
            raise ValidationError("Training session is not deleted")

        session.deleted_at = None
        session.deleted_reason = None

        await self.db.flush()
        await self.db.refresh(session)

        logger.info(
            f"Restored training session {session_id} by user {self.context.user_id}"
        )
        return session

    async def get_by_team_and_date(
        self,
        team_id: UUID,
        session_date: datetime,
    ) -> Optional[TrainingSession]:
        """
        Busca sessão por time e data (para evitar duplicatas no mesmo dia).
        """
        # Busca sessões no mesmo dia
        start_of_day = session_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        query = select(TrainingSession).where(
            and_(
                TrainingSession.team_id == team_id,
                TrainingSession.session_at >= start_of_day,
                TrainingSession.session_at < end_of_day,
                TrainingSession.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    # ========== NOVOS MÉTODOS (TRAINNIG.MD) ==========

    # Constantes para validação de revisão operacional
    MIN_JUSTIFICATION_LENGTH = 50

    async def _get_athletes_without_presence(
        self,
        session: TrainingSession,
    ) -> List[AthleteWithoutPresence]:
        """
        Retorna lista de atletas ativos na equipe sem presença registrada.

        Regra: Para fechar sessão, todo team_registration.is_active deve ter
        attendance.presence_status IS NOT NULL.
        """
        # Buscar team_registrations ativos para o time da sessão
        # is_active = end_at IS NULL AND deleted_at IS NULL
        active_registrations_query = (
            select(TeamRegistration)
            .options(
                joinedload(TeamRegistration.athlete).joinedload(Athlete.person)
            )
            .where(
                and_(
                    TeamRegistration.team_id == session.team_id,
                    TeamRegistration.end_at.is_(None),
                    TeamRegistration.deleted_at.is_(None),
                )
            )
        )
        result = await self.db.execute(active_registrations_query)
        active_registrations = result.scalars().unique().all()

        # Buscar presenças já registradas para esta sessão
        attendance_query = select(Attendance.athlete_id).where(
            and_(
                Attendance.training_session_id == session.id,
                Attendance.presence_status.isnot(None),
                Attendance.deleted_at.is_(None),
            )
        )
        attendance_result = await self.db.execute(attendance_query)
        athletes_with_presence = {row[0] for row in attendance_result.fetchall()}

        # Filtrar atletas sem presença
        athletes_without = []
        for reg in active_registrations:
            if reg.athlete_id not in athletes_with_presence:
                athlete_name = "Atleta"
                if reg.athlete and reg.athlete.person:
                    person = reg.athlete.person
                    athlete_name = f"{person.first_name} {person.last_name}".strip()
                elif reg.athlete:
                    athlete_name = f"Atleta {str(reg.athlete_id)[:8]}"

                athletes_without.append(AthleteWithoutPresence(
                    athlete_id=reg.athlete_id,
                    athlete_name=athlete_name,
                    team_registration_id=reg.id,
                ))

        return athletes_without

    async def validate_session_closure(
        self,
        session_id: UUID,
    ) -> SessionClosureValidationResult:
        """
        Valida se uma sessão pode ter a revisão operacional finalizada.

        Regras de validação:
        1. Status deve ser 'pending_review'
        2. execution_outcome obrigatório
        3. Campos condicionais conforme outcome (delay, duration, cancellation)
        4. Justificativa obrigatória quando outcome != on_time
        5. Presenças completas (exceto quando canceled)

        Returns:
            SessionClosureValidationResult com can_close e field_errors
        """
        session = await self.get_by_id(session_id)
        field_errors = SessionClosureFieldErrors()
        error_code: Optional[str] = None
        athletes_without_presence: List[AthleteWithoutPresence] = []

        # 1. Validar status
        if session.status != "pending_review":
            error_code = "INVALID_STATUS"
            field_errors.execution_outcome = (
                f"Sessão não está em revisão operacional (status: {session.status})"
            )
        else:
            outcome = session.execution_outcome

            if not outcome:
                error_code = "MISSING_OUTCOME"
                field_errors.execution_outcome = "Resultado da execução é obrigatório"
            elif outcome == "delayed":
                if not session.delay_minutes or session.delay_minutes <= 0:
                    error_code = "MISSING_DELAY"
                    field_errors.delay_minutes = "Informe o atraso em minutos"
            elif outcome == "canceled":
                if not session.cancellation_reason or not session.cancellation_reason.strip():
                    error_code = "MISSING_CANCELLATION"
                    field_errors.cancellation_reason = "Informe o motivo do cancelamento"
            elif outcome in ["shortened", "extended"]:
                if not session.duration_actual_minutes or session.duration_actual_minutes <= 0:
                    error_code = "MISSING_DURATION"
                    field_errors.duration_actual_minutes = "Informe a duração real em minutos"

            # Justificativa obrigatória se execução != on_time
            if outcome and outcome != "on_time":
                justification = session.deviation_justification or ""
                if len(justification.strip()) < self.MIN_JUSTIFICATION_LENGTH:
                    if not error_code:
                        error_code = "MISSING_DEVIATION_JUSTIFICATION"
                    field_errors.deviation_justification = (
                        f"Justificativa obrigatória (mínimo {self.MIN_JUSTIFICATION_LENGTH} caracteres)"
                    )

            # Presenças completas (exceto se cancelado)
            if outcome != "canceled":
                athletes_without_presence = await self._get_athletes_without_presence(session)
                if athletes_without_presence:
                    if not error_code:
                        error_code = "INCOMPLETE_PRESENCE"
                    count = len(athletes_without_presence)
                    names = ', '.join(a.athlete_name for a in athletes_without_presence[:3])
                    if count > 3:
                        names += f' e mais {count - 3}'
                    field_errors.presence = f'{count} atleta(s) sem presença registrada: {names}'

        can_close = error_code is None

        return SessionClosureValidationResult(
            can_close=can_close,
            error_code=error_code,
            field_errors=field_errors,
            athletes_without_presence=athletes_without_presence,
        )

    async def close_session(
        self,
        session_id: UUID,
        *,
        force: bool = False,
    ) -> SessionClosureResponse:
        """
        Finaliza a revisão operacional e congela a sessão.

        Validações (todas bloqueantes):
        - Status deve ser pending_review
        - execution_outcome e campos condicionais
        - Justificativa obrigatória se execução != on_time
        - Presenças completas (exceto cancelado)

        Args:
            session_id: ID da sessão
            force: Se True, ignora validações (apenas admin) - NÃO IMPLEMENTADO

        Returns:
            SessionClosureResponse com success, session ou validation

        Ref: Fluxo de revisão operacional (pending_review -> readonly)
        """
        # Executar validação
        validation = await self.validate_session_closure(session_id)

        if not validation.can_close:
            logger.warning(
                f"Sessão {session_id} não pode ser fechada: {validation.error_code}"
            )
            return SessionClosureResponse(
                success=False,
                session=None,
                validation=validation,
                message=f"Sessão não pode ser fechada: {validation.error_code}",
            )

        # Buscar sessão para finalizar revisão
        session = await self.get_by_id(session_id)

        # Ajustar timestamps de execução
        if session.started_at is None:
            session.started_at = session.session_at

        if session.duration_actual_minutes:
            session.ended_at = session.started_at + timedelta(
                minutes=int(session.duration_actual_minutes)
            )
        elif session.ended_at is None:
            session.ended_at = session.session_at + timedelta(
                minutes=int(session.duration_planned_minutes or 120)
            )

        # Flag de desvio quando execução não prevista
        session.planning_deviation_flag = session.execution_outcome != "on_time"

        # Concluir revisão (congelamento)
        session.post_review_completed_at = datetime.now(timezone.utc)
        session.post_review_completed_by_user_id = self.context.user_id
        session.closed_at = session.post_review_completed_at
        session.closed_by_user_id = self.context.user_id
        session.status = "readonly"

        await self.db.flush()
        await self.db.refresh(session)

        await self._audit_session_action(
            session,
            action="close",
            context={"status": session.status},
            old_value={"status": "pending_review"},
            new_value={"status": session.status},
        )

        logger.info(
            f"Sessão {session_id} revisada e congelada pelo usuário {self.context.user_id}"
        )

        # Importar schema de resposta para converter
        from app.schemas.training_sessions import TrainingSessionResponse

        return SessionClosureResponse(
            success=True,
            session=TrainingSessionResponse.model_validate(session),
            validation=None,
            message="Revisão concluída e sessão congelada",
        )

    async def _check_season_locked(self, season_id: UUID) -> None:
        """
        Verifica se temporada está interrompida (RF5.2 / TASK-TRN-052).

        Levanta ValidationError se `interrupted_at` estiver preenchido,
        impedindo a criação de treinos em temporadas suspensas.
        """
        season = await self.db.get(Season, season_id)
        if season and season.interrupted_at:
            raise ValidationError("season_locked")

    async def _audit_session_action(
        self,
        session: TrainingSession,
        *,
        action: str,
        context: dict | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
    ) -> None:
        payload = {
            "entity": "training_session",
            "entity_id": str(session.id),
            "action": action,
            "actor_id": str(self.context.user_id) if self.context.user_id else None,
            "context": json.dumps(context, default=str) if context is not None else None,
            "old_value": json.dumps(old_value, default=str) if old_value is not None else None,
            "new_value": json.dumps(new_value, default=str) if new_value is not None else None,
            "justification": None,
        }

        await self.db.execute(
            text(
                """
                INSERT INTO audit_logs (
                    entity,
                    entity_id,
                    action,
                    actor_id,
                    context,
                    old_value,
                    new_value,
                    justification
                )
                VALUES (
                    :entity,
                    :entity_id,
                    :action,
                    :actor_id,
                    CAST(:context AS jsonb),
                    CAST(:old_value AS jsonb),
                    CAST(:new_value AS jsonb),
                    :justification
                )
                """
            ),
            payload,
        )

    async def calculate_deviation(
        self,
        session_id: UUID,
    ) -> Optional[dict]:
        """
        Calcula desvio entre planejado e executado.

        Regras (conforme TRAINNIG.MD):
        - Desvio absoluto ≥ 20 pontos percentuais em qualquer foco OU
        - Desvio agregado ≥ 30% entre planejamento e execução

        Retorna:
        - None se sessão não tem microciclo
        - dict com desvios por foco e flag de significância
        """
        from app.models.training_microcycle import TrainingMicrocycle

        session = await self.get_by_id(session_id)

        if not session.microcycle_id:
            return None

        # Buscar microciclo
        query = select(TrainingMicrocycle).where(
            TrainingMicrocycle.id == session.microcycle_id
        )
        result = await self.db.execute(query)
        microcycle = result.scalar_one_or_none()

        if not microcycle:
            logger.warning(
                f"Microciclo {session.microcycle_id} não encontrado para sessão {session_id}"
            )
            return None

        # Calcular desvios por foco
        deviations = {}
        focus_fields = [
            'attack_positional',
            'defense_positional',
            'transition_offense',
            'transition_defense',
            'attack_technical',
            'defense_technical',
            'physical',
        ]

        total_deviation = 0.0
        significant_deviation = False
        deviation_details = []

        for field in focus_fields:
            planned = getattr(microcycle, f'planned_focus_{field}_pct') or 0
            executed = getattr(session, f'focus_{field}_pct') or 0

            deviation = float(executed) - float(planned)
            deviations[f'deviation_{field}_pct'] = deviation

            # Verifica desvio absoluto ≥ 20pts
            if abs(deviation) >= 20:
                significant_deviation = True
                field_name = field.replace('_', ' ').title()
                direction = "acima" if deviation > 0 else "abaixo"
                deviation_details.append(
                    f"{field_name}: {abs(deviation):.1f}% {direction} do planejado"
                )

            # Acumula para desvio agregado
            total_deviation += abs(deviation)

        # Verifica desvio agregado ≥ 30%
        if total_deviation >= 30:
            significant_deviation = True

        # Mensagem explicativa
        if significant_deviation:
            message = "Diferença relevante entre planejamento e execução"
            if deviation_details:
                message += ":\n" + "\n".join(deviation_details)
        else:
            message = "Execução dentro do esperado em relação ao planejamento"

        return {
            'training_session_id': session_id,
            'microcycle_id': microcycle.id,
            **deviations,
            'total_deviation_pct': total_deviation,
            'is_significant_deviation': significant_deviation,
            'deviation_message': message,
            'suggestions': []  # TODO: implementar sugestões inteligentes
        }
    
    async def _check_and_generate_compensation_suggestion(
        self,
        session: TrainingSession
    ) -> None:
        """
        Step 18: Verifica se sessão tem sobrecarga (total_focus_pct > 100%)
        e auto-gera sugestão de compensação.
        
        Args:
            session: TrainingSession recém-criada ou atualizada
        
        Lógica:
            - Calcula total_focus_pct somando todos os focos
            - Se total > 100%: chama TrainingSuggestionService.generate_compensation_suggestion()
            - Não bloqueia criação/edição se falhar (apenas log erro)
        """
        try:
            # Calcula total_focus_pct
            total_focus = sum([
                session.focus_attack_positional_pct or 0,
                session.focus_defense_positional_pct or 0,
                session.focus_transition_offense_pct or 0,
                session.focus_transition_defense_pct or 0,
                session.focus_attack_technical_pct or 0,
                session.focus_defense_technical_pct or 0,
                session.focus_physical_pct or 0
            ])
            
            # Verifica se há sobrecarga
            if total_focus <= 100:
                return  # Nenhuma ação necessária
            
            logger.info(
                f"[Step 18] Session {session.id} has overload: {total_focus}% > 100%. "
                f"Generating compensation suggestion..."
            )
            
            # Cria service de sugestões
            suggestion_service = TrainingSuggestionService(self.db)
            
            # Gera sugestão de compensação
            suggestion = await suggestion_service.generate_compensation_suggestion(
                session_id=session.id,
                adjustment_pct=None  # Auto-calcula
            )
            
            if suggestion:
                logger.info(
                    f"[Step 18] Created compensation suggestion {suggestion.id} "
                    f"for session {session.id} (adjustment: {suggestion.recommended_adjustment_pct}%)"
                )
            else:
                logger.warning(
                    f"[Step 18] Could not create compensation suggestion for session {session.id}. "
                    f"Possible reasons: no future unlocked sessions available."
                )
        
        except Exception as e:
            # Não bloqueia operação se sugestão falhar
            logger.error(
                f"[Step 18] Error generating compensation suggestion for session {session.id}: {e}",
                exc_info=True
            )
