"""
Router: Team Invites (convites RESTful aninhados em /teams/{team_id}/invites)

Sprint 1 - MVP Invite:
- GET  /teams/{team_id}/invites       → Lista convites pendentes
- POST /teams/{team_id}/invites       → Envia novo convite
- POST /teams/{team_id}/invites/{id}/resend → Reenvia convite
- DELETE /teams/{team_id}/invites/{id} → Cancela convite

Sprint 3 - Hardening:
- Códigos de erro padronizados (INVITE_EXISTS, INVITE_EXPIRED, etc.)
- Validação de membro já ativo
- Idempotência: reenviar não cria novo token se ainda válido

Substitui rotas legadas em team_members.py:
- POST /team-members/invite
- GET  /team-members/pending
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, or_, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import permission_dep
from app.core.auth import ExecutionContext
from app.core.config import settings
from app.core.db import get_async_db
from app.models.user import User
from app.models.person import Person, PersonContact
from app.models.role import Role
from app.models.membership import OrgMembership
from app.models.password_reset import PasswordReset
from app.models.team_membership import TeamMembership
from app.models.team_registration import TeamRegistration
from app.models.team import Team
from app.models.category import Category
from app.models.athlete import Athlete
from pydantic import BaseModel, EmailStr, Field
from app.services.intake.email_service_v2 import email_service_v2
from app.services.password_reset_service import PasswordResetService


# ══════════════════════════════════════════════════════════════════════════════
# Error Codes (Sprint 3 - Padronização)
# ══════════════════════════════════════════════════════════════════════════════

class InviteErrorCode:
    """Códigos de erro padronizados para convites"""
    TEAM_NOT_FOUND = "TEAM_NOT_FOUND"
    INVITE_NOT_FOUND = "INVITE_NOT_FOUND"
    INVITE_EXISTS = "INVITE_EXISTS"          # Já existe convite pendente
    INVITE_EXPIRED = "INVITE_EXPIRED"        # Token expirado
    INVITE_REVOKED = "INVITE_REVOKED"        # Convite cancelado
    MEMBER_ACTIVE = "MEMBER_ACTIVE"          # Já é membro ativo
    FORBIDDEN = "FORBIDDEN"                  # Sem permissão
    BINDING_CONFLICT = "BINDING_CONFLICT"    # Conflito de vínculo (gênero/categoria)
    EMAIL_FAILED = "EMAIL_FAILED"            # Falha ao enviar email


def raise_invite_error(code: str, message: str, status_code: int = 400):
    """Helper para lançar HTTPException com código padronizado"""
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message}
    )


# ══════════════════════════════════════════════════════════════════════════════
# Schemas
# ══════════════════════════════════════════════════════════════════════════════

class InviteCreateRequest(BaseModel):
    """Payload para criar convite"""
    email: EmailStr
    role: Optional[str] = Field(default="membro", description="Role do membro na organização")


class InviteResponse(BaseModel):
    """Resposta de um convite"""
    id: str
    person_id: str
    name: str
    email: str
    role: str
    status: str
    invited_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_expired: bool = False                 # Sprint 3: indica se token expirou
    hours_remaining: Optional[int] = None    # Sprint 3: horas restantes
    initials: str = ""


class InviteListResponse(BaseModel):
    """Lista de convites pendentes"""
    items: List[InviteResponse]
    total: int


class InviteActionResponse(BaseModel):
    """Resposta de ação em convite"""
    success: bool
    message: str
    code: Optional[str] = None               # Sprint 3: código de erro/sucesso
    person_id: Optional[str] = None
    email_sent: bool = False


# ══════════════════════════════════════════════════════════════════════════════
# Router (aninhado em /teams/{team_id}/invites)
# ══════════════════════════════════════════════════════════════════════════════

router = APIRouter(tags=["Team Invites"])


@router.get(
    "/teams/{team_id}/invites",
    response_model=InviteListResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista convites pendentes da equipe"
)
async def list_team_invites(
    team_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador"], require_org=True)
    ),
):
    """
    Lista todos os convites pendentes de uma equipe.
    
    Retorna membros com status='pendente' no TeamMembership.
    """
    # Validar que a equipe existe e pertence à organização
    result = await db.execute(
        select(Team).filter(
            Team.id == team_id,
            Team.organization_id == ctx.organization_id,
            Team.deleted_at.is_(None)
        )
    )
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipe não encontrada"
        )
    
    # Buscar membros pendentes
    stmt = (
        select(TeamMembership, Person, PersonContact, User)
        .join(Person, TeamMembership.person_id == Person.id)
        .outerjoin(User, User.person_id == Person.id)
        .outerjoin(
            PersonContact,
            and_(
                PersonContact.person_id == Person.id,
                PersonContact.contact_type == "email",
                PersonContact.is_primary == True,
                PersonContact.deleted_at.is_(None)
            )
        )
        .where(
            TeamMembership.team_id == team_id,
            TeamMembership.status == "pendente",
            TeamMembership.deleted_at.is_(None),
            Person.deleted_at.is_(None),
        )
    )
    
    result = await db.execute(stmt)
    results = result.all()
    
    invites = []
    seen_ids = set()
    
    for membership, person, contact, user in results:
        if membership.id in seen_ids:
            continue
        seen_ids.add(membership.id)
        
        # Determinar email
        email = "sem-email@pendente"
        if contact and contact.contact_value:
            email = contact.contact_value
        elif user and user.email:
            email = user.email
        
        # Buscar role name
        role_name = "Membro"
        if membership.org_membership_id:
            org_result = await db.execute(
                select(OrgMembership).filter(
                    OrgMembership.id == membership.org_membership_id
                )
            )
            org_membership = org_result.scalar_one_or_none()
            if org_membership and org_membership.role_id:
                role_result = await db.execute(
                    select(Role).filter(Role.id == org_membership.role_id)
                )
                role = role_result.scalar_one_or_none()
                if role:
                    role_name = role.name
        
        # Buscar token info (para expires_at)
        expires_at = None
        invited_at = membership.created_at
        is_expired = True  # Default: expirado se não houver token
        hours_remaining = None
        
        if user:
            token_result = await db.execute(
                select(PasswordReset)
                .filter(
                    PasswordReset.user_id == user.id,
                    PasswordReset.token_type == "welcome",
                    PasswordReset.used_at.is_(None),
                )
                .order_by(PasswordReset.created_at.desc())
            )
            token_record = token_result.scalar_one_or_none()
            
            if token_record:
                expires_at = token_record.expires_at
                invited_at = token_record.created_at
                
                # Sprint 3: Calcular expiração
                now = datetime.now(timezone.utc)
                if expires_at:
                    # Garantir timezone aware
                    if expires_at.tzinfo is None:
                        expires_at = expires_at.replace(tzinfo=timezone.utc)
                    
                    is_expired = now > expires_at
                    if not is_expired:
                        remaining = expires_at - now
                        hours_remaining = int(remaining.total_seconds() / 3600)
        
        # Gerar iniciais
        initials = ""
        if person.full_name:
            parts = person.full_name.strip().split()
            if len(parts) >= 2:
                initials = f"{parts[0][0]}{parts[-1][0]}".upper()
            elif len(parts) == 1:
                initials = parts[0][:2].upper()
        
        invites.append(InviteResponse(
            id=str(membership.id),
            person_id=str(person.id),
            name=person.full_name or email,
            email=email,
            role=role_name,
            status="pendente",
            invited_at=invited_at,
            expires_at=expires_at,
            is_expired=is_expired,
            hours_remaining=hours_remaining,
            initials=initials,
        ))
    
    return InviteListResponse(items=invites, total=len(invites))


@router.post(
    "/teams/{team_id}/invites",
    response_model=InviteActionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Envia convite para novo membro"
)
async def create_team_invite(
    team_id: UUID,
    data: InviteCreateRequest,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador"], require_org=True)
    ),
):
    """
    Envia convite para membro de equipe, gerando token de boas-vindas (48h).
    
    Regras de Negócio (Sprint 3 - Hardening):
    - Verifica se já é membro ATIVO → bloqueia (MEMBER_ACTIVE)
    - Verifica se já existe convite pendente → bloqueia (INVITE_EXISTS)
    - Verifica conflitos de gênero/categoria → bloqueia (BINDING_CONFLICT)
    """
    try:
        # Validar equipe
        team_result = await db.execute(
            select(Team).filter(
                Team.id == team_id,
                Team.organization_id == ctx.organization_id,
                Team.deleted_at.is_(None)
            )
        )
        team = team_result.scalar_one_or_none()
        
        if not team:
            raise_invite_error(
                InviteErrorCode.TEAM_NOT_FOUND,
                "Equipe não encontrada",
                status_code=404
            )
        
        category_result = await db.execute(
            select(Category).filter(Category.id == team.category_id)
        )
        target_category = category_result.scalar_one_or_none()
        if not target_category:
            raise_invite_error(
                InviteErrorCode.TEAM_NOT_FOUND,
                "Categoria da equipe não encontrada",
                status_code=404
            )
        
        email_lower = data.email.strip().lower()
        
        # Verificar se já existe User
        user_result = await db.execute(
            select(User).filter(
                User.email == email_lower,
                User.deleted_at.is_(None)
            )
        )
        existing_user = user_result.scalar_one_or_none()
        
        if existing_user:
            person_result = await db.execute(
                select(Person).filter(
                    Person.id == existing_user.person_id,
                    Person.deleted_at.is_(None)
                )
            )
            person = person_result.scalar_one_or_none()
            if not person:
                raise_invite_error(
                    InviteErrorCode.BINDING_CONFLICT,
                    "Usuário existe mas Person vinculada não encontrada.",
                    status_code=400
                )
            
            # Sprint 3: Verificar se JÁ É MEMBRO ATIVO desta equipe
            active_result = await db.execute(
                select(TeamMembership).filter(
                    TeamMembership.team_id == team_id,
                    TeamMembership.person_id == person.id,
                    TeamMembership.status == "ativo",
                    TeamMembership.deleted_at.is_(None)
                )
            )
            active_membership = active_result.scalar_one_or_none()
            
            if active_membership:
                raise_invite_error(
                    InviteErrorCode.MEMBER_ACTIVE,
                    f"Este email já é membro ativo desta equipe.",
                    status_code=409
                )
            
            # Sprint 3: Verificar se já existe convite PENDENTE
            pending_result = await db.execute(
                select(TeamMembership).filter(
                    TeamMembership.team_id == team_id,
                    TeamMembership.person_id == person.id,
                    TeamMembership.status == "pendente",
                    TeamMembership.deleted_at.is_(None)
                )
            )
            pending_membership = pending_result.scalar_one_or_none()
            
            if pending_membership:
                raise_invite_error(
                    InviteErrorCode.INVITE_EXISTS,
                    f"Já existe um convite pendente para este email nesta equipe.",
                    status_code=409
                )
        else:
            # Buscar por PersonContact
            person_contact_result = await db.execute(
                select(PersonContact)
                .where(
                    PersonContact.contact_type == "email",
                    PersonContact.contact_value == email_lower,
                    PersonContact.deleted_at.is_(None)
                )
            )
            person_contact = person_contact_result.scalar_one_or_none()
            
            if person_contact:
                person_result = await db.execute(
                    select(Person).filter(
                        Person.id == person_contact.person_id,
                        Person.deleted_at.is_(None)
                    )
                )
                person = person_result.scalar_one_or_none()
            else:
                person = None
            
            # Criar nova Person se necessário
            if not person:
                person = Person(
                    full_name=email_lower.split("@")[0].title(),
                    first_name=email_lower.split("@")[0].title(),
                    last_name="",
                    gender="feminino",
                    birth_date=datetime.now(timezone.utc).date(),
                )
                db.add(person)
                await db.flush()
                
                contact = PersonContact(
                    person_id=person.id,
                    contact_type="email",
                    contact_value=email_lower,
                    is_primary=True,
                )
                db.add(contact)
                await db.flush()
        
        # Validar vínculos existentes
        await _validate_existing_bindings(db, person, team, target_category)
        
        # Criar ou obter User
        user = existing_user
        if not user:
            user = User(
                email=email_lower,
                person_id=person.id,
                status="inativo",
            )
            db.add(user)
            await db.flush()
        
        # Gerar token (welcome, 48h)
        reset_service = PasswordResetService(db)
        password_reset = await reset_service.create_reset_token(
            user_id=user.id,
            token_type="welcome",
            expires_in_hours=48,
        )
        
        # Buscar role do convite por code (mapeamento correto)
        role_code = (data.role or "membro").lower()
        role_result = await db.execute(
            select(Role).filter(Role.code == role_code)
        )
        role = role_result.scalar_one_or_none()
        
        # Se não encontrar, usar 'membro' como fallback
        if not role:
            role_fallback_result = await db.execute(
                select(Role).filter(Role.code == "membro")
            )
            role = role_fallback_result.scalar_one_or_none()
        
        # Se ainda não encontrar, usar ID 5 (membro) diretamente
        if not role:
            role_id_result = await db.execute(
                select(Role).filter(Role.id == 5)
            )
            role = role_id_result.scalar_one_or_none()
        
        # Buscar ou criar OrgMembership
        org_result = await db.execute(
            select(OrgMembership).filter(
                OrgMembership.person_id == person.id,
                OrgMembership.organization_id == ctx.organization_id,
                OrgMembership.deleted_at.is_(None)
            )
        )
        org_membership = org_result.scalar_one_or_none()
        
        org_membership_id = None
        if not org_membership:
            # Criar novo OrgMembership com role do convite
            if role:
                org_membership = OrgMembership(
                    person_id=person.id,
                    organization_id=ctx.organization_id,
                    role_id=role.id,
                )
                db.add(org_membership)
                await db.flush()
                org_membership_id = org_membership.id
        else:
            # ATUALIZAR role do OrgMembership existente com role do convite atual
            if role:
                org_membership.role_id = role.id
                await db.flush()
            org_membership_id = org_membership.id
        
        # Criar TeamMembership pendente
        existing_tm_result = await db.execute(
            select(TeamMembership).filter(
                TeamMembership.team_id == team_id,
                TeamMembership.person_id == person.id,
                TeamMembership.deleted_at.is_(None)
            )
        )
        existing_team_membership = existing_tm_result.scalar_one_or_none()
        
        if not existing_team_membership:
            team_membership = TeamMembership(
                team_id=team_id,
                person_id=person.id,
                org_membership_id=org_membership_id,
                status="pendente",
            )
            db.add(team_membership)
            await db.flush()
        
        # Enviar e-mail
        app_url = getattr(settings, "APP_URL", settings.FRONTEND_URL or "http://localhost:3000")
        email_sent = email_service_v2.send_invite_email(
            to_email=email_lower,
            person_name=person.full_name or email_lower,
            token=password_reset.token,
            app_url=app_url,
            organization_name=None,
            role_name=data.role,
        )
        
        if email_sent:
            await db.commit()
            return InviteActionResponse(
                success=True,
                message="Convite enviado com sucesso",
                code="INVITE_SENT",
                person_id=str(person.id),
                email_sent=True,
            )
        else:
            await db.rollback()
            raise_invite_error(
                InviteErrorCode.EMAIL_FAILED,
                "Usuário criado, mas falha ao enviar email",
                status_code=500
            )
    
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={"code": "INTERNAL_ERROR", "message": f"Erro ao enviar convite: {str(e)}"}
        )


@router.post(
    "/teams/{team_id}/invites/{invite_id}/resend",
    response_model=InviteActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Reenvia convite expirado"
)
async def resend_team_invite(
    team_id: UUID,
    invite_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador"], require_org=True)
    ),
):
    """
    Reenvia convite para membro pendente.
    
    Sprint 3 - Idempotência:
    - Se token ainda válido (>4h restantes), apenas reenvia email sem criar novo token
    - Se token expirado ou <4h restantes, cria novo token (48h)
    """
    # Validar equipe
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == ctx.organization_id,
        Team.deleted_at.is_(None)
    ).first()
    
    if not team:
        raise_invite_error(
            InviteErrorCode.TEAM_NOT_FOUND,
            "Equipe não encontrada",
            status_code=404
        )
    
    # Buscar membership pendente
    membership = db.query(TeamMembership).filter(
        TeamMembership.id == invite_id,
        TeamMembership.team_id == team_id,
        TeamMembership.status == "pendente",
        TeamMembership.deleted_at.is_(None)
    ).first()
    
    if not membership:
        raise_invite_error(
            InviteErrorCode.INVITE_NOT_FOUND,
            "Convite não encontrado ou não está pendente",
            status_code=404
        )
    
    # Buscar Person e email
    person_result = await db.execute(
        select(Person).filter(Person.id == membership.person_id)
    )
    person = person_result.scalar_one_or_none()
    if not person:
        raise_invite_error(
            InviteErrorCode.INVITE_NOT_FOUND,
            "Person não encontrada",
            status_code=404
        )
    
    # Obter email
    user_result = await db.execute(
        select(User).filter(User.person_id == person.id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise_invite_error(
            InviteErrorCode.INVITE_NOT_FOUND,
            "Usuário não encontrado",
            status_code=404
        )
    
    email = user.email
    
    # Sprint 3: Verificar se token atual ainda é válido (idempotência)
    now = datetime.now(timezone.utc)
    token_result = await db.execute(
        select(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.token_type == "welcome",
            PasswordReset.used_at.is_(None),
            PasswordReset.expires_at > now,
        ).order_by(PasswordReset.created_at.desc())
    )
    existing_token = token_result.scalar_one_or_none()
    
    reuse_token = False
    if existing_token:
        # Garantir timezone aware
        expires_at = existing_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        remaining = expires_at - now
        hours_remaining = remaining.total_seconds() / 3600
        
        # Se ainda tem >4h restantes, reutiliza o token
        if hours_remaining > 4:
            reuse_token = True
            password_reset = existing_token
    
    if not reuse_token:
        # Invalidar tokens antigos
        await db.execute(
            update(PasswordReset).filter(
                PasswordReset.user_id == user.id,
                PasswordReset.token_type == "welcome",
                PasswordReset.used_at.is_(None)
            ).values(used_at=datetime.now(timezone.utc))
        )
        
        # Gerar novo token (48h)
        reset_service = PasswordResetService(db)
        password_reset = await reset_service.create_reset_token(
            user_id=user.id,
            token_type="welcome",
            expires_in_hours=48,
        )
    
    # Reenviar email
    app_url = getattr(settings, "APP_URL", settings.FRONTEND_URL or "http://localhost:3000")
    email_sent = email_service_v2.send_invite_email(
        to_email=email,
        person_name=person.full_name or email,
        token=password_reset.token,
        app_url=app_url,
        organization_name=None,
        role_name=None,
    )
    
    if email_sent:
        await db.commit()
        return InviteActionResponse(
            success=True,
            message="Convite reenviado com sucesso" + (" (token reutilizado)" if reuse_token else ""),
            code="INVITE_RESENT",
            person_id=str(person.id),
            email_sent=True,
        )
    else:
        await db.rollback()
        raise_invite_error(
            InviteErrorCode.EMAIL_FAILED,
            "Erro ao reenviar email",
            status_code=500
        )


@router.delete(
    "/teams/{team_id}/invites/{invite_id}",
    response_model=InviteActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancela convite pendente"
)
async def cancel_team_invite(
    team_id: UUID,
    invite_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador"], require_org=True)
    ),
):
    """
    Cancela convite pendente (soft delete).
    
    Invalida tokens e marca TeamMembership como deleted.
    """
    # Validar equipe
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == ctx.organization_id,
        Team.deleted_at.is_(None)
    ).first()
    
    if not team:
        raise_invite_error(
            InviteErrorCode.TEAM_NOT_FOUND,
            "Equipe não encontrada",
            status_code=404
        )
    
    # Buscar membership pendente
    membership = db.query(TeamMembership).filter(
        TeamMembership.id == invite_id,
        TeamMembership.team_id == team_id,
        TeamMembership.status == "pendente",
        TeamMembership.deleted_at.is_(None)
    ).first()
    
    if not membership:
        raise_invite_error(
            InviteErrorCode.INVITE_NOT_FOUND,
            "Convite não encontrado ou não está pendente",
            status_code=404
        )
    
    # Buscar User para invalidar tokens
    person_result = await db.execute(
        select(Person).filter(Person.id == membership.person_id)
    )
    person = person_result.scalar_one_or_none()
    if person:
        user_result = await db.execute(
            select(User).filter(User.person_id == person.id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            # Invalidar tokens welcome
            await db.execute(
                update(PasswordReset).filter(
                    PasswordReset.user_id == user.id,
                    PasswordReset.token_type == "welcome",
                    PasswordReset.used_at.is_(None)
                ).values(used_at=datetime.now(timezone.utc))
            )
    # Soft delete do membership
    membership.deleted_at = datetime.now(timezone.utc)
    membership.deleted_reason = "Convite cancelado"
    
    await db.commit()
    
    return InviteActionResponse(
        success=True,
        message="Convite cancelado com sucesso",
        code="INVITE_REVOKED",
        person_id=str(membership.person_id) if membership.person_id else None,
        email_sent=False,
    )


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

async def _validate_existing_bindings(
    db: AsyncSession,
    person: Person,
    target_team: Team,
    target_category: Category
):
    """
    Valida se a pessoa pode receber convite para a equipe.
    
    Sprint 3 - Regras:
    - Não pode ter vínculo ativo/pendente em equipe de gênero diferente
    - Só pode receber convite para categoria inferior (max_age menor)
    """
    # Verificar se é atleta (TeamRegistration)
    athlete_result = await db.execute(
        select(Athlete).filter(
            Athlete.person_id == person.id,
            Athlete.deleted_at.is_(None)
        )
    )
    athlete = athlete_result.scalar_one_or_none()
    
    if athlete:
        existing_registrations_result = await db.execute(
            select(TeamRegistration, Team, Category)
            .join(Team, TeamRegistration.team_id == Team.id)
            .join(Category, Team.category_id == Category.id)
            .where(
                TeamRegistration.athlete_id == athlete.id,
                or_(
                    TeamRegistration.end_at.is_(None),
                    TeamRegistration.end_at > datetime.now(timezone.utc)
                ),
                TeamRegistration.deleted_at.is_(None),
                Team.deleted_at.is_(None)
            )
        )
        existing_registrations = existing_registrations_result.all()
        
        for reg, team, category in existing_registrations:
            if team.gender != target_team.gender:
                raise_invite_error(
                    InviteErrorCode.BINDING_CONFLICT,
                    f"Atleta já possui vínculo com equipe de gênero diferente ({team.name})",
                    status_code=409
                )
            
            if target_category.max_age >= category.max_age:
                raise_invite_error(
                    InviteErrorCode.BINDING_CONFLICT,
                    f"Atleta já possui vínculo com {team.name} ({category.name}). Só pode convidar para categorias inferiores.",
                    status_code=409
                )
    
    # Verificar se é staff (TeamMembership)
    existing_memberships_result = await db.execute(
        select(TeamMembership, Team, Category)
        .join(Team, TeamMembership.team_id == Team.id)
        .join(Category, Team.category_id == Category.id)
        .where(
            TeamMembership.person_id == person.id,
            TeamMembership.status.in_(["pendente", "ativo"]),
            TeamMembership.deleted_at.is_(None),
            Team.deleted_at.is_(None)
        )
    )
    existing_memberships = existing_memberships_result.all()
    
    for membership, team, category in existing_memberships:
        if team.gender != target_team.gender:
            raise_invite_error(
                InviteErrorCode.BINDING_CONFLICT,
                f"Membro já possui vínculo com equipe de gênero diferente ({team.name})",
                status_code=409
            )
        
        if target_category.max_age >= category.max_age:
            raise_invite_error(
                InviteErrorCode.BINDING_CONFLICT,
                f"Membro já possui vínculo com {team.name} ({category.name}). Só pode convidar para categorias inferiores.",
                status_code=409
            )
