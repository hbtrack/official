"""
Router para presenças em sessões de treino (Attendance).

Rotas canônicas:
/teams/{team_id}/trainings/{training_id}/attendance[...]

Regras aplicáveis:
- R22: Dados de treino são métricas operacionais.
- R40: Limite temporal de edição (10min autor; até 24h perfil superior; >24h somente leitura).
- R25/R26: Permissões por papel e escopo.
- RF10: Podem registrar presença: Dirigentes, Coordenadores e Treinadores.
- RF5.2: Temporada interrompida bloqueia criação/edição.
- R29/R33: Sem DELETE físico; histórico com rastro.
- 2.X.2: Presença registrada por team_registration ativo no momento do treino.

Campos do banco (attendance):
- id, training_session_id, team_registration_id, athlete_id, presence_status,
  minutes_effective, comment, source, participation_type, reason_absence,
  is_medical_restriction, created_at, created_by_user_id, updated_at, deleted_at
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps.auth import permission_dep
from app.core.cache import invalidate_report_cache
from app.core.context import ExecutionContext
from app.core.db import get_db
from app.models.attendance import Attendance as AttendanceModel
from app.models.training_session import TrainingSession
from app.models.team import Team
from app.models.team_registration import TeamRegistration
from app.schemas.attendance import (
    Attendance,
    AttendanceCreate,
    AttendanceUpdate,
    AthleteLoadSummary,
)

router = APIRouter(tags=["attendance"])
scoped_router = APIRouter(prefix="/teams/{team_id}", tags=["attendance"])


def _get_training_scoped(
    db: Session,
    ctx: ExecutionContext,
    team_id: UUID,
    training_id: UUID
) -> TrainingSession:
    """
    Busca sessão de treino verificando escopo via team -> organization.
    """
    query = (
        select(TrainingSession)
        .join(Team, Team.id == TrainingSession.team_id)
        .where(
            TrainingSession.id == training_id,
            TrainingSession.team_id == team_id,
            TrainingSession.deleted_at.is_(None)
        )
    )
    if not ctx.is_superadmin:
        query = query.where(Team.organization_id == ctx.organization_id)
    
    training = db.execute(query).scalar_one_or_none()
    if not training:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="training_not_found")
    return training


def _get_team_registration_for_athlete(
    db: Session,
    team_id: UUID,
    athlete_id: UUID,
    training_date: datetime
) -> Optional[TeamRegistration]:
    """
    Busca team_registration ativo do atleta no momento do treino.
    Valida se atleta estava vinculado à equipe na data do treino.
    """
    query = (
        select(TeamRegistration)
        .where(
            TeamRegistration.athlete_id == athlete_id,
            TeamRegistration.team_id == team_id,
            TeamRegistration.start_at <= training_date,
            TeamRegistration.deleted_at.is_(None),
        )
    )
    # Verifica se não terminou antes do treino
    # end_at é NULL (ativo) ou > training_date
    query = query.where(
        (TeamRegistration.end_at.is_(None)) |
        (TeamRegistration.end_at >= training_date)
    )
    return db.execute(query).scalar_one_or_none()


# =============================================================================
# ROTAS DEPRECATED (mantidas para compatibilidade)
# =============================================================================

@router.get(
    "/training_sessions/{training_session_id}/attendance",
    response_model=List[Attendance],
    summary="[DEPRECATED] Lista presenças da sessão",
    deprecated=True,
)
def list_attendance_by_session(
    training_session_id: UUID,
    db: Session = Depends(get_db),
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="deprecated_use_scoped_routes"
    )


@router.post(
    "/training_sessions/{training_session_id}/attendance",
    response_model=Attendance,
    status_code=status.HTTP_201_CREATED,
    summary="[DEPRECATED] Registra presença",
    deprecated=True,
)
def add_attendance_to_session(
    training_session_id: UUID,
    payload: AttendanceCreate,
    db: Session = Depends(get_db),
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="deprecated_use_scoped_routes"
    )


@router.patch(
    "/attendance/{attendance_id}",
    response_model=Attendance,
    summary="[DEPRECATED] Atualiza presença",
    deprecated=True,
)
def update_attendance(
    attendance_id: UUID,
    payload: AttendanceUpdate,
    db: Session = Depends(get_db),
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="deprecated_use_scoped_routes"
    )


# =============================================================================
# ROTAS CANÔNICAS - ATTENDANCE EM TREINO
# =============================================================================

@scoped_router.get(
    "/trainings/{training_id}/attendance",
    status_code=status.HTTP_200_OK,
    summary="Listar presenças do treino",
    response_model=List[Attendance],
)
async def scoped_list_training_attendance(
    team_id: UUID,
    training_id: UUID,
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> List[Attendance]:
    """
    Lista todos os registros de presença de um treino.
    Retorna lista vazia se não houver registros.
    """
    training = _get_training_scoped(db, ctx, team_id, training_id)
    
    query = (
        select(AttendanceModel)
        .where(
            AttendanceModel.training_session_id == training_id,
            AttendanceModel.deleted_at.is_(None)
        )
    )
    results = db.execute(query).scalars().all()
    return [Attendance.model_validate(r) for r in results]


@scoped_router.post(
    "/trainings/{training_id}/attendance",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar presença no treino",
    response_model=Attendance,
)
async def scoped_add_training_attendance(
    team_id: UUID,
    training_id: UUID,
    payload: AttendanceCreate,
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> Attendance:
    """
    Registra presença de um atleta em uma sessão de treino.
    
    Validações:
    - Atleta deve ter team_registration ativo na data do treino
    - Não permite duplicata (1 presença por atleta por treino)
    """
    training = _get_training_scoped(db, ctx, team_id, training_id)
    
    # Buscar team_registration ativo do atleta
    team_reg = _get_team_registration_for_athlete(
        db, team_id, payload.athlete_id, training.session_at
    )
    if not team_reg:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="athlete_not_registered_in_team"
        )
    
    # Verificar duplicata
    existing = db.execute(
        select(AttendanceModel)
        .where(
            AttendanceModel.training_session_id == training_id,
            AttendanceModel.athlete_id == payload.athlete_id,
            AttendanceModel.deleted_at.is_(None)
        )
    ).scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="attendance_already_exists"
        )
    
    # Criar registro
    attendance = AttendanceModel(
        training_session_id=training_id,
        team_registration_id=team_reg.id,
        athlete_id=payload.athlete_id,
        presence_status=payload.presence_status.value,
        minutes_effective=payload.minutes_effective,
        participation_type=payload.participation_type.value if payload.participation_type else None,
        reason_absence=payload.reason_absence.value if payload.reason_absence else None,
        comment=payload.comment,
        is_medical_restriction=payload.is_medical_restriction,
        source="manual",
        created_by_user_id=ctx.user_id,
    )
    db.add(attendance)
    db.commit()
    invalidate_report_cache()
    db.refresh(attendance)
    return Attendance.model_validate(attendance)


@scoped_router.patch(
    "/trainings/{training_id}/attendance/{attendance_id}",
    status_code=status.HTTP_200_OK,
    summary="Atualizar registro de presença",
    response_model=Attendance,
)
async def scoped_update_training_attendance(
    team_id: UUID,
    training_id: UUID,
    attendance_id: UUID,
    payload: AttendanceUpdate,
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> Attendance:
    """
    Atualiza registro de presença existente.
    
    Regras:
    - R40: Janela de edição (10min/24h) - não implementado nesta versão
    """
    _get_training_scoped(db, ctx, team_id, training_id)
    
    # Buscar attendance
    attendance = db.execute(
        select(AttendanceModel)
        .where(
            AttendanceModel.id == attendance_id,
            AttendanceModel.training_session_id == training_id,
            AttendanceModel.deleted_at.is_(None)
        )
    ).scalar_one_or_none()
    
    if not attendance:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="attendance_not_found")
    
    # Atualizar campos
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "presence_status" and value:
            setattr(attendance, key, value.value if hasattr(value, 'value') else value)
        elif key == "participation_type" and value:
            setattr(attendance, key, value.value if hasattr(value, 'value') else value)
        elif key == "reason_absence" and value:
            setattr(attendance, key, value.value if hasattr(value, 'value') else value)
        else:
            setattr(attendance, key, value)
    
    attendance.updated_at = datetime.utcnow()
    db.commit()
    invalidate_report_cache()
    db.refresh(attendance)
    return Attendance.model_validate(attendance)


@scoped_router.delete(
    "/trainings/{training_id}/attendance/{attendance_id}",
    status_code=status.HTTP_200_OK,
    summary="Remover registro de presença (soft delete)",
    response_model=dict,
)
async def scoped_delete_training_attendance(
    team_id: UUID,
    training_id: UUID,
    attendance_id: UUID,
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> dict:
    """
    Remove registro de presença via soft delete.
    
    Regras:
    - R29/R33: Sem DELETE físico; histórico com rastro
    """
    _get_training_scoped(db, ctx, team_id, training_id)
    
    # Buscar attendance
    attendance = db.execute(
        select(AttendanceModel)
        .where(
            AttendanceModel.id == attendance_id,
            AttendanceModel.training_session_id == training_id,
            AttendanceModel.deleted_at.is_(None)
        )
    ).scalar_one_or_none()
    
    if not attendance:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="attendance_not_found")
    
    # Soft delete
    attendance.deleted_at = datetime.utcnow()
    attendance.deleted_reason = "Removed by user"
    db.commit()
    invalidate_report_cache()
    
    return {"detail": "attendance_deleted"}


# =============================================================================
# ROTAS DE CARGA (LOAD)
# =============================================================================

@scoped_router.get(
    "/athletes/{athlete_id}/load",
    status_code=status.HTTP_200_OK,
    summary="Obter carga do atleta",
    response_model=AthleteLoadSummary,
)
async def scoped_get_athlete_load(
    team_id: UUID,
    athlete_id: UUID,
    season_id: Optional[UUID] = Query(default=None, description="Filtrar por temporada"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> AthleteLoadSummary:
    """
    Retorna resumo de carga do atleta (treinos + minutos).
    
    Carga é calculada a partir das presenças registradas.
    """
    # Verificar se equipe pertence à organização
    team = db.execute(
        select(Team)
        .where(Team.id == team_id, Team.deleted_at.is_(None))
    ).scalar_one_or_none()
    
    if not team:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="team_not_found")
    
    if not ctx.is_superadmin and team.organization_id != ctx.organization_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="team_out_of_scope")
    
    # Query de presenças do atleta
    query = (
        select(AttendanceModel)
        .join(TrainingSession, TrainingSession.id == AttendanceModel.training_session_id)
        .where(
            AttendanceModel.athlete_id == athlete_id,
            AttendanceModel.deleted_at.is_(None),
            TrainingSession.team_id == team_id,
            TrainingSession.deleted_at.is_(None)
        )
    )
    
    # Filtro por temporada
    if season_id:
        query = query.where(TrainingSession.season_id == season_id)
    
    results = db.execute(query).scalars().all()
    
    # Calcular métricas
    total_trainings = len(results)
    total_presences = sum(1 for r in results if r.presence_status == "present")
    total_absences = sum(1 for r in results if r.presence_status == "absent")
    total_minutes = sum(r.minutes_effective or 0 for r in results if r.presence_status == "present")
    
    attendance_rate = (total_presences / total_trainings * 100) if total_trainings > 0 else 0.0
    avg_minutes = (total_minutes / total_presences) if total_presences > 0 else 0.0
    
    return AthleteLoadSummary(
        athlete_id=athlete_id,
        total_trainings=total_trainings,
        total_minutes=total_minutes,
        total_presences=total_presences,
        total_absences=total_absences,
        attendance_rate=round(attendance_rate, 2),
        avg_minutes_per_session=round(avg_minutes, 2)
    )
