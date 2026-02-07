"""
Schemas Pydantic para Athletes (VERSÃO 2 - PÓS RDB AJUSTES).

ATUALIZADO: 2025-12-27 - Migrations e1-e3

Mudanças principais:
- full_name → athlete_name
- nickname → athlete_nickname
- category_id REMOVIDO do create (agora em team_registrations)
- athlete_age, athlete_age_at_registration CALCULADOS (não persistidos)
- Novos campos: documentos (RG, CPF), contatos, endereço, escolaridade, posições
- Constraint RD13: goleiras não têm posição ofensiva

Schemas:
- AthleteCreate: Criar nova atleta
- AthleteUpdate: Atualizar atleta
- AthleteResponse: Resposta da API (GET)
- AthleteStateHistoryResponse: Histórico de estados
- ChangeStateRequest: Mudar estado da atleta
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, EmailStr


# =============================================================================
# Enums
# =============================================================================

class AthleteStateEnum(str, Enum):
    """
    Estados operacionais da atleta (R12, REGRAS.md V1.2).
    
    IMPORTANTE: 'lesionada' NÃO é um estado - é uma flag (injured=true).
    Estados base são: ativa, dispensada, arquivada.
    """
    ATIVA = "ativa"
    DISPENSADA = "dispensada"
    ARQUIVADA = "arquivada"


# =============================================================================
# Athlete Create
# =============================================================================

class AthleteCreate(BaseModel):
    """
    Payload para criação de atleta.

    Campos obrigatórios:
    - athlete_name (min 3 chars)
    - birth_date
    - main_defensive_position_id
    - athlete_rg (UNIQUE)
    - athlete_cpf (UNIQUE)
    - athlete_phone
    - team_id (UUID opcional; se ausente, usa equipe institucional)

    Campos opcionais:
    - athlete_nickname
    - shirt_number (1-99)
    - main_offensive_position_id (OBRIGATÓRIO exceto goleiras - RD13)
    - secondary_defensive_position_id
    - secondary_offensive_position_id
    - athlete_email (UNIQUE, case-insensitive)
    - guardian_name, guardian_phone
    - schooling_id
    - zip_code, street, neighborhood, city, address_state, address_number, address_complement

    NOTA: category_id NÃO está aqui (será atribuído em team_registrations - RD1/RD2)
    """

    # ==================== DADOS PESSOAIS (OBRIGATÓRIOS) ====================
    athlete_name: str = Field(..., min_length=3, max_length=100, description="Nome completo da atleta")
    birth_date: str = Field(..., description="Data de nascimento (YYYY-MM-DD)")
    gender: str = Field(
        ...,
        description="Gênero: 'masculino' ou 'feminino' (obrigatório para validação R15)"
    )

    # ==================== POSIÇÕES ====================
    main_defensive_position_id: int = Field(..., description="Posição defensiva principal (FK defensive_positions)")
    secondary_defensive_position_id: Optional[int] = Field(None, description="Posição defensiva secundária")
    main_offensive_position_id: Optional[int] = Field(None, description="Posição ofensiva principal (obrigatória exceto goleiras - RD13)")
    secondary_offensive_position_id: Optional[int] = Field(None, description="Posição ofensiva secundária")

    # ==================== DOCUMENTOS (OBRIGATÓRIOS) ====================
    athlete_rg: str = Field(..., max_length=20, description="RG (UNIQUE)")
    athlete_cpf: str = Field(..., max_length=14, description="CPF (UNIQUE)")

    # ==================== CONTATOS (OBRIGATÓRIOS) ====================
    athlete_phone: str = Field(..., max_length=20, description="Telefone")

    # ==================== EQUIPE (OBRIGATÓRIO - R38) ====================
    team_id: Optional[UUID] = Field(
        None,
        description="UUID da equipe (opcional; se vazio, equipe institucional)"
    )

    # ==================== OPCIONAIS ====================
    athlete_nickname: Optional[str] = Field(None, max_length=50, description="Apelido")
    shirt_number: Optional[int] = Field(None, ge=1, le=99, description="Número da camisa (1-99)")
    athlete_email: Optional[EmailStr] = Field(None, description="Email (UNIQUE, case-insensitive)")
    guardian_name: Optional[str] = Field(None, max_length=100, description="Nome do responsável")
    guardian_phone: Optional[str] = Field(None, max_length=20, description="Telefone do responsável")
    schooling_id: Optional[int] = Field(None, description="Nível de escolaridade (FK schooling_levels)")

    # Endereço
    zip_code: Optional[str] = Field(None, max_length=9, description="CEP")
    street: Optional[str] = Field(None, max_length=120, description="Rua/Logradouro")
    neighborhood: Optional[str] = Field(None, max_length=80, description="Bairro")
    city: Optional[str] = Field(None, max_length=80, description="Cidade")
    address_state: Optional[str] = Field(None, max_length=2, description="UF (ex: SP, RJ)")
    address_number: Optional[str] = Field(None, max_length=20, description="Número")
    address_complement: Optional[str] = Field(None, max_length=80, description="Complemento")

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: str) -> str:
        """Valida formato da data de nascimento."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('birth_date deve estar no formato YYYY-MM-DD')

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """Valida gênero: apenas 'masculino' ou 'feminino'."""
        allowed = {'masculino', 'feminino'}
        if v.lower().strip() not in allowed:
            raise ValueError(f"gender deve ser 'masculino' ou 'feminino', recebido: '{v}'")
        return v.lower().strip()

    # NOTA: Validação RD13 (goleira sem posição ofensiva) é feita no serviço
    # para evitar problemas com validação cross-field no Pydantic


# =============================================================================
# Athlete Update
# =============================================================================

class AthleteUpdate(BaseModel):
    """
    Payload para atualização parcial de atleta.

    Todos os campos são opcionais. Apenas campos fornecidos serão atualizados.
    """
    athlete_name: Optional[str] = Field(None, min_length=3, max_length=100)
    athlete_nickname: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[str] = Field(None)
    gender: Optional[str] = Field(None, description="Gênero: 'masculino' ou 'feminino'")
    shirt_number: Optional[int] = Field(None, ge=1, le=99)

    main_defensive_position_id: Optional[int] = None
    secondary_defensive_position_id: Optional[int] = None
    main_offensive_position_id: Optional[int] = None
    secondary_offensive_position_id: Optional[int] = None

    athlete_rg: Optional[str] = Field(None, max_length=20)
    athlete_cpf: Optional[str] = Field(None, max_length=14)
    athlete_phone: Optional[str] = Field(None, max_length=20)
    athlete_email: Optional[EmailStr] = None

    guardian_name: Optional[str] = Field(None, max_length=100)
    guardian_phone: Optional[str] = Field(None, max_length=20)
    schooling_id: Optional[int] = None

    zip_code: Optional[str] = Field(None, max_length=9)
    street: Optional[str] = Field(None, max_length=120)
    neighborhood: Optional[str] = Field(None, max_length=80)
    city: Optional[str] = Field(None, max_length=80)
    address_state: Optional[str] = Field(None, max_length=2)
    address_number: Optional[str] = Field(None, max_length=20)
    address_complement: Optional[str] = Field(None, max_length=80)

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        """Valida gênero se fornecido."""
        if v is None:
            return None
        allowed = {'masculino', 'feminino'}
        if v.lower().strip() not in allowed:
            raise ValueError(f"gender deve ser 'masculino' ou 'feminino', recebido: '{v}'")
        return v.lower().strip()


# =============================================================================
# Athlete Response
# =============================================================================

class AthleteResponse(BaseModel):
    """
    Resposta da API para GET /athletes/{id}.

    V1.2: organization_id é derivado via team_registrations, não é campo direto.
    """
    # Identificação
    id: UUID
    organization_id: Optional[UUID] = None  # V1.2: derivado via team_registrations
    person_id: UUID

    # Dados pessoais
    athlete_name: str
    athlete_nickname: Optional[str] = None
    birth_date: date
    gender: Optional[str] = None  # CANÔNICO: Gênero de persons.gender

    # Timestamps
    registered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Número da camisa
    shirt_number: Optional[int] = None

    # Posições
    main_defensive_position_id: Optional[int] = None
    secondary_defensive_position_id: Optional[int] = None
    main_offensive_position_id: Optional[int] = None
    secondary_offensive_position_id: Optional[int] = None

    # Documentos
    athlete_rg: Optional[str] = None
    athlete_cpf: Optional[str] = None

    # Contatos
    athlete_phone: Optional[str] = None
    athlete_email: Optional[str] = None

    # Responsável
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None

    # Escolaridade
    schooling_id: Optional[int] = None

    # Endereço
    zip_code: Optional[str] = None
    street: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    address_state: Optional[str] = None
    address_number: Optional[str] = None
    address_complement: Optional[str] = None
    
    # Foto
    athlete_photo_path: Optional[str] = None

    # Status e flags (V1.2: R12/R13)
    state: AthleteStateEnum
    injured: bool = False
    medical_restriction: bool = False
    suspended_until: Optional[date] = None
    load_restricted: bool = False
    deleted_at: Optional[datetime] = None

    # ==================== CAMPOS CALCULADOS ====================
    athlete_age_at_registration: Optional[int] = Field(None, description="Idade no momento do registro")
    athlete_age: Optional[int] = Field(None, description="Idade atual (calculado em runtime)")

    # Team registrations (V1.2)
    team_registrations: Optional[List] = None

    class Config:
        from_attributes = True


# =============================================================================
# State History
# =============================================================================

class AthleteStateHistoryResponse(BaseModel):
    """Histórico de mudanças de estado."""
    id: UUID
    athlete_id: UUID
    state: AthleteStateEnum
    changed_at: datetime
    effective_from: datetime
    effective_until: Optional[datetime]
    changed_by_membership_id: Optional[UUID]
    reason: Optional[str]
    is_current: bool

    class Config:
        from_attributes = True


# =============================================================================
# Change State Request
# =============================================================================

class ChangeStateRequest(BaseModel):
    """
    Payload para POST /athletes/{id}/state.

    Muda o estado da atleta (ativa → lesionada → dispensada).
    """
    state: AthleteStateEnum = Field(..., description="Novo estado")
    reason: Optional[str] = Field(None, max_length=500, description="Motivo da mudança (opcional)")


# =============================================================================
# Paginated Response
# =============================================================================

class AthletePaginatedResponse(BaseModel):
    """Resposta paginada de atletas."""
    items: List[AthleteResponse]
    page: int
    limit: int
    total: int


# =============================================================================
# Dashboard Stats
# =============================================================================

class AthleteStatsResponse(BaseModel):
    """
    Estatísticas de atletas para dashboard (FASE 2 - FLUXO_GERENCIAMENTO_ATLETAS.md).
    
    KPIs:
    - Total de atletas
    - Em captação (sem team_registration ativo)
    - Lesionadas (injured=true)
    - Suspensas (suspended_until >= hoje)
    - Por estado (ativa, dispensada, arquivada)
    - Por categoria
    """
    total: int = Field(..., description="Total de atletas")
    em_captacao: int = Field(..., description="Atletas sem equipe (fase captação/avaliação)")
    lesionadas: int = Field(..., description="Atletas com flag injured=true")
    suspensas: int = Field(..., description="Atletas com suspensão ativa")
    ativas: int = Field(..., description="Atletas no estado ativa")
    dispensadas: int = Field(..., description="Atletas dispensadas")
    arquivadas: int = Field(..., description="Atletas arquivadas")
    com_restricao_medica: int = Field(..., description="Atletas com restrição médica")
    carga_restrita: int = Field(..., description="Atletas com carga restrita")
    por_categoria: dict = Field(default_factory=dict, description="Contagem por categoria (categoria_name: count)")
