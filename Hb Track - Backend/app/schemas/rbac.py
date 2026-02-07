"""
Schemas Pydantic para RBAC (Users, Organizations, Roles, Permissions, Memberships).

Conforme definido em:
- docs/openapi/rbac.yaml (OpenAPI 3.1)
- docs/fluxo-backend-oficial_Version12.md (Contrato de erros por regra)

Regras de negócio aplicáveis:
- R25/R26: Permissões por papel e escopo
- R29/R33: Exclusão lógica e histórico com rastro
- R31/R32: Ações críticas auditadas
- R34: Clube único na V1
- R42: Usuários sem vínculo ativo não podem operar
"""

from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# =============================================================================
# Enums
# =============================================================================

class RoleCode(str, Enum):
    """
    Códigos de papel do sistema (R4/R25).
    
    Papéis V1:
    - superadmin: Acesso total ao sistema
    - dirigente: Gestão administrativa do clube
    - coordenador: Coordenação técnica de equipes
    - treinador: Gestão de treinos e atletas
    - atleta: Acesso aos próprios dados
    """
    SUPERADMIN = "superadmin"
    DIRIGENTE = "dirigente"
    COORDENADOR = "coordenador"
    TREINADOR = "treinador"
    ATLETA = "atleta"


class RoleCodeCreate(str, Enum):
    """
    Códigos de papel permitidos na criação via API.
    
    superadmin não pode ser criado via API (apenas seed/admin).
    """
    DIRIGENTE = "dirigente"
    COORDENADOR = "coordenador"
    TREINADOR = "treinador"
    ATLETA = "atleta"


class UserOrderBy(str, Enum):
    """Campos permitidos para ordenação de usuários."""
    CREATED_AT = "created_at"
    FULL_NAME = "full_name"
    UPDATED_AT = "updated_at"


class OrganizationOrderBy(str, Enum):
    """Campos permitidos para ordenação de organizações."""
    CREATED_AT = "created_at"
    NAME = "name"
    UPDATED_AT = "updated_at"


class MembershipOrderBy(str, Enum):
    """Campos permitidos para ordenação de memberships."""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class OrderDirection(str, Enum):
    """Direção da ordenação."""
    ASC = "asc"
    DESC = "desc"


# =============================================================================
# User Schemas
# =============================================================================

class UserBase(BaseModel):
    """
    Campos base compartilhados entre schemas de User.
    V1.2: User não tem full_name/phone - isso está em Person (R1).
    """
    email: EmailStr = Field(
        ...,
        description="Email (único no sistema)"
    )


class User(BaseModel):
    """
    Schema completo de User para responses.
    
    Inclui campos somente leitura (id, created_at, updated_at).
    Inclui campos de soft delete (deleted_at, deleted_reason) para suporte RDB4.
    
    V1.2: full_name vem de Person (R1), não é campo direto de User.
    
    Note: Uses str for email instead of EmailStr to allow special addresses like
    superadmin@seed.local which are used in database seeds.
    """
    id: UUID = Field(
        ...,
        description="ID único do usuário"
    )
    person_id: Optional[UUID] = Field(
        None,
        description="ID da pessoa associada (R1)"
    )
    email: str = Field(
        ...,
        description="Email (único no sistema)"
    )
    status: str = Field(
        "ativo",
        description="Status do usuário: ativo, inativo, arquivado"
    )
    is_superadmin: bool = Field(
        False,
        description="Se é Super Administrador (R3)"
    )
    deleted_at: Optional[datetime] = Field(
        None,
        description="Data/hora de exclusão lógica (RDB4)"
    )
    deleted_reason: Optional[str] = Field(
        None,
        description="Motivo da exclusão lógica"
    )
    created_at: datetime = Field(
        ...,
        description="Data/hora de criação"
    )
    updated_at: datetime = Field(
        ...,
        description="Data/hora da última atualização"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "person_id": "660e8400-e29b-41d4-a716-446655440001",
                "email": "maria@exemplo.com",
                "status": "ativo",
                "is_superadmin": False,
                "deleted_at": None,
                "deleted_reason": None,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    )


class UserCreate(BaseModel):
    """
    Payload para criação de usuário.
    
    V1.2 - RF1.1:
    - person_id obrigatório (Person deve existir antes)
    - full_name/phone pertencem a Person, não a User
    - role define o papel do usuário
    """
    email: EmailStr = Field(
        ...,
        description="Email (único no sistema)"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        description="Senha do usuario (minimo 8 caracteres). Se não fornecida, email de boas-vindas será enviado."
    )
    person_id: UUID = Field(
        ...,
        description="ID da pessoa associada (R1 - Person deve existir)"
    )
    role: str = Field(
        "dirigente",
        description="Papel do usuário: dirigente, coordenador, treinador"
    )
    send_welcome_email: bool = Field(
        True,
        description="Se true, envia email de boas-vindas com link para criar senha"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "maria@exemplo.com",
                "person_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "dirigente",
                "send_welcome_email": True
            }
        }
    )


class UserUpdate(BaseModel):
    """
    Payload para atualização de usuário.
    V1.2: full_name/phone pertencem a Person - usar endpoint /persons para atualizar.
    """
    email: Optional[EmailStr] = Field(
        None,
        description="Email (único no sistema)"
    )
    status: Optional[str] = Field(
        None,
        description="Status: ativo, inativo, arquivado"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Maria Silva Santos",
                "phone": "+5511999997777"
            }
        }
    )


class UserPaginatedResponse(BaseModel):
    """Resposta paginada de usuários."""
    items: List[User] = Field(
        ...,
        description="Lista de usuários"
    )
    page: int = Field(
        ...,
        ge=1,
        description="Página atual"
    )
    limit: int = Field(
        ...,
        ge=1,
        le=100,
        description="Itens por página"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total de itens"
    )


# =============================================================================
# Organization Schemas
# =============================================================================

class OrganizationBase(BaseModel):
    """Campos base compartilhados entre schemas de Organization."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome da organização"
    )
    code: Optional[str] = Field(
        None,
        max_length=50,
        description="Código curto (sigla)"
    )


class Organization(OrganizationBase):
    """
    Schema completo de Organization para responses.
    
    Inclui campos somente leitura (id, created_at, updated_at).
    Inclui campos de soft delete (deleted_at, deleted_reason) para suporte RDB4.
    """
    id: UUID = Field(
        ...,
        description="ID único da organização"
    )
    deleted_at: Optional[datetime] = Field(
        None,
        description="Data/hora de exclusão lógica (RDB4)"
    )
    deleted_reason: Optional[str] = Field(
        None,
        description="Motivo da exclusão lógica"
    )
    created_at: datetime = Field(
        ...,
        description="Data/hora de criação"
    )
    updated_at: datetime = Field(
        ...,
        description="Data/hora da última atualização"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "name": "Clube Handebol São Paulo",
                "code": "CHSP",
                "deleted_at": None,
                "deleted_reason": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )


class OrganizationCreate(BaseModel):
    """Payload para criação de organização."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome da organização"
    )
    code: Optional[str] = Field(
        None,
        max_length=50,
        description="Código curto (sigla)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Clube Handebol São Paulo",
                "code": "CHSP"
            }
        }
    )


class OrganizationUpdate(BaseModel):
    """Payload para atualização de organização."""
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Nome da organização"
    )
    code: Optional[str] = Field(
        None,
        max_length=50,
        description="Código curto (sigla)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Clube Handebol SP - Atualizado"
            }
        }
    )


class OrganizationPaginatedResponse(BaseModel):
    """Resposta paginada de organizações."""
    items: List[Organization] = Field(
        ...,
        description="Lista de organizações"
    )
    page: int = Field(
        ...,
        ge=1,
        description="Página atual"
    )
    limit: int = Field(
        ...,
        ge=1,
        le=100,
        description="Itens por página"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total de itens"
    )


# =============================================================================
# Role Schema
# =============================================================================

class Role(BaseModel):
    """
    Schema de Role (catálogo de papéis).
    
    Papéis V1: dirigente, coordenador, treinador, atleta
    Ref: R4, RDB2.1
    """
    id: int = Field(
        ...,
        description="ID do papel (smallint)"
    )
    code: str = Field(
        ...,
        description="Código único do papel"
    )
    name: str = Field(
        ...,
        description="Nome exibível do papel"
    )
    description: Optional[str] = Field(
        None,
        description="Descrição do papel"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 3,
                "code": "treinador",
                "name": "Treinador",
                "description": "Gestão de treinos e atletas"
            }
        }
    )


# =============================================================================
# Permission Schema
# =============================================================================

class Permission(BaseModel):
    """
    Schema de Permission (catálogo de permissões).
    
    Permissões V1:
    - read_athlete, edit_athlete
    - read_training, edit_training
    - read_match, edit_match
    - admin_memberships, admin_organization
    """
    code: str = Field(
        ...,
        description="Código único da permissão"
    )
    name: str = Field(
        ...,
        description="Nome exibível da permissão"
    )
    description: Optional[str] = Field(
        None,
        description="Descrição da permissão"
    )
    roles: List[str] = Field(
        ...,
        description="Papéis que possuem esta permissão"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "edit_training",
                "name": "Editar Treinos",
                "description": "Permissão para criar/editar sessões de treino",
                "roles": ["superadmin", "dirigente", "coordenador", "treinador"]
            }
        }
    )


# =============================================================================
# Membership Schemas (RBAC - user↔organization+role)
# =============================================================================

class MembershipBase(BaseModel):
    """Campos base compartilhados entre schemas de Membership."""
    user_id: UUID = Field(
        ...,
        description="ID do usuário vinculado"
    )
    organization_id: UUID = Field(
        ...,
        description="ID da organização"
    )
    role_code: RoleCode = Field(
        ...,
        description="Código do papel atribuído"
    )
    is_active: bool = Field(
        True,
        description="Se o vínculo está ativo"
    )


class Membership(BaseModel):
    """
    Schema completo de Membership para responses.
    
    Vínculo user↔organization+role com constraint:
    UNIQUE(user_id, organization_id) onde is_active=true
    """
    id: UUID = Field(
        ...,
        description="ID único do vínculo"
    )
    user_id: UUID = Field(
        ...,
        description="ID do usuário vinculado"
    )
    organization_id: UUID = Field(
        ...,
        description="ID da organização"
    )
    role_code: RoleCode = Field(
        ...,
        description="Código do papel atribuído"
    )
    is_active: bool = Field(
        ...,
        description="Se o vínculo está ativo"
    )
    created_at: datetime = Field(
        ...,
        description="Data/hora de criação"
    )
    updated_at: datetime = Field(
        ...,
        description="Data/hora da última atualização"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440002",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "organization_id": "660e8400-e29b-41d4-a716-446655440001",
                "role_code": "treinador",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    )


class MembershipCreate(BaseModel):
    """
    Payload para criação de vínculo (V1.2).
    
    V1.2: usa person_id (não user_id), sem season_id.
    organization_id vem da URL path parameter.
    superadmin não pode ser criado via API.
    """
    person_id: UUID = Field(
        ...,
        description="ID da pessoa a vincular (V1.2: usa person_id)"
    )
    role_code: RoleCodeCreate = Field(
        ...,
        description="Código do papel (superadmin não permitido via API)"
    )
    start_date: Optional[date] = Field(
        None,
        description="Data de início do vínculo (default: hoje)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "person_id": "550e8400-e29b-41d4-a716-446655440000",
                "role_code": "treinador",
                "start_date": "2025-01-01"
            }
        }
    )


class MembershipUpdate(BaseModel):
    """
    Payload para atualização de vínculo.
    
    user_id e organization_id não podem ser alterados via API.
    superadmin não pode ser atribuído via API.
    """
    role_code: Optional[RoleCodeCreate] = Field(
        None,
        description="Código do papel (superadmin não permitido via API)"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Se o vínculo está ativo"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role_code": "coordenador",
                "is_active": True
            }
        }
    )


class MembershipPaginatedResponse(BaseModel):
    """Resposta paginada de vínculos."""
    items: List[Membership] = Field(
        ...,
        description="Lista de vínculos"
    )
    page: int = Field(
        ...,
        ge=1,
        description="Página atual"
    )
    limit: int = Field(
        ...,
        ge=1,
        le=100,
        description="Itens por página"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total de itens"
    )
