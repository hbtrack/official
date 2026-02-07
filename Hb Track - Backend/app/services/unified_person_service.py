"""
UnifiedPersonService - Ficha Única para cadastro de pessoas com diferentes papéis.

CANÔNICO (31/12/2025): Cadastro unificado para todos os papéis (Atleta, Dirigente, Coordenador, Treinador).

O formulário é o mesmo, com seções que aparecem/ocultam baseado no tipo de papel:
- Dados Pessoais: sempre visível (nome, nascimento, gênero, documentos, contatos)
- Dados de Atleta: visível apenas para papel Atleta (posições, camisa, responsável)
- Dados de Staff: visível para Dirigente/Coordenador/Treinador (cargo adicional)
- Acesso ao Sistema: opcional para todos (cria user com email/senha)

Fluxo:
1. Criar Person com dados básicos + documents + contacts
2. Se papel=Atleta: criar Athlete
3. Se papel=Staff: criar OrgMembership
4. Se criar_acesso=True: criar User e enviar email via Resend
"""

import logging
from datetime import datetime, timezone, date
from typing import Optional, List, Literal
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.person import Person, PersonContact, PersonDocument, PersonAddress
from app.models.athlete import Athlete, AthleteState
from app.models.membership import OrgMembership
from app.models.user import User
from app.models.team import Team
from app.models.team_registration import TeamRegistration
from app.core.security import hash_password
from pydantic import BaseModel, Field, EmailStr

logger = logging.getLogger(__name__)


class RoleType(str, Enum):
    """Tipos de papel disponíveis na Ficha Única."""
    ATLETA = "atleta"
    DIRIGENTE = "dirigente"
    COORDENADOR = "coordenador"
    TREINADOR = "treinador"


class PersonalDataInput(BaseModel):
    """Dados pessoais (comum a todos os papéis)."""
    full_name: str = Field(..., min_length=3, max_length=200)
    birth_date: date
    gender: Literal["masculino", "feminino"]
    
    # Documentos
    rg: str = Field(..., max_length=20)
    cpf: Optional[str] = Field(None, max_length=14)
    
    # Contatos
    phone: str = Field(..., max_length=20)
    email: Optional[EmailStr] = None
    
    # Endereço (opcional)
    zip_code: Optional[str] = Field(None, max_length=9)
    street: Optional[str] = Field(None, max_length=120)
    number: Optional[str] = Field(None, max_length=20)
    complement: Optional[str] = Field(None, max_length=80)
    neighborhood: Optional[str] = Field(None, max_length=80)
    city: Optional[str] = Field(None, max_length=80)
    state: Optional[str] = Field(None, max_length=2)


class AthleteDataInput(BaseModel):
    """Dados específicos de atleta."""
    main_defensive_position_id: int
    secondary_defensive_position_id: Optional[int] = None
    main_offensive_position_id: Optional[int] = None
    secondary_offensive_position_id: Optional[int] = None
    shirt_number: Optional[int] = Field(None, ge=1, le=99)
    guardian_name: Optional[str] = Field(None, max_length=100)
    guardian_phone: Optional[str] = Field(None, max_length=20)
    team_id: Optional[UUID] = None  # Se informado, cria team_registration


class SystemAccessInput(BaseModel):
    """Configurações de acesso ao sistema."""
    create_access: bool = False
    email: Optional[EmailStr] = None  # Obrigatório se create_access=True
    send_welcome_email: bool = True  # Envia email com link para criar senha


class UnifiedPersonCreateInput(BaseModel):
    """
    Input unificado para Ficha Única.
    
    Campos obrigatórios variam por papel:
    - Atleta: personal_data + athlete_data obrigatórios
    - Staff: personal_data obrigatório, athlete_data ignorado
    """
    role_type: RoleType
    organization_id: UUID
    personal_data: PersonalDataInput
    athlete_data: Optional[AthleteDataInput] = None
    system_access: SystemAccessInput = SystemAccessInput()


class UnifiedPersonService:
    """
    Serviço unificado para criar pessoas com diferentes papéis.
    
    Implementa a Ficha Única conforme REGRAS_GERENCIAMENTO_ATLETAS.md.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_person_with_role(
        self,
        data: UnifiedPersonCreateInput,
        created_by_user_id: Optional[UUID] = None,
    ) -> dict:
        """
        Cria pessoa com papel especificado.
        
        Args:
            data: Dados da pessoa e papel
            created_by_user_id: ID do usuário que está criando
            
        Returns:
            Dict com person_id e entity_id (athlete_id ou membership_id)
            
        Raises:
            ValueError: Se validações falharem
        """
        # Validar dados específicos por papel
        if data.role_type == RoleType.ATLETA:
            if not data.athlete_data:
                raise ValueError("athlete_data_required")
            
            # Validar RD13: Goleira sem posição ofensiva
            if data.athlete_data.main_defensive_position_id == 5:  # Goleira
                if data.athlete_data.main_offensive_position_id:
                    raise ValueError("goleira_no_offensive_position")
            else:
                if not data.athlete_data.main_offensive_position_id:
                    raise ValueError("non_goalkeeper_requires_offensive_position")
        
        # Validar email obrigatório para acesso ao sistema
        if data.system_access.create_access:
            email = data.system_access.email or data.personal_data.email
            if not email:
                raise ValueError("email_required_for_system_access")
        
        # 1. Criar Person
        name_parts = data.personal_data.full_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        person = Person(
            id=str(uuid4()),
            full_name=data.personal_data.full_name,
            first_name=first_name,
            last_name=last_name,
            birth_date=data.personal_data.birth_date,
            gender=data.personal_data.gender,
        )
        self.db.add(person)
        await self.db.flush()
        
        # 2. Criar PersonDocuments
        rg_doc = PersonDocument(
            id=str(uuid4()),
            person_id=person.id,
            document_type='rg',
            document_number=data.personal_data.rg,
            is_verified=False,
        )
        self.db.add(rg_doc)
        
        if data.personal_data.cpf:
            cpf_doc = PersonDocument(
                id=str(uuid4()),
                person_id=person.id,
                document_type='cpf',
                document_number=data.personal_data.cpf.replace('.', '').replace('-', ''),
                is_verified=False,
            )
            self.db.add(cpf_doc)
        
        # 3. Criar PersonContacts
        phone_contact = PersonContact(
            id=str(uuid4()),
            person_id=person.id,
            contact_type='telefone',
            contact_value=data.personal_data.phone,
            is_primary=True,
            is_verified=False,
        )
        self.db.add(phone_contact)
        
        if data.personal_data.email:
            email_contact = PersonContact(
                id=str(uuid4()),
                person_id=person.id,
                contact_type='email',
                contact_value=data.personal_data.email,
                is_primary=True,
                is_verified=False,
            )
            self.db.add(email_contact)
        
        # 4. Criar PersonAddress (se fornecido)
        if data.personal_data.zip_code or data.personal_data.city:
            address = PersonAddress(
                id=str(uuid4()),
                person_id=person.id,
                address_type='residencial_1',
                postal_code=data.personal_data.zip_code,
                street=data.personal_data.street or 'Não informado',
                number=data.personal_data.number,
                complement=data.personal_data.complement,
                neighborhood=data.personal_data.neighborhood,
                city=data.personal_data.city or 'Não informado',
                state=data.personal_data.state or 'XX',
                country='Brasil',
                is_primary=True,
            )
            self.db.add(address)
        
        entity_id = None
        entity_type = None
        
        # 5. Criar entidade específica por papel
        if data.role_type == RoleType.ATLETA:
            entity_id, entity_type = await self._create_athlete(
                person=person,
                data=data,
                organization_id=data.organization_id,
            )
        else:
            entity_id, entity_type = await self._create_membership(
                person=person,
                role_type=data.role_type,
                organization_id=data.organization_id,
            )
        
        # 6. Criar User se solicitado
        user_id = None
        if data.system_access.create_access:
            user_id = await self._create_user(
                person=person,
                email=data.system_access.email or data.personal_data.email,
                send_welcome_email=data.system_access.send_welcome_email,
            )
        
        await self.db.commit()
        
        return {
            "person_id": person.id,
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "user_id": str(user_id) if user_id else None,
        }
    
    async def _create_athlete(
        self,
        person: Person,
        data: UnifiedPersonCreateInput,
        organization_id: UUID,
    ) -> tuple:
        """Cria Athlete e opcionalmente TeamRegistration."""
        athlete_data = data.athlete_data
        
        athlete = Athlete(
            id=uuid4(),
            person_id=person.id,
            organization_id=organization_id,
            state=AthleteState.ATIVA.value,
            injured=False,
            medical_restriction=False,
            load_restricted=False,
            athlete_name=person.full_name,
            birth_date=person.birth_date,
            shirt_number=athlete_data.shirt_number,
            main_defensive_position_id=athlete_data.main_defensive_position_id,
            secondary_defensive_position_id=athlete_data.secondary_defensive_position_id,
            main_offensive_position_id=athlete_data.main_offensive_position_id,
            secondary_offensive_position_id=athlete_data.secondary_offensive_position_id,
            guardian_name=athlete_data.guardian_name,
            guardian_phone=athlete_data.guardian_phone,
        )
        self.db.add(athlete)
        await self.db.flush()
        
        # Criar team_registration se team_id informado
        if athlete_data.team_id:
            result = await self.db.execute(
                select(Team).where(
                    Team.id == athlete_data.team_id,
                    Team.organization_id == organization_id,
                    Team.deleted_at.is_(None)
                )
            )
            team = result.scalar_one_or_none()
            if team:
                registration = TeamRegistration(
                    id=uuid4(),
                    athlete_id=athlete.id,
                    team_id=athlete_data.team_id,
                    start_at=datetime.now(timezone.utc),
                )
                self.db.add(registration)
        
        return athlete.id, "athlete"
    
    async def _create_membership(
        self,
        person: Person,
        role_type: RoleType,
        organization_id: UUID,
    ) -> tuple:
        """Cria OrgMembership para staff."""
        # Mapear role_type para role_id
        role_map = {
            RoleType.DIRIGENTE: 1,
            RoleType.COORDENADOR: 2,
            RoleType.TREINADOR: 3,
        }
        role_id = role_map.get(role_type, 1)
        
        membership = OrgMembership(
            id=str(uuid4()),
            person_id=person.id,
            role_id=role_id,
            organization_id=str(organization_id),
            start_at=datetime.now(timezone.utc),
        )
        self.db.add(membership)
        await self.db.flush()
        
        return membership.id, "membership"
    
    async def _create_user(
        self,
        person: Person,
        email: str,
        send_welcome_email: bool = True,
    ) -> UUID:
        """
        Cria User para acesso ao sistema.
        
        Se send_welcome_email=True, gera token de reset de senha e envia email via SendGrid.
        """
        import secrets
        
        # Gerar senha temporária (será trocada via email)
        temp_password = secrets.token_urlsafe(16)
        password_hash = hash_password(temp_password)
        
        user = User(
            id=str(uuid4()),
            email=email.lower(),
            password_hash=password_hash,
            person_id=person.id,
            status='pendente',  # Aguardando confirmação de email
        )
        self.db.add(user)
        await self.db.flush()
        
        if send_welcome_email:
            self._send_welcome_email(user, email)
        
        return UUID(user.id)
    
    def _send_welcome_email(self, user: User, email: str) -> None:
        """
        Envia email de boas-vindas com link para criar senha.
        """
        import secrets

        from app.core.config import settings
        from app.services.email_service import email_service

        try:
            reset_token = secrets.token_urlsafe(32)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            person_name = user.person.full_name if getattr(user, "person", None) else None

            sent = email_service.send_welcome_email(
                user_email=email,
                reset_link=reset_url,
                user_name=person_name,
            )
            if not sent:
                logger.warning(
                    "Falha ao enviar email de boas-vindas",
                    extra={"email": email, "user_id": user.id},
                )
        except Exception as exc:
            # Não deve bloquear o fluxo de criação
            logger.error(f"Erro ao enviar email de boas-vindas para {email}: {exc}")
