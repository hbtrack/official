"""
Router: Team Members (convites, listagem de pendentes)
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, or_
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
from pydantic import BaseModel, EmailStr
from app.services.intake.email_service_v2 import email_service_v2
from app.services.password_reset_service import PasswordResetService

router = APIRouter(tags=["team_members"])


# Schemas locais (substitui app.schemas.team_members)
class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: Optional[str] = "membro"
    team_id: UUID  # Obrigatório - não pode ser None


class InviteMemberResponse(BaseModel):
    success: bool
    message: str
    person_id: Optional[str] = None
    email_sent: bool = False


class PendingMemberItem(BaseModel):
    id: str
    person_id: str
    name: str
    email: str
    role: str
    status: str = "Pendente"
    initials: str = ""


class PendingMembersResponse(BaseModel):
    items: list[PendingMemberItem]
    total: int


@router.post("/invite", response_model=InviteMemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    data: InviteMemberRequest,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente", "coordenador"], require_org=True)),
):
    """
    Envia convite para membro de equipe, gerando token de boas-vindas (48h).
    
    Regra de Negócio:
    - Usuários pendentes ou com vínculos ativos NÃO podem receber novos convites
    - EXCEÇÃO: Podem receber se for para equipes do mesmo gênero e categorias inferiores (max_age menor)
    
    Step 2: Validação de permissão can_manage_members
    """
    # Step 2: Validar permissão can_manage_members
    ctx.requires("can_manage_members")
    
    try:
        # Validar que team_id foi fornecido
        if not data.team_id:
            raise HTTPException(
                status_code=400,
                detail="team_id é obrigatório para enviar convite"
            )
        
        email_lower = data.email.strip().lower()

        # PASSO 1: Verificar se já existe User com esse email (evita UniqueViolation)
        existing_user = db.query(User).filter(
            User.email == email_lower,
            User.deleted_at.is_(None)
        ).first()
        
        if existing_user:
            # Usuário já existe - usar a Person vinculada
            person = db.query(Person).filter(
                Person.id == existing_user.person_id,
                Person.deleted_at.is_(None)
            ).first()
            if not person:
                raise HTTPException(
                    status_code=400,
                    detail="Usuário existe mas Person vinculada não encontrada. Contate o suporte."
                )
        else:
            # PASSO 2: Buscar pessoa pelo email (via person_contacts)
            person_contact = db.execute(
                select(PersonContact)
                .where(
                    PersonContact.contact_type == "email",
                    PersonContact.contact_value == email_lower,
                    PersonContact.deleted_at.is_(None)
                )
            ).scalar_one_or_none()
            
            if person_contact:
                person = db.query(Person).filter(Person.id == person_contact.person_id, Person.deleted_at.is_(None)).first()
            else:
                person = None
            
            # PASSO 3: Criar nova Person apenas se não existe User nem PersonContact
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
                
                # Criar contato de email
                contact = PersonContact(
                    person_id=person.id,
                    contact_type="email",
                    contact_value=email_lower,
                    is_primary=True,
                )
                db.add(contact)
                await db.flush()
        
        # VALIDAÇÃO: Verificar se pessoa já tem vínculos pendentes ou ativos
        if data.team_id:
            # Buscar informações da equipe de destino
            target_team = db.query(Team).filter(Team.id == data.team_id, Team.deleted_at.is_(None)).first()
            if not target_team:
                raise HTTPException(status_code=404, detail="Equipe não encontrada")
            
            target_category = db.query(Category).filter(Category.id == target_team.category_id).first()
            if not target_category:
                raise HTTPException(status_code=404, detail="Categoria da equipe não encontrada")
            
            # Verificar se é atleta (TeamRegistration)
            athlete = db.query(Athlete).filter(Athlete.person_id == person.id, Athlete.deleted_at.is_(None)).first()
            
            if athlete:
                # Buscar vínculos pendentes ou ativos do atleta
                existing_registrations = db.execute(
                    select(TeamRegistration, Team, Category)
                    .join(Team, TeamRegistration.team_id == Team.id)
                    .join(Category, Team.category_id == Category.id)
                    .where(
                        TeamRegistration.athlete_id == athlete.id,
                        or_(
                            TeamRegistration.end_at.is_(None),  # Ativo
                            TeamRegistration.end_at > datetime.now(timezone.utc)  # Ainda não encerrado
                        ),
                        TeamRegistration.deleted_at.is_(None),
                        Team.deleted_at.is_(None)
                    )
                ).all()
                
                if existing_registrations:
                    # Validar se pode receber convite (mesmo gênero e categoria inferior)
                    for reg, team, category in existing_registrations:
                        # Diferentes gêneros: não permitido
                        if team.gender != target_team.gender:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Atleta já possui vínculo ativo com equipe de gênero diferente ({team.name} - {team.gender}). Não é possível convidar para equipe {target_team.name} ({target_team.gender})."
                            )
                        
                        # Mesmo gênero: só pode se categoria de destino for inferior (max_age menor)
                        if target_category.max_age >= category.max_age:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Atleta já possui vínculo ativo com equipe {team.name} (categoria {category.name}, max_age={category.max_age}). Só pode receber convite para categorias inferiores (max_age < {category.max_age})."
                            )
            
            # Verificar se é staff (TeamMembership)
            existing_memberships = db.execute(
                select(TeamMembership, Team, Category)
                .join(Team, TeamMembership.team_id == Team.id)
                .join(Category, Team.category_id == Category.id)
                .where(
                    TeamMembership.person_id == person.id,
                    TeamMembership.status.in_(["pendente", "ativo"]),
                    TeamMembership.deleted_at.is_(None),
                    Team.deleted_at.is_(None)
                )
            ).all()
            
            if existing_memberships:
                # Validar se pode receber convite (mesmo gênero e categoria inferior)
                for membership, team, category in existing_memberships:
                    # Diferentes gêneros: não permitido
                    if team.gender != target_team.gender:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Membro já possui vínculo com equipe de gênero diferente ({team.name} - {team.gender}). Não é possível convidar para equipe {target_team.name} ({target_team.gender})."
                        )
                    
                    # Mesmo gênero: só pode se categoria de destino for inferior (max_age menor)
                    if target_category.max_age >= category.max_age:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Membro já possui vínculo com equipe {team.name} (categoria {category.name}, max_age={category.max_age}). Só pode receber convite para categorias inferiores (max_age < {category.max_age})."
                        )

        # Usar existing_user se já foi encontrado no início, senão criar novo
        user = existing_user
        if not user:
            user = User(
                email=email_lower,
                person_id=person.id,
                status="inativo",
            )
            db.add(user)
            await db.flush()

        # Gerar token (welcome, 48h) em texto puro
        reset_service = PasswordResetService(db)
        password_reset = await reset_service.create_reset_token(
            user_id=user.id,
            token_type="welcome",
            expires_in_hours=48,
        )

        # Buscar role do convite por code (mapeamento correto)
        role_code = (data.role or "membro").lower()
        role = db.query(Role).filter(Role.code == role_code).first()
        
        # Se não encontrar, usar 'membro' como fallback
        if not role:
            role = db.query(Role).filter(Role.code == "membro").first()
        
        # Se ainda não encontrar, usar ID 5 (membro) diretamente
        if not role:
            role = db.query(Role).filter(Role.id == 5).first()
        
        # Buscar ou criar OrgMembership
        org_membership = db.query(OrgMembership).filter(
            OrgMembership.person_id == person.id,
            OrgMembership.organization_id == ctx.organization_id,
            OrgMembership.deleted_at.is_(None)
        ).first()
        
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

        # CRIAR TEAMMEMBERSHIP COM STATUS PENDENTE (sempre, mesmo sem OrgMembership)
        if data.team_id:
            # Verificar se já existe
            existing_team_membership = db.query(TeamMembership).filter(
                TeamMembership.team_id == data.team_id,
                TeamMembership.person_id == person.id,
                TeamMembership.deleted_at.is_(None)
            ).first()
            
            if not existing_team_membership:
                team_membership = TeamMembership(
                    team_id=data.team_id,
                    person_id=person.id,
                    org_membership_id=org_membership_id,  # Pode ser None
                    status="pendente",
                )
                db.add(team_membership)
                await db.flush()

        # Enviar e-mail de convite
        app_url = getattr(settings, "APP_URL", settings.FRONTEND_URL or "http://localhost:3000")
        
        logger.info(
            f"Tentando enviar email de convite: to={email_lower}, token={password_reset.token[:8]}..., role={data.role}"
        )
        
        email_sent = email_service_v2.send_invite_email(
            to_email=email_lower,
            person_name=person.full_name or email_lower,
            token=password_reset.token,
            app_url=app_url,
            organization_name=None,
            role_name=data.role,
        )

        logger.info(f"Resultado do envio de email: email_sent={email_sent}")
        
        if email_sent:
            await db.commit()
        else:
            await db.rollback()

        return InviteMemberResponse(
            success=email_sent,
            message="Convite enviado com sucesso" if email_sent else "Usuário criado, mas email não enviado",
            person_id=str(person.id),
            email_sent=email_sent,
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao enviar convite: {e}")


@router.get("/pending", response_model=PendingMembersResponse, status_code=status.HTTP_200_OK)
async def list_pending_members(
    team_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador"], require_org=True)
    ),
):
    """
    Lista membros pendentes (convites enviados, ainda não ativos).
    - Se team_id for informado, filtra pelos vínculos pendentes daquela equipe.
    - Caso contrário, retorna todos pendentes da organização.
    
    SIMPLIFICADO: Busca direto por TeamMembership com status="pendente"
    """
    try:
        # Query simplificada: buscar direto pelos TeamMembership pendentes
        if team_id:
            # Buscar membros pendentes de uma equipe específica
            stmt = (
                select(TeamMembership, Person, PersonContact)
                .join(Person, TeamMembership.person_id == Person.id)
                .outerjoin(
                    PersonContact, 
                    (PersonContact.person_id == Person.id) & 
                    (PersonContact.contact_type == "email") &
                    (PersonContact.is_primary == True)
                )
                .where(
                    TeamMembership.team_id == team_id,
                    TeamMembership.status == "pendente",
                    TeamMembership.deleted_at.is_(None),
                    Person.deleted_at.is_(None),
                )
            )
        else:
            # Buscar todos os membros pendentes da organização
            stmt = (
                select(TeamMembership, Person, PersonContact, Team)
                .join(Person, TeamMembership.person_id == Person.id)
                .join(Team, TeamMembership.team_id == Team.id)
                .outerjoin(
                    PersonContact, 
                    (PersonContact.person_id == Person.id) & 
                    (PersonContact.contact_type == "email") &
                    (PersonContact.is_primary == True)
                )
                .where(
                    Team.organization_id == ctx.organization_id,
                    TeamMembership.status == "pendente",
                    TeamMembership.deleted_at.is_(None),
                    Team.deleted_at.is_(None),
                    Person.deleted_at.is_(None),
                )
            )

        results = db.execute(stmt).all()

        pending_members = []
        seen_ids = set()  # Evitar duplicatas
        
        for row in results:
            if team_id:
                membership, person, contact = row
            else:
                membership, person, contact, team = row
            
            # Evitar duplicatas (pode haver múltiplos contatos)
            if membership.id in seen_ids:
                continue
            seen_ids.add(membership.id)
            
            # Buscar email do contato ou do usuário
            email = "sem-email@pendente"
            if contact and contact.contact_value:
                email = contact.contact_value
            else:
                # Tentar buscar do User
                user = db.query(User).filter(User.person_id == person.id).first()
                if user:
                    email = user.email
            
            # Buscar role name se tiver org_membership
            role_name = "Membro"
            if membership.org_membership_id:
                org_membership = db.query(OrgMembership).filter(OrgMembership.id == membership.org_membership_id).first()
                if org_membership and org_membership.role_id:
                    role = db.query(Role).filter(Role.id == org_membership.role_id).first()
                    if role:
                        role_name = role.name
            
            # Gerar iniciais
            initials = ""
            if person.full_name:
                parts = person.full_name.strip().split()
                if len(parts) >= 2:
                    initials = f"{parts[0][0]}{parts[-1][0]}".upper()
                elif len(parts) == 1:
                    initials = parts[0][:2].upper()
            
            pending_members.append(
                PendingMemberItem(
                    id=str(membership.id),
                    person_id=str(person.id),
                    name=person.full_name or email,
                    email=email,
                    role=role_name,
                    status="Pendente",
                    initials=initials,
                )
            )

        return PendingMembersResponse(items=pending_members, total=len(pending_members))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar membros pendentes: {e}",
        )
