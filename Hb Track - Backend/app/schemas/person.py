"""
Schemas: Person (R1) - V1.2 Normalizado

Referências RAG:
- R1: Pessoa é entidade raiz
- RDB4: Soft delete obrigatório (deleted_reason)

V1.2: Estrutura normalizada
- persons: identidade básica (nome, gênero, nascimento)
- person_contacts: telefone, email, whatsapp (1:N)
- person_addresses: endereços residenciais (1:N)
- person_documents: CPF, RG, CNH, passaporte (1:N)
- person_media: fotos de perfil e documentos (1:N)
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from uuid import UUID
from datetime import date, datetime
from typing import Optional, List, Literal
from enum import Enum
from app.schemas.base import BaseResponseSchema, SoftDeleteMixin


# =====================================================
# ENUMS
# =====================================================

class ContactTypeEnum(str, Enum):
    """Tipos de contato permitidos"""
    TELEFONE = "telefone"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    OUTRO = "outro"


class AddressTypeEnum(str, Enum):
    """Tipos de endereço permitidos"""
    RESIDENCIAL_1 = "residencial_1"
    RESIDENCIAL_2 = "residencial_2"
    COMERCIAL = "comercial"
    OUTRO = "outro"


class DocumentTypeEnum(str, Enum):
    """Tipos de documento permitidos"""
    CPF = "cpf"
    RG = "rg"
    CNH = "cnh"
    PASSAPORTE = "passaporte"
    CERTIDAO_NASCIMENTO = "certidao_nascimento"
    TITULO_ELEITOR = "titulo_eleitor"
    OUTRO = "outro"


class MediaTypeEnum(str, Enum):
    """Tipos de mídia permitidos"""
    FOTO_PERFIL = "foto_perfil"
    FOTO_DOCUMENTO = "foto_documento"
    VIDEO = "video"
    OUTRO = "outro"


class GenderEnum(str, Enum):
    """Gêneros permitidos"""
    MASCULINO = "masculino"
    FEMININO = "feminino"
    OUTRO = "outro"
    PREFIRO_NAO_DIZER = "prefiro_nao_dizer"


# =====================================================
# PERSON CONTACT SCHEMAS
# =====================================================

class PersonContactBase(BaseModel):
    """Campos comuns de PersonContact"""
    contact_type: ContactTypeEnum = Field(..., description="Tipo de contato")
    contact_value: str = Field(..., min_length=1, max_length=200, description="Valor do contato")
    is_primary: bool = Field(default=False, description="Se é o contato primário deste tipo")
    is_verified: bool = Field(default=False, description="Se o contato foi verificado")
    notes: Optional[str] = Field(None, description="Observações")


class PersonContactCreate(PersonContactBase):
    """Schema para criação de PersonContact"""
    pass


class PersonContactUpdate(BaseModel):
    """Schema para atualização de PersonContact"""
    contact_value: Optional[str] = Field(None, min_length=1, max_length=200)
    is_primary: Optional[bool] = None
    is_verified: Optional[bool] = None
    notes: Optional[str] = None


class PersonContactResponse(PersonContactBase, BaseResponseSchema, SoftDeleteMixin):
    """Schema de resposta de PersonContact"""
    person_id: UUID


# =====================================================
# PERSON ADDRESS SCHEMAS
# =====================================================

class PersonAddressBase(BaseModel):
    """Campos comuns de PersonAddress"""
    address_type: AddressTypeEnum = Field(..., description="Tipo de endereço")
    street: str = Field(..., min_length=1, max_length=200, description="Logradouro")
    number: Optional[str] = Field(None, max_length=20, description="Número")
    complement: Optional[str] = Field(None, max_length=100, description="Complemento")
    neighborhood: Optional[str] = Field(None, max_length=100, description="Bairro")
    city: str = Field(..., min_length=1, max_length=100, description="Cidade")
    state: str = Field(..., min_length=2, max_length=2, description="Estado (UF)")
    postal_code: Optional[str] = Field(None, max_length=10, description="CEP")
    country: str = Field(default="Brasil", max_length=100, description="País")
    is_primary: bool = Field(default=False, description="Se é o endereço primário")

    @field_validator('state')
    @classmethod
    def validate_state(cls, v: str) -> str:
        """Valida UF brasileira"""
        valid_states = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        if v.upper() not in valid_states:
            raise ValueError(f"UF inválida: {v}")
        return v.upper()


class PersonAddressCreate(PersonAddressBase):
    """Schema para criação de PersonAddress"""
    pass


class PersonAddressUpdate(BaseModel):
    """Schema para atualização de PersonAddress"""
    street: Optional[str] = Field(None, min_length=1, max_length=200)
    number: Optional[str] = Field(None, max_length=20)
    complement: Optional[str] = Field(None, max_length=100)
    neighborhood: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    postal_code: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    is_primary: Optional[bool] = None


class PersonAddressResponse(PersonAddressBase, BaseResponseSchema, SoftDeleteMixin):
    """Schema de resposta de PersonAddress"""
    person_id: UUID


# =====================================================
# PERSON DOCUMENT SCHEMAS
# =====================================================

class PersonDocumentBase(BaseModel):
    """Campos comuns de PersonDocument"""
    document_type: DocumentTypeEnum = Field(..., description="Tipo de documento")
    document_number: str = Field(..., min_length=1, max_length=100, description="Número do documento")
    issuing_authority: Optional[str] = Field(None, max_length=100, description="Órgão emissor")
    issue_date: Optional[date] = Field(None, description="Data de emissão")
    expiry_date: Optional[date] = Field(None, description="Data de validade")
    document_file_url: Optional[str] = Field(None, description="URL do arquivo digitalizado")
    is_verified: bool = Field(default=False, description="Se o documento foi verificado")
    notes: Optional[str] = Field(None, description="Observações")

    @field_validator('document_number')
    @classmethod
    def validate_document_number(cls, v: str, info) -> str:
        """Valida número do documento baseado no tipo"""
        # Remove caracteres não numéricos para CPF
        if hasattr(info, 'data') and info.data.get('document_type') == 'cpf':
            v = ''.join(filter(str.isdigit, v))
            if len(v) != 11:
                raise ValueError("CPF deve ter 11 dígitos")
        return v


class PersonDocumentCreate(PersonDocumentBase):
    """Schema para criação de PersonDocument"""
    pass


class PersonDocumentUpdate(BaseModel):
    """Schema para atualização de PersonDocument"""
    document_number: Optional[str] = Field(None, min_length=1, max_length=100)
    issuing_authority: Optional[str] = Field(None, max_length=100)
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    document_file_url: Optional[str] = None
    is_verified: Optional[bool] = None
    notes: Optional[str] = None


class PersonDocumentResponse(PersonDocumentBase, BaseResponseSchema, SoftDeleteMixin):
    """Schema de resposta de PersonDocument"""
    person_id: UUID


# =====================================================
# PERSON MEDIA SCHEMAS
# =====================================================

class PersonMediaBase(BaseModel):
    """Campos comuns de PersonMedia"""
    media_type: MediaTypeEnum = Field(..., description="Tipo de mídia")
    file_url: str = Field(..., min_length=1, description="URL do arquivo")
    file_name: Optional[str] = Field(None, max_length=255, description="Nome do arquivo")
    file_size: Optional[int] = Field(None, ge=0, description="Tamanho do arquivo em bytes")
    mime_type: Optional[str] = Field(None, max_length=100, description="MIME type do arquivo")
    is_primary: bool = Field(default=False, description="Se é a mídia primária deste tipo")
    description: Optional[str] = Field(None, description="Descrição")


class PersonMediaCreate(PersonMediaBase):
    """Schema para criação de PersonMedia"""
    pass


class PersonMediaUpdate(BaseModel):
    """Schema para atualização de PersonMedia"""
    file_url: Optional[str] = Field(None, min_length=1)
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    is_primary: Optional[bool] = None
    description: Optional[str] = None


class PersonMediaResponse(PersonMediaBase, BaseResponseSchema, SoftDeleteMixin):
    """Schema de resposta de PersonMedia"""
    person_id: UUID


# =====================================================
# PERSON SCHEMAS (V1.2 NORMALIZADO)
# =====================================================

class PersonBase(BaseModel):
    """Campos comuns de Person (V1.2)"""
    first_name: str = Field(..., min_length=1, max_length=100, description="Primeiro nome")
    last_name: str = Field(..., min_length=1, max_length=100, description="Sobrenome")
    birth_date: Optional[date] = Field(None, description="Data de nascimento")
    gender: Optional[GenderEnum] = Field(None, description="Gênero")
    nationality: Optional[str] = Field(default="brasileira", max_length=100, description="Nacionalidade")
    notes: Optional[str] = Field(None, description="Observações")


class PersonCreate(PersonBase):
    """
    Schema para criação de Person (V1.2)
    
    Permite criar pessoa com contatos, endereços, documentos e mídias de uma vez.
    """
    # Nested creates (opcionais)
    contacts: Optional[List[PersonContactCreate]] = Field(default=None, description="Contatos")
    addresses: Optional[List[PersonAddressCreate]] = Field(default=None, description="Endereços")
    documents: Optional[List[PersonDocumentCreate]] = Field(default=None, description="Documentos")
    media: Optional[List[PersonMediaCreate]] = Field(default=None, description="Mídias")


class PersonUpdate(BaseModel):
    """Schema para atualização parcial de Person (V1.2)"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    birth_date: Optional[date] = None
    gender: Optional[GenderEnum] = None
    nationality: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class PersonResponse(PersonBase, BaseResponseSchema, SoftDeleteMixin):
    """
    Schema de resposta de Person (V1.2)
    
    Inclui todos os dados relacionados (contatos, endereços, documentos, mídias).
    """
    full_name: str = Field(..., description="Nome completo")
    
    # Nested responses
    contacts: List[PersonContactResponse] = Field(default=[], description="Contatos")
    addresses: List[PersonAddressResponse] = Field(default=[], description="Endereços")
    documents: List[PersonDocumentResponse] = Field(default=[], description="Documentos")
    media: List[PersonMediaResponse] = Field(default=[], description="Mídias")
    
    # Campos computados para compatibilidade
    primary_phone: Optional[str] = Field(None, description="Telefone primário")
    primary_email: Optional[str] = Field(None, description="Email primário")
    cpf: Optional[str] = Field(None, description="CPF (compatibilidade)")

    class Config:
        from_attributes = True


class PersonListResponse(BaseModel):
    """Schema de resposta para listagem de Person (simplificado)"""
    id: UUID
    full_name: str
    first_name: str
    last_name: str
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    primary_phone: Optional[str] = None
    primary_email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PersonSoftDelete(BaseModel):
    """
    Schema para soft delete de Person e entidades relacionadas

    Referências RAG:
    - RDB4: deleted_reason obrigatório quando deleted_at não é null
    """
    deleted_reason: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Motivo da exclusão (RDB4 - obrigatório)"
    )


# =====================================================
# SCHEMAS AUXILIARES
# =====================================================

class PersonContactSoftDelete(BaseModel):
    """Schema para soft delete de PersonContact"""
    deleted_reason: str = Field(..., min_length=10, max_length=500)


class PersonAddressSoftDelete(BaseModel):
    """Schema para soft delete de PersonAddress"""
    deleted_reason: str = Field(..., min_length=10, max_length=500)


class PersonDocumentSoftDelete(BaseModel):
    """Schema para soft delete de PersonDocument"""
    deleted_reason: str = Field(..., min_length=10, max_length=500)


class PersonMediaSoftDelete(BaseModel):
    """Schema para soft delete de PersonMedia"""
    deleted_reason: str = Field(..., min_length=10, max_length=500)
