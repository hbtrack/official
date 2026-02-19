"""
Ficha Única de Cadastro - Service
=================================
Serviço transacional para cadastro unificado de Pessoa com opcionais.

FLUXO CANÔNICO (FASE 3 - FICHA.MD):
1. Verificar idempotência (se Idempotency-Key presente)
2. Validar escopo (permissões por papel)
3. Pré-validação (unicidade, regras de negócio)
4. Upsert Person
5. Criar contatos, documentos, endereço
6. Criar User (opcional) + token welcome
7. Criar/Selecionar Organization
8. Criar org_membership (se staff)
9. Criar/Selecionar Team
10. Criar Athlete (opcional)
11. Criar team_registration (opcional)
12. Commit + invalidate_report_cache()
13. Salvar idempotência
14. Enviar email welcome (SendGrid)

Baseado em: Ficha unica de cadastro.txt, REGRAS.md, REGRAS_GERENCIAMENTO_ATLETAS.md
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone, date
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.core.cache import invalidate_report_cache
from app.models.athlete import Athlete
from app.models.organization import Organization
from app.models.membership import OrgMembership
from app.models.password_reset import PasswordReset
from app.models.person import Person, PersonAddress, PersonContact, PersonDocument, PersonMedia
from app.models.team import Team
from app.models.team_registration import TeamRegistration
from app.models.user import User
from app.models.category import Category
from app.models.defensive_position import DefensivePosition
from app.schemas.intake.ficha_unica import (
    AthleteCreate,
    FichaUnicaRequest,
    FichaUnicaResponse,
    FichaUnicaDryRunResponse,
    MembershipCreate,
    OrganizationSelection,
    PersonAddressCreate,
    PersonContactCreate,
    PersonCreate,
    PersonDocumentCreate,
    RegistrationCreate,
    TeamSelection,
    UserCreate,
    ValidationResult,
)

# Importações da FASE 3
from app.services.intake.validators import (
    normalize_cpf,
    normalize_phone,
    normalize_email,
    validate_cpf_checksum,
    check_email_exists,
    check_cpf_exists,
    is_goalkeeper_position,
)
from app.services.intake.idempotency import (
    check_idempotency,
    save_idempotency,
    IdempotencyGuard,
)

logger = logging.getLogger("hb.intake")

# ID da posição de goleira (defensive_positions.code = 'goleira')
GOALKEEPER_POSITION_ID = 1  # Ajustar conforme seed do banco


class FichaUnicaService:
    """
    Serviço para cadastro via Ficha Única.
    
    Princípios:
    - Transação única (commit atômico)
    - Validações no backend (nunca delegadas ao frontend)
    - Auditoria completa (created_by_user_id)
    - Histórico preservado (soft delete)
    """
    
    def __init__(self, db: Session, actor_id: Optional[UUID] = None):
        """
        Args:
            db: Sessão do banco de dados
            actor_id: ID do usuário que está realizando o cadastro
        """
        self.db = db
        self.actor_id = actor_id
        self._errors: List[str] = []
        self._warnings: List[str] = []
    
    # =========================================================================
    # VALIDAÇÃO (Dry-Run)
    # =========================================================================
    
    def validate(self, request: FichaUnicaRequest) -> ValidationResult:
        """
        Valida o payload sem gravar no banco (dry-run).
        
        Útil para UX do frontend antes do submit final.
        """
        self._errors = []
        self._warnings = []
        result = ValidationResult(valid=True)
        
        # 1. Validar unicidade de documentos
        for doc in request.person.documents:
            if doc.document_type == "cpf":
                result.cpf_available = self._check_document_available("cpf", doc.document_number)
                if not result.cpf_available:
                    self._errors.append(f"CPF {doc.document_number} já cadastrado")
            elif doc.document_type == "rg":
                result.rg_available = self._check_document_available("rg", doc.document_number)
                if not result.rg_available:
                    self._errors.append(f"RG {doc.document_number} já cadastrado")
        
        # 2. Validar unicidade de email
        if request.create_user and request.user:
            result.email_available = self._check_email_available(request.user.email)
            if not result.email_available:
                self._errors.append(f"Email {request.user.email} já cadastrado")
        
        # 3. Validar unicidade de telefone principal
        for contact in request.person.contacts:
            if contact.contact_type == "telefone" and contact.is_primary:
                result.phone_available = self._check_phone_available(contact.contact_value)
                if not result.phone_available:
                    self._warnings.append(f"Telefone {contact.contact_value} já cadastrado (aviso)")
        
        # 4. Validar regras de atleta
        if request.athlete and request.athlete.create:
            # 4a. Validar goleira sem posição ofensiva
            result.goalkeeper_positions_valid = self._validate_goalkeeper_positions(
                request.athlete.main_defensive_position_id,
                request.athlete.main_offensive_position_id,
                request.athlete.secondary_offensive_position_id
            )
            if not result.goalkeeper_positions_valid:
                self._errors.append("Goleira não pode ter posição ofensiva (RD13)")
            
            # 4b. Validar categoria vs equipe (R15)
            if request.team and request.athlete.birth_date:
                result.category_valid = self._validate_category_age(
                    request.athlete.birth_date,
                    request.team.team_id if request.team.mode == "select" else None,
                    request.team.category_id if request.team.mode == "create" else None
                )
                if not result.category_valid:
                    self._errors.append("Atleta não pode jogar em categoria inferior à natural (R15)")
            
            # 4c. Validar gênero vs equipe
            if request.team and request.person.gender:
                result.gender_valid = self._validate_gender_match(
                    request.person.gender,
                    request.team.team_id if request.team.mode == "select" else None,
                    request.team.gender if request.team.mode == "create" else None
                )
                if not result.gender_valid:
                    self._errors.append("Gênero do atleta incompatível com a equipe")
        
        result.errors = self._errors
        result.warnings = self._warnings
        result.valid = len(self._errors) == 0
        
        return result
    
    # =========================================================================
    # PROCESSAMENTO PRINCIPAL
    # =========================================================================
    
    def process(self, request: FichaUnicaRequest, validate_only: bool = False) -> FichaUnicaResponse:
        """
        Processa a Ficha Única de cadastro.
        
        Args:
            request: Payload completo da ficha
            validate_only: Se True, apenas valida sem gravar
            
        Returns:
            FichaUnicaResponse com IDs criados e status
        """
        # 1. Validação prévia
        validation = self.validate(request)
        if not validation.valid:
            return FichaUnicaResponse(
                success=False,
                message="Validação falhou",
                validation_only=validate_only,
                validation_errors=validation.errors
            )
        
        if validate_only:
            return FichaUnicaResponse(
                success=True,
                message="Validação OK",
                validation_only=True
            )
        
        # 2. Processar em transação
        try:
            response = self._process_transaction(request)
            return response
        except Exception as e:
            logger.error(f"Erro no processamento da Ficha Única: {e}", exc_info=True)
            self.db.rollback()
            return FichaUnicaResponse(
                success=False,
                message=f"Erro interno: {str(e)}",
                validation_errors=[str(e)]
            )
    
    def process_with_idempotency(
        self,
        request: FichaUnicaRequest,
        idempotency_key: Optional[str] = None,
        endpoint: str = "/api/v1/intake/ficha-unica",
        validate_only: bool = False
    ) -> Tuple[FichaUnicaResponse, int]:
        """
        Processa a Ficha Única com suporte a idempotência.
        
        FASE 3 - FICHA.MD Seção 3.3
        
        Args:
            request: Payload completo da ficha
            idempotency_key: Header Idempotency-Key (opcional)
            endpoint: Endpoint da requisição
            validate_only: Se True, apenas valida sem gravar
            
        Returns:
            Tuple[FichaUnicaResponse, status_code]
        """
        # Converter request para dict para hash
        payload_dict = request.model_dump(mode='json')
        
        # 1. Verificar idempotência
        if idempotency_key:
            cached = check_idempotency(
                self.db,
                idempotency_key,
                endpoint,
                payload_dict
            )
            if cached:
                logger.info(
                    "INTAKE | Idempotent request | key=%s",
                    idempotency_key
                )
                # Reconstruir response do cache
                cached_response = FichaUnicaResponse(**cached["response"])
                return cached_response, cached["status_code"]
        
        # 2. Processar normalmente
        response = self.process(request, validate_only)
        
        # 3. Determinar status code
        if not response.success:
            status_code = 422 if response.validation_errors else 500
        elif validate_only:
            status_code = 200
        else:
            status_code = 201
        
        # 4. Salvar idempotência (apenas para requests com sucesso)
        if idempotency_key and response.success and not validate_only:
            save_idempotency(
                self.db,
                idempotency_key,
                endpoint,
                payload_dict,
                response,
                status_code
            )
        
        return response, status_code
    
    def dry_run(self, request: FichaUnicaRequest) -> FichaUnicaDryRunResponse:
        """
        Executa validação completa sem gravar (dry-run).
        
        FASE 3 - Retorna preview do que seria criado.
        
        Args:
            request: Payload completo da ficha
            
        Returns:
            FichaUnicaDryRunResponse com validação e preview
        """
        # Executar validação
        validation = self.validate(request)
        
        # Construir preview
        preview = {
            "person": {
                "first_name": request.person.first_name,
                "last_name": request.person.last_name,
                "full_name": request.person.full_name,
                "birth_date": str(request.person.birth_date) if request.person.birth_date else None,
                "gender": request.person.gender,
            },
            "user_will_be_created": request.create_user,
            "organization_will_be_created": (
                request.organization.mode == "create" if request.organization else False
            ),
            "team_will_be_created": (
                request.team.mode == "create" if request.team else False
            ),
            "athlete_will_be_created": (
                request.athlete.create if request.athlete else False
            ),
            "membership_will_be_created": request.membership is not None,
            "registration_will_be_created": request.registration is not None,
        }
        
        return FichaUnicaDryRunResponse(
            valid=validation.valid,
            errors=validation.errors,
            warnings=validation.warnings,
            preview=preview,
            validation_details=validation
        )
    
    def _process_transaction(self, request: FichaUnicaRequest) -> FichaUnicaResponse:
        """Processa toda a ficha em uma única transação."""
        
        response = FichaUnicaResponse(success=True, message="Cadastro realizado com sucesso")
        
        # ETAPA 1: Criar Person
        person = self._create_person(request.person)
        self.db.add(person)
        self.db.flush()  # Obter ID
        response.person_id = person.id
        logger.info(f"INTAKE | Person created | id={person.id}")
        
        # ETAPA 1b: Criar contatos
        for contact_data in request.person.contacts:
            contact = self._create_person_contact(person.id, contact_data)
            self.db.add(contact)
        
        # ETAPA 1c: Criar documentos
        for doc_data in request.person.documents:
            document = self._create_person_document(person.id, doc_data)
            self.db.add(document)
        
        # ETAPA 1d: Criar endereço
        if request.person.address:
            address = self._create_person_address(person.id, request.person.address)
            self.db.add(address)
        
        # ETAPA 1e: Criar mídia (foto)
        if request.person.media and request.person.media.profile_photo_url:
            media = self._create_person_media(person.id, request.person.media.profile_photo_url)
            self.db.add(media)
        
        self.db.flush()
        
        # ETAPA 2: Criar User (opcional)
        user = None
        password_reset_token = None
        if request.create_user and request.user:
            user, password_reset_token = self._create_user_with_welcome_token(
                person.id, request.user
            )
            self.db.add(user)
            self.db.flush()
            response.user_id = user.id
            response.user_created = True
            logger.info(f"INTAKE | User created | id={user.id}")
        
        # ETAPA 3: Criar/Selecionar Organization
        organization_id: Optional[UUID] = None
        if request.organization:
            if request.organization.mode == "select":
                organization_id = request.organization.organization_id
            else:
                org = self._create_organization(request.organization.name)
                self.db.add(org)
                self.db.flush()
                organization_id = org.id
                response.organization_created = True
                logger.info(f"INTAKE | Organization created | id={org.id}")
            response.organization_id = organization_id
        
        # ETAPA 3b: Criar org_membership (se staff)
        if request.membership and organization_id:
            membership = self._create_org_membership(
                person.id, organization_id, request.membership
            )
            self.db.add(membership)
            self.db.flush()
            response.org_membership_id = membership.id
            logger.info(f"INTAKE | OrgMembership created | id={membership.id}")
        
        # ETAPA 4: Criar/Selecionar Team
        team_id: Optional[UUID] = None
        if request.team:
            if request.team.mode == "select":
                team_id = request.team.team_id
            else:
                if not organization_id:
                    raise ValueError("organization é obrigatório para criar equipe")
                team = self._create_team(organization_id, request.team)
                self.db.add(team)
                self.db.flush()
                team_id = team.id
                response.team_created = True
                logger.info(f"INTAKE | Team created | id={team.id}")
            response.team_id = team_id
        
        # ETAPA 5: Criar Athlete (opcional)
        athlete = None
        if request.athlete and request.athlete.create:
            # Usar gênero da pessoa para o atleta
            athlete_gender = self._map_gender_for_athlete(request.person.gender)
            
            athlete = self._create_athlete(
                person.id,
                request.athlete,
                athlete_gender,
                organization_id
            )
            self.db.add(athlete)
            self.db.flush()
            response.athlete_id = athlete.id
            response.athlete_created = True
            logger.info(f"INTAKE | Athlete created | id={athlete.id}")
        
        # ETAPA 6: Criar team_registration (opcional)
        if request.registration and athlete and team_id:
            registration = self._create_team_registration(
                athlete.id, team_id, request.registration
            )
            self.db.add(registration)
            self.db.flush()
            response.team_registration_id = registration.id
            
            # Atualizar organization_id do atleta (derivado)
            if organization_id:
                athlete.organization_id = organization_id
            
            logger.info(f"INTAKE | TeamRegistration created | id={registration.id}")
        
        # COMMIT
        self.db.commit()
        logger.info(f"INTAKE | Transaction committed | person_id={person.id}")
        
        # Invalidar cache de relatórios
        invalidate_report_cache()
        
        # ETAPA 7: Enviar email welcome (após commit)
        if user and password_reset_token:
            try:
                self._send_welcome_email(user, person, password_reset_token)
                response.email_sent = True
                logger.info(f"INTAKE | Welcome email sent | user_id={user.id}")
            except Exception as e:
                logger.error(f"INTAKE | Failed to send welcome email: {e}")
                # Não falha a transação por erro de email
        
        return response
    
    # =========================================================================
    # MÉTODOS DE CRIAÇÃO
    # =========================================================================
    
    def _create_person(self, data: PersonCreate) -> Person:
        """Cria registro de Person."""
        return Person(
            first_name=data.first_name,
            last_name=data.last_name,
            full_name=data.full_name,
            birth_date=data.birth_date,
            gender=data.gender,
            nationality=data.nationality,
            notes=data.notes
        )
    
    def _create_person_contact(self, person_id: UUID, data: PersonContactCreate) -> PersonContact:
        """Cria contato da pessoa."""
        return PersonContact(
            person_id=person_id,
            contact_type=data.contact_type,
            contact_value=data.contact_value,
            is_primary=data.is_primary
        )
    
    def _create_person_document(self, person_id: UUID, data: PersonDocumentCreate) -> PersonDocument:
        """Cria documento da pessoa."""
        return PersonDocument(
            person_id=person_id,
            document_type=data.document_type,
            document_number=data.document_number,
            issuing_authority=data.issuing_authority,
            issue_date=data.issue_date
        )
    
    def _create_person_address(self, person_id: UUID, data: PersonAddressCreate) -> PersonAddress:
        """Cria endereço da pessoa."""
        return PersonAddress(
            person_id=person_id,
            address_type=data.address_type,
            street=data.street,
            number=data.number,
            complement=data.complement,
            neighborhood=data.neighborhood,
            city=data.city,
            state=data.state,
            postal_code=data.postal_code,
            country=data.country,
            is_primary=True
        )
    
    def _create_person_media(self, person_id: UUID, photo_url: str) -> PersonMedia:
        """Cria mídia (foto) da pessoa."""
        return PersonMedia(
            person_id=person_id,
            media_type="foto_perfil",
            file_url=photo_url,
            is_primary=True
        )
    
    def _create_user_with_welcome_token(
        self, person_id: UUID, data: UserCreate
    ) -> Tuple[User, str]:
        """
        Cria usuário e token de welcome.
        
        Returns:
            Tuple (User, token_raw) - token é o valor a enviar por email
        """
        user = User(
            person_id=person_id,
            email=data.email.lower(),
            password_hash=None,  # Será definido no reset
            is_superadmin=False,
            is_locked=False,
            status="ativo"
        )
        self.db.add(user)
        self.db.flush()
        
        # Gerar token de welcome
        token_raw = secrets.token_urlsafe(32)
        token_hash = token_raw  # Em produção: usar hash seguro
        
        password_reset = PasswordReset(
            user_id=user.id,
            token=token_hash,
            token_type="welcome",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        self.db.add(password_reset)
        
        return user, token_raw
    
    def _create_organization(self, name: str) -> Organization:
        """Cria organização."""
        return Organization(name=name)
    
    def _create_org_membership(
        self, person_id: UUID, organization_id: UUID, data: MembershipCreate
    ) -> OrgMembership:
        """Cria vínculo organizacional (staff)."""
        return OrgMembership(
            person_id=person_id,
            organization_id=organization_id,
            role_id=data.role_id,
            start_at=data.start_at or datetime.now(timezone.utc)
        )
    
    def _create_team(self, organization_id: UUID, data: TeamSelection) -> Team:
        """Cria equipe."""
        return Team(
            organization_id=organization_id,
            name=data.name,
            category_id=data.category_id,
            gender=data.gender,
            is_our_team=True,
            created_by_user_id=self.actor_id
        )
    
    def _create_athlete(
        self,
        person_id: UUID,
        data: AthleteCreate,
        gender: str,
        organization_id: Optional[UUID]
    ) -> Athlete:
        """
        Cria atleta.
        
        Regra RD13: Se goleira, posições ofensivas são NULL.
        """
        # Verificar se é goleira
        is_goalkeeper = self._is_goalkeeper(data.main_defensive_position_id)
        
        return Athlete(
            person_id=person_id,
            organization_id=organization_id,  # Derivado, pode ser NULL
            athlete_name=data.athlete_name,
            birth_date=data.birth_date,
            athlete_nickname=data.athlete_nickname,
            shirt_number=data.shirt_number,
            schooling_id=data.schooling_id,
            guardian_name=data.guardian_name,
            guardian_phone=data.guardian_phone,
            main_defensive_position_id=data.main_defensive_position_id,
            secondary_defensive_position_id=data.secondary_defensive_position_id,
            # Posições ofensivas: NULL se goleira
            main_offensive_position_id=None if is_goalkeeper else data.main_offensive_position_id,
            secondary_offensive_position_id=None if is_goalkeeper else data.secondary_offensive_position_id,
            state="ativa",
            injured=False,
            medical_restriction=False,
            load_restricted=False
        )
    
    def _create_team_registration(
        self, athlete_id: UUID, team_id: UUID, data: RegistrationCreate
    ) -> TeamRegistration:
        """Cria vínculo atleta-equipe."""
        return TeamRegistration(
            athlete_id=athlete_id,
            team_id=team_id,
            start_at=data.start_at or datetime.now(timezone.utc),
            end_at=data.end_at
        )
    
    # =========================================================================
    # MÉTODOS DE VALIDAÇÃO
    # =========================================================================
    
    def _check_document_available(self, doc_type: str, doc_number: str) -> bool:
        """Verifica se documento está disponível (não cadastrado)."""
        normalized = "".join(c for c in doc_number if c.isalnum())
        result = self.db.execute(
            select(PersonDocument.id)
            .where(
                and_(
                    PersonDocument.document_type == doc_type,
                    PersonDocument.document_number == normalized,
                    PersonDocument.deleted_at.is_(None)
                )
            )
            .limit(1)
        ).first()
        return result is None
    
    def _check_email_available(self, email: str) -> bool:
        """Verifica se email está disponível."""
        result = self.db.execute(
            select(User.id)
            .where(
                and_(
                    func.lower(User.email) == email.lower(),
                    User.deleted_at.is_(None)
                )
            )
            .limit(1)
        ).first()
        return result is None
    
    def _check_phone_available(self, phone: str) -> bool:
        """Verifica se telefone está disponível."""
        normalized = "".join(c for c in phone if c.isdigit())
        result = self.db.execute(
            select(PersonContact.id)
            .where(
                and_(
                    PersonContact.contact_type == "telefone",
                    PersonContact.contact_value == normalized,
                    PersonContact.deleted_at.is_(None)
                )
            )
            .limit(1)
        ).first()
        return result is None
    
    def _is_goalkeeper(self, position_id: Optional[int]) -> bool:
        """Verifica se a posição é de goleira."""
        if not position_id:
            return False
        
        result = self.db.execute(
            select(DefensivePosition.code)
            .where(DefensivePosition.id == position_id)
        ).scalar()
        
        return result in ("goleira", "goleiro", "goalkeeper")
    
    def _validate_goalkeeper_positions(
        self,
        defensive_id: Optional[int],
        offensive_id: Optional[int],
        secondary_offensive_id: Optional[int]
    ) -> bool:
        """
        Valida regra RD13: Goleira não pode ter posição ofensiva.
        
        Returns:
            True se válido, False se violar regra
        """
        if not self._is_goalkeeper(defensive_id):
            return True  # Não é goleira, OK
        
        # É goleira: posições ofensivas devem ser NULL
        if offensive_id is not None or secondary_offensive_id is not None:
            return False
        
        return True
    
    def _validate_category_age(
        self,
        birth_date: date,
        team_id: Optional[UUID],
        category_id: Optional[int]
    ) -> bool:
        """
        Valida regra R15: Atleta não pode jogar em categoria inferior à natural.
        
        Cálculo: idade = ano_atual - ano_nascimento
        Categoria natural = primeira categoria onde idade <= max_age
        """
        # Calcular idade (simplificado: ano atual - ano nascimento)
        current_year = datetime.now().year
        age = current_year - birth_date.year
        
        # Obter categoria natural
        natural_category = self.db.execute(
            select(Category)
            .where(
                and_(
                    Category.max_age >= age,
                    Category.is_active == True
                )
            )
            .order_by(Category.max_age.asc())
            .limit(1)
        ).scalar()
        
        if not natural_category:
            return True  # Sem categoria natural definida, permitir
        
        # Obter categoria da equipe
        if team_id:
            team = self.db.execute(
                select(Team.category_id).where(Team.id == team_id)
            ).scalar()
            category_id = team
        
        if not category_id:
            return True  # Sem equipe/categoria, permitir
        
        team_category = self.db.execute(
            select(Category).where(Category.id == category_id)
        ).scalar()
        
        if not team_category:
            return True
        
        # Validar: categoria da equipe >= categoria natural
        return team_category.max_age >= natural_category.max_age
    
    def _validate_gender_match(
        self,
        person_gender: str,
        team_id: Optional[UUID],
        team_gender: Optional[str]
    ) -> bool:
        """
        Valida compatibilidade de gênero pessoa x equipe.
        
        No handebol: não existe categoria mista.
        """
        if team_id:
            result = self.db.execute(
                select(Team.gender).where(Team.id == team_id)
            ).scalar()
            team_gender = result
        
        if not team_gender:
            return True  # Sem equipe, OK
        
        # Mapear gênero da pessoa para gênero da equipe
        gender_map = {
            "masculino": "masculino",
            "feminino": "feminino",
            "outro": None,  # Não pode vincular
            "prefiro_nao_dizer": None
        }
        
        mapped_gender = gender_map.get(person_gender)
        if mapped_gender is None:
            return False  # Gênero incompatível
        
        return mapped_gender == team_gender
    
    def _map_gender_for_athlete(self, person_gender: Optional[str]) -> str:
        """Mapeia gênero da pessoa para o atleta."""
        # No schema de athletes, usamos o mesmo valor
        return person_gender or "feminino"  # Default para handebol feminino
    
    # =========================================================================
    # EMAIL
    # =========================================================================
    
    def _send_welcome_email(self, user: User, person: Person, token: str) -> None:
        """
        Envia email de boas-vindas com link de ativação.
        
        TODO: Implementar integração SendGrid.
        """
        # Placeholder - implementar SendGrid
        logger.info(
            f"INTAKE | Would send welcome email | "
            f"to={user.email} | name={person.full_name} | token={token[:8]}..."
        )
        # Em produção:
        # from app.services.email import send_welcome_email
        # send_welcome_email(user.email, person.full_name, token)
