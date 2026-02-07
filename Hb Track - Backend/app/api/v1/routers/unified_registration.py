"""
Router para Ficha Única de Cadastro (Unified Registration)

Este módulo implementa o endpoint para cadastro unificado de pessoas no sistema,
permitindo criar em uma única operação:
- Pessoa (persons)
- Documentos (person_documents)
- Contatos (person_contacts)
- Endereço (person_addresses)
- Atleta ou Membership (athletes / org_memberships)
- Usuário (users) - opcional, se email preenchido
- Team Registration (team_registrations) - para atletas
- Organização (organizations) - opcional, criar nova

Permissões de Criação (RF1/R41):
- super_admin: pode criar todos os tipos
- dirigente: pode criar atleta, treinador, coordenador
- coordenador: pode criar atleta, treinador
- treinador: pode criar atleta
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from enum import Enum

from app.core.db import get_async_db
from app.core.auth import get_current_user, MockUser
from app.services.unified_person_service import UnifiedPersonService

router = APIRouter(prefix="/unified-registration", tags=["unified-registration"])

# ============================================================================
# SCHEMAS
# ============================================================================

class RegistrationType(str, Enum):
    atleta = "atleta"
    treinador = "treinador"
    coordenador = "coordenador"
    dirigente = "dirigente"

class Gender(str, Enum):
    masculino = "masculino"
    feminino = "feminino"

class CoreDataSchema(BaseModel):
    """Dados pessoais básicos (obrigatórios)"""
    full_name: str
    birth_date: str
    gender: Gender
    email: Optional[EmailStr] = None

class DocumentsSchema(BaseModel):
    """Documentos"""
    rg: Optional[str] = None
    cpf: Optional[str] = None

class ContactsSchema(BaseModel):
    """Contatos"""
    phone: Optional[str] = None
    whatsapp: Optional[str] = None

class AddressSchema(BaseModel):
    """Endereço"""
    zip_code: Optional[str] = None
    street: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

class AthleteDataSchema(BaseModel):
    """Dados específicos de atleta"""
    main_defensive_position_id: int
    secondary_defensive_position_id: Optional[int] = None
    main_offensive_position_id: Optional[int] = None
    secondary_offensive_position_id: Optional[int] = None
    shirt_number: Optional[int] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    schooling_level_id: Optional[int] = None
    
    @field_validator('shirt_number')
    @classmethod
    def validate_shirt_number(cls, v):
        if v is not None and (v < 1 or v > 99):
            raise ValueError('Número da camisa deve estar entre 1 e 99')
        return v

class CreateOrganizationSchema(BaseModel):
    """Dados para criar nova organização"""
    name: str
    legal_name: Optional[str] = None
    document: Optional[str] = None

class OrganizationBindingSchema(BaseModel):
    """Vínculo com organização"""
    existing_organization_id: Optional[int] = None
    create_organization: Optional[CreateOrganizationSchema] = None

class CreateTeamSchema(BaseModel):
    """Dados para criar nova equipe"""
    name: str
    category_id: int
    gender: Gender

class TeamBindingSchema(BaseModel):
    """Vínculo com equipe"""
    existing_team_id: Optional[int] = None
    create_team: Optional[CreateTeamSchema] = None

class UnifiedRegistrationRequest(BaseModel):
    """Request completo para cadastro unificado"""
    registration_type: Optional[RegistrationType] = None
    create_user: bool = False
    
    core: CoreDataSchema
    documents: Optional[DocumentsSchema] = None
    contacts: Optional[ContactsSchema] = None
    address: Optional[AddressSchema] = None
    athlete: Optional[AthleteDataSchema] = None
    organization: Optional[OrganizationBindingSchema] = None
    team: Optional[TeamBindingSchema] = None

class UnifiedRegistrationResponse(BaseModel):
    """Response do cadastro unificado"""
    success: bool
    person_id: int
    entity_type: Optional[str] = None  # 'athlete' ou 'membership'
    entity_id: Optional[int] = None
    user_id: Optional[int] = None
    team_id: Optional[int] = None
    organization_id: Optional[int] = None
    message: Optional[str] = None

# ============================================================================
# PERMISSÕES
# ============================================================================

ROLE_CREATION_PERMISSIONS = {
    'super_admin': ['atleta', 'treinador', 'coordenador', 'dirigente'],
    'dirigente': ['atleta', 'treinador', 'coordenador'],
    'coordenador': ['atleta', 'treinador'],
    'treinador': ['atleta'],
    'atleta': [],
}

def get_user_role_name(user: User) -> str:
    """Obtém o nome do papel do usuário"""
    if user.is_super_admin:
        return 'super_admin'
    
    if user.roles:
        role = user.roles[0]
        return role.name.lower() if hasattr(role, 'name') else 'atleta'
    
    return 'atleta'

def can_create_type(user_role: str, registration_type: str) -> bool:
    """Verifica se o usuário pode criar o tipo de cadastro"""
    allowed = ROLE_CREATION_PERMISSIONS.get(user_role, [])
    return registration_type in allowed

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=UnifiedRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastro Unificado de Pessoa",
    description="""
    Cria uma pessoa no sistema com todos os dados relacionados em uma única operação.
    
    **Tipos de Cadastro:**
    - atleta: Cria pessoa + atleta + team_registration
    - treinador/coordenador/dirigente: Cria pessoa + membership
    
    **Permissões:**
    - super_admin: pode criar todos os tipos
    - dirigente: pode criar atleta, treinador, coordenador
    - coordenador: pode criar atleta, treinador
    - treinador: pode criar atleta
    
    **Criação de Usuário:**
    - Se `create_user=true` e email preenchido, cria usuário com acesso ao sistema
    - Email de boas-vindas é enviado automaticamente
    """
)
async def create_unified_registration(
    request: UnifiedRegistrationRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: MockUser = Depends(get_current_user),
):
    """Endpoint para cadastro unificado"""
    
    # Verificar permissões se tipo foi especificado
    if request.registration_type:
        user_role = get_user_role_name(current_user)
        
        if not can_create_type(user_role, request.registration_type.value):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Usuário com papel '{user_role}' não pode criar cadastro do tipo '{request.registration_type.value}'"
            )
    
    # Validações específicas para atleta
    if request.registration_type == RegistrationType.atleta:
        # RG é obrigatório para atletas
        if not request.documents or not request.documents.rg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="RG é obrigatório para cadastro de atletas"
            )
        
        # Telefone é obrigatório para atletas
        if not request.contacts or not request.contacts.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telefone é obrigatório para cadastro de atletas"
            )
        
        # Dados de atleta são obrigatórios
        if not request.athlete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dados de atleta são obrigatórios para cadastro de atletas"
            )
        
        # Posição defensiva é obrigatória
        if not request.athlete.main_defensive_position_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Posição defensiva principal é obrigatória"
            )
        
        # RD13: Goleira não pode ter posição ofensiva
        if request.athlete.main_defensive_position_id == 5:  # 5 = Goleira
            if request.athlete.main_offensive_position_id or request.athlete.secondary_offensive_position_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Goleiras não podem ter posição ofensiva (RD13)"
                )
        else:
            # Não-goleiras devem ter posição ofensiva
            if not request.athlete.main_offensive_position_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Posição ofensiva principal é obrigatória (exceto goleiras)"
                )
    
    # Converter request para dicionário para o serviço
    data = {
        'registration_type': request.registration_type.value if request.registration_type else None,
        'create_user': request.create_user,
        'core': request.core.model_dump(),
        'documents': request.documents.model_dump() if request.documents else None,
        'contacts': request.contacts.model_dump() if request.contacts else None,
        'address': request.address.model_dump() if request.address else None,
        'athlete': request.athlete.model_dump() if request.athlete else None,
        'organization': request.organization.model_dump() if request.organization else None,
        'team': request.team.model_dump() if request.team else None,
    }
    
    # Chamar serviço unificado
    service = UnifiedPersonService(db)
    
    try:
        result = await service.create_person_with_role(data, current_user.id)
        
        return UnifiedRegistrationResponse(
            success=True,
            person_id=result['person_id'],
            entity_type=result.get('entity_type'),
            entity_id=result.get('entity_id'),
            user_id=result.get('user_id'),
            team_id=result.get('team_id'),
            organization_id=result.get('organization_id'),
            message=result.get('message', 'Cadastro realizado com sucesso')
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar cadastro: {str(e)}"
        )


@router.get(
    "/permissions",
    summary="Permissões de Criação",
    description="Retorna os tipos de cadastro que o usuário atual pode criar"
)
def get_creation_permissions(
    current_user: MockUser = Depends(get_current_user),
):
    """Retorna permissões de criação do usuário"""
    user_role = get_user_role_name(current_user)
    allowed_types = ROLE_CREATION_PERMISSIONS.get(user_role, [])
    
    return {
        "user_role": user_role,
        "allowed_types": allowed_types,
    }
