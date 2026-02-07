"""
Schemas Pydantic para Match Events (Eventos de Partida / Estatísticas).

Regras RAG aplicadas:
- RD1-RD91: Tipos de eventos estatísticos do handball
- R23/R24: Correção de eventos com histórico
- RDB13: match_events com tracking de correções
- RF15: Eventos só editáveis enquanto match.status != finalizado
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.match_event import EventType


class MatchEventBase(BaseModel):
    """
    Campos base para evento de partida.
    Ref: RD1-RD91 - Eventos estatísticos do handball
    """
    event_type: EventType = Field(..., description="Tipo do evento")
    minute: int = Field(..., ge=0, le=60, description="Minuto do evento (0-60)")
    period: int = Field(..., ge=1, le=2, description="Período (1 ou 2)")
    x_position: Optional[float] = Field(None, ge=0, le=100, description="Posição X no campo (0-100)")
    y_position: Optional[float] = Field(None, ge=0, le=100, description="Posição Y no campo (0-100)")
    notes: Optional[str] = Field(None, max_length=500, description="Observações do evento")

    @field_validator("minute")
    @classmethod
    def validate_minute(cls, v: int, info) -> int:
        """Valida minuto conforme período."""
        # Cada período tem 30 minutos no handball
        if v > 30:
            # Permitir até 35 para acréscimos
            if v > 35:
                raise ValueError("Minuto não pode exceder 35 (incluindo acréscimos)")
        return v


class MatchEventCreate(MatchEventBase):
    """
    Schema para criação de evento.
    Ref: RD4 - Atleta deve estar no roster do jogo
    """
    match_id: UUID = Field(..., description="ID da partida")
    athlete_id: UUID = Field(..., description="ID do atleta (deve estar no roster)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "match_id": "123e4567-e89b-12d3-a456-426614174000",
                "athlete_id": "123e4567-e89b-12d3-a456-426614174001",
                "event_type": "goal",
                "minute": 15,
                "period": 1,
                "x_position": 50.0,
                "y_position": 80.0,
                "notes": "Gol de pivô"
            }
        }
    )


class MatchEventUpdate(BaseModel):
    """
    Schema para atualização de evento.
    Ref: R23/R24 - Correções geram histórico
    """
    event_type: Optional[EventType] = None
    minute: Optional[int] = Field(None, ge=0, le=60)
    period: Optional[int] = Field(None, ge=1, le=2)
    x_position: Optional[float] = Field(None, ge=0, le=100)
    y_position: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "assist",
                "notes": "Corrigido: era assistência, não gol"
            }
        }
    )


class MatchEventCorrection(BaseModel):
    """
    Schema para correção de evento com justificativa.
    Ref: R23/R24 - Correção obrigatória com motivo após X minutos
    """
    event_type: Optional[EventType] = None
    minute: Optional[int] = Field(None, ge=0, le=60)
    period: Optional[int] = Field(None, ge=1, le=2)
    correction_note: str = Field(..., min_length=10, max_length=500, description="Justificativa da correção (obrigatória)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "own_goal",
                "correction_note": "Revisão de vídeo mostrou que foi gol contra, não gol normal"
            }
        }
    )


class MatchEventResponse(BaseModel):
    """
    Schema de resposta para evento.
    Ref: RD1-RD91, R23/R24
    """
    id: UUID
    match_id: UUID
    athlete_id: UUID
    event_type: EventType
    minute: int
    period: int
    x_position: Optional[float]
    y_position: Optional[float]
    notes: Optional[str]
    
    # Campos de correção (R23/R24)
    corrected_at: Optional[datetime] = Field(None, description="Data/hora da última correção")
    correction_note: Optional[str] = Field(None, description="Motivo da correção")
    previous_value: Optional[str] = Field(None, description="JSON com valores anteriores à correção")
    
    # Soft delete
    deleted_at: Optional[datetime] = None
    deleted_reason: Optional[str] = None
    
    # Auditoria
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MatchEventSummary(BaseModel):
    """
    Schema resumido para listagens.
    """
    id: UUID
    athlete_id: UUID
    event_type: EventType
    minute: int
    period: int
    
    model_config = ConfigDict(from_attributes=True)


class MatchEventList(BaseModel):
    """
    Schema para listagem de eventos.
    Ref: RDB14 - Paginação padrão
    """
    items: list[MatchEventSummary]
    total: int
    page: int
    size: int
    pages: int


class AthleteMatchStats(BaseModel):
    """
    Schema para estatísticas agregadas de um atleta em uma partida.
    Ref: RD1-RD91 - Estatísticas consolidadas
    """
    athlete_id: UUID
    match_id: UUID
    
    # Gols
    goals: int = 0
    goals_7m: int = 0
    own_goals: int = 0
    
    # Finalizações
    shots: int = 0
    shots_on_target: int = 0
    
    # Goleiro
    saves: int = 0
    goals_conceded: int = 0
    
    # Assistências
    assists: int = 0
    
    # Cartões
    yellow_cards: int = 0
    red_cards: int = 0
    two_minutes: int = 0
    
    # Erros
    turnovers: int = 0
    technical_fouls: int = 0
    
    # Tempo
    minutes_played: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class TeamMatchStats(BaseModel):
    """
    Schema para estatísticas agregadas do time em uma partida.
    Ref: RD1-RD91
    """
    match_id: UUID
    team_id: UUID
    
    total_goals: int = 0
    total_shots: int = 0
    shot_accuracy: float = 0.0  # goals / shots * 100
    total_saves: int = 0
    total_turnovers: int = 0
    total_assists: int = 0
    
    # Por atleta
    athlete_stats: list[AthleteMatchStats] = []
    
    model_config = ConfigDict(from_attributes=True)
