"""
Relatórios operacionais consolidados para a rota /statistics.

Contratos alinhados ao ESTATISTICAS.MD e ao frontend:
- GET /reports/operational-session
- GET /reports/athlete-self

Implementação com consolidação real mínima (attendance + roster ativo)
e placeholders onde os cálculos de carga/wellness/engajamento ainda não
foram formalizados. Frontend não calcula nada; snapshot vem do backend.
"""
from datetime import datetime, timezone, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth import get_current_context
from app.core.context import ExecutionContext
from app.models.training_session import TrainingSession
from app.models.team_registration import TeamRegistration
from app.models.attendance import Attendance
from app.models.wellness_post import WellnessPost
from app.models.athlete import Athlete
from app.models.team import Team

router = APIRouter()


def _get_session_or_404(db: Session, session_id: UUID) -> TrainingSession:
    session = db.get(TrainingSession, session_id)
    if not session or session.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="session_not_found")
    return session


def _assert_scope(session: TrainingSession, ctx: ExecutionContext) -> None:
    if ctx.is_superadmin:
        return
    if ctx.organization_id and session.organization_id != ctx.organization_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="forbidden")


def _active_roster(db: Session, session: TrainingSession):
    if not session.team_id:
        return []
    stmt = (
        select(TeamRegistration.athlete_id, Athlete.athlete_name)
        .where(
            TeamRegistration.team_id == session.team_id,
            TeamRegistration.start_at <= session.session_at,
            TeamRegistration.deleted_at.is_(None),
        )
        .where(
            (TeamRegistration.end_at.is_(None))
            | (TeamRegistration.end_at >= session.session_at)
        )
        .join(Athlete, Athlete.id == TeamRegistration.athlete_id)
    )
    rows = db.execute(stmt).all()
    return rows


def _attendance_map(db: Session, session_id: UUID):
    stmt = select(Attendance.athlete_id, Attendance.presence_status).where(
        Attendance.training_session_id == session_id,
        Attendance.deleted_at.is_(None),
    )
    rows = db.execute(stmt).all()
    return {athlete_id: status for athlete_id, status in rows}


def _wellness_map(db: Session, session_id: UUID):
    stmt = select(WellnessPost.athlete_id, WellnessPost.session_rpe, WellnessPost.flag_medical_followup).where(
        WellnessPost.training_session_id == session_id,
        WellnessPost.deleted_at.is_(None),
    )
    rows = db.execute(stmt).all()
    posted = {ath_id: {"rpe": rpe, "medical": flag} for ath_id, rpe, flag in rows}
    return posted


def _baseline_team_load(db: Session, team_id: UUID, session_at: datetime):
    window_start = session_at - timedelta(days=7)
    stmt = (
        select(func.avg(WellnessPost.session_rpe))
        .join(TrainingSession, TrainingSession.id == WellnessPost.training_session_id)
        .where(
            TrainingSession.team_id == team_id,
            TrainingSession.session_at >= window_start,
            TrainingSession.session_at <= session_at,
            WellnessPost.deleted_at.is_(None),
        )
    )
    return db.execute(stmt).scalar() or 0


def _engagement_status(absent_count: int, wellness_pending: int, total: int) -> str:
    if total == 0:
        return "inactive"
    ratio_inactive = (absent_count + wellness_pending) / total
    if ratio_inactive >= 0.5:
        return "inactive"
    if ratio_inactive > 0:
        return "partial"
    return "active"



def _athlete_self_data(db: Session, athlete_id: UUID):
    # Ultimas 8 sessoes com attendance e wellness
    attendance_rows = db.execute(
        select(
            Attendance.presence_status,
            TrainingSession.session_at,
            TrainingSession.id,
        )
        .join(TrainingSession, TrainingSession.id == Attendance.training_session_id)
        .where(
            Attendance.athlete_id == athlete_id,
            Attendance.deleted_at.is_(None),
            TrainingSession.deleted_at.is_(None),
        )
        .order_by(TrainingSession.session_at.desc())
        .limit(8)
    ).all()

    wellness_rows = db.execute(
        select(
            WellnessPost.training_session_id,
            WellnessPost.session_rpe,
            WellnessPost.flag_medical_followup,
            WellnessPost.filled_at,
        )
        .where(
            WellnessPost.athlete_id == athlete_id,
            WellnessPost.deleted_at.is_(None),
        )
        .order_by(WellnessPost.filled_at.desc())
        .limit(8)
    ).all()

    wellness_map = {
        ts_id: {"rpe": rpe, "medical": flag_medical, "filled_at": filled_at}
        for ts_id, rpe, flag_medical, filled_at in wellness_rows
    }

    streak = 0
    recent_absences = 0
    last_sessions_labels = []
    pending_wellness = 0
    for status, _, session_id in attendance_rows:
        label = "P" if status == "present" else "A"
        last_sessions_labels.append(label)
        if status == "present":
            streak += 1
            if session_id not in wellness_map:
                pending_wellness += 1
        else:
            recent_absences += 1
            break  # streak quebra na primeira ausencia

    trend = "stable"
    rpe_values = [r[1] for r in wellness_rows if r[1] is not None]
    if rpe_values:
        if len(rpe_values) < 3:
            trend = "attention"
        else:
            avg = sum(rpe_values) / len(rpe_values)
            if avg > 8.5 or avg < 4:
                trend = "attention"
    else:
        trend = "attention"

    load_zone = "within_zone"
    if rpe_values:
        avg_rpe = sum(rpe_values) / len(rpe_values)
        if avg_rpe > 8.5:
            load_zone = "above_zone"
        elif avg_rpe < 4:
            load_zone = "below_zone"

    alerts = []
    if pending_wellness > 0:
        alerts.append({"type": "compliance", "level": "warning", "message": f"{pending_wellness} wellness pendente nas ultimas sessoes"})
    if recent_absences > 0:
        alerts.append({"type": "attendance", "level": "warning", "message": "Faltas recentes registradas"})
    if any(item.get("medical") for item in wellness_map.values() if item.get("medical") is not None):
        alerts.append({"type": "medical", "level": "warning", "message": "Acompanhamento medico recomendado"})
    if load_zone != "within_zone":
        alerts.append({"type": "load", "level": "warning", "message": "Ajuste de carga pessoal recomendado"})

    insights = []
    if pending_wellness > 0:
        insights.append("Responda o wellness pos-sessao para fechar o ciclo.")
    if trend == "attention":
        insights.append("Priorize recuperacao curta (sono/descanso) nos proximos dias.")
    if load_zone == "above_zone":
        insights.append("Reduza intensidade do proximo treino para equilibrar a carga.")
    if not insights:
        insights.append("Mantenha a rotina atual, voce esta equilibrada.")

    return {
        "presence": {
            "streak": streak,
            "recent_absences": recent_absences,
            "last_sessions": last_sessions_labels,
        },
        "wellness": {"trend": trend, "note": None},
        "load": {"zone": load_zone, "note": None},
        "overall_status": "attention" if alerts else "ok",
        "alerts": alerts,
        "insights": insights,
    }
@router.get(
    "/operational-session",
    summary="Snapshot operacional da sessão (treino/jogo)",
    description="Retorna contexto, pendências, carga, lista operacional e alertas consolidados.",
)
def get_operational_session(
    session_id: UUID = Query(..., description="ID da sessão (treino ou jogo)"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    session = _get_session_or_404(db, session_id)
    _assert_scope(session, ctx)

    roster = _active_roster(db, session)
    attendance = _attendance_map(db, session_id)
    wellness_posted = _wellness_map(db, session_id)
    team_baseline = _baseline_team_load(db, session.team_id, session.session_at) if session.team_id else 0

    # Buscar nome da equipe
    team_name = ""
    if session.team_id:
        team = db.get(Team, session.team_id)
        if team:
            team_name = team.name

    total = len(roster)
    present = sum(1 for aid, _ in roster if attendance.get(aid) == "present")
    absent = total - present
    now = datetime.now(timezone.utc)
    session_done = session.session_at < now
    wellness_pending = sum(1 for aid, _ in roster if aid not in wellness_posted)
    engagement_status = _engagement_status(absent, wellness_pending, total)
    inactive_engagement = sum(1 for aid, _ in roster if attendance.get(aid) != "present" or aid not in wellness_posted)

    athletes_list = []
    load_values = []
    out_of_zone = 0
    for aid, name in roster:
        presence = attendance.get(aid, "absent")
        wellness = "pending_post" if (session_done and aid not in wellness_posted) else ("pending_pre" if aid not in wellness_posted else "ok")
        wp_info = wellness_posted.get(aid)
        rpe = wp_info["rpe"] if wp_info else None
        load_status = "ok"
        if rpe is not None:
            load_values.append(rpe)
        if team_baseline and rpe is not None:
            if rpe > team_baseline * 1.2:
                load_status = "critical"
            elif rpe > team_baseline * 1.1 or rpe < team_baseline * 0.8:
                load_status = "alert"
            if load_status != "ok":
                out_of_zone += 1
        if presence == "absent" or wellness == "pending_post" or load_status == "critical":
            overall = "critical"
        elif wellness != "ok" or load_status == "alert":
            overall = "attention"
        else:
            overall = "ok"
        athletes_list.append(
            {
                "athlete_id": str(aid),
                "name": name or "",
                "presence": presence,
                "wellness": wellness,
                "load_status": load_status,
                "overall_status": overall,
            }
        )

    alerts = []
    for aid, _ in roster:
        presence = attendance.get(aid, "absent")
        if presence == "absent":
            alerts.append(
                {
                    "type": "attendance",
                    "level": "critical",
                    "athlete_id": str(aid),
                    "message": "Ausência registrada na sessão",
                }
            )
        if aid not in wellness_posted:
            alerts.append(
                {
                    "type": "compliance",
                    "level": "warning",
                    "athlete_id": str(aid),
                    "message": "Wellness pos-sessao pendente",
                }
            )
        wp_info = wellness_posted.get(aid)
        rpe = wp_info["rpe"] if wp_info else None
        medical_flag = wp_info["medical"] if wp_info else False
        if rpe is not None and rpe > max(team_baseline * 1.2, team_baseline + 50):
            alerts.append(
                {
                    "type": "load",
                    "level": "warning",
                    "athlete_id": str(aid),
                    "message": "Carga acima da zona segura",
                }
            )
        if medical_flag:
            alerts.append(
                {
                    "type": "medical",
                    "level": "warning",
                    "athlete_id": str(aid),
                    "message": "Acompanhamento médico recomendado",
                }
            )

    snapshot = {
        "context": {
            "session_id": str(session_id),
            "session_type": "training",
            "team": {"id": str(session.team_id) if session.team_id else "", "name": team_name},
            "date": session.session_at.date().isoformat(),
            "status": "completed" if session.session_at < now - timedelta(hours=3) else ("ongoing" if session.session_at <= now else "scheduled"),
        },
        "process_status": {
            "total_athletes": total,
            "present": present,
            "absent": absent,
            "wellness_pending": wellness_pending,
            "inactive_engagement": inactive_engagement,
            "engagement_status": engagement_status,
            "session_risk": absent > 0 or (total > 0 and present / max(total, 1) < 0.8),
        },
        "load_summary": {
            "session_load_avg": float(sum(load_values) / len(load_values)) if load_values else 0,
            "team_baseline_avg": float(team_baseline),
            "deviation_pct": float(
                ((sum(load_values) / len(load_values)) - team_baseline) / team_baseline * 100
            ) if load_values and team_baseline else 0,
            "out_of_zone_athletes": out_of_zone,
        },
        "athletes": athletes_list,
        "alerts": alerts,
    }
    return snapshot


@router.get(
    "/athlete-self",
    summary="Visão individual do atleta (autoconhecimento)",
    description="Retorna presença, wellness, carga, status e insights do próprio atleta.",
)
def get_athlete_self(
    ctx: ExecutionContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    if not ctx.person_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="forbidden")

    athlete = db.execute(
        select(Athlete).where(
            Athlete.person_id == str(ctx.person_id),
            Athlete.deleted_at.is_(None),
        )
    ).scalar_one_or_none()

    if not athlete:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="athlete_not_found")

    payload = _athlete_self_data(db, athlete.id)

    return {
        "context": {
            "athlete_id": str(athlete.id),
            "period": "last_8_sessions",
        },
        "presence": payload["presence"],
        "wellness": payload["wellness"],
        "load": payload["load"],
        "overall_status": payload["overall_status"],
        "alerts": payload["alerts"],
        "insights": payload["insights"],
    }






