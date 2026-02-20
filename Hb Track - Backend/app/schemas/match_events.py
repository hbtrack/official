"""
Schemas Pydantic para Match Events (Eventos de Partida / Estatísticas).

Schemas canônicos alinhados com o SSOT (schema.sql):
- Tabela match_events com campos: period_number, game_time_seconds, x_coord, y_coord, etc.
- Tabela event_types com códigos: goal, shot, seven_meter, goalkeeper_save, etc.

AR_003: Substituição de enums inválidos por canônicos.
"""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CanonicalEventType(str, Enum):
    """
    Tipos de evento canônicos conforme tabela event_types do banco.
    NÃO incluir: goal_7m, own_goal, shot_on_target, assist, technical_foul (inválidos).
    """
    goal = 'goal'
    shot = 'shot'
    seven_meter = 'seven_meter'
    goalkeeper_save = 'goalkeeper_save'
    turnover = 'turnover'
    foul = 'foul'
    exclusion_2min = 'exclusion_2min'
    yellow_card = 'yellow_card'
    red_card = 'red_card'
    substitution = 'substitution'
    timeout = 'timeout'


# Alias para compatibilidade com imports existentes
EventType = CanonicalEventType


# ============================================================================
# SCOUT EVENT SCHEMAS (Canônicos - alinhados com DB)
# ============================================================================

class ScoutEventCreate(BaseModel):
    """
    Schema para criação de evento de scout.
    Campos alinhados com a tabela match_events do banco de dados.
    
    Validações especiais:
    - event_type='goalkeeper_save' exige related_event_id obrigatório
    """
    # Campos obrigatórios
    team_id: UUID = Field(..., description="ID do time que executou o evento")
    period_number: int = Field(..., ge=1, description="Número do período (1, 2, etc.)")
    game_time_seconds: int = Field(..., ge=0, description="Tempo de jogo em segundos")
    phase_of_play: str = Field(..., max_length=32, description="FK para phases_of_play.code")
    advantage_state: str = Field(..., max_length=32, description="FK para advantage_states.code")
    score_our: int = Field(..., ge=0, description="Placar do nosso time")
    score_opponent: int = Field(..., ge=0, description="Placar do adversário")
    event_type: CanonicalEventType = Field(..., description="Tipo do evento (canônico)")
    outcome: str = Field(..., max_length=64, description="Resultado do evento")
    is_shot: bool = Field(..., description="Se o evento é uma finalização")
    is_goal: bool = Field(..., description="Se o evento resultou em gol")
    source: Literal['live', 'video', 'post_game_correction'] = Field(
        ..., description="Fonte do registro"
    )
    
    # Campos opcionais
    athlete_id: Optional[UUID] = Field(None, description="ID do atleta principal")
    assisting_athlete_id: Optional[UUID] = Field(None, description="ID do atleta que deu assistência")
    secondary_athlete_id: Optional[UUID] = Field(None, description="ID do atleta secundário")
    opponent_team_id: Optional[UUID] = Field(None, description="ID do time adversário")
    possession_id: Optional[UUID] = Field(None, description="ID da posse de bola")
    event_subtype: Optional[str] = Field(None, max_length=64, description="FK para event_subtypes.code")
    x_coord: Optional[float] = Field(None, ge=0, le=100, description="Coordenada X (0-100)")
    y_coord: Optional[float] = Field(None, ge=0, le=100, description="Coordenada Y (0-100)")
    related_event_id: Optional[UUID] = Field(None, description="ID do evento relacionado")
    notes: Optional[str] = Field(None, description="Observações do evento")
    
    @model_validator(mode='after')
    def validate_goalkeeper_save_requires_related_event(self):
        """Quando event_type='goalkeeper_save', related_event_id é obrigatório."""
        if self.event_type == CanonicalEventType.goalkeeper_save and self.related_event_id is None:
            raise ValueError(
                "related_event_id é obrigatório quando event_type='goalkeeper_save'. "
                "Uma defesa deve estar vinculada ao evento de finalização original."
            )
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "team_id": "123e4567-e89b-12d3-a456-426614174000",
                "period_number": 1,
                "game_time_seconds": 900,
                "phase_of_play": "attack_positional",
                "advantage_state": "even",
                "score_our": 5,
                "score_opponent": 3,
                "event_type": "goal",
                "outcome": "scored",
                "is_shot": True,
                "is_goal": True,
                "source": "live",
                "athlete_id": "123e4567-e89b-12d3-a456-426614174001",
                "x_coord": 50.0,
                "y_coord": 80.0,
                "notes": "Gol de pivô"
            }
        }
    )


class ScoutEventRead(BaseModel):
    """
    Schema de resposta para evento de scout.
    Inclui todos os campos de ScoutEventCreate mais campos de auditoria.
    """
    # Campos de ScoutEventCreate
    team_id: UUID
    period_number: int
    game_time_seconds: int
    phase_of_play: str
    advantage_state: str
    score_our: int
    score_opponent: int
    event_type: CanonicalEventType
    outcome: str
    is_shot: bool
    is_goal: bool
    source: str
    
    athlete_id: Optional[UUID] = None
    assisting_athlete_id: Optional[UUID] = None
    secondary_athlete_id: Optional[UUID] = None
    opponent_team_id: Optional[UUID] = None
    possession_id: Optional[UUID] = None
    event_subtype: Optional[str] = None
    x_coord: Optional[float] = None
    y_coord: Optional[float] = None
    related_event_id: Optional[UUID] = None
    notes: Optional[str] = None
    
    # Campos adicionais de resposta
    id: UUID
    match_id: UUID
    created_at: datetime
    created_by_user_id: UUID
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# LEGACY SCHEMAS (Compatibilidade - corrigidos)
# ============================================================================

class MatchEventUpdate(BaseModel):
    """
    Schema para atualização de evento.
    Mantido para compatibilidade. Campos corrigidos para o enum canônico.
    """
    event_type: Optional[CanonicalEventType] = None
    period_number: Optional[int] = Field(None, ge=1)
    game_time_seconds: Optional[int] = Field(None, ge=0)
    x_coord: Optional[float] = Field(None, ge=0, le=100)
    y_coord: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = Field(None, max_length=500)
    outcome: Optional[str] = Field(None, max_length=64)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "shot",
                "notes": "Corrigido: era finalização, não gol"
            }
        }
    )


class MatchEventCorrection(BaseModel):
    """
    Schema para correção de evento com justificativa.
    Mantido para compatibilidade. Campos corrigidos para o enum canônico.
    """
    event_type: Optional[CanonicalEventType] = None
    period_number: Optional[int] = Field(None, ge=1)
    game_time_seconds: Optional[int] = Field(None, ge=0)
    correction_note: str = Field(
        ..., min_length=10, max_length=500, 
        description="Justificativa da correção (obrigatória)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "turnover",
                "correction_note": "Revisão de vídeo mostrou que foi erro de passe, não finalização"
            }
        }
    )


class MatchEventSummary(BaseModel):
    """
    Schema resumido para listagens.
    """
    id: UUID
    athlete_id: Optional[UUID]
    event_type: CanonicalEventType
    period_number: int
    game_time_seconds: int
    
    model_config = ConfigDict(from_attributes=True)


class MatchEventList(BaseModel):
    """
    Schema para listagem de eventos com paginação.
    """
    items: list[MatchEventSummary]
    total: int
    page: int
    size: int
    pages: int


class AthleteMatchStats(BaseModel):
    """
    Schema para estatísticas agregadas de um atleta em uma partida.
    Campos corrigidos para usar apenas tipos canônicos.
    """
    athlete_id: UUID
    match_id: UUID
    
    # Gols (goal e seven_meter são tipos canônicos)
    goals: int = 0
    goals_7m: int = 0  # Contagem de gols de 7m (event_type='seven_meter' + is_goal=True)
    
    # Finalizações (shot e seven_meter são tipos canônicos)
    shots: int = 0
    
    # Goleiro (goalkeeper_save é tipo canônico)
    saves: int = 0
    goals_conceded: int = 0
    
    # Cartões (yellow_card e red_card são tipos canônicos)
    yellow_cards: int = 0
    red_cards: int = 0
    two_minutes: int = 0  # exclusion_2min é tipo canônico
    
    # Erros (turnover é tipo canônico)
    turnovers: int = 0
    
    # Tempo
    minutes_played: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class TeamMatchStats(BaseModel):
    """
    Schema para estatísticas agregadas do time em uma partida.
    """
    match_id: UUID
    team_id: UUID
    
    total_goals: int = 0
    total_shots: int = 0
    shot_accuracy: float = 0.0  # goals / shots * 100
    total_saves: int = 0
    total_turnovers: int = 0
    
    # Por atleta
    athlete_stats: list[AthleteMatchStats] = []
    
    model_config = ConfigDict(from_attributes=True)