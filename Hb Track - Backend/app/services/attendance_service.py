"""
Service: Attendance Management with Eager Loading and LGPD Compliance

Implementa operações de gerenciamento de presenças com:
- Eager loading para resolver N+1 (joinedload)
- Filtros de permissão por team_memberships (LGPD)
- Registro automático em data_access_logs
- Batch operations para performance
- Validação de constraints (unique session_id + athlete_id)

Regras:
- R22: Dados de treino são métricas operacionais
- R25/R26: Permissões por papel e escopo organizacional
- R40: Janelas de edição temporais
- LGPD: Auditoria de acesso apenas para staff (não self-access)
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, and_, func, case
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError

from app.core.db import AsyncSession
from app.models.attendance import Attendance as AttendanceModel
from app.models.athlete import Athlete
from app.models.person import Person
from app.models.training_session import TrainingSession
from app.models.team_membership import TeamMembership
from app.models.team_registration import TeamRegistration
from app.models.data_access_log import DataAccessLog
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceCorrection
from app.core.exceptions import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    ConflictError
)


class AttendanceService:
    """Service para gerenciamento de presenças com eager loading e LGPD compliance."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def _get_user_team_ids(self, person_id: UUID) -> List[UUID]:
        """
        Retorna lista de team_ids que a pessoa tem permissão de acessar.

        Usado para filtrar dados conforme escopo organizacional (LGPD).
        """
        stmt = select(TeamMembership.team_id).where(
            and_(
                TeamMembership.person_id == person_id,
                TeamMembership.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]
    
    async def _log_access(
        self,
        user_id: UUID,
        entity_type: str,
        entity_id: UUID,
        athlete_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Registra acesso em data_access_logs conforme LGPD.
        
        Regra: Registra apenas staff reading outros, NÃO self-access.
        """
        # TODO: Implementar verificação se é self-access (atleta acessando próprios dados)
        # Por ora, registra todos acessos de leitura
        log = DataAccessLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            athlete_id=athlete_id,
            accessed_at=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(log)
        await self.db.flush()
    
    async def get_session_attendance(
        self,
        session_id: UUID,
        user_id: UUID,
        user_role: str,
        person_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        athlete_id_filter: Optional[UUID] = None,
        status_filter: Optional[str] = None
    ) -> List[AttendanceModel]:
        """
        Retorna lista de presenças de uma sessão com eager loading.
        
        Performance: Usa joinedload para resolver N+1 queries.
        LGPD: Filtra por team_memberships e registra acesso.
        
        Args:
            session_id: ID da sessão de treino
            user_id: ID do usuário solicitante
            user_role: Role do usuário (para permissões)
            ip_address: IP da requisição (para audit log)
            user_agent: User agent (para audit log)
            athlete_id_filter: Filtro opcional por atleta
            status_filter: Filtro opcional por status ('present', 'absent')
        
        Returns:
            Lista de registros de presença com relações carregadas
        
        Raises:
            NotFoundError: Sessão não encontrada
            PermissionDeniedError: Usuário sem acesso à equipe da sessão
        """
        # 1. Verificar se sessão existe e obter team_id
        session_stmt = select(TrainingSession.team_id).where(
            and_(
                TrainingSession.id == session_id,
                TrainingSession.deleted_at.is_(None)
            )
        )
        session_result = await self.db.execute(session_stmt)
        session_team_id = session_result.scalar_one_or_none()
        
        if not session_team_id:
            raise NotFoundError("Sessão de treino não encontrada")
        
        # 2. Verificar permissões (LGPD - escopo organizacional)
        if person_id:
            user_team_ids = await self._get_user_team_ids(person_id)
            if session_team_id not in user_team_ids:
                raise PermissionDeniedError("Você não tem permissão para acessar esta sessão")
        
        # 3. Construir query com eager loading (resolver N+1)
        stmt = (
            select(AttendanceModel)
            .options(
                joinedload(AttendanceModel.athlete),
                selectinload(AttendanceModel.team_registration),
                selectinload(AttendanceModel.training_session)
            )
            .where(
                and_(
                    AttendanceModel.training_session_id == session_id,
                    AttendanceModel.deleted_at.is_(None)
                )
            )
        )

        # 4. Aplicar filtros opcionais
        if athlete_id_filter:
            stmt = stmt.where(AttendanceModel.athlete_id == athlete_id_filter)

        if status_filter:
            stmt = stmt.where(AttendanceModel.presence_status == status_filter)

        # 5. Ordenar por nome do atleta
        stmt = stmt.join(AttendanceModel.athlete).order_by(Athlete.athlete_name)
        
        # 6. Executar query
        result = await self.db.execute(stmt)
        attendances = result.scalars().unique().all()
        
        # 7. Registrar acesso em data_access_logs (apenas staff reading outros)
        await self._log_access(
            user_id=user_id,
            entity_type='attendance',
            entity_id=session_id,
            athlete_id=None,  # NULL porque é lista completa
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return list(attendances)
    
    async def record_batch(
        self,
        session_id: UUID,
        attendances: List[AttendanceCreate],
        user_id: UUID,
        user_role: str,
        person_id: Optional[UUID] = None
    ) -> List[AttendanceModel]:
        """
        Registra múltiplas presenças em batch (operação otimizada).
        
        Validações:
        - Unique constraint (session_id, athlete_id)
        - Sessão existe e usuário tem permissão
        - minutes_effective <= duração da sessão
        
        Args:
            session_id: ID da sessão de treino
            attendances: Lista de dados de presença a criar
            user_id: ID do usuário criador
            user_role: Role do usuário
        
        Returns:
            Lista de registros criados
        
        Raises:
            NotFoundError: Sessão não encontrada
            PermissionDeniedError: Sem permissão para a equipe
            ConflictError: Presença duplicada (unique constraint)
            ValidationError: Dados inválidos
        """
        # 1. Verificar sessão e permissões
        session_stmt = select(TrainingSession).where(
            and_(
                TrainingSession.id == session_id,
                TrainingSession.deleted_at.is_(None)
            )
        )
        session_result = await self.db.execute(session_stmt)
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise NotFoundError("Sessão de treino não encontrada")

        if person_id:
            user_team_ids = await self._get_user_team_ids(person_id)
            if session.team_id not in user_team_ids:
                raise PermissionDeniedError("Você não tem permissão para registrar presenças nesta sessão")

        if session.status != "pending_review":
            raise ValidationError(
                "Presenças só podem ser registradas durante a revisão operacional."
            )

        if not session.team_id:
            raise ValidationError("Sessão sem equipe não permite registro de presença.")
        
        # 2. Validar dados
        athlete_ids = [att.athlete_id for att in attendances]
        if len(athlete_ids) != len(set(athlete_ids)):
            raise ValidationError("Lista contém atletas duplicados")

        # 2.1 Resolver team_registration_id ativo para cada atleta
        registration_stmt = (
            select(TeamRegistration)
            .where(
                TeamRegistration.team_id == session.team_id,
                TeamRegistration.athlete_id.in_(athlete_ids),
                TeamRegistration.end_at.is_(None),
                TeamRegistration.deleted_at.is_(None),
            )
            .order_by(TeamRegistration.athlete_id, TeamRegistration.start_at.desc())
        )
        registration_result = await self.db.execute(registration_stmt)
        registrations = registration_result.scalars().all()

        registration_by_athlete: dict[UUID, UUID] = {}
        for reg in registrations:
            if reg.athlete_id not in registration_by_athlete:
                registration_by_athlete[reg.athlete_id] = reg.id

        duration_cap = session.duration_actual_minutes or session.duration_planned_minutes

        # 3. Criar registros em batch
        created_attendances = []
        for attendance_data in attendances:
            # Validar minutes_effective <= duração sessão
            if attendance_data.minutes_effective is not None and duration_cap:
                if attendance_data.minutes_effective > duration_cap:
                    raise ValidationError(
                        f"Minutos efetivos ({attendance_data.minutes_effective}) "
                        f"não podem exceder duração da sessão ({duration_cap})"
                    )

            resolved_registration_id = registration_by_athlete.get(attendance_data.athlete_id)
            if not resolved_registration_id:
                raise ValidationError(
                    "Atleta sem vínculo ativo na equipe da sessão."
                )
            if attendance_data.team_registration_id and attendance_data.team_registration_id != resolved_registration_id:
                raise ValidationError(
                    "team_registration_id informado não corresponde ao vínculo ativo do atleta."
                )
            
            source_value = getattr(attendance_data, "source", None) or "manual"

            # Criar registro
            new_attendance = AttendanceModel(
                training_session_id=session_id,
                athlete_id=attendance_data.athlete_id,
                team_registration_id=resolved_registration_id,
                presence_status=attendance_data.presence_status,
                minutes_effective=attendance_data.minutes_effective,
                comment=attendance_data.comment,
                source=source_value,
                participation_type=attendance_data.participation_type,
                reason_absence=attendance_data.reason_absence,
                is_medical_restriction=attendance_data.is_medical_restriction,
                created_by_user_id=user_id
            )
            self.db.add(new_attendance)
            created_attendances.append(new_attendance)
        
        # 4. Flush para detectar unique constraint violations
        try:
            await self.db.flush()
        except IntegrityError as e:
            if 'unique' in str(e).lower():
                raise ConflictError("Presença duplicada: atleta já registrado nesta sessão")
            raise ValidationError(f"Erro de integridade: {str(e)}")
        
        # 5. Recarregar com eager loading
        ids = [att.id for att in created_attendances]
        stmt = (
            select(AttendanceModel)
            .options(
                joinedload(AttendanceModel.athlete),
                selectinload(AttendanceModel.team_registration)
            )
            .where(AttendanceModel.id.in_(ids))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())
    
    async def update_participation(
        self,
        attendance_id: UUID,
        data: AttendanceUpdate,
        user_id: UUID,
        user_role: str,
        person_id: Optional[UUID] = None
    ) -> AttendanceModel:
        """
        Atualiza dados de participação de uma presença existente.
        
        Validações:
        - R40: Janelas de edição temporais
        - Permissões por escopo organizacional
        
        Args:
            attendance_id: ID do registro de presença
            data: Dados a atualizar
            user_id: ID do usuário editor
            user_role: Role do usuário
        
        Returns:
            Registro atualizado
        
        Raises:
            NotFoundError: Presença não encontrada
            PermissionDeniedError: Sem permissão
            ValidationError: Dados inválidos ou janela de edição expirada
        """
        # 1. Buscar presença com eager loading
        stmt = (
            select(AttendanceModel)
            .options(
                joinedload(AttendanceModel.training_session),
                joinedload(AttendanceModel.athlete)
            )
            .where(
                and_(
                    AttendanceModel.id == attendance_id,
                    AttendanceModel.deleted_at.is_(None)
                )
            )
        )
        result = await self.db.execute(stmt)
        attendance = result.scalar_one_or_none()
        
        if not attendance:
            raise NotFoundError("Registro de presença não encontrado")

        # 2. Verificar permissões
        if person_id:
            user_team_ids = await self._get_user_team_ids(person_id)
            if attendance.training_session.team_id not in user_team_ids:
                raise PermissionDeniedError("Você não tem permissão para editar esta presença")

        if attendance.training_session.status != "pending_review":
            raise ValidationError(
                "Presenças só podem ser editadas durante a revisão operacional."
            )
        
        # 3. Validar janela de edição (R40)
        # TODO: Implementar validação de janela temporal
        # - 10min autor
        # - até 24h perfil superior
        # - >24h readonly
        
        # 4. Atualizar campos
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(attendance, field):
                setattr(attendance, field, value)
        
        attendance.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(attendance)
        
        return attendance
    
    async def get_session_statistics(
        self,
        session_id: UUID,
        user_id: UUID,
        person_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Retorna estatísticas agregadas de presença de uma sessão.
        
        Retorna:
            {
                'total_athletes': int,
                'present_count': int,
                'absent_count': int,
                'attendance_rate': float (0-100)
            }
        """
        # Verificar permissões
        session_stmt = select(TrainingSession.team_id).where(
            TrainingSession.id == session_id
        )
        session_result = await self.db.execute(session_stmt)
        session_team_id = session_result.scalar_one_or_none()
        
        if not session_team_id:
            raise NotFoundError("Sessão não encontrada")

        if person_id:
            user_team_ids = await self._get_user_team_ids(person_id)
            if session_team_id not in user_team_ids:
                raise PermissionDeniedError("Sem permissão para acessar esta sessão")
        
        # Contar presenças - usar select_from explícito
        count_stmt = select(
            func.count().label('total'),
            func.sum(
                case(
                    (AttendanceModel.presence_status == 'present', 1),
                    else_=0
                )
            ).label('present')
        ).select_from(AttendanceModel).where(
            and_(
                AttendanceModel.training_session_id == session_id,
                AttendanceModel.deleted_at.is_(None)
            )
        )
        
        result = await self.db.execute(count_stmt)
        row = result.one()
        
        total = int(row[0]) if row[0] is not None else 0
        present = int(row[1]) if row[1] is not None else 0
        absent = total - present
        rate = (present / total * 100) if total > 0 else 0.0
        
        return {
            'total_athletes': total,
            'present_count': present,
            'absent_count': absent,
            'attendance_rate': round(rate, 2)
        }

    async def correct_attendance(
        self,
        attendance_id: UUID,
        data: AttendanceCorrection,
        user_id: UUID,
        user_role: str,
        person_id: Optional[UUID] = None
    ) -> AttendanceModel:
        """
        Aplica correção administrativa a um registro de presença.

        Correções são permitidas após fechamento da sessão (R37: ação administrativa auditada).
        Requer permissão attendance:correction_write.

        Campos preenchidos automaticamente:
        - source = 'correction'
        - correction_by_user_id = user_id
        - correction_at = now()

        Args:
            attendance_id: ID do registro de presença
            data: Dados da correção (inclui comment obrigatório)
            user_id: ID do usuário que está corrigindo
            user_role: Role do usuário (deve ter permissão de correção)

        Returns:
            Registro corrigido

        Raises:
            NotFoundError: Presença não encontrada
            PermissionDeniedError: Sem permissão para correção
            ValidationError: Dados inválidos ou sessão não fechada
        """
        # 1. Buscar presença com eager loading
        stmt = (
            select(AttendanceModel)
            .options(
                joinedload(AttendanceModel.training_session),
                joinedload(AttendanceModel.athlete)
            )
            .where(
                and_(
                    AttendanceModel.id == attendance_id,
                    AttendanceModel.deleted_at.is_(None)
                )
            )
        )
        result = await self.db.execute(stmt)
        attendance = result.scalar_one_or_none()

        if not attendance:
            raise NotFoundError("Registro de presença não encontrado")

        # 2. Verificar permissões de escopo
        if person_id:
            user_team_ids = await self._get_user_team_ids(person_id)
            if attendance.training_session.team_id not in user_team_ids:
                raise PermissionDeniedError("Você não tem permissão para corrigir esta presença")

        # 3. Verificar role com permissão de correção
        # Apenas coordinator e acima podem corrigir (ou superadmin)
        allowed_roles = ['coordinator', 'admin', 'superadmin']
        if user_role not in allowed_roles:
            raise PermissionDeniedError(
                "Apenas coordenadores ou superiores podem realizar correções administrativas"
            )

        # 4. Verificar se sessão está fechada (R37: correção apenas pós-fechamento)
        if attendance.training_session.status != "pending_review":
            raise ValidationError(
                "Correções administrativas são permitidas apenas durante a revisão operacional."
            )

        # 5. Validar comment obrigatório (já validado pelo schema, mas double-check)
        if not data.comment or len(data.comment.strip()) < 10:
            raise ValidationError("Motivo da correção deve ter pelo menos 10 caracteres")

        # 6. Aplicar correção
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(attendance, field) and field != 'comment':
                setattr(attendance, field, value)

        # 7. Preencher campos de auditoria
        attendance.source = 'correction'
        attendance.correction_by_user_id = user_id
        attendance.correction_at = datetime.utcnow()
        attendance.comment = data.comment  # Sobrescreve com motivo da correção
        attendance.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(attendance)

        return attendance

    async def set_preconfirm(
        self,
        session_id: UUID,
        athlete_id: UUID,
        user_id: UUID,
    ) -> "AttendanceModel":
        """
        Registra pré-confirmação de presença pelo atleta (INV-TRAIN-063).

        Cria ou atualiza attendance com presence_status='preconfirm'.
        Só permitido antes do início da sessão (status in ['scheduled', 'draft']).
        Presença oficial é consolidada pelo treinador no encerramento (INV-TRAIN-064).

        Args:
            session_id: ID da sessão de treino
            athlete_id: ID do atleta que está pré-confirmando
            user_id: ID do usuário que está realizando a ação

        Returns:
            Registro de presença com presence_status='preconfirm'

        Raises:
            NotFoundError: Sessão não encontrada
            ValidationError: Sessão já iniciada (in_progress, pending_review, readonly)
        """
        # 1. Carregar sessão e verificar status
        session_stmt = select(TrainingSession).where(
            and_(
                TrainingSession.id == session_id,
                TrainingSession.deleted_at.is_(None)
            )
        )
        session_result = await self.db.execute(session_stmt)
        session = session_result.scalar_one_or_none()

        if not session:
            raise NotFoundError("Sessão de treino não encontrada")

        allowed_statuses = ['scheduled', 'draft']
        if session.status not in allowed_statuses:
            raise ValidationError(
                f"Pré-confirmação só é permitida antes do início da sessão "
                f"(status atual: '{session.status}', permitidos: {allowed_statuses})"
            )

        # 2. Verificar se já existe attendance para (session_id, athlete_id)
        existing_stmt = select(AttendanceModel).where(
            and_(
                AttendanceModel.training_session_id == session_id,
                AttendanceModel.athlete_id == athlete_id,
                AttendanceModel.deleted_at.is_(None)
            )
        )
        existing_result = await self.db.execute(existing_stmt)
        attendance = existing_result.scalar_one_or_none()

        if attendance:
            # Atualizar existente para preconfirm
            attendance.presence_status = 'preconfirm'
            attendance.updated_at = datetime.utcnow()
        else:
            # Criar novo registro de pré-confirmação
            attendance = AttendanceModel(
                training_session_id=session_id,
                athlete_id=athlete_id,
                presence_status='preconfirm',
                source='preconfirm',
                created_by_user_id=user_id,
            )
            self.db.add(attendance)

        await self.db.flush()
        await self.db.refresh(attendance)

        return attendance

    async def close_session_attendance(
        self,
        session_id: UUID,
        closed_by_user_id: UUID,
    ) -> int:
        """
        Consolida presenças no encerramento da sessão (INV-TRAIN-064).

        Converte todos os registros com presence_status='preconfirm' para 'absent'
        (regra padrão: preconfirm não confirmado pelo treinador = ausente).
        Correção posterior é possível via correct_attendance().

        Deve ser chamado quando session.status transita para 'readonly'.
        Integração automática requer modificação em training_session_service.py
        (fora do WRITE_SCOPE desta AR).

        Args:
            session_id: ID da sessão sendo encerrada
            closed_by_user_id: ID do usuário que está fechando

        Returns:
            Quantidade de registros convertidos de preconfirm→absent
        """
        # Buscar todos os attendance com preconfirm para esta sessão
        stmt = select(AttendanceModel).where(
            and_(
                AttendanceModel.training_session_id == session_id,
                AttendanceModel.presence_status == 'preconfirm',
                AttendanceModel.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        preconfirm_records = result.scalars().all()

        converted = 0
        for record in preconfirm_records:
            record.presence_status = 'absent'
            record.updated_at = datetime.utcnow()
            converted += 1

        if converted > 0:
            await self.db.flush()

        return converted
