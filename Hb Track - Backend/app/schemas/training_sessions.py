"""
Schemas Pydantic para sessões de treino (Training Sessions).

Campos baseados na tabela training_sessions:
- id: UUID PK
- organization_id: UUID NOT NULL
- created_by_membership_id: UUID NOT NULL
- session_at: timestamptz NOT NULL
- main_objective: text (opcional)
- planned_load: int (opcional)
- actual_load_avg: int (opcional)
- group_climate: int (opcional)
- highlight: text (opcional)
- next_corrections: text (opcional)
- created_at: timestamptz
- updated_at: timestamptz
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SessionTypeEnum(str, Enum):
    """Tipos de sessão de treino permitidos (constraint: ck_training_sessions_type)."""
    QUADRA = "quadra"      # Treino em quadra (padrão)
    FISICO = "fisico"      # Treino físico/preparação
    VIDEO = "video"        # Análise de vídeo
    REUNIAO = "reuniao"    # Reunião técnica/tática
    TESTE = "teste"        # Testes físicos/técnicos


class TrainingExecutionOutcome(str, Enum):
    """Resultado da execução real do treino (revisão operacional)."""
    ON_TIME = "on_time"
    DELAYED = "delayed"
    CANCELED = "canceled"
    SHORTENED = "shortened"
    EXTENDED = "extended"


class TrainingSessionBase(BaseModel):
    """Campos compartilhados de sessão de treino."""

    organization_id: UUID = Field(..., description="ID da organização")
    team_id: Optional[UUID] = Field(None, description="ID da equipe")
    season_id: Optional[UUID] = Field(None, description="ID da temporada")
    created_by_user_id: Optional[UUID] = Field(None, description="ID do usuário que criou")
    session_at: datetime = Field(..., description="Data/hora da sessão de treino")
    session_type: SessionTypeEnum = Field(..., description="Tipo de sessão: quadra, fisico, video, reuniao, teste")
    main_objective: Optional[str] = Field(None, description="Objetivo principal do treino")
    secondary_objective: Optional[str] = Field(None, description="Objetivo secundário do treino")
    notes: Optional[str] = Field(None, description="Observações adicionais")
    planned_load: Optional[int] = Field(None, description="Carga planejada (escala 1-10)")
    group_climate: Optional[int] = Field(None, description="Clima do grupo (escala 1-5)")
    intensity_target: Optional[int] = Field(None, description="Intensidade alvo (escala 1-10)")
    duration_planned_minutes: Optional[int] = Field(None, description="Duração planejada em minutos")
    location: Optional[str] = Field(None, description="Local do treino")


class TrainingSessionCreate(BaseModel):
    """Payload para criação de sessão de treino."""

    organization_id: UUID = Field(..., description="ID da organização")
    team_id: UUID = Field(..., description="ID do time")
    season_id: Optional[UUID] = Field(None, description="ID da temporada")
    session_at: datetime = Field(..., description="Data/hora da sessão de treino")
    session_type: SessionTypeEnum = Field(
        SessionTypeEnum.QUADRA,
        description="Tipo de sessão: quadra, fisico, video, reuniao, teste",
    )
    main_objective: Optional[str] = Field(None, description="Objetivo principal do treino")
    duration_planned_minutes: Optional[int] = Field(None, description="Duração planejada em minutos")
    location: Optional[str] = Field(None, description="Local do treino")
    notes: Optional[str] = Field(None, description="Observações adicionais")
    planned_load: Optional[int] = Field(None, description="Carga planejada (escala 0-10)")
    group_climate: Optional[int] = Field(None, description="Clima do grupo (escala 1-5)")
    intensity_target: Optional[int] = Field(None, description="Intensidade alvo (escala 1-10)")
    highlight: Optional[str] = Field(None, description="Destaques do treino")
    next_corrections: Optional[str] = Field(None, description="Correções para próximas sessões")

    # Microciclo associado
    microcycle_id: Optional[UUID] = Field(None, description="ID do microciclo associado")

    # Focos de treino (percentuais 0-100) - Análise estratégica /statistics/teams
    focus_attack_positional_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em ataque posicionado (0-100)"
    )
    focus_defense_positional_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em defesa posicionada (0-100)"
    )
    focus_transition_offense_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em transição ofensiva (0-100)"
    )
    focus_transition_defense_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em transição defensiva (0-100)"
    )
    focus_attack_technical_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em ataque técnico (0-100)"
    )
    focus_defense_technical_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em defesa técnica (0-100)"
    )
    focus_physical_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em treino físico (0-100)"
    )

    # Justificativa para desvio (>100%)
    deviation_justification: Optional[str] = Field(
        None,
        description="Justificativa para distribuição de foco acima de 100%"
    )

    @model_validator(mode='after')
    def validate_focus_sum(self):
        """Valida que a soma dos focos não excede 120% (treinos híbridos permitidos)."""
        focus_fields = [
            self.focus_attack_positional_pct,
            self.focus_defense_positional_pct,
            self.focus_transition_offense_pct,
            self.focus_transition_defense_pct,
            self.focus_attack_technical_pct,
            self.focus_defense_technical_pct,
            self.focus_physical_pct,
        ]
        total = sum(f for f in focus_fields if f is not None)
        if total > 120:
            raise ValueError(f'Soma dos focos ({total}%) excede o máximo permitido (120%)')
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "team_id": "123e4567-e89b-12d3-a456-426614174001",
                "session_at": "2025-01-20T10:00:00Z",
                "session_type": "quadra",
                "main_objective": "Preparação física e técnica",
                "duration_planned_minutes": 90,
                "planned_load": 8,
                "group_climate": 4,
                "focus_attack_positional_pct": 30,
                "focus_defense_positional_pct": 25,
            }
        }
    )


class ScopedTrainingSessionCreate(BaseModel):
    """Payload para criação de sessão de treino em rotas scoped (organization_id inferido do team)."""

    organization_id: Optional[UUID] = Field(None, description="ID da organização (inferido do team se omitido)")
    season_id: Optional[UUID] = Field(None, description="ID da temporada")
    session_at: datetime = Field(..., description="Data/hora da sessão de treino")
    session_type: SessionTypeEnum = Field(SessionTypeEnum.QUADRA, description="Tipo de sessão: quadra, fisico, video, reuniao, teste")
    main_objective: Optional[str] = Field(None, description="Objetivo principal do treino")
    planned_load: Optional[int] = Field(None, description="Carga planejada (escala 0-10)")
    group_climate: Optional[int] = Field(None, description="Clima do grupo (escala 1-5)")
    highlight: Optional[str] = Field(None, description="Destaques do treino")
    next_corrections: Optional[str] = Field(None, description="Correções para próximas sessões")
    
    # Focos de treino (percentuais 0-100) - Análise estratégica /statistics/teams
    focus_attack_positional_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em ataque posicionado (0-100)"
    )
    focus_defense_positional_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em defesa posicionada (0-100)"
    )
    focus_transition_offense_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em transição ofensiva (0-100)"
    )
    focus_transition_defense_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em transição defensiva (0-100)"
    )
    focus_attack_technical_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em ataque técnico (0-100)"
    )
    focus_defense_technical_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em defesa técnica (0-100)"
    )
    focus_physical_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em treino físico (0-100)"
    )
    
    @model_validator(mode='after')
    def validate_focus_sum(self):
        """Valida que a soma dos focos não excede 120% (treinos híbridos permitidos)."""
        focus_fields = [
            self.focus_attack_positional_pct,
            self.focus_defense_positional_pct,
            self.focus_transition_offense_pct,
            self.focus_transition_defense_pct,
            self.focus_attack_technical_pct,
            self.focus_defense_technical_pct,
            self.focus_physical_pct,
        ]
        
        total = sum(f for f in focus_fields if f is not None)
        
        if total > 120:
            raise ValueError(
                f'A soma dos focos de treino não pode exceder 120% (atual: {total}%). '
                'Treinos híbridos são permitidos até este limite.'
            )
        
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_at": "2025-01-20T10:00:00Z",
                "session_type": "quadra",
                "main_objective": "Preparação física e técnica",
                "planned_load": 8,
                "focus_attack_positional_pct": 25.0,
                "focus_defense_positional_pct": 20.0,
                "focus_transition_offense_pct": 15.0,
            }
        }
    )


class TrainingSessionUpdate(BaseModel):
    """Payload para atualização de sessão de treino."""

    session_at: Optional[datetime] = Field(None, description="Data/hora da sessão de treino")
    session_type: Optional[SessionTypeEnum] = Field(None, description="Tipo de sessão: quadra, fisico, video, reuniao, teste")
    main_objective: Optional[str] = Field(None, description="Objetivo principal do treino")
    secondary_objective: Optional[str] = Field(None, description="Objetivo secundário do treino")
    planned_load: Optional[int] = Field(None, description="Carga planejada (escala 0-10)")
    intensity_target: Optional[int] = Field(None, description="Intensidade alvo (escala 1-10)")
    actual_load_avg: Optional[int] = Field(None, description="Média de carga realizada")
    group_climate: Optional[int] = Field(None, description="Clima do grupo (escala 1-5)")
    duration_planned_minutes: Optional[int] = Field(None, description="Duração planejada em minutos")
    duration_actual_minutes: Optional[int] = Field(None, ge=0, description="Duração real em minutos")
    location: Optional[str] = Field(None, description="Local do treino")
    highlight: Optional[str] = Field(None, description="Destaques do treino")
    next_corrections: Optional[str] = Field(None, description="Correções para próximas sessões")
    execution_outcome: Optional[TrainingExecutionOutcome] = Field(
        None,
        description="Resultado da execução real (on_time, delayed, canceled, shortened, extended)"
    )
    delay_minutes: Optional[int] = Field(None, ge=0, description="Atraso em minutos (se delayed)")
    cancellation_reason: Optional[str] = Field(None, description="Motivo do cancelamento (se canceled)")
    deviation_justification: Optional[str] = Field(
        None,
        description="Justificativa de desvio (obrigatória se execução != on_time)"
    )
    
    # Focos de treino (percentuais 0-100) - Análise estratégica /statistics/teams
    focus_attack_positional_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em ataque posicionado (0-100)"
    )
    focus_defense_positional_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em defesa posicionada (0-100)"
    )
    focus_transition_offense_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em transição ofensiva (0-100)"
    )
    focus_transition_defense_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em transição defensiva (0-100)"
    )
    focus_attack_technical_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em ataque técnico (0-100)"
    )
    focus_defense_technical_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em defesa técnica (0-100)"
    )
    focus_physical_pct: Optional[Decimal] = Field(
        None, ge=0, le=100,
        description="Percentual de foco em treino físico (0-100)"
    )
    
    @model_validator(mode='after')
    def validate_focus_sum(self):
        """Valida que a soma dos focos não excede 120% (treinos híbridos permitidos)."""
        focus_fields = [
            self.focus_attack_positional_pct,
            self.focus_defense_positional_pct,
            self.focus_transition_offense_pct,
            self.focus_transition_defense_pct,
            self.focus_attack_technical_pct,
            self.focus_defense_technical_pct,
            self.focus_physical_pct,
        ]
        
        total = sum(f for f in focus_fields if f is not None)
        
        if total > 120:
            raise ValueError(
                f'A soma dos focos de treino não pode exceder 120% (atual: {total}%). '
                'Treinos híbridos são permitidos até este limite.'
            )
        
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "actual_load_avg": 7,
                "highlight": "Treino intenso, boa recuperação",
                "next_corrections": "Ajustar carga no próximo ciclo",
            }
        }
    )


class TrainingSession(TrainingSessionBase):
    """Resposta completa de sessão de treino."""

    id: UUID = Field(..., description="ID da sessão de treino")
    status: str = Field(
        ...,
        description="Estado: draft, scheduled, in_progress, pending_review, readonly"
    )
    started_at: Optional[datetime] = Field(None, description="Início real registrado")
    ended_at: Optional[datetime] = Field(None, description="Fim real/planejado registrado")
    duration_actual_minutes: Optional[int] = Field(None, description="Duração real em minutos")
    execution_outcome: TrainingExecutionOutcome = Field(
        ...,
        description="Resultado da execução real (on_time, delayed, canceled, shortened, extended)"
    )
    delay_minutes: Optional[int] = Field(None, description="Atraso em minutos (se delayed)")
    cancellation_reason: Optional[str] = Field(None, description="Motivo do cancelamento (se canceled)")
    post_review_completed_at: Optional[datetime] = Field(
        None,
        description="Data/hora de conclusão da revisão operacional"
    )
    post_review_completed_by_user_id: Optional[UUID] = Field(
        None,
        description="Usuário que concluiu a revisão operacional"
    )
    post_review_deadline_at: Optional[datetime] = Field(
        None,
        description="Prazo operacional para revisão (alertas)"
    )
    closed_at: Optional[datetime] = Field(None, description="Data/hora de congelamento final")
    closed_by_user_id: Optional[UUID] = Field(None, description="Usuário que concluiu o congelamento")
    exercises_count: Optional[int] = Field(
        None,
        description="Quantidade de exercícios vinculados à sessão"
    )
    attendance_present_count: Optional[int] = Field(
        None,
        description="Quantidade de atletas presentes na sessão"
    )
    attendance_total_count: Optional[int] = Field(
        None,
        description="Quantidade total de atletas elegíveis para a sessão"
    )
    created_at: datetime = Field(..., description="Data/hora de criação")
    updated_at: datetime = Field(..., description="Data/hora da última atualização")
    deleted_at: Optional[datetime] = Field(None, description="Data/hora de exclusão (soft delete)")
    deleted_reason: Optional[str] = Field(None, description="Motivo da exclusão")
    
    # Focos de treino (percentuais 0-100) - Análise estratégica /statistics/teams
    focus_attack_positional_pct: Optional[Decimal] = Field(
        None, description="Percentual de foco em ataque posicionado (0-100)"
    )
    focus_defense_positional_pct: Optional[Decimal] = Field(
        None, description="Percentual de foco em defesa posicionada (0-100)"
    )
    focus_transition_offense_pct: Optional[Decimal] = Field(
        None, description="Percentual de foco em transição ofensiva (0-100)"
    )
    focus_transition_defense_pct: Optional[Decimal] = Field(
        None, description="Percentual de foco em transição defensiva (0-100)"
    )
    focus_attack_technical_pct: Optional[Decimal] = Field(
        None, description="Percentual de foco em ataque técnico (0-100)"
    )
    focus_defense_technical_pct: Optional[Decimal] = Field(
        None, description="Percentual de foco em defesa técnica (0-100)"
    )
    focus_physical_pct: Optional[Decimal] = Field(
        None, description="Percentual de foco em treino físico (0-100)"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "team_id": "123e4567-e89b-12d3-a456-426614174003",
                "session_at": "2025-01-20T10:00:00Z",
                "session_type": "quadra",
                "main_objective": "Preparação física e técnica",
                "planned_load": 8,
                "group_climate": 4,
                "created_at": "2025-01-20T08:00:00Z",
                "updated_at": "2025-01-20T12:30:00Z",
            }
        },
    )


class TrainingSessionPaginatedResponse(BaseModel):
    """Resposta paginada de sessões de treino."""

    items: List[TrainingSession] = Field(..., description="Lista de sessões de treino")
    page: int = Field(..., ge=1, description="Número da página atual")
    limit: int = Field(..., ge=1, le=100, description="Itens por página")
    total: int = Field(..., ge=0, description="Total de itens")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174002",
                        "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                        "created_by_membership_id": "123e4567-e89b-12d3-a456-426614174001",
                        "session_at": "2025-01-20T10:00:00Z",
                        "main_objective": "Preparação física e técnica",
                        "planned_load": 8,
                        "actual_load_avg": 7,
                        "group_climate": 4,
                        "highlight": "Boa intensidade geral",
                        "next_corrections": None,
                        "created_at": "2025-01-20T08:00:00Z",
                        "updated_at": "2025-01-20T12:30:00Z",
                    }
                ],
                "page": 1,
                "limit": 50,
                "total": 1,
            }
        }
    )


# Novos schemas para estados e desvios (TRAINNIG.MD)

class TrainingSessionCloseRequest(BaseModel):
    """Payload para fechamento de sessão."""
    confirm: bool = Field(default=True, description="Confirmação de fechamento")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "confirm": True
            }
        }
    )


class TrainingSessionDeviationResponse(BaseModel):
    """Resposta de análise de desvio (planejado vs executado)."""
    training_session_id: UUID = Field(..., description="ID da sessão")
    microcycle_id: Optional[UUID] = Field(None, description="ID do microciclo")

    # Desvios por foco (executado - planejado)
    deviation_attack_positional_pct: Optional[Decimal] = Field(
        None,
        description="Desvio em ataque posicionado (positivo = acima do planejado)"
    )
    deviation_defense_positional_pct: Optional[Decimal] = Field(
        None,
        description="Desvio em defesa posicionada"
    )
    deviation_transition_offense_pct: Optional[Decimal] = Field(
        None,
        description="Desvio em transição ofensiva"
    )
    deviation_transition_defense_pct: Optional[Decimal] = Field(
        None,
        description="Desvio em transição defensiva"
    )
    deviation_attack_technical_pct: Optional[Decimal] = Field(
        None,
        description="Desvio em ataque técnico"
    )
    deviation_defense_technical_pct: Optional[Decimal] = Field(
        None,
        description="Desvio em defesa técnica"
    )
    deviation_physical_pct: Optional[Decimal] = Field(
        None,
        description="Desvio em físico"
    )

    # Desvio total
    total_deviation_pct: Decimal = Field(..., description="Desvio agregado (soma dos absolutos)")
    is_significant_deviation: bool = Field(
        ...,
        description="Flag de desvio significativo (≥20pts em algum foco OU ≥30% agregado)"
    )

    # Mensagens explicativas
    deviation_message: str = Field(..., description="Mensagem explicativa do desvio")
    suggestions: List[str] = Field(
        default_factory=list,
        description="Sugestões de ajuste (futuro)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "training_session_id": "123e4567-e89b-12d3-a456-426614174002",
                "microcycle_id": "123e4567-e89b-12d3-a456-426614174004",
                "deviation_attack_positional_pct": 5.0,
                "deviation_defense_positional_pct": -3.0,
                "deviation_transition_offense_pct": 2.0,
                "deviation_transition_defense_pct": -5.0,
                "deviation_attack_technical_pct": 0.0,
                "deviation_defense_technical_pct": 0.0,
                "deviation_physical_pct": 1.0,
                "total_deviation_pct": 16.0,
                "is_significant_deviation": False,
                "deviation_message": "Execução dentro do esperado em relação ao planejamento",
                "suggestions": []
            }
        }
    )


class TrainingSessionResponse(TrainingSession):
    """Resposta completa com dados adicionais de estado."""
    microcycle_id: Optional[UUID] = Field(None, description="ID do microciclo")
    status: str = Field(
        ...,
        description="Estado: draft, scheduled, in_progress, pending_review, readonly"
    )
    closed_at: Optional[datetime] = Field(None, description="Data/hora de fechamento")
    closed_by_user_id: Optional[UUID] = Field(None, description="ID do usuário que fechou")
    deviation_justification: Optional[str] = Field(
        None,
        description="Justificativa de desvio"
    )
    planning_deviation_flag: bool = Field(
        default=False,
        description="Flag de desvio significativo"
    )

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# SCHEMAS PARA FECHAMENTO DE SESSÃO COM VALIDAÇÃO (Step 1 - Plano Refatoração)
# ============================================================================

class SessionClosureFieldErrors(BaseModel):
    """
    Erros estruturados por campo para revisão operacional.

    Usado para retornar validações detalhadas ao frontend, permitindo
    exibição de erros inline no fluxo de revisão.
    """
    execution_outcome: Optional[str] = Field(
        None,
        description="Erro no resultado de execução"
    )
    delay_minutes: Optional[str] = Field(
        None,
        description="Erro no atraso informado (se delayed)"
    )
    duration_actual_minutes: Optional[str] = Field(
        None,
        description="Erro na duração real (se shortened/extended)"
    )
    cancellation_reason: Optional[str] = Field(
        None,
        description="Erro no motivo do cancelamento (se canceled)"
    )
    deviation_justification: Optional[str] = Field(
        None,
        description="Erro na justificativa de desvio (quando execução != on_time)"
    )
    presence: Optional[str] = Field(
        None,
        description="Erro nas presenças (atletas sem status definido)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "execution_outcome": "Resultado de execução é obrigatório",
                "presence": "3 atletas sem presença registrada: João, Maria, Pedro",
                "deviation_justification": "Justificativa obrigatória para execução não prevista"
            }
        }
    )


class AthleteWithoutPresence(BaseModel):
    """Atleta sem presença registrada."""
    athlete_id: UUID = Field(..., description="ID do atleta")
    athlete_name: str = Field(..., description="Nome do atleta")
    team_registration_id: UUID = Field(..., description="ID do vínculo com a equipe")


class SessionClosureValidationResult(BaseModel):
    """
    Resultado da validação de revisão operacional.

    Retornado pelo endpoint de revisão para informar
    ao frontend quais campos precisam de correção antes de finalizar.
    """
    can_close: bool = Field(
        ...,
        description="True se a sessão pode ser finalizada sem erros"
    )
    error_code: Optional[str] = Field(
        None,
        description="Código do erro principal: INVALID_STATUS, INCOMPLETE_PRESENCE, "
                    "MISSING_OUTCOME, MISSING_DELAY, MISSING_DURATION, MISSING_CANCELLATION, "
                    "MISSING_DEVIATION_JUSTIFICATION"
    )
    field_errors: SessionClosureFieldErrors = Field(
        default_factory=SessionClosureFieldErrors,
        description="Erros detalhados por campo"
    )
    athletes_without_presence: List[AthleteWithoutPresence] = Field(
        default_factory=list,
        description="Lista de atletas ativos sem presença registrada"
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "can_close": False,
                "error_code": "INCOMPLETE_PRESENCE",
                "field_errors": {
                    "presence": "3 atletas sem presença registrada"
                },
                "athletes_without_presence": [
                    {
                        "athlete_id": "123e4567-e89b-12d3-a456-426614174005",
                        "athlete_name": "João Silva",
                        "team_registration_id": "123e4567-e89b-12d3-a456-426614174006"
                    }
                ]
            }
        }
    )


class SessionClosureResponse(BaseModel):
    """
    Resposta do fechamento de sessão.

    Se success=True, session contém a sessão atualizada.
    Se success=False, validation contém os erros detalhados.
    """
    success: bool = Field(..., description="True se fechou com sucesso")
    session: Optional[TrainingSessionResponse] = Field(
        None,
        description="Sessão atualizada (se success=True)"
    )
    validation: Optional[SessionClosureValidationResult] = Field(
        None,
        description="Resultado da validação (se success=False)"
    )
    message: str = Field(..., description="Mensagem descritiva")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "session": {
                    "id": "123e4567-e89b-12d3-a456-426614174002",
                    "status": "readonly",
                    "closed_at": "2025-01-21T15:30:00Z"
                },
                "validation": None,
                "message": "Sessão fechada com sucesso"
            }
        }
    )
