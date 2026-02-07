"""
Serviço Principal da Ficha Única
FASE 3 - Service Layer

Orquestra criação transacional de:
- Person (+ contacts, documents, address, media)
- User (opcional)
- Organization (inline opcional)
- Team (inline opcional)
- Athlete (opcional)
- OrgMembership (opcional)
- TeamRegistration (opcional)
"""
import logging
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.core.auth import ExecutionContext
from app.schemas.intake import FichaUnicaRequest, FichaUnicaResponse
from app.models.person import Person, PersonContact, PersonDocument, PersonAddress, PersonMedia
from app.models.user import User
from app.models.password_reset import PasswordReset
from app.models.organization import Organization
from app.models.membership import Membership
from app.models.team import Team
from app.models.athlete import Athlete
from app.models.team_registration import TeamRegistration
from app.models.season import Season

from app.services.intake.validators import (
    normalize_cpf,
    normalize_email,
    normalize_phone,
    check_duplicate_contact,
    check_duplicate_document,
    validate_goalkeeper_positions,
    validate_category_eligibility
)

logger = logging.getLogger("hb.intake.service")


class FichaUnicaService:
    """
    Serviço transacional da Ficha Única.
    
    Implementa lógica de negócio completa para cadastro unificado.
    """
    
    def __init__(self, db: Session, ctx: ExecutionContext):
        self.db = db
        self.ctx = ctx
        self.created_entities: Dict[str, UUID] = {}
    
    def execute(self, payload: FichaUnicaRequest) -> FichaUnicaResponse:
        """
        Executa criação transacional da Ficha Única.
        
        Args:
            payload: Dados completos da ficha
        
        Returns:
            Response com IDs das entidades criadas
        
        Raises:
            HTTPException: 409 para duplicidades, 422 para validações
        """
        logger.info(f"Starting Ficha Única execution | actor={self.ctx.user.id}")
        
        try:
            # Validações de duplicidade ANTES da transação
            self._validate_duplicates(payload)
            
            # Cria pessoa
            person = self._create_or_update_person(payload)
            self.created_entities['person_id'] = person.id
            
            # Cria contatos
            self._create_contacts(person.id, payload.person.contacts)
            
            # Cria documentos
            self._create_documents(person.id, payload.person.documents)
            
            # Cria endereço (opcional)
            if payload.person.address:
                self._create_address(person.id, payload.person.address)
            
            # Cria mídia/foto (opcional)
            if payload.person.media and payload.person.media.profile_photo_url:
                self._create_media(person.id, payload.person.media)
            
            # Cria/seleciona temporada (FASE 4.1)
            season_id = None
            if payload.season:
                season_id = self._handle_season(payload.season)
                self.created_entities['season_id'] = season_id
            
            # Cria organização (inline opcional)
            organization_id = None
            if payload.organization:
                organization_id = self._handle_organization(payload.organization, season_id)
                self.created_entities['organization_id'] = organization_id
            
            # Cria equipe (inline opcional)
            team_id = None
            if payload.team:
                if not organization_id:
                    raise HTTPException(
                        status_code=422,
                        detail="organization é obrigatória quando team é fornecida"
                    )
                if not season_id:
                    raise HTTPException(
                        status_code=422,
                        detail="season é obrigatória quando team é fornecida"
                    )
                team_id = self._handle_team(payload.team, organization_id, season_id)
                self.created_entities['team_id'] = team_id
            
            # Cria atleta (opcional)
            athlete_id = None
            if payload.athlete and payload.athlete.create:
                athlete_id = self._create_athlete(person.id, organization_id, payload.athlete)
                self.created_entities['athlete_id'] = athlete_id
            
            # Cria vínculo atleta-equipe (opcional)
            registration_id = None
            if payload.registration and athlete_id and team_id:
                registration_id = self._create_team_registration(athlete_id, team_id, payload.registration)
                self.created_entities['registration_id'] = registration_id
            
            # Cria membership organizacional (opcional)
            membership_id = None
            if payload.membership and organization_id:
                membership_id = self._create_membership(person.id, organization_id, payload.membership)
                self.created_entities['membership_id'] = membership_id
            
            # Cria usuário/login (opcional)
            user_id = None
            if payload.create_user and payload.user:
                user_id = self._create_user(person.id, payload.user)
                self.created_entities['user_id'] = user_id
            
            logger.info(f"Ficha Única executed successfully | entities={self.created_entities}")
            
            return FichaUnicaResponse(
                person_id=self.created_entities['person_id'],
                user_id=self.created_entities.get('user_id'),
                season_id=self.created_entities.get('season_id'),
                organization_id=self.created_entities.get('organization_id'),
                team_id=self.created_entities.get('team_id'),
                athlete_id=self.created_entities.get('athlete_id'),
                membership_id=self.created_entities.get('membership_id'),
                registration_id=self.created_entities.get('registration_id')
            )
        
        except HTTPException:
            raise
        except IntegrityError as e:
            logger.error(f"Integrity error in Ficha Única: {str(e)}")
            raise HTTPException(
                status_code=409,
                detail="Violação de constraint de unicidade. Verifique duplicidades."
            )
        except Exception as e:
            logger.error(f"Unexpected error in Ficha Única: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Erro interno ao processar Ficha Única"
            )
    
    def _validate_duplicates(self, payload: FichaUnicaRequest) -> None:
        """Valida duplicidades antes da transação"""
        # Valida contatos
        for contact in payload.person.contacts:
            dup = check_duplicate_contact(
                self.db,
                contact.contact_type,
                contact.contact_value
            )
            if dup:
                person, contact_obj = dup
                raise HTTPException(
                    status_code=409,
                    detail={
                        "type": "duplicate_contact",
                        "field": contact.contact_type,
                        "value": contact.contact_value,
                        "existing_person_id": str(person.id),
                        "message": f"{contact.contact_type.capitalize()} já cadastrado para outra pessoa"
                    }
                )
        
        # Valida documentos
        for doc in payload.person.documents:
            dup = check_duplicate_document(
                self.db,
                doc.document_type,
                doc.document_number
            )
            if dup:
                person, doc_obj = dup
                raise HTTPException(
                    status_code=409,
                    detail={
                        "type": "duplicate_document",
                        "field": doc.document_type,
                        "value": doc.document_number,
                        "existing_person_id": str(person.id),
                        "message": f"{doc.document_type.upper()} já cadastrado para outra pessoa"
                    }
                )
    
    def _create_or_update_person(self, payload: FichaUnicaRequest) -> Person:
        """Cria nova pessoa"""
        person = Person(
            id=uuid4(),
            first_name=payload.person.first_name,
            last_name=payload.person.last_name,
            full_name=f"{payload.person.first_name} {payload.person.last_name}",
            birth_date=payload.person.birth_date,
            gender=payload.person.gender,
            nationality=payload.person.nationality,
            notes=payload.person.notes,
            created_by_user_id=self.ctx.user.id,
            updated_by_user_id=self.ctx.user.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(person)
        self.db.flush()  # Garante ID disponível
        
        logger.info(f"Person created | id={person.id} | name={person.full_name}")
        return person
    
    def _create_contacts(self, person_id: UUID, contacts) -> None:
        """Cria contatos da pessoa"""
        for contact_data in contacts:
            # Normaliza valor
            value = contact_data.contact_value
            if contact_data.contact_type == "email":
                value = normalize_email(value)
            elif contact_data.contact_type in ("telefone", "whatsapp"):
                value = normalize_phone(value)
            
            contact = PersonContact(
                id=uuid4(),
                person_id=person_id,
                contact_type=contact_data.contact_type,
                contact_value=value,
                is_primary=contact_data.is_primary,
                created_by_user_id=self.ctx.user.id,
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(contact)
        
        self.db.flush()
        logger.info(f"Contacts created | person_id={person_id} | count={len(contacts)}")
    
    def _create_documents(self, person_id: UUID, documents) -> None:
        """Cria documentos da pessoa"""
        for doc_data in documents:
            # Normaliza CPF
            number = doc_data.document_number
            if doc_data.document_type == "cpf":
                number = normalize_cpf(number)
            
            document = PersonDocument(
                id=uuid4(),
                person_id=person_id,
                document_type=doc_data.document_type,
                document_number=number,
                issuing_authority=doc_data.issuing_authority,
                issue_date=doc_data.issue_date,
                expiry_date=doc_data.expiry_date,
                is_verified=doc_data.is_verified,
                created_by_user_id=self.ctx.user.id,
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(document)
        
        self.db.flush()
        logger.info(f"Documents created | person_id={person_id} | count={len(documents)}")
    
    def _create_address(self, person_id: UUID, address_data) -> None:
        """Cria endereço da pessoa"""
        address = PersonAddress(
            id=uuid4(),
            person_id=person_id,
            address_type=address_data.address_type,
            street=address_data.street,
            number=address_data.number,
            complement=address_data.complement,
            neighborhood=address_data.neighborhood,
            city=address_data.city,
            state=address_data.state,
            postal_code=address_data.postal_code,
            country=address_data.country,
            created_by_user_id=self.ctx.user.id,
            created_at=datetime.now(timezone.utc)
        )
        
        self.db.add(address)
        self.db.flush()
        logger.info(f"Address created | person_id={person_id}")
    
    def _create_media(self, person_id: UUID, media_data) -> None:
        """Cria mídia (foto) da pessoa"""
        # Desmarca primária anterior
        self.db.query(PersonMedia).filter(
            PersonMedia.person_id == person_id,
            PersonMedia.media_type == 'foto_perfil',
            PersonMedia.is_primary == True
        ).update({'is_primary': False})
        
        media = PersonMedia(
            id=uuid4(),
            person_id=person_id,
            media_type='foto_perfil',
            file_url=media_data.profile_photo_url,
            is_primary=True,
            created_by_user_id=self.ctx.user.id,
            created_at=datetime.now(timezone.utc)
        )
        
        self.db.add(media)
        self.db.flush()
        logger.info(f"Media created | person_id={person_id} | url={media_data.profile_photo_url}")
    
    def _handle_season(self, season_data) -> UUID:
        """
        Cria ou seleciona temporada.
        
        FASE 4.1 - Season Management
        
        Regras:
        - mode='create': Cria temporada para o ano (01/01/YYYY → 31/12/YYYY)
        - mode='select': Seleciona temporada existente
        - Temporada única por ano (não permite duplicatas)
        
        Args:
            season_data: SeasonSelection com mode e year/season_id
        
        Returns:
            UUID da temporada
        
        Raises:
            HTTPException 404: Temporada não encontrada (mode='select')
            HTTPException 409: Temporada do ano já existe (mode='create')
        """
        from datetime import date
        
        if season_data.mode == "select":
            # Seleciona existente
            season = self.db.query(Season).filter(
                Season.id == season_data.season_id,
                Season.deleted_at.is_(None)
            ).first()
            
            if not season:
                raise HTTPException(
                    status_code=404,
                    detail=f"Temporada não encontrada: {season_data.season_id}"
                )
            
            logger.info(f"Season selected | id={season.id} | year={season.year}")
            return season.id
        
        elif season_data.mode == "create":
            # Valida se temporada do ano já existe
            existing = self.db.query(Season).filter(
                Season.year == season_data.year,
                Season.deleted_at.is_(None)
            ).first()
            
            if existing:
                # Reutiliza temporada existente (comportamento idempotente)
                logger.info(f"Season already exists, reusing | id={existing.id} | year={existing.year}")
                return existing.id
            
            # Cria nova temporada
            season = Season(
                id=uuid4(),
                year=season_data.year,
                start_date=date(season_data.year, 1, 1),
                end_date=date(season_data.year, 12, 31),
                is_active=True,
                created_by_user_id=self.ctx.user.id,
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(season)
            self.db.flush()
            logger.info(f"Season created | id={season.id} | year={season.year}")
            return season.id
    
    def _handle_organization(self, org_data, season_id: Optional[UUID] = None) -> UUID:
        """Cria ou seleciona organização"""
        if org_data.mode == "select":
            # Seleciona existente
            org = self.db.query(Organization).filter(
                Organization.id == org_data.organization_id,
                Organization.deleted_at.is_(None)
            ).first()
            
            if not org:
                raise HTTPException(
                    status_code=404,
                    detail=f"Organização não encontrada: {org_data.organization_id}"
                )
            
            logger.info(f"Organization selected | id={org.id} | name={org.name}")
            return org.id
        
        elif org_data.mode == "create":
            # Cria nova
            org = Organization(
                id=uuid4(),
                name=org_data.name,
                season_id=season_id,  # Vincula à temporada
                created_by_user_id=self.ctx.user.id,
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(org)
            self.db.flush()
            logger.info(f"Organization created | id={org.id} | name={org.name} | season_id={season_id}")
            return org.id
    
    def _handle_team(self, team_data, organization_id: UUID, season_id: Optional[UUID] = None) -> UUID:
        """Cria ou seleciona equipe"""
        if team_data.mode == "select":
            # Seleciona existente
            team = self.db.query(Team).filter(
                Team.id == team_data.team_id,
                Team.deleted_at.is_(None)
            ).first()
            
            if not team:
                raise HTTPException(
                    status_code=404,
                    detail=f"Equipe não encontrada: {team_data.team_id}"
                )
            
            # Valida que pertence à organização
            if team.organization_id != organization_id:
                raise HTTPException(
                    status_code=422,
                    detail="Equipe não pertence à organização selecionada"
                )
            
            logger.info(f"Team selected | id={team.id} | name={team.name}")
            return team.id
        
        elif team_data.mode == "create":
            # Cria nova
            team = Team(
                id=uuid4(),
                name=team_data.name,
                organization_id=organization_id,
                season_id=season_id,  # Vincula à temporada
                category_id=team_data.category_id,
                gender=team_data.gender,
                created_by_user_id=self.ctx.user.id,
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(team)
            self.db.flush()
            logger.info(f"Team created | id={team.id} | name={team.name} | season_id={season_id}")
            return team.id
    
    def _create_athlete(self, person_id: UUID, organization_id: Optional[UUID], athlete_data) -> UUID:
        """Cria atleta"""
        # Valida posições (regra do goleiro)
        validate_goalkeeper_positions(
            self.db,
            athlete_data.main_defensive_position_id,
            athlete_data.main_offensive_position_id,
            athlete_data.secondary_offensive_position_id
        )
        
        athlete = Athlete(
            id=uuid4(),
            person_id=person_id,
            organization_id=organization_id,  # Pode ser NULL
            athlete_name=athlete_data.athlete_name,
            birth_date=athlete_data.birth_date,
            athlete_nickname=athlete_data.athlete_nickname,
            shirt_number=athlete_data.shirt_number,
            schooling_id=athlete_data.schooling_id,
            guardian_name=athlete_data.guardian_name,
            guardian_phone=athlete_data.guardian_phone,
            main_defensive_position_id=athlete_data.main_defensive_position_id,
            secondary_defensive_position_id=athlete_data.secondary_defensive_position_id,
            main_offensive_position_id=athlete_data.main_offensive_position_id,
            secondary_offensive_position_id=athlete_data.secondary_offensive_position_id,
            state='ativa',
            created_by_user_id=self.ctx.user.id,
            created_at=datetime.now(timezone.utc)
        )
        
        self.db.add(athlete)
        self.db.flush()
        logger.info(f"Athlete created | id={athlete.id} | name={athlete.athlete_name}")
        return athlete.id
    
    def _create_team_registration(self, athlete_id: UUID, team_id: UUID, registration_data) -> UUID:
        """Cria vínculo atleta-equipe"""
        # Busca equipe para validar categoria
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Equipe não encontrada")
        
        # Busca atleta para pegar person.birth_date
        athlete = self.db.query(Athlete).filter(Athlete.id == athlete_id).first()
        person = self.db.query(Person).filter(Person.id == athlete.person_id).first()
        
        # Busca temporada ativa
        season = self.db.query(Season).filter(
            Season.organization_id == team.organization_id,
            Season.is_active == True
        ).first()
        
        if season and person.birth_date:
            # Valida categoria (R15)
            validate_category_eligibility(
                self.db,
                person.birth_date,
                team.category_id,
                season.year
            )
        
        registration = TeamRegistration(
            id=uuid4(),
            athlete_id=athlete_id,
            team_id=team_id,
            start_at=registration_data.start_at or datetime.now(timezone.utc),
            end_at=registration_data.end_at,
            created_by_user_id=self.ctx.user.id,
            created_at=datetime.now(timezone.utc)
        )
        
        self.db.add(registration)
        self.db.flush()
        logger.info(f"Team registration created | id={registration.id} | athlete={athlete_id} | team={team_id}")
        return registration.id
    
    def _create_membership(self, person_id: UUID, organization_id: UUID, membership_data) -> UUID:
        """Cria vínculo organizacional"""
        membership = Membership(
            id=uuid4(),
            person_id=person_id,
            organization_id=organization_id,
            role_id=membership_data.role_id,
            start_at=membership_data.start_at or datetime.now(timezone.utc),
            created_by_user_id=self.ctx.user.id,
            created_at=datetime.now(timezone.utc)
        )
        
        self.db.add(membership)
        self.db.flush()
        logger.info(f"Membership created | id={membership.id} | person={person_id} | org={organization_id}")
        return membership.id
    
    def _create_user(self, person_id: UUID, user_data) -> UUID:
        """Cria usuário/login"""
        # Valida email único
        existing_user = self.db.query(User).filter(
            User.email == user_data.email.lower()
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail={
                    "type": "duplicate_user",
                    "field": "email",
                    "value": user_data.email,
                    "message": "Email já cadastrado como usuário"
                }
            )
        
        user = User(
            id=uuid4(),
            person_id=person_id,
            email=user_data.email.lower(),
            role_id=user_data.role_id,
            password_hash=None,  # Será definida via token
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        self.db.add(user)
        self.db.flush()
        logger.info(f"User created | id={user.id} | email={user.email}")
        return user.id
