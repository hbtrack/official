"""
Ficha Única de Cadastro - Schemas
=================================
Payload unificado para cadastro de Pessoa com opcionais:
- Usuário (login)
- Organização (criar/selecionar)
- Equipe (criar/selecionar)
- Atleta
- Vínculos (org_membership, team_registration)

Baseado em: Ficha unica de cadastro.txt, REGRAS.md, REGRAS_GERENCIAMENTO_ATLETAS.md

FASE 2 - FICHA.MD Seção 2.2 e 2.3
"""

import re
from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# =============================================================================
# UTILITÁRIOS DE NORMALIZAÇÃO
# =============================================================================

def normalize_cpf(cpf: str) -> str:
    """Remove caracteres não numéricos do CPF"""
    return re.sub(r'\D', '', cpf)


def normalize_phone(phone: str) -> str:
    """Remove caracteres não numéricos do telefone"""
    return re.sub(r'\D', '', phone)


def normalize_email(email: str) -> str:
    """Normaliza email para lowercase e remove espaços"""
    return email.strip().lower()


def validate_cpf(cpf: str) -> bool:
    """
    Valida CPF usando algoritmo oficial.
    
    Returns:
        True se CPF válido, False caso contrário
    """
    cpf = normalize_cpf(cpf)
    
    if len(cpf) != 11:
        return False
    
    # CPFs inválidos conhecidos
    if cpf == cpf[0] * 11:
        return False
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(cpf[10]) == digito2


# =============================================================================
# ETAPA 1 - PESSOA (persons + subentidades)
# =============================================================================

class PersonContactCreate(BaseModel):
    """Contato da pessoa (person_contacts)"""
    contact_type: Literal["telefone", "email", "whatsapp", "outro"]
    contact_value: str = Field(..., min_length=1, max_length=200)
    is_primary: bool = False
    
    @field_validator("contact_value")
    @classmethod
    def normalize_contact_value(cls, v: str, info) -> str:
        """Normaliza valor do contato baseado no tipo"""
        # O tipo vem de info.data se disponível
        return v.strip()


class PersonDocumentCreate(BaseModel):
    """Documento da pessoa (person_documents)"""
    document_type: Literal["cpf", "rg", "cnh", "passaporte", "certidao_nascimento", "titulo_eleitor", "outro"]
    document_number: str = Field(..., min_length=1, max_length=100)
    issuing_authority: Optional[str] = Field(None, max_length=100)
    issue_date: Optional[date] = None

    @field_validator("document_number")
    @classmethod
    def normalize_document_number(cls, v: str) -> str:
        """Remove caracteres especiais do documento"""
        return "".join(c for c in v if c.isalnum())
    
    @model_validator(mode="after")
    def validate_cpf_if_type(self):
        """Valida CPF se document_type='cpf'"""
        if self.document_type == "cpf":
            cpf_normalized = normalize_cpf(self.document_number)
            if not validate_cpf(cpf_normalized):
                raise ValueError("CPF inválido")
            # Atualiza para versão normalizada
            self.document_number = cpf_normalized
        return self


class PersonAddressCreate(BaseModel):
    """Endereço da pessoa (person_addresses)"""
    address_type: Literal["residencial_1", "residencial_2", "comercial", "outro"] = "residencial_1"
    street: str = Field(..., min_length=1, max_length=200)
    number: Optional[str] = Field(None, max_length=20)
    complement: Optional[str] = Field(None, max_length=100)
    neighborhood: Optional[str] = Field(None, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    postal_code: Optional[str] = Field(None, max_length=10)
    country: str = Field(default="Brasil", max_length=100)


class PersonMediaCreate(BaseModel):
    """Mídia da pessoa (person_media) - foto de perfil"""
    profile_photo_url: Optional[str] = None


class PersonCreate(BaseModel):
    """
    Dados da pessoa (persons).
    
    Campos obrigatórios: first_name, last_name
    Campos derivados: full_name (gerado automaticamente)
    
    REGRAS (FICHA.MD):
    - Ao menos um contato é obrigatório
    - Ao menos um e-mail é obrigatório nos contatos
    """
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    birth_date: Optional[date] = None
    gender: Optional[Literal["masculino", "feminino", "outro", "prefiro_nao_dizer"]] = None
    nationality: str = Field(default="brasileira", max_length=100)
    notes: Optional[str] = None
    
    # Subentidades opcionais
    contacts: List[PersonContactCreate] = Field(default_factory=list)
    documents: List[PersonDocumentCreate] = Field(default_factory=list)
    address: Optional[PersonAddressCreate] = None
    media: Optional[PersonMediaCreate] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @field_validator("contacts")
    @classmethod
    def validate_contacts(cls, v: List[PersonContactCreate]) -> List[PersonContactCreate]:
        """
        Valida que ao menos um contato existe e que há pelo menos um email.
        
        Regra FICHA.MD Seção 2.2:
        - Ao menos um contato é obrigatório
        - Ao menos um e-mail é obrigatório
        """
        if not v:
            raise ValueError("Ao menos um contato é obrigatório")
        
        emails = [c for c in v if c.contact_type == "email"]
        if not emails:
            raise ValueError("Ao menos um e-mail é obrigatório nos contatos")
        
        return v


# =============================================================================
# ETAPA 2 - USUÁRIO (users)
# =============================================================================

class UserCreate(BaseModel):
    """
    Usuário para login (users).
    
    Se create_user=True no payload principal, este bloco é processado.
    - Cria user vinculado à person
    - Gera password_reset com token_type='welcome'
    - Envia email de ativação via SendGrid
    """
    email: EmailStr
    role_id: int = Field(..., ge=1, le=5, description="ID do papel: 1=dirigente, 2=coordenador, 3=treinador, 4=atleta")


# =============================================================================
# ETAPA 2.5 - TEMPORADA (seasons)
# =============================================================================

class SeasonCreateInline(BaseModel):
    """
    Criar nova temporada inline.
    
    Temporada sempre: 01/01/YYYY → 31/12/YYYY (ano civil).
    """
    year: int = Field(..., ge=2020, le=2050, description="Ano da temporada (ex: 2026)")


class SeasonSelection(BaseModel):
    """
    Seleção de temporada.
    
    mode='select': usar season_id existente
    mode='create': criar nova temporada para o ano especificado
    
    REGRA: Temporada sempre 01/01 → 31/12 do ano vigente.
    Organizações/equipes são vinculadas a temporadas.
    """
    mode: Literal["select", "create"]
    season_id: Optional[UUID] = None
    year: Optional[int] = Field(None, ge=2020, le=2050, description="Ano da temporada")

    @model_validator(mode="after")
    def validate_mode(self):
        if self.mode == "select" and not self.season_id:
            raise ValueError("season_id é obrigatório quando mode='select'")
        if self.mode == "create" and not self.year:
            raise ValueError("year é obrigatório quando mode='create'")
        return self


# =============================================================================
# ETAPA 3 - ORGANIZAÇÃO (organizations + org_memberships)
# =============================================================================

class OrganizationCreateInline(BaseModel):
    """Criar nova organização inline"""
    name: str = Field(..., min_length=1, max_length=100)


class OrganizationSelection(BaseModel):
    """
    Seleção de organização.
    
    mode='select': usar organization_id existente
    mode='create': criar nova organização com name
    """
    mode: Literal["select", "create"]
    organization_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_mode(self):
        if self.mode == "select" and not self.organization_id:
            raise ValueError("organization_id é obrigatório quando mode='select'")
        if self.mode == "create" and not self.name:
            raise ValueError("name é obrigatório quando mode='create'")
        return self


class MembershipCreate(BaseModel):
    """
    Vínculo organizacional (org_memberships).
    
    Criado para staff (dirigente, coordenador, treinador).
    Atletas não têm org_membership, apenas team_registration.
    """
    role_id: int = Field(..., ge=1, le=4, description="ID do papel no vínculo")
    start_at: Optional[datetime] = None  # Default: now()


# =============================================================================
# ETAPA 4 - EQUIPE (teams)
# =============================================================================

class TeamCreateInline(BaseModel):
    """Criar nova equipe inline"""
    name: str = Field(..., min_length=1, max_length=120)
    category_id: int = Field(..., ge=1, description="ID da categoria")
    gender: Literal["masculino", "feminino"]


class TeamSelection(BaseModel):
    """
    Seleção de equipe.
    
    mode='select': usar team_id existente
    mode='create': criar nova equipe
    """
    mode: Literal["select", "create"]
    team_id: Optional[UUID] = None
    name: Optional[str] = Field(None, max_length=120)
    category_id: Optional[int] = None
    gender: Optional[Literal["masculino", "feminino"]] = None
    organization_id: Optional[UUID] = None  # Obrigatório quando mode='create' com organization.mode='select'

    @model_validator(mode="after")
    def validate_mode(self):
        if self.mode == "select" and not self.team_id:
            raise ValueError("team_id é obrigatório quando mode='select'")
        if self.mode == "create":
            if not self.name:
                raise ValueError("name é obrigatório quando mode='create'")
            if not self.category_id:
                raise ValueError("category_id é obrigatório quando mode='create'")
            if not self.gender:
                raise ValueError("gender é obrigatório quando mode='create'")
        return self


# =============================================================================
# ETAPA 5 - ATLETA (athletes)
# =============================================================================

class AthleteCreate(BaseModel):
    """
    Dados do atleta (athletes).
    
    Criado apenas se create=True.
    
    REGRAS:
    - Posição defensiva primária é OBRIGATÓRIA
    - Posição ofensiva primária é OBRIGATÓRIA, EXCETO para goleira (RD13)
    - Se posição defensiva = goleira, posições ofensivas são NULL
    """
    create: bool = False
    
    # Campos obrigatórios quando create=True
    athlete_name: str = Field(default="", max_length=100)
    birth_date: Optional[date] = None
    
    # Campos opcionais
    athlete_nickname: Optional[str] = Field(None, max_length=50)
    shirt_number: Optional[int] = Field(None, ge=1, le=99)
    schooling_id: Optional[int] = None
    guardian_name: Optional[str] = Field(None, max_length=100)
    guardian_phone: Optional[str] = Field(None, max_length=20)
    
    # Posições - OBRIGATÓRIAS (exceto ofensiva para goleira)
    main_defensive_position_id: Optional[int] = None
    secondary_defensive_position_id: Optional[int] = None
    main_offensive_position_id: Optional[int] = None
    secondary_offensive_position_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_athlete_fields(self):
        if self.create:
            if not self.athlete_name:
                raise ValueError("athlete_name é obrigatório quando create=True")
            if not self.main_defensive_position_id:
                raise ValueError("main_defensive_position_id é obrigatório quando create=True")
            # Posição ofensiva é validada no service (verifica se é goleira)
        return self


# =============================================================================
# ETAPA 6 - VÍNCULO COM EQUIPE (team_registrations)
# =============================================================================

class RegistrationCreate(BaseModel):
    """
    Vínculo atleta-equipe (team_registrations).
    
    Só processado se athlete.create=True e team selecionada/criada.
    """
    team_id: Optional[UUID] = None  # Pode ser preenchido pelo fluxo
    start_at: Optional[datetime] = None  # Default: now()
    end_at: Optional[datetime] = None  # NULL = vínculo ativo


# =============================================================================
# PAYLOAD PRINCIPAL - FICHA ÚNICA
# =============================================================================

class FichaUnicaRequest(BaseModel):
    """
    Payload completo da Ficha Única.
    
    Transação atômica:
    1. Upsert Person (valida CPF/RG, email, telefone; dedup)
    2. Criar User (opcional) - envia email welcome
    3. Criar/Selecionar Season (obrigatório se criar/selecionar org/team)
    4. Criar/Selecionar Organization (vinculada à temporada)
    5. Criar/Selecionar Team (vinculada à temporada)
    6. Criar Athlete (opcional)
    7. Criar Vínculos (membership, team_registration)
    8. Commit + invalidate_report_cache()
    
    Suporta:
    - Idempotency-Key header para evitar duplicação
    - ?validate_only=true para dry-run
    """
    # ETAPA 1 - Pessoa (obrigatório)
    person: PersonCreate
    
    # ETAPA 2 - Usuário (opcional)
    create_user: bool = False
    user: Optional[UserCreate] = None
    
    # ETAPA 2.5 - Temporada (obrigatório se criar/selecionar org/team)
    season: Optional[SeasonSelection] = None
    
    # ETAPA 3 - Organização (opcional para atletas em captação)
    organization: Optional[OrganizationSelection] = None
    membership: Optional[MembershipCreate] = None
    
    # ETAPA 4 - Equipe (opcional)
    team: Optional[TeamSelection] = None
    
    # ETAPA 5 - Atleta (opcional)
    athlete: Optional[AthleteCreate] = None
    
    # ETAPA 6 - Vínculo com equipe (opcional)
    registration: Optional[RegistrationCreate] = None

    @model_validator(mode="after")
    def validate_dependencies(self):
        # Se criar usuário, precisa de email
        if self.create_user and not self.user:
            raise ValueError("user é obrigatório quando create_user=True")
        
        # Se criar/selecionar organização, precisa de temporada
        if self.organization and not self.season:
            raise ValueError("season é obrigatório quando organization é definida")
        
        # Se criar/selecionar equipe, precisa de temporada
        if self.team and not self.season:
            raise ValueError("season é obrigatório quando team é definida")
        
        # Se criar membership, precisa de organização
        if self.membership and not self.organization:
            raise ValueError("organization é obrigatório quando membership é definido")
        
        # Se criar equipe, precisa de organização
        if self.team and self.team.mode == "create" and not self.organization:
            raise ValueError("organization é obrigatório para criar equipe")
        
        # Se criar registration, precisa de atleta e equipe
        if self.registration:
            if not self.athlete or not self.athlete.create:
                raise ValueError("athlete.create=True é obrigatório para criar registration")
            if not self.team:
                raise ValueError("team é obrigatório para criar registration")
        
        return self


# =============================================================================
# RESPONSE
# =============================================================================

class FichaUnicaResponse(BaseModel):
    """Resposta da criação via Ficha Única"""
    success: bool
    message: str
    
    # IDs criados
    person_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    season_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    athlete_id: Optional[UUID] = None
    team_registration_id: Optional[UUID] = None
    org_membership_id: Optional[UUID] = None
    
    # Flags de ação
    user_created: bool = False
    season_created: bool = False
    organization_created: bool = False
    team_created: bool = False
    athlete_created: bool = False
    email_sent: bool = False
    
    # Validação only
    validation_only: bool = False
    validation_errors: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


# =============================================================================
# VALIDATION RESPONSE (para dry-run)
# =============================================================================

class ValidationResult(BaseModel):
    """Resultado de validação (dry-run)"""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Verificações de unicidade
    cpf_available: Optional[bool] = None
    rg_available: Optional[bool] = None
    email_available: Optional[bool] = None
    phone_available: Optional[bool] = None
    
    # Verificações de regras
    category_valid: Optional[bool] = None
    gender_valid: Optional[bool] = None
    goalkeeper_positions_valid: Optional[bool] = None


# =============================================================================
# DRY-RUN RESPONSE (FICHA.MD Seção 2.3)
# =============================================================================

class FichaUnicaDryRunResponse(BaseModel):
    """
    Resposta do modo dry-run (validate_only=true).
    
    Usado para pré-validação do formulário sem efetivar a criação.
    Retorna validação completa + preview das entidades que seriam criadas.
    
    Exemplo de uso:
        POST /api/v1/intake/ficha-unica?validate_only=true
        
    Response:
        {
            "valid": true,
            "warnings": ["Atleta será cadastrada em categoria acima da natural"],
            "preview": {
                "person": {"first_name": "Maria", "last_name": "Silva", ...},
                "user_will_be_created": true,
                "organization_will_be_created": false,
                "team_will_be_created": false,
                "athlete_will_be_created": true,
                "membership_will_be_created": false,
                "registration_will_be_created": true
            }
        }
    """
    valid: bool
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    preview: Dict[str, Any] = Field(default_factory=dict)
    
    # Detalhes de validação
    validation_details: Optional[ValidationResult] = None

# =============================================================================
# AUTOCOMPLETE RESPONSES (FASE 4)
# =============================================================================

class OrganizationAutocompleteItem(BaseModel):
    """Item de organização para autocomplete"""
    id: UUID
    name: str
    abbrev: Optional[str] = None
    
    class Config:
        from_attributes = True


class OrganizationAutocompleteResponse(BaseModel):
    """Resposta de autocomplete de organizações"""
    items: List[OrganizationAutocompleteItem]
    total: int


class TeamAutocompleteItem(BaseModel):
    """Item de equipe para autocomplete"""
    id: UUID
    name: str
    category_code: Optional[str] = None
    
    class Config:
        from_attributes = True


class TeamAutocompleteResponse(BaseModel):
    """Resposta de autocomplete de equipes"""
    items: List[TeamAutocompleteItem]
    total: int