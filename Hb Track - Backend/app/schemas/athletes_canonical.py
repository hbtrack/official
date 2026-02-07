"""
Schemas Canônicos de Atletas (V1.2 Normalizada)

Este arquivo contém os schemas Pydantic para operações com atletas
usando a estrutura CANÔNICA com tabelas normalizadas:
- person_documents (RG, CPF)
- person_contacts (telefone, email)
- person_addresses (endereço completo)

Data de canonização: 31/12/2025

IMPORTANTE: Este arquivo substitui gradualmente athletes_v2.py.
Novos endpoints devem usar estes schemas canônicos.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ==================== SCHEMAS DE DOCUMENTOS ====================

class PersonDocumentBase(BaseModel):
    """Schema base para documentos de pessoa."""
    document_type: str = Field(..., description="Tipo: 'rg', 'cpf', 'passport'")
    document_number: str = Field(..., min_length=1, max_length=50)
    issuer: Optional[str] = Field(None, max_length=100, description="Órgão emissor")
    issue_date: Optional[date] = Field(None, description="Data de emissão")


class PersonDocumentCreate(PersonDocumentBase):
    """Schema para criação de documento."""
    pass


class PersonDocumentResponse(PersonDocumentBase):
    """Schema de resposta de documento."""
    id: UUID
    person_id: UUID
    created_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== SCHEMAS DE CONTATOS ====================

class PersonContactBase(BaseModel):
    """Schema base para contatos de pessoa."""
    contact_type: str = Field(..., description="Tipo: 'phone', 'email', 'whatsapp'")
    contact_value: str = Field(..., min_length=1, max_length=255)
    is_primary: bool = Field(False, description="Contato principal deste tipo")


class PersonContactCreate(PersonContactBase):
    """Schema para criação de contato."""
    
    @field_validator('contact_value')
    @classmethod
    def validate_email_format(cls, v: str, info) -> str:
        """Validar formato de email se contact_type for 'email'."""
        contact_type = info.data.get('contact_type')
        if contact_type == 'email':
            # Validação básica de email
            if '@' not in v or '.' not in v.split('@')[1]:
                raise ValueError('Formato de email inválido')
        return v


class PersonContactResponse(PersonContactBase):
    """Schema de resposta de contato."""
    id: UUID
    person_id: UUID
    created_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== SCHEMAS DE ENDEREÇOS ====================

class PersonAddressBase(BaseModel):
    """Schema base para endereços de pessoa."""
    zip_code: Optional[str] = Field(None, max_length=9, description="Formato: 12345-678")
    street: Optional[str] = Field(None, max_length=200)
    number: Optional[str] = Field(None, max_length=20, description="Permite 'S/N'")
    complement: Optional[str] = Field(None, max_length=100)
    neighborhood: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2, description="Sigla UF (SP, RJ, MG, etc.)")
    country: str = Field("Brasil", max_length=100)
    is_primary: bool = Field(True, description="Endereço principal")


class PersonAddressCreate(PersonAddressBase):
    """Schema para criação de endereço."""
    
    @field_validator('state')
    @classmethod
    def validate_state_uf(cls, v: Optional[str]) -> Optional[str]:
        """Validar se state é uma sigla UF válida."""
        if v is None:
            return v
        
        valid_ufs = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        
        v_upper = v.upper()
        if v_upper not in valid_ufs:
            raise ValueError(f'Estado inválido. Use sigla UF válida: {", ".join(valid_ufs)}')
        
        return v_upper


class PersonAddressResponse(PersonAddressBase):
    """Schema de resposta de endereço."""
    id: UUID
    person_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== SCHEMAS DE ATLETA CANÔNICO ====================

class AthleteCreateCanonical(BaseModel):
    """
    Schema CANÔNICO para criação de atleta.
    
    Usa tabelas normalizadas para documentos, contatos e endereços.
    organization_id é derivado automaticamente de team_registration.
    """
    # Dados pessoais básicos (persons)
    full_name: str = Field(..., min_length=3, max_length=200)
    birth_date: date = Field(..., description="Data de nascimento (idade 8-60 anos)")
    gender: Optional[str] = Field(None, description="male, female, other")
    nationality: Optional[str] = Field("Brasil", max_length=100)
    
    # Dados do atleta (athletes)
    athlete_nickname: Optional[str] = Field(None, max_length=50)
    shirt_number: Optional[int] = Field(None, ge=1, le=99)
    
    # Posições
    main_defensive_position_id: Optional[int] = None
    secondary_defensive_position_id: Optional[int] = None
    main_offensive_position_id: Optional[int] = None
    secondary_offensive_position_id: Optional[int] = None
    
    # Escolaridade
    schooling_id: Optional[int] = None
    
    # Responsável
    guardian_name: Optional[str] = Field(None, max_length=100)
    guardian_phone: Optional[str] = Field(None, max_length=20)
    
    # Documentos (opcional - serão criados em person_documents se fornecidos)
    rg: Optional[str] = Field(None, max_length=20, description="RG - será criado em person_documents")
    cpf: Optional[str] = Field(None, max_length=14, description="CPF - será criado em person_documents")
    
    # Contatos (opcional - serão criados em person_contacts se fornecidos)
    phone: Optional[str] = Field(None, max_length=20, description="Telefone - será criado em person_contacts")
    email: Optional[EmailStr] = Field(None, description="Email - será criado em person_contacts")
    
    # Endereço (opcional - será criado em person_addresses se fornecido)
    address_zip_code: Optional[str] = Field(None, max_length=9)
    address_street: Optional[str] = Field(None, max_length=200)
    address_number: Optional[str] = Field(None, max_length=20)
    address_complement: Optional[str] = Field(None, max_length=100)
    address_neighborhood: Optional[str] = Field(None, max_length=100)
    address_city: Optional[str] = Field(None, max_length=100)
    address_state: Optional[str] = Field(None, max_length=2, description="Sigla UF")
    address_country: Optional[str] = Field("Brasil", max_length=100)
    
    # Vínculo com equipe (opcional - será criado em team_registrations se fornecido)
    team_id: Optional[UUID] = Field(None, description="Equipe para vincular (opcional)")
    team_registration_start: Optional[datetime] = Field(None, description="Data início do vínculo")
    
    # Acesso ao sistema (opcional)
    create_user: bool = Field(False, description="Criar usuário para login")
    user_email: Optional[EmailStr] = Field(None, description="Email para login (se create_user=True)")
    
    @field_validator('birth_date')
    @classmethod
    def validate_age(cls, v: date) -> date:
        """Validar idade entre 8-60 anos."""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        if age < 8:
            raise ValueError('Atleta deve ter pelo menos 8 anos')
        if age > 60:
            raise ValueError('Atleta deve ter no máximo 60 anos')
        
        return v
    
    @field_validator('cpf')
    @classmethod
    def validate_cpf_format(cls, v: Optional[str]) -> Optional[str]:
        """Validar formato básico de CPF."""
        if v is None:
            return v
        
        # Remover caracteres não numéricos
        cpf_digits = ''.join(filter(str.isdigit, v))
        
        if len(cpf_digits) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        
        # TODO: Implementar validação de dígitos verificadores
        
        return cpf_digits
    
    @field_validator('address_state')
    @classmethod
    def validate_state_uf(cls, v: Optional[str]) -> Optional[str]:
        """Validar sigla UF."""
        if v is None:
            return v
        
        valid_ufs = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        
        v_upper = v.upper()
        if v_upper not in valid_ufs:
            raise ValueError(f'Estado inválido. Use sigla UF válida')
        
        return v_upper


class AthleteUpdateCanonical(BaseModel):
    """
    Schema CANÔNICO para atualização de atleta.
    
    Todos os campos são opcionais.
    Documentos, contatos e endereços devem ser atualizados via endpoints dedicados.
    """
    # Dados pessoais
    full_name: Optional[str] = Field(None, min_length=3, max_length=200)
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = Field(None, max_length=100)
    
    # Dados do atleta
    athlete_nickname: Optional[str] = Field(None, max_length=50)
    shirt_number: Optional[int] = Field(None, ge=1, le=99)
    
    # Posições
    main_defensive_position_id: Optional[int] = None
    secondary_defensive_position_id: Optional[int] = None
    main_offensive_position_id: Optional[int] = None
    secondary_offensive_position_id: Optional[int] = None
    
    # Escolaridade
    schooling_id: Optional[int] = None
    
    # Responsável
    guardian_name: Optional[str] = Field(None, max_length=100)
    guardian_phone: Optional[str] = Field(None, max_length=20)
    
    # Estado e flags
    state: Optional[str] = Field(None, description="ativa, dispensada, arquivada")
    injured: Optional[bool] = None
    medical_restriction: Optional[bool] = None
    suspended_until: Optional[date] = None
    load_restricted: Optional[bool] = None


class AthleteResponseCanonical(BaseModel):
    """
    Schema CANÔNICO de resposta de atleta.
    
    Inclui dados agregados de person_documents, person_contacts, person_addresses.
    """
    # Identificação
    id: UUID
    person_id: UUID
    organization_id: Optional[UUID] = Field(None, description="Derivado de team_registration")
    
    # Dados pessoais (de persons)
    full_name: str
    first_name: str
    last_name: str
    birth_date: date
    gender: Optional[str]
    nationality: Optional[str]
    
    # Dados do atleta
    athlete_nickname: Optional[str]
    shirt_number: Optional[int]
    
    # Posições
    main_defensive_position_id: Optional[int]
    secondary_defensive_position_id: Optional[int]
    main_offensive_position_id: Optional[int]
    secondary_offensive_position_id: Optional[int]
    
    # Escolaridade
    schooling_id: Optional[int]
    
    # Responsável
    guardian_name: Optional[str]
    guardian_phone: Optional[str]
    
    # Estado e flags
    state: str
    injured: bool
    medical_restriction: bool
    suspended_until: Optional[date]
    load_restricted: bool
    
    # Documentos (agregados de person_documents)
    documents: list[PersonDocumentResponse] = []
    
    # Contatos (agregados de person_contacts)
    contacts: list[PersonContactResponse] = []
    
    # Endereços (agregados de person_addresses)
    addresses: list[PersonAddressResponse] = []
    
    # Timestamps
    registered_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}
