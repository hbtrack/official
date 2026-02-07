"""
Router Team - Endpoints de equipes.
Regras: RF6, RF7, RF8, R25/R26, RF5.2
"""
import logging
from uuid import UUID
from typing import Optional
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.api.v1.deps.auth import permission_dep
from app.core.auth import ExecutionContext
from app.models.athlete import Athlete
from app.models.category import Category
from app.models.season import Season
from app.models.team import Team
from app.models.membership import OrgMembership
from app.models.organization import Organization
from app.models.person import Person
from app.models.role import Role
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.models.password_reset import PasswordReset
from app.services.team_service import TeamService
from app.services.team_registration_service import TeamRegistrationService
from app.services.notification_service import NotificationService
from app.services.intake.email_service_v2 import email_service_v2
from app.core.config import settings
from app.schemas.teams import (
    TeamBase,
    TeamCreate,
    TeamUpdate,
    TeamCoachUpdate,
    CoachHistoryItem,
    TeamCoachHistoryResponse,
    TeamPaginatedResponse,
    TeamStaffResponse,
    TeamStaffMember,
    TeamSettingsUpdate,
)
from app.schemas.team_registrations import (
    TeamRegistration,
    TeamRegistrationMoveRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["teams"])


@router.get("", response_model=TeamPaginatedResponse)
async def list_teams(
    season_id: Optional[UUID] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(True, description="Incluir equipes arquivadas"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador", "membro"], require_org=True)
    ),
):
    """
    Lista equipes da organização.
    
    Regras:
    - R25/R26: RBAC
    - R34: Escopo organizacional
    - R3: Superadmin vê todas, demais veem apenas equipes vinculadas
    - RDB10: Filtro por team_membership
    """
    service = TeamService(db)
    items, total = await service.list_teams(
        organization_id=ctx.organization_id,
        person_id=ctx.person_id,
        is_superadmin=ctx.is_superadmin,
        season_id=season_id,
        page=page,
        limit=limit,
        include_deleted=include_deleted,
    )
    
    return TeamPaginatedResponse(
        items=[TeamBase.model_validate(t) for t in items],
        page=page,
        limit=limit,
        total=total,
    )


@router.post("", response_model=TeamBase, status_code=status.HTTP_201_CREATED)
async def create_team(
    data: TeamCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador"], require_org=True)
    ),
):
    """
    Cria nova equipe.
    Regras: RF6
    Step 4: Implementar lógica role-based - treinador se auto-atribui
    """
    service = TeamService(db)
    
    try:
        # Step 4: Lógica role-based
        if ctx.role_code == "treinador":
            coach_id = ctx.membership_id
        else:
            coach_id = data.coach_membership_id
        
        # Step 4c: Validar coach
        coach = await db.get(OrgMembership, coach_id)
        if not coach:
            raise HTTPException(status_code=400, detail="coach_not_found")
        
        # Buscar role do coach
        coach_role = await db.get(Role, coach.role_id)
        if not coach_role or coach_role.id != 3:  # role_id 3 = treinador
            raise HTTPException(status_code=400, detail="coach_must_be_trainer_role")
        
        if coach.end_at is not None:
            raise HTTPException(status_code=400, detail="coach_is_inactive")
        
        # Comparar organization_id como UUID para evitar problemas de tipo (UUID vs str)
        from uuid import UUID
        coach_org_id = coach.organization_id if isinstance(coach.organization_id, UUID) else UUID(str(coach.organization_id))
        ctx_org_id = ctx.organization_id if isinstance(ctx.organization_id, UUID) else UUID(str(ctx.organization_id))
        
        if coach_org_id != ctx_org_id:
            raise HTTPException(status_code=400, detail="coach_must_belong_to_same_organization")
        
        team = await service.create(
            name=data.name,
            organization_id=ctx.organization_id,
            category_id=data.category_id,
            gender=data.gender,
            is_our_team=data.is_our_team,
            coach_membership_id=coach_id,
            created_by_user_id=ctx.user_id,  # Auditoria: quem criou
            creator_person_id=ctx.person_id,  # Para team_membership
            creator_org_membership_id=ctx.membership_id,  # Para team_membership
        )
        await db.commit()
        await db.refresh(team)
        return TeamBase.model_validate(team)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail={"code": str(e), "message": str(e)})


@router.get("/{team_id}", response_model=TeamBase)
async def get_team(
    team_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador", "membro"], require_team=True)
    ),
):
    """Retorna equipe por ID."""
    service = TeamService(db)
    team = await service.get_by_id(team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail="not_found")
    
    # TODO: Habilitar após migration RDB4
    # if team.deleted_at:
    #     raise HTTPException(status_code=404, detail="not_found")
    
    return TeamBase.model_validate(team)


@router.patch("/{team_id}", response_model=TeamBase)
async def update_team(
    team_id: UUID,
    data: TeamUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador"], require_team=True)
    ),
):
    """Atualiza equipe. Regras: RF7, Step 2: Validação de permissão can_manage_teams"""
    # Step 2: Validar permissão can_manage_teams (plural - consistente com permissions_map)
    ctx.requires("can_manage_teams")
    
    service = TeamService(db)
    team = await service.get_by_id(team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail="not_found")
    
    # TODO: Habilitar após migration RDB4
    # if team.deleted_at:
    #     raise HTTPException(status_code=404, detail="not_found")
    
    updated = await service.update(team, **data.model_dump(exclude_unset=True))
    return TeamBase.model_validate(updated)


@router.patch("/{team_id}/settings", response_model=TeamBase)
async def update_team_settings(
    team_id: UUID,
    data: TeamSettingsUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador"], require_team=True)
    ),
):
    """
    Atualiza configurações da equipe (Step 15).
    
    Permite ajustar o alert_threshold_multiplier que controla a sensibilidade
    dos alertas de wellness automáticos.
    
    Valores recomendados:
    - 1.5: Juvenis (mais sensível)
    - 2.0: Padrão adultos
    - 2.5: Adultos tolerantes (menos alertas)
    
    Permissões: Dirigente, Coordenador, ou Treinador responsável
    """
    service = TeamService(db)
    team = await service.get_by_id(team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    updated = await service.update_settings(
        team=team,
        alert_threshold_multiplier=data.alert_threshold_multiplier
    )
    
    await db.commit()
    await db.refresh(updated)
    
    logger.info(
        f"Updated team {team_id} settings: alert_threshold_multiplier={data.alert_threshold_multiplier} "
        f"by user {ctx.user_id}"
    )
    
    return TeamBase.model_validate(updated)


@router.patch(
    "/{team_id}/coach",
    response_model=TeamBase,
    summary="Reatribuir treinador da equipe",
    description="""
Substitui o treinador atual por um novo.

**Steps 18 + 21:** Endpoint com notificações integradas.

**Ordem de operações:**
1. Busca equipe e valida coach antigo
2. Busca dados do coach antigo (user_id, nome)
3. **PRIMEIRO:** Encerra vínculo antigo (end_at, status='inativo')
4. Valida novo coach (role_id=3, ativo, mesma org)
5. **DEPOIS:** Cria novo TeamMembership
6. Atualiza team.coach_membership_id
7. Commit
8. Envia notificação + email ao novo coach
9. Envia notificação ao coach antigo (removido)

**Permissão:** Dirigente ou Coordenador
""",
    responses={
        200: {"description": "Coach reatribuído com sucesso"},
        400: {"description": "Validação falhou (novo coach inválido)"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Equipe não encontrada"},
    },
)
async def reassign_team_coach(
    team_id: UUID,
    data: TeamCoachUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador"], require_team=True)
    ),
):
    """
    Reatribui treinador de uma equipe (Steps 18 + 21).
    
    - Remove coach antigo (end_at, notifica)
    - Atribui novo coach (TeamMembership, notifica + email)
    - Valida integridade (role_id=3, org, ativo)
    """
    from datetime import datetime, timezone
    
    service = TeamService(db)
    notification_service = NotificationService(db)
    
    # 1. Buscar equipe
    team = await service.get_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="team_not_found")
    
    old_coach_id = team.coach_membership_id
    
    # 2. Buscar dados do coach antigo (para notificação)
    old_coach_user_id = None
    old_coach_name = None
    if old_coach_id:
        stmt = (
            select(User, Person)
            .join(Person, User.person_id == Person.id)
            .join(OrgMembership, OrgMembership.user_id == User.id)
            .where(OrgMembership.id == old_coach_id)
        )
        result = await db.execute(stmt)
        row = result.first()
        if row:
            old_coach_user_id = row[0].id
            old_coach_name = row[1].full_name
    
    # 3. PRIMEIRO - Encerrar vínculo antigo
    if old_coach_id:
        stmt_tm = select(TeamMembership).where(
            TeamMembership.team_id == team_id,
            TeamMembership.org_membership_id == old_coach_id,
            TeamMembership.status == 'ativo',
            TeamMembership.end_at.is_(None)
        )
        result_tm = await db.execute(stmt_tm)
        old_tm = result_tm.scalar_one_or_none()
        
        if old_tm:
            now = datetime.now(timezone.utc)
            old_tm.end_at = now
            old_tm.status = 'inativo'
            db.add(old_tm)
    
    # 4. Validar novo coach
    new_coach = await db.get(OrgMembership, data.new_coach_membership_id)
    if not new_coach:
        raise HTTPException(status_code=400, detail="new_coach_not_found")
    
    if new_coach.role_id != 3:
        raise HTTPException(status_code=400, detail="new_coach_must_be_trainer_role")
    
    if new_coach.end_at is not None:
        raise HTTPException(status_code=400, detail="new_coach_membership_inactive")
    
    if new_coach.organization_id != ctx.organization_id:
        raise HTTPException(status_code=400, detail="new_coach_different_organization")
    
    # 5. DEPOIS - Criar novo TeamMembership
    now = datetime.now(timezone.utc)
    new_tm = TeamMembership(
        team_id=team.id,
        person_id=new_coach.person_id,
        org_membership_id=data.new_coach_membership_id,
        status='ativo',
        start_at=now,
        resend_count=0,
    )
    db.add(new_tm)
    
    # 6. Atualizar team.coach_membership_id
    team.coach_membership_id = data.new_coach_membership_id
    db.add(team)
    
    # 7. Commit
    await db.commit()
    await db.refresh(team)
    
    # 8. Notificar novo coach (Step 21)
    stmt_new_coach = (
        select(User, Person)
        .join(Person, User.person_id == Person.id)
        .where(Person.id == new_coach.person_id)
    )
    result_new = await db.execute(stmt_new_coach)
    row_new = result_new.first()
    
    if row_new:
        new_coach_user = row_new[0]
        new_coach_person = row_new[1]
        
        # Email
        email_service_v2.send_coach_assigned_email(
            to_email=new_coach_user.email,
            coach_name=new_coach_person.full_name,
            team_name=team.name,
            start_date=now.isoformat(),
            team_url=f"{settings.FRONTEND_URL}/teams/{team.id}",
            organization_name=team.organization.name if team.organization else None,
        )
        
        # Notificação
        notification = await notification_service.create(
            user_id=new_coach_user.id,
            type='team_assignment',
            message=f'Você foi designado como treinador da equipe {team.name}',
            notification_data={
                'team_id': str(team.id),
                'team_name': team.name,
                'start_date': now.isoformat(),
            }
        )
        
        # WebSocket broadcast
        await notification_service.broadcast_to_user(new_coach_user.id, notification)
    
    # 9. Notificar coach antigo
    if old_coach_user_id and old_coach_name:
        notification_old = await notification_service.create(
            user_id=old_coach_user_id,
            type='coach_removal',
            message=f'Você foi removido como treinador da equipe {team.name}',
            notification_data={
                'team_id': str(team.id),
                'team_name': team.name,
                'removed_at': now.isoformat(),
            }
        )
        await notification_service.broadcast_to_user(old_coach_user_id, notification_old)
    
    return TeamBase.model_validate(team)


@router.get(
    "/{team_id}/coaches/history",
    response_model=TeamCoachHistoryResponse,
    summary="Histórico de treinadores da equipe",
    description="""
Retorna todos os treinadores que já foram vinculados à equipe (ativos e inativos).

**Step 19:** Endpoint de histórico de coaches.

**Consulta:**
- Busca todos TeamMemberships onde OrgMembership.role_id == 3 (treinador)
- Ordena por start_at DESC (mais recente primeiro)
- Inclui coach atual (end_at IS NULL) e coaches anteriores (end_at preenchido)

**Permissão:** Qualquer membro da equipe
""",
    responses={
        200: {"description": "Histórico retornado com sucesso"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Equipe não encontrada"},
    },
)
async def get_team_coaches_history(
    team_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador", "membro"], require_team=True)
    ),
):
    """
    Retorna histórico de treinadores da equipe (Step 19).
    
    - Lista todos coaches (ativos + inativos)
    - Ordena por data de início (mais recente primeiro)
    - Marca qual é o atual (end_at IS NULL)
    """
    service = TeamService(db)
    team = await service.get_by_id(team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail="team_not_found")
    
    # Query: buscar todos coaches (role_id=3) da equipe
    stmt = (
        select(TeamMembership, Person)
        .join(Person, TeamMembership.person_id == Person.id)
        .join(OrgMembership, TeamMembership.org_membership_id == OrgMembership.id)
        .join(Role, OrgMembership.role_id == Role.id)
        .where(
            TeamMembership.team_id == team_id,
            OrgMembership.role_id == 3,  # role_id=3 = treinador
            TeamMembership.deleted_at.is_(None),
        )
        .order_by(TeamMembership.start_at.desc())
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    items = []
    for tm, person in rows:
        is_current = tm.end_at is None and tm.status == 'ativo'
        items.append(
            CoachHistoryItem(
                id=tm.id,
                person_id=person.id,
                person_name=person.full_name,
                start_at=tm.start_at,
                end_at=tm.end_at,
                is_current=is_current,
            )
        )
    
    return TeamCoachHistoryResponse(
        items=items,
        total=len(items),
    )


@router.post(
    "/{team_id}/members/{membership_id}/resend-invite",
)
async def resend_team_member_invite(
    team_id: UUID,
    membership_id: UUID,
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente", "coordenador"], require_team=True)),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Reenvia convite para membro pendente da equipe.
    
    **Regras:**
    - Apenas membros com status='pendente'
    - Cooldown de 48h entre reenvios (configurável via INVITE_RESEND_COOLDOWN_HOURS)
    - Máximo de 3 reenvios por convite (configurável via INVITE_MAX_RESEND_COUNT)
    - Incrementa resend_count a cada reenvio
    - Atualiza updated_at para marcar último reenvio
    - Busca PasswordReset vinculado ao email da pessoa
    - Atualiza created_at do token para resetar expiry
    - Reenvia email de convite
    
    **Permissões:** Dirigente ou Coordenador
    
    **Step 16** do plano de gestão de staff.
    """
    # Buscar team_membership
    stmt = (
        select(TeamMembership, Person)
        .join(Person, TeamMembership.person_id == Person.id)
        .where(
            TeamMembership.id == membership_id,
            TeamMembership.team_id == team_id,
            TeamMembership.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "membership_not_found", "message": "Vínculo não encontrado"}
        )
    
    tm, person = row
    
    # Validar status pendente
    if tm.status != "pendente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "member_not_pending",
                "message": "Apenas membros pendentes podem receber reenvio de convite"
            }
        )
    
    # Validar limite de reenvios
    if tm.resend_count >= settings.INVITE_MAX_RESEND_COUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "resend_limit_reached",
                "message": f"Limite de {settings.INVITE_MAX_RESEND_COUNT} reenvios atingido"
            }
        )
    
    # Validar cooldown de 48h (usar updated_at como referência)
    now = datetime.now()
    cooldown_hours = settings.INVITE_RESEND_COOLDOWN_HOURS
    time_since_last_send = now - tm.updated_at.replace(tzinfo=None)
    cooldown_delta = timedelta(hours=cooldown_hours)
    
    if time_since_last_send < cooldown_delta:
        hours_remaining = (cooldown_delta - time_since_last_send).total_seconds() / 3600
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "resend_cooldown_active",
                "message": f"Aguarde {cooldown_hours}h entre reenvios. Restam {hours_remaining:.1f}h"
            }
        )
    
    # Buscar token de convite (PasswordReset vinculado ao email)
    user_stmt = select(User).where(User.person_id == person.id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "user_not_found", "message": "Usuário não encontrado para este membro"}
        )
    
    # Buscar PasswordReset ativo (token_type='welcome', used=False ou used_at IS NULL)
    token_stmt = (
        select(PasswordReset)
        .where(
            PasswordReset.user_id == user.id,
            PasswordReset.token_type == "welcome",
            PasswordReset.deleted_at.is_(None),
        )
        .order_by(PasswordReset.created_at.desc())
    )
    token_result = await db.execute(token_stmt)
    password_reset = token_result.scalar_one_or_none()
    
    if not password_reset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "invite_token_not_found",
                "message": "Token de convite não encontrado. Crie um novo convite."
            }
        )
    
    # Atualizar resend_count e updated_at
    tm.resend_count += 1
    tm.updated_at = now
    
    # Atualizar created_at do token para resetar expiry (48h a partir de agora)
    password_reset.created_at = now
    password_reset.expires_at = now + timedelta(hours=48)
    
    # Buscar dados da equipe para email
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "team_not_found", "message": "Equipe não encontrada"}
        )
    
    # Buscar organização para nome no email
    org_stmt = select(OrgMembership).where(OrgMembership.id == tm.org_membership_id)
    org_result = await db.execute(org_stmt)
    org_membership = org_result.scalar_one_or_none()
    
    organization_name = None
    role_name = None
    if org_membership:
        from app.models.organization import Organization
        org = await db.get(Organization, org_membership.organization_id)
        organization_name = org.name if org else None
        
        role = await db.get(Role, org_membership.role_id)
        role_name = role.name if role else None
    
    # Commit das alterações
    await db.commit()
    
    # Reenviar email de convite
    app_url = settings.FRONTEND_URL
    email_sent = email_service_v2.send_invite_email(
        to_email=user.email,
        person_name=person.full_name,
        token=password_reset.token,
        app_url=app_url,
        organization_name=organization_name,
        role_name=role_name,
    )
    
    if not email_sent:
        logger.warning(f"Falha ao reenviar convite para {user.email}")
    
    # Calcular próximo reenvio possível
    next_resend_at = tm.updated_at + timedelta(hours=cooldown_hours)
    resends_remaining = settings.INVITE_MAX_RESEND_COUNT - tm.resend_count
    
    return {
        "success": True,
        "resend_count": tm.resend_count,
        "next_resend_at": next_resend_at.isoformat(),
        "resends_remaining": resends_remaining,
        "email_sent": email_sent,
    }


@router.delete(
    "/{team_id}/members/{membership_id}/cancel-invite",
)
async def cancel_team_member_invite(
    team_id: UUID,
    membership_id: UUID,
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente", "coordenador"], require_team=True)),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Cancela convite pendente de membro da equipe.
    
    **Ações:**
    - Busca TeamMembership com status='pendente'
    - Busca PasswordReset vinculado ao usuário
    - Marca token como usado (used_at = now) para desativar
    - Soft delete do TeamMembership
    - **NÃO envia email ao convidado** (cancelamento silencioso)
    
    **Permissões:** Dirigente ou Coordenador
    
    **Step 16** do plano de gestão de staff.
    """
    # Buscar team_membership
    stmt = (
        select(TeamMembership, Person)
        .join(Person, TeamMembership.person_id == Person.id)
        .where(
            TeamMembership.id == membership_id,
            TeamMembership.team_id == team_id,
            TeamMembership.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "membership_not_found", "message": "Vínculo não encontrado"}
        )
    
    tm, person = row
    
    # Validar status pendente
    if tm.status != "pendente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "member_not_pending",
                "message": "Apenas convites pendentes podem ser cancelados"
            }
        )
    
    # Buscar usuário vinculado
    user_stmt = select(User).where(User.person_id == person.id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    if user:
        # Buscar e desativar todos os tokens de convite ativos
        token_stmt = (
            select(PasswordReset)
            .where(
                PasswordReset.user_id == user.id,
                PasswordReset.token_type == "welcome",
                PasswordReset.deleted_at.is_(None),
            )
        )
        token_result = await db.execute(token_stmt)
        tokens = token_result.scalars().all()
        
        now = datetime.now()
        for token in tokens:
            token.used_at = now  # Marca como usado para desativar
    
    # Soft delete do TeamMembership
    tm.deleted_at = datetime.now()
    tm.deleted_reason = "Convite cancelado por dirigente/coordenador"
    
    await db.commit()
    
    # NÃO enviar email ao convidado (cancelamento silencioso)
    
    return {"success": True}


@router.post(
    "/{team_id}/registrations",
    status_code=status.HTTP_201_CREATED,
    summary="Mover atleta para equipe",
    operation_id="moveAthleteToTeam",
    response_model=TeamRegistration,
    responses={
        201: {"description": "Inscricao criada com sucesso"},
        401: {"description": "Token invalido ou ausente"},
        403: {"description": "Permissao insuficiente"},
        404: {"description": "Atleta ou equipe nao encontrada"},
        409: {"description": "Periodo sobreposto (RDB10)"},
    },
)
async def move_athlete_to_team(
    team_id: UUID,
    payload: TeamRegistrationMoveRequest,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"], require_org=True, require_team=True)
    ),
) -> TeamRegistration:
    """
    Move atleta para equipe na temporada.

    - Encerra inscricoes ativas na temporada (RDB10)
    - Cria nova inscricao na equipe alvo
    """
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="team_not_found")

    athlete = await db.get(Athlete, payload.athlete_id)
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="athlete_not_found")

    if str(athlete.organization_id) != str(ctx.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission_denied")

    season = await db.get(Season, team.season_id)
    if not season:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="season_not_found")

    season_start = season.starts_at or date.today()
    age = season_start.year - athlete.birth_date.year
    if (season_start.month, season_start.day) < (athlete.birth_date.month, athlete.birth_date.day):
        age -= 1

    category_result = await db.execute(
        select(Category)
        .where(or_(Category.min_age.is_(None), Category.min_age <= age))
        .where(or_(Category.max_age.is_(None), Category.max_age >= age))
        .order_by(Category.min_age.desc())
        .limit(1)
    )
    category = category_result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="category_not_found")

    start_at = payload.start_at or date.today()
    end_previous_at = payload.end_previous_at or start_at

    service = TeamRegistrationService(db)
    await service.close_active_registrations(
        athlete_id=payload.athlete_id,
        season_id=team.season_id,
        end_at=end_previous_at,
    )

    try:
        registration = await service.create(
            athlete_id=payload.athlete_id,
            season_id=team.season_id,
            category_id=category.id,
            team_id=team.id,
            organization_id=team.organization_id,
            created_by_membership_id=ctx.membership_id,
            role=payload.role,
            start_at=start_at,
            end_at=None,
        )
        await db.commit()
        await db.refresh(registration)
        return TeamRegistration.model_validate(registration)
    except ValueError as e:
        await db.rollback()
        if str(e) == "period_overlap":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="period_overlap",
            )
        if str(e) == "invalid_date_range":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="invalid_date_range",
            )
        raise


@router.get("/{team_id}/wellness-top-performers")
async def get_team_wellness_top_performers(
    team_id: UUID,
    month: Optional[str] = Query(None, description="Mês de referência (YYYY-MM), default: mês anterior"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador"], require_org=True)
    ),
):
    """
    Retorna Top 5 atletas com melhor taxa de resposta de wellness
    
    Relatório de desempenho dos atletas mais comprometidos com wellness.
    
    Args:
        team_id: ID do team
        month: Mês específico (YYYY-MM) ou None para mês anterior
        
    Returns:
        {
            "month": "2026-01",
            "team_id": "uuid",
            "team_name": "Sub-20",
            "top_performers": [
                {
                    "athlete_id": 10,
                    "athlete_name": "João Silva",
                    "response_rate": 95.5,
                    "badges_earned_count": 3,
                    "current_streak_months": 2,
                    "total_expected": 20,
                    "total_responded": 19
                }
            ]
        }
    
    Ordenação: Por response_rate DESC LIMIT 5
    
    Acesso:
    - Dirigente: Qualquer team da organização
    - Coordenador/Treinador: Apenas teams que coordena/treina
    """
    from datetime import datetime, timedelta
    from app.services.wellness_gamification_service import WellnessGamificationService
    from app.models.team_membership import TeamMembership
    from app.models.persons import Person
    
    # Verificar se team existe e pertence à org
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team não encontrado")
    
    if team.organization_id != ctx.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Team não pertence à sua organização"
        )
    
    # TODO: Verificar se usuário tem acesso ao team (se não é dirigente)
    # if "dirigente" not in ctx.roles:
    #     # Verificar team_memberships do usuário
    #     pass
    
    # Determinar mês de referência
    if month is None:
        today = datetime.now()
        if today.month == 1:
            target_month = datetime(today.year - 1, 12, 1)
        else:
            target_month = datetime(today.year, today.month - 1, 1)
        month = target_month.strftime("%Y-%m")
    else:
        # Validar formato
        try:
            year, month_num = month.split("-")
            target_month = datetime(int(year), int(month_num), 1)
        except (ValueError, AttributeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de mês inválido. Use YYYY-MM"
            )
    
    # Calcular período do mês
    year, month_num = month.split("-")
    month_start = datetime(int(year), int(month_num), 1)
    if int(month_num) == 12:
        month_end = datetime(int(year) + 1, 1, 1) - timedelta(seconds=1)
    else:
        month_end = datetime(int(year), int(month_num) + 1, 1) - timedelta(seconds=1)
    
    # Buscar atletas ativos do team
    from app.models.wellness_pre import WellnessPre
    from app.models.wellness_post import WellnessPost
    from app.models.training_sessions import TrainingSession
    from app.models.attendance import Attendance
    from sqlalchemy import func, and_
    
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
    result = await db.execute(stmt)
    rows = result.all()
    
    # Calcular métricas para cada atleta
    performers = []
    
    gamification_service = WellnessGamificationService(db)
    
    for athlete, person in rows:
        # Calcular response rate usando método do service
        rate_data = await gamification_service._calculate_athlete_monthly_rate(
            athlete_id=athlete.id,
            month_start=month_start,
            month_end=month_end
        )
        
        # Contar badges conquistados (lifetime)
        badges = await gamification_service.get_athlete_badges(
            athlete_id=athlete.id,
            limit=100
        )
        badges_count = len(badges)
        
        # Calcular streak atual
        current_streak = 0
        if badges_count >= 3:
            # Verificar quantos meses consecutivos com badge monthly
            monthly_badges = [
                b for b in badges 
                if b['badge_type'] == 'wellness_champion_monthly'
            ]
            monthly_badges.sort(key=lambda x: x['month_reference'], reverse=True)
            
            # Contar streak a partir do mais recente
            if monthly_badges:
                last_month = datetime.strptime(monthly_badges[0]['month_reference'], "%Y-%m")
                current_streak = 1
                
                for i in range(1, len(monthly_badges)):
                    badge_month = datetime.strptime(monthly_badges[i]['month_reference'], "%Y-%m")
                    # Verificar se é mês consecutivo
                    if last_month.month == 1:
                        expected_prev = datetime(last_month.year - 1, 12, 1)
                    else:
                        expected_prev = datetime(last_month.year, last_month.month - 1, 1)
                    
                    if badge_month == expected_prev:
                        current_streak += 1
                        last_month = badge_month
                    else:
                        break
        
        performers.append({
            "athlete_id": athlete.id,
            "athlete_name": person.full_name,
            "response_rate": rate_data["response_rate"],
            "badges_earned_count": badges_count,
            "current_streak_months": current_streak,
            "total_expected": rate_data["expected_responses"],
            "total_responded": rate_data["actual_responses"]
        })
    
    # Ordenar por response_rate DESC e pegar top 5
    performers.sort(key=lambda x: x["response_rate"], reverse=True)
    top_5 = performers[:5]
    
    return {
        "month": month,
        "team_id": str(team_id),
        "team_name": team.name,
        "top_performers": top_5,
        "total_athletes": len(performers)
    }


@router.get("/{team_id}/staff", response_model=TeamStaffResponse)
async def get_team_staff(
    team_id: UUID,
    active_only: bool = Query(True, description="Apenas vínculos ativos"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador"], require_team=True)
    ),
):
    """
    Lista staff (treinadores) vinculados à equipe.
    
    Regras:
    - R25/R26: Permissões por papel
    - RF7: coach_membership_id principal
    
    Returns:
        Lista de membros do staff com informações da pessoa
    """
    # Verificar se equipe existe
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="team_not_found")
    
    # Step 1: Buscar staff via team_memberships (correto) em vez de coach_membership_id
    # Inclui membros ativos E pendentes (fluxo welcome)
    query = (
        select(TeamMembership, Person, OrgMembership, Role)
        .join(Person, TeamMembership.person_id == Person.id)
        .join(OrgMembership, TeamMembership.org_membership_id == OrgMembership.id)
        .join(Role, OrgMembership.role_id == Role.id)
        .filter(
            TeamMembership.team_id == team_id,
            TeamMembership.status.in_(["ativo", "pendente"]),
            TeamMembership.deleted_at.is_(None)
        )
    )
    
    if active_only:
        query = query.filter(
            TeamMembership.status == "ativo",
            TeamMembership.end_at.is_(None)
        )
    
    result = await db.execute(query)
    rows = result.all()
    
    staff_members = []
    for team_membership, person, org_membership, role in rows:
        # TODO Step 16: Calcular can_resend_invite (48h + resend_count < 3)
        # Por enquanto, deixar False
        staff_members.append(TeamStaffMember(
            id=team_membership.id,
            person_id=person.id,
            full_name=person.full_name,
            role=role.code,
            status=team_membership.status,
            start_at=team_membership.start_at,
            end_at=team_membership.end_at,
            invite_token=None,  # TODO: buscar token se status=pendente
            invited_at=team_membership.created_at if team_membership.status == "pendente" else None,
            resend_count=team_membership.resend_count,
            can_resend_invite=False,  # TODO: implementar lógica
        ))
    
    return TeamStaffResponse(
        items=staff_members,
        total=len(staff_members),
    )


@router.delete(
    "/{team_id}/staff/{membership_id}",
    summary="Remover membro do staff",
    description="""
Remove membro da comissão técnica (dirigente, coordenador ou treinador).

**Step 35:** Endpoint universal com lógica condicional baseada no papel.

**Comportamento:**
- **SE treinador (role_id=3):**
  - Encerra vínculo (end_at=now(), status='inativo')
  - Remove referência team.coach_membership_id = NULL
  - Envia notificação via WebSocket ao treinador removido
  - Retorna {team_without_coach: true}
- **SENÃO (dirigente/coordenador):**
  - Soft delete (deleted_at=now(), deleted_reason)
  - Retorna {team_without_coach: false}

**Validações:**
- 404: team ou membership não encontrado
- 400: membership não pertence à equipe
- 403: sem permissão (apenas dirigente/coordenador)

**Permissão:** Dirigente ou Coordenador
""",
    responses={
        200: {"description": "Membro removido com sucesso"},
        400: {"description": "Membership não pertence à equipe"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Equipe ou membership não encontrado"},
    },
)
async def remove_staff_member(
    team_id: UUID,
    membership_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador"], require_team=True)
    ),
):
    """
    Remove membro do staff (Step 35).
    
    Lógica condicional:
    - Treinador: encerra vínculo + notifica + remove referência do team
    - Outros: soft delete
    """
    now = datetime.now(timezone.utc)
    notification_service = NotificationService(db)
    
    # 1. Buscar equipe
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="team_not_found")
    
    # 2. Buscar TeamMembership com joins para validar papel
    query = (
        select(TeamMembership, Person, OrgMembership, Role, User)
        .join(Person, TeamMembership.person_id == Person.id)
        .join(OrgMembership, TeamMembership.org_membership_id == OrgMembership.id)
        .join(Role, OrgMembership.role_id == Role.id)
        .join(User, Person.id == User.person_id)
        .filter(
            TeamMembership.id == membership_id,
            TeamMembership.deleted_at.is_(None)
        )
    )
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="membership_not_found")
    
    team_membership, person, org_membership, role, user = row
    
    # 3. Validar que membership pertence à equipe
    if team_membership.team_id != team_id:
        raise HTTPException(
            status_code=400,
            detail="membership_does_not_belong_to_team"
        )
    
    # 4. Lógica condicional baseada no papel
    is_coach = role.id == 3  # role_id=3 → treinador
    team_without_coach = False
    
    if is_coach:
        # **CASO TREINADOR:** Encerrar vínculo + notificar + remover referência
        team_membership.end_at = now
        team_membership.status = "inativo"
        
        # Remover referência do team se este membership for o coach atual
        if team.coach_membership_id == org_membership.id:
            team.coach_membership_id = None
            team_without_coach = True
        
        # Notificar coach removido via WebSocket + banco
        notification = await notification_service.create(
            user_id=user.id,
            type="coach_removal",
            message=f"Você foi removido como treinador da equipe {team.name}",
            notification_data={
                "team_id": str(team.id),
                "team_name": team.name,
                "removed_at": now.isoformat(),
                "removed_by": ctx.user_full_name or "Administrador",
            }
        )
        
        # Broadcast via WebSocket se usuário estiver online
        await notification_service.broadcast_to_user(user.id, notification)
        
        logger.info(
            f"Coach removed from team: team_id={team_id}, "
            f"coach_name={person.full_name}, removed_by={ctx.user_id}"
        )
    else:
        # **CASO DIRIGENTE/COORDENADOR:** Soft delete
        team_membership.deleted_at = now
        team_membership.deleted_reason = f"Removido por {ctx.user_full_name or 'administrador'}"
        
        logger.info(
            f"Staff member soft deleted: team_id={team_id}, "
            f"member_name={person.full_name}, role={role.code}, removed_by={ctx.user_id}"
        )
    
    # 5. Commit mudanças
    await db.commit()
    
    return {
        "success": True,
        "team_without_coach": team_without_coach,
        "message": f"{person.full_name} removido da equipe {team.name}",
    }


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: UUID,
    reason: str = Query("Exclusão manual", description="Motivo da exclusão"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["coordenador", "dirigente"], require_team=True)
    ),
):
    """
    Exclui equipe (soft delete). Regras: R29/R33
    
    Comportamento:
    - Soft delete: marca deleted_at e deleted_reason
    - Não remove fisicamente do banco
    """
    service = TeamService(db)
    team = await service.get_by_id(team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail="not_found")

    await service.soft_delete(team, reason=reason)
    await db.commit()
    return None
