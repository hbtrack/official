"""
Pydantic schemas for Competitions V2 - Module with AI Import.

Este módulo adiciona schemas para:
- Importação via IA (PDF parsing com Gemini)
- Fases de competição
- Equipes adversárias
- Jogos da competição
- Classificação

Novos campos em Competition:
- team_id, season, modality
- competition_type, format_details
- tiebreaker_criteria, points_per_win
- status, current_phase_id
- regulation_file_url, regulation_notes
"""

from datetime import datetime, date, time
from typing import Optional, List, Any, Dict
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


# =============================================================================
# ENUMS
# =============================================================================

class CompetitionType(str, Enum):
    """Tipos de formato de competição."""
    TURNO_UNICO = "turno_unico"
    TURNO_RETURNO = "turno_returno"
    GRUPOS = "grupos"
    GRUPOS_MATA_MATA = "grupos_mata_mata"
    MATA_MATA = "mata_mata"
    TRIANGULAR = "triangular"
    QUADRANGULAR = "quadrangular"
    CUSTOM = "custom"


class CompetitionStatus(str, Enum):
    """Status de uma competição."""
    DRAFT = "draft"
    ACTIVE = "active"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class Modality(str, Enum):
    """Modalidade (gênero) da competição."""
    MASCULINO = "masculino"
    FEMININO = "feminino"
    MISTO = "misto"


class PhaseType(str, Enum):
    """Tipos de fase de competição."""
    GROUP = "group"
    KNOCKOUT = "knockout"
    ROUND_ROBIN = "round_robin"
    SEMIFINAL = "semifinal"
    FINAL = "final"
    THIRD_PLACE = "third_place"
    QUARTERFINAL = "quarterfinal"
    ROUND_OF_16 = "round_of_16"
    CUSTOM = "custom"


class PhaseStatus(str, Enum):
    """Status de uma fase."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class MatchStatus(str, Enum):
    """Status de um jogo."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class OpponentTeamStatus(str, Enum):
    """Status de uma equipe adversária na competição."""
    ACTIVE = "active"
    ELIMINATED = "eliminated"
    QUALIFIED = "qualified"
    WITHDRAWN = "withdrawn"


class QualificationStatus(str, Enum):
    """Status de classificação."""
    QUALIFIED = "qualified"
    PLAYOFFS = "playoffs"
    RELEGATION = "relegation"
    ELIMINATED = "eliminated"


# =============================================================================
# COMPETITION V2 SCHEMAS
# =============================================================================

class CompetitionV2Create(BaseModel):
    """
    Schema para criação de competição V2 (POST).
    Suporta todos os novos campos do módulo de IA.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Copa Estadual Sub-17 Masculino 2025",
                "team_id": "550e8400-e29b-41d4-a716-446655440000",
                "season": "2025",
                "modality": "masculino",
                "competition_type": "grupos_mata_mata",
                "format_details": {
                    "num_grupos": 4,
                    "classificados_por_grupo": 2
                },
                "tiebreaker_criteria": ["pontos", "saldo_gols", "gols_pro", "confronto_direto"],
                "points_per_win": 2,
                "regulation_notes": "Competição organizada pela Federação Estadual"
            }
        }
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nome da competição",
    )
    team_id: Optional[UUID] = Field(
        default=None,
        description="ID da nossa equipe que participa",
    )
    season: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Temporada (ex: 2025, 2025/2026)",
    )
    modality: Optional[Modality] = Field(
        default=Modality.MASCULINO,
        description="Modalidade: masculino, feminino, misto",
    )
    kind: Optional[str] = Field(
        default=None,
        description="Tipo legado: official, friendly, training-game",
    )
    competition_type: Optional[CompetitionType] = Field(
        default=None,
        description="Formato da competição",
    )
    format_details: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Detalhes específicos do formato",
    )
    tiebreaker_criteria: Optional[List[str]] = Field(
        default_factory=lambda: ["pontos", "saldo_gols", "gols_pro", "confronto_direto"],
        description="Critérios de desempate em ordem",
    )
    points_per_win: Optional[int] = Field(
        default=2,
        ge=1,
        le=5,
        description="Pontos por vitória (handebol = 2)",
    )
    regulation_file_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL do arquivo de regulamento",
    )
    regulation_notes: Optional[str] = Field(
        default=None,
        description="Anotações sobre o regulamento",
    )


class CompetitionV2Update(BaseModel):
    """Schema para atualização de competição V2 (PATCH)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Copa Estadual Sub-17 Masculino 2025 - Atualizado",
                "status": "active"
            }
        }
    )

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    team_id: Optional[UUID] = Field(default=None)
    season: Optional[str] = Field(default=None, max_length=50)
    modality: Optional[Modality] = Field(default=None)
    kind: Optional[str] = Field(default=None)
    competition_type: Optional[CompetitionType] = Field(default=None)
    format_details: Optional[Dict[str, Any]] = Field(default=None)
    tiebreaker_criteria: Optional[List[str]] = Field(default=None)
    points_per_win: Optional[int] = Field(default=None, ge=1, le=5)
    status: Optional[CompetitionStatus] = Field(default=None)
    current_phase_id: Optional[UUID] = Field(default=None)
    regulation_file_url: Optional[str] = Field(default=None, max_length=500)
    regulation_notes: Optional[str] = Field(default=None)


class CompetitionV2Response(BaseModel):
    """Schema de resposta completo para competição V2."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    kind: Optional[str] = None
    team_id: Optional[UUID] = None
    season: Optional[str] = None
    modality: Optional[str] = None
    competition_type: Optional[str] = None
    format_details: Optional[Dict[str, Any]] = None
    tiebreaker_criteria: Optional[List[str]] = None
    points_per_win: Optional[int] = None
    status: Optional[str] = None
    current_phase_id: Optional[UUID] = None
    regulation_file_url: Optional[str] = None
    regulation_notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


# =============================================================================
# COMPETITION PHASE SCHEMAS
# =============================================================================

class CompetitionPhaseCreate(BaseModel):
    """Schema para criação de fase."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Fase de Grupos",
                "phase_type": "group",
                "order_index": 0,
                "is_olympic_cross": False,
                "config": {"num_groups": 4}
            }
        }
    )

    name: str = Field(..., min_length=1, max_length=100)
    phase_type: PhaseType
    order_index: int = Field(default=0, ge=0)
    is_olympic_cross: bool = Field(default=False)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CompetitionPhaseUpdate(BaseModel):
    """Schema para atualização de fase."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phase_type: Optional[PhaseType] = Field(default=None)
    order_index: Optional[int] = Field(default=None, ge=0)
    is_olympic_cross: Optional[bool] = Field(default=None)
    config: Optional[Dict[str, Any]] = Field(default=None)
    status: Optional[PhaseStatus] = Field(default=None)


class CompetitionPhaseResponse(BaseModel):
    """Schema de resposta para fase."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    competition_id: UUID
    name: str
    phase_type: str
    order_index: int
    is_olympic_cross: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =============================================================================
# OPPONENT TEAM SCHEMAS
# =============================================================================

class OpponentTeamStats(BaseModel):
    """Estatísticas de uma equipe."""
    points: int = 0
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    goal_difference: int = 0


class CompetitionOpponentTeamCreate(BaseModel):
    """Schema para criação de equipe adversária."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Esporte Clube Exemplo",
                "short_name": "ECE",
                "city": "São Paulo",
                "group_name": "A"
            }
        }
    )

    name: str = Field(..., min_length=1, max_length=255)
    short_name: Optional[str] = Field(default=None, max_length=50)
    category: Optional[str] = Field(default=None, max_length=50)
    city: Optional[str] = Field(default=None, max_length=100)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    linked_team_id: Optional[UUID] = Field(default=None)
    group_name: Optional[str] = Field(default=None, max_length=50)


class CompetitionOpponentTeamUpdate(BaseModel):
    """Schema para atualização de equipe adversária."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    short_name: Optional[str] = Field(default=None, max_length=50)
    category: Optional[str] = Field(default=None, max_length=50)
    city: Optional[str] = Field(default=None, max_length=100)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    linked_team_id: Optional[UUID] = Field(default=None)
    group_name: Optional[str] = Field(default=None, max_length=50)
    status: Optional[OpponentTeamStatus] = Field(default=None)


class CompetitionOpponentTeamResponse(BaseModel):
    """Schema de resposta para equipe adversária."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    competition_id: UUID
    name: str
    short_name: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    logo_url: Optional[str] = None
    linked_team_id: Optional[UUID] = None
    group_name: Optional[str] = None
    stats: Optional[OpponentTeamStats] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =============================================================================
# COMPETITION MATCH SCHEMAS
# =============================================================================

class CompetitionMatchCreate(BaseModel):
    """Schema para criação de jogo da competição."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "phase_id": "550e8400-e29b-41d4-a716-446655440001",
                "home_team_id": "550e8400-e29b-41d4-a716-446655440002",
                "away_team_id": "550e8400-e29b-41d4-a716-446655440003",
                "match_date": "2025-03-15",
                "match_time": "15:00:00",
                "location": "Ginásio Municipal",
                "round_number": 1
            }
        }
    )

    phase_id: Optional[UUID] = Field(default=None)
    external_reference_id: Optional[str] = Field(default=None, max_length=100)
    home_team_id: Optional[UUID] = Field(default=None)
    away_team_id: Optional[UUID] = Field(default=None)
    is_our_match: bool = Field(default=False)
    our_team_is_home: Optional[bool] = Field(default=None)
    match_date: Optional[date] = Field(default=None)
    match_time: Optional[time] = Field(default=None)
    location: Optional[str] = Field(default=None, max_length=255)
    round_number: Optional[int] = Field(default=None, ge=1)
    round_name: Optional[str] = Field(default=None, max_length=100)


class CompetitionMatchUpdate(BaseModel):
    """Schema para atualização de jogo."""

    phase_id: Optional[UUID] = Field(default=None)
    home_team_id: Optional[UUID] = Field(default=None)
    away_team_id: Optional[UUID] = Field(default=None)
    is_our_match: Optional[bool] = Field(default=None)
    our_team_is_home: Optional[bool] = Field(default=None)
    linked_match_id: Optional[UUID] = Field(default=None)
    match_date: Optional[date] = Field(default=None)
    match_time: Optional[time] = Field(default=None)
    location: Optional[str] = Field(default=None, max_length=255)
    round_number: Optional[int] = Field(default=None, ge=1)
    round_name: Optional[str] = Field(default=None, max_length=100)
    home_score: Optional[int] = Field(default=None, ge=0)
    away_score: Optional[int] = Field(default=None, ge=0)
    home_score_extra: Optional[int] = Field(default=None, ge=0)
    away_score_extra: Optional[int] = Field(default=None, ge=0)
    home_score_penalties: Optional[int] = Field(default=None, ge=0)
    away_score_penalties: Optional[int] = Field(default=None, ge=0)
    status: Optional[MatchStatus] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class CompetitionMatchResultUpdate(BaseModel):
    """Schema específico para atualização de resultado."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "home_score": 28,
                "away_score": 25,
                "status": "finished"
            }
        }
    )

    home_score: int = Field(..., ge=0)
    away_score: int = Field(..., ge=0)
    home_score_extra: Optional[int] = Field(default=None, ge=0)
    away_score_extra: Optional[int] = Field(default=None, ge=0)
    home_score_penalties: Optional[int] = Field(default=None, ge=0)
    away_score_penalties: Optional[int] = Field(default=None, ge=0)
    status: MatchStatus = Field(default=MatchStatus.FINISHED)


class CompetitionMatchResponse(BaseModel):
    """Schema de resposta para jogo."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    competition_id: UUID
    phase_id: Optional[UUID] = None
    external_reference_id: Optional[str] = None
    home_team_id: Optional[UUID] = None
    away_team_id: Optional[UUID] = None
    is_our_match: Optional[bool] = None
    our_team_is_home: Optional[bool] = None
    linked_match_id: Optional[UUID] = None
    match_date: Optional[date] = None
    match_time: Optional[time] = None
    match_datetime: Optional[datetime] = None
    location: Optional[str] = None
    round_number: Optional[int] = None
    round_name: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_score_extra: Optional[int] = None
    away_score_extra: Optional[int] = None
    home_score_penalties: Optional[int] = None
    away_score_penalties: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Nested relations (populated when requested)
    home_team: Optional[CompetitionOpponentTeamResponse] = None
    away_team: Optional[CompetitionOpponentTeamResponse] = None


# =============================================================================
# COMPETITION STANDING SCHEMAS
# =============================================================================

class CompetitionStandingResponse(BaseModel):
    """Schema de resposta para classificação."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    competition_id: UUID
    phase_id: Optional[UUID] = None
    opponent_team_id: UUID
    position: int
    group_name: Optional[str] = None
    points: Optional[int] = None
    played: Optional[int] = None
    wins: Optional[int] = None
    draws: Optional[int] = None
    losses: Optional[int] = None
    goals_for: Optional[int] = None
    goals_against: Optional[int] = None
    goal_difference: Optional[int] = None
    recent_form: Optional[str] = None
    qualification_status: Optional[str] = None
    updated_at: Optional[datetime] = None

    # Nested relation
    opponent_team: Optional[CompetitionOpponentTeamResponse] = None


# =============================================================================
# AI IMPORT SCHEMAS
# =============================================================================

class AIExtractedTeam(BaseModel):
    """Equipe extraída pelo Gemini."""
    name: str
    short_name: Optional[str] = None
    city: Optional[str] = None
    group_name: Optional[str] = None
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1)


class AIExtractedMatch(BaseModel):
    """Jogo extraído pelo Gemini."""
    external_reference_id: Optional[str] = None
    home_team_name: str
    away_team_name: str
    match_date: Optional[date] = None
    match_time: Optional[time] = None
    location: Optional[str] = None
    round_number: Optional[int] = None
    round_name: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1)


class AIExtractedPhase(BaseModel):
    """Fase extraída pelo Gemini."""
    name: str
    phase_type: str
    order_index: int = 0
    teams: List[AIExtractedTeam] = []
    matches: List[AIExtractedMatch] = []
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1)


class AIExtractedCompetition(BaseModel):
    """
    Dados completos extraídos pelo Gemini de um PDF de regulamento.
    Este é o formato retornado pela IA para validação do usuário.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Copa Estadual Sub-17 Masculino 2025",
                "season": "2025",
                "modality": "masculino",
                "competition_type": "grupos_mata_mata",
                "format_details": {
                    "num_grupos": 4,
                    "classificados_por_grupo": 2
                },
                "tiebreaker_criteria": ["pontos", "saldo_gols", "gols_pro"],
                "points_per_win": 2,
                "phases": [],
                "teams": [],
                "matches": [],
                "overall_confidence_score": 0.85
            }
        }
    )

    name: str
    season: Optional[str] = None
    modality: Optional[str] = None
    competition_type: Optional[str] = None
    format_details: Optional[Dict[str, Any]] = None
    tiebreaker_criteria: Optional[List[str]] = None
    points_per_win: Optional[int] = None
    regulation_notes: Optional[str] = None
    
    phases: List[AIExtractedPhase] = []
    teams: List[AIExtractedTeam] = []
    matches: List[AIExtractedMatch] = []
    
    overall_confidence_score: Optional[float] = Field(default=None, ge=0, le=1)


class AIParseRequest(BaseModel):
    """Request para parse de PDF via Gemini."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pdf_base64": "JVBERi0xLjQK...",
                "our_team_name": "Clube Atlético Example",
                "hints": {
                    "expected_teams_count": 16,
                    "expected_format": "grupos_mata_mata"
                }
            }
        }
    )

    pdf_base64: str = Field(
        ...,
        description="Conteúdo do PDF em base64",
    )
    our_team_name: Optional[str] = Field(
        default=None,
        description="Nome da nossa equipe para identificar nossos jogos",
    )
    hints: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Dicas para ajudar a IA (número de equipes, formato esperado, etc.)",
    )


class AIParseResponse(BaseModel):
    """Response do parse de PDF via Gemini."""

    success: bool
    extracted_data: Optional[AIExtractedCompetition] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None


class AIValidateAndSaveRequest(BaseModel):
    """Request para validar e salvar dados extraídos pela IA."""

    extracted_data: AIExtractedCompetition
    team_id: Optional[UUID] = Field(
        default=None,
        description="ID da nossa equipe que participa",
    )
    auto_link_teams: bool = Field(
        default=True,
        description="Tentar vincular equipes automaticamente via fuzzy search",
    )


# =============================================================================
# RESPONSE WRAPPERS
# =============================================================================

class CompetitionV2WithRelations(CompetitionV2Response):
    """Competition V2 com relacionamentos expandidos."""

    phases: List[CompetitionPhaseResponse] = []
    opponent_teams: List[CompetitionOpponentTeamResponse] = []
    matches_count: Optional[int] = None
    our_matches_count: Optional[int] = None


class CompetitionV2PaginatedResponse(BaseModel):
    """Resposta paginada para competições V2."""

    items: List[CompetitionV2Response]
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)
