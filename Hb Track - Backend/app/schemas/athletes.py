"""
Schemas Pydantic para Athletes e subrecursos.

FASE 3 — Contrato da API (Athletes).

Schemas:
- Athlete, AthleteCreate, AthleteUpdate
- AthleteState, AthleteStateCreate
- TeamRegistration, TeamRegistrationCreate, TeamRegistrationUpdate
- AthletePaginatedResponse

Regras aplicáveis:
- R13/R14: Estados operacionais (ativa, lesionada, dispensada)
- R16/RD1-RD2: Regra etária/categoria fixa na temporada
- R38: Obrigatoriedade de equipe para atuação
- RDB10: Períodos não sobrepostos em team_registrations
- R25/R26: Permissões por papel
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------


class AthleteStateEnum(str, Enum):
    """
    Estados operacionais da atleta (R13/R14).

    - ativa: participa de tudo
    - lesionada: participa normalmente; estatísticas entram nos agregados; alertas específicos
    - dispensada: aparece apenas em histórico; não entra em estatísticas

    Complemento V1.1 (R13):
    - Ao mudar para "dispensada", sistema encerra participações em equipes
    - Reativações criam novas linhas em team_registrations (novo UUID)
    """

    ATIVA = "ativa"
    LESIONADA = "lesionada"
    DISPENSADA = "dispensada"


# -----------------------------------------------------------------------------
# Athlete Schemas
# -----------------------------------------------------------------------------


class AthleteBase(BaseModel):
    """Campos base compartilhados entre schemas de Athlete."""

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome completo da atleta",
    )
    nickname: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Apelido esportivo",
    )
    birth_date: Optional[date] = Field(
        default=None,
        description="Data de nascimento (YYYY-MM-DD)",
    )
    position: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Posição em quadra (ex: goleira, pivo, armadora)",
    )


class AthleteCreate(AthleteBase):
    """
    Payload para criação de atleta.

    Regras:
    - R12: Papel atleta é permanente no histórico
    - R38: Para atuação na temporada, deve haver team_registrations
    - R25/R26: Checar permissões
    - RF1: Treinadores criam atletas (cadeia hierárquica)
    """

    organization_id: Optional[UUID] = Field(
        default=None,
        description="UUID da organização (inferido do token se não fornecido)",
    )
    created_by_membership_id: Optional[UUID] = Field(
        default=None,
        description="UUID do membership que está criando (inferido do token se não fornecido)",
    )
    team_id: UUID = Field(
        ...,
        description="UUID da equipe onde a atleta será registrada (obrigatório - R38)",
    )
    state: AthleteStateEnum = Field(
        default=AthleteStateEnum.ATIVA,
        description="Estado inicial da atleta (default: ativa)",
    )


class AthleteUpdate(BaseModel):
    """
    Payload para atualização parcial de atleta.

    Campos editáveis: full_name, nickname, birth_date, position

    Campos imutáveis via API (não incluídos):
    - organization_id
    - created_by_membership_id
    - person_id

    Regras:
    - R25/R26: Permissões por papel
    - R37: Edições pós-temporada exigem ação administrativa auditada

    Observação: Para alteração de estado, use POST /athletes/{id}/state
    """

    full_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="Nome completo da atleta",
    )
    nickname: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Apelido esportivo",
    )
    birth_date: Optional[date] = Field(
        default=None,
        description="Data de nascimento (YYYY-MM-DD)",
    )
    position: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Posição em quadra",
    )


class Athlete(AthleteBase):
    """
    Representação completa de uma atleta (response).

    Inclui todos os campos, incluindo os de sistema.
    """

    id: UUID = Field(..., description="Identificador único (UUID v4)")
    organization_id: UUID = Field(..., description="UUID da organização")
    created_by_membership_id: UUID = Field(
        ..., description="UUID do membership que criou o registro"
    )
    state: AthleteStateEnum = Field(..., description="Estado operacional atual (R13/R14)")
    person_id: Optional[UUID] = Field(
        default=None, description="UUID da pessoa associada"
    )
    created_at: datetime = Field(..., description="Data/hora de criação (UTC)")
    updated_at: datetime = Field(..., description="Data/hora da última atualização (UTC)")

    model_config = {"from_attributes": True}


class AthletePaginatedResponse(BaseModel):
    """
    Resposta paginada de atletas.

    Envelope: { items, page, limit, total }
    Conforme convenções FASE 3.
    """

    items: List[Athlete] = Field(..., description="Lista de atletas")
    page: int = Field(..., ge=1, description="Página atual")
    limit: int = Field(..., ge=1, le=100, description="Itens por página")
    total: int = Field(..., ge=0, description="Total de itens")


# -----------------------------------------------------------------------------
# AthleteState Schemas
# -----------------------------------------------------------------------------


class AthleteStateBase(BaseModel):
    """Campos base para estado da atleta."""

    state: AthleteStateEnum = Field(
        ...,
        description="Estado operacional (ativa, lesionada, dispensada)",
    )
    reason: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Motivo da mudança de estado",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Observações adicionais",
    )


class AthleteStateCreate(AthleteStateBase):
    """
    Payload para alteração de estado da atleta.

    Regras:
    - R13/RF16: Alteração auditável
    - R14: Impacto nos relatórios/estatísticas

    Efeitos automáticos (R13 Complemento V1.1):
    - Ao mudar para "dispensada": encerra team_registrations ativas
    - Reativações criam novas linhas (novo UUID)

    Transições válidas:
    - ativa → lesionada, dispensada
    - lesionada → ativa, dispensada
    - dispensada → ativa (reativação)
    """

    started_at: Optional[date] = Field(
        default=None,
        description="Data de início do estado (default: hoje)",
    )


class AthleteState(AthleteStateBase):
    """
    Registro de estado da atleta no histórico (response).

    Apenas 1 estado ativo por atleta (ended_at IS NULL).
    """

    id: UUID = Field(..., description="Identificador único do registro de estado")
    athlete_id: UUID = Field(..., description="UUID da atleta")
    started_at: datetime = Field(..., description="Data/hora de início do estado")
    ended_at: Optional[datetime] = Field(
        default=None,
        description="Data/hora de término do estado (null = estado atual)",
    )
    created_at: datetime = Field(..., description="Data/hora de criação do registro")
    updated_at: datetime = Field(..., description="Data/hora da última atualização")

    model_config = {"from_attributes": True}


# -----------------------------------------------------------------------------
# TeamRegistration Schemas
# -----------------------------------------------------------------------------


class TeamRegistrationBase(BaseModel):
    """Campos base para inscrição em equipe."""

    role: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Função na equipe (ex: goleira, pivo)",
    )


class TeamRegistrationCreate(TeamRegistrationBase):
    """
    Payload para criação de inscrição (team_registration).

    Regras:
    - R38: Associação imediata exigida para atuação na temporada
    - RDB10: Períodos não sobrepostos; reativação cria nova linha (novo UUID)
    - R16/RD1-RD2: Categoria fixa na temporada; atuação só na própria ou acima
    - RF5.2: Temporada interrompida bloqueia criação

    Validações no serviço:
    - category_id vs birth_date/season (R16)
    - Sobreposição de períodos (RDB10)
    - Status da temporada (RF5.2)
    """

    season_id: UUID = Field(..., description="UUID da temporada")
    category_id: int = Field(..., description="ID da categoria")
    team_id: UUID = Field(..., description="UUID da equipe")
    organization_id: UUID = Field(..., description="UUID da organização")
    created_by_membership_id: UUID = Field(
        ..., description="UUID do membership que está criando"
    )
    start_at: date = Field(
        ...,
        description="Data de início da inscrição (RDB10)",
    )
    end_at: Optional[date] = Field(
        default=None,
        description="Data de término da inscrição (RDB10)",
    )

    @field_validator("end_at")
    @classmethod
    def validate_end_at(cls, v: Optional[date], info) -> Optional[date]:
        """Valida que end_at >= start_at quando informado."""
        if v is not None:
            start_at = info.data.get("start_at")
            if start_at and v < start_at:
                raise ValueError("end_at deve ser >= start_at")
        return v


class TeamRegistrationUpdate(BaseModel):
    """
    Payload para atualização de inscrição.

    Campos editáveis:
    - end_at: para encerrar inscrição
    - role: função na equipe

    Regras:
    - RDB10: Não reabrir período encerrado; validar sobreposição
    - R13: Estado "dispensada" encerra participações automaticamente
    - RF5.2: Temporada interrompida bloqueia edição

    Observação: Não é possível reabrir (set end_at = null) um período já encerrado.
    """

    end_at: Optional[date] = Field(
        default=None,
        description="Data de término (para encerrar inscrição)",
    )
    role: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Função na equipe",
    )


class TeamRegistration(TeamRegistrationBase):
    """
    Inscrição de atleta em equipe/temporada (response).

    Representa um período de vínculo entre atleta e equipe dentro de uma temporada.
    """

    id: UUID = Field(..., description="Identificador único da inscrição")
    athlete_id: UUID = Field(..., description="UUID da atleta")
    season_id: UUID = Field(..., description="UUID da temporada")
    category_id: int = Field(..., description="ID da categoria")
    team_id: UUID = Field(..., description="UUID da equipe")
    organization_id: UUID = Field(..., description="UUID da organização")
    created_by_membership_id: UUID = Field(..., description="UUID do membership que criou")
    start_at: date = Field(..., description="Data de início da inscrição (RDB10)")
    end_at: Optional[date] = Field(
        default=None,
        description="Data de término da inscrição (RDB10)",
    )
    created_at: datetime = Field(..., description="Data/hora de criação")
    updated_at: datetime = Field(..., description="Data/hora da última atualização")

    model_config = {"from_attributes": True}
