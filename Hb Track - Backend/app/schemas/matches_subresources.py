"""
Pydantic schemas for Match Subresources (match_teams, match_roster, match_events).

Regras de negócio documentadas:
- R25/R26: Permissões por papel e escopo
- R29/R33: Exclusão lógica obrigatória; histórico com rastro
- R42: Modo somente leitura sem vínculo ativo
- RDB13/RF15: Jogo finalizado é somente leitura; reabertura auditável
- RF5.2/R37: Temporada interrompida bloqueia criação/edição de novos eventos
- RD18: Limite máximo de 16 atletas relacionadas por jogo
- RD4/RD7: Participação oficial exige convocação/lista
- RD13/RD22: Regras de goleira e goleiro-linha

Campo event_type (MatchEvent):
- Texto livre na V1
- Exemplos: goal, 7m_shot, 2min_exclusion, red_card, assist, blocked_shot,
  goalkeeper_save, turnover, interception, timeout, substitution
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# MATCH TEAMS SCHEMAS
# =============================================================================


class MatchTeamCreate(BaseModel):
    """
    Schema para adicionar equipe ao jogo (POST).

    Campos obrigatórios:
    - team_id: UUID da equipe
    - is_home: boolean (true = mandante, false = visitante)
    - is_our_team: boolean (true = nossa equipe)

    Constraints (banco):
    - UNIQUE (match_id, team_id)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "team_id": "cc0e8400-e29b-41d4-a716-446655440002",
                "is_home": True,
                "is_our_team": True,
            }
        }
    )

    team_id: UUID = Field(
        ...,
        description="ID da equipe (obrigatório)",
    )
    is_home: bool = Field(
        ...,
        description="True = mandante, False = visitante (obrigatório)",
    )
    is_our_team: bool = Field(
        ...,
        description="True = nossa equipe (obrigatório)",
    )


class MatchTeamUpdate(BaseModel):
    """
    Schema para atualizar equipe do jogo (PATCH).

    Campos editáveis:
    - is_home: Lado da equipe (pode trocar mandante/visitante)
    - is_our_team: Se é nossa equipe

    Campos NÃO editáveis:
    - team_id (imutável)
    - match_id (imutável)

    Regras: RDB13/RF15 - Bloquear se jogo finalizado
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_home": True,
                "is_our_team": True,
            }
        }
    )

    is_home: Optional[bool] = Field(
        default=None,
        description="True = mandante, False = visitante",
    )
    is_our_team: Optional[bool] = Field(
        default=None,
        description="True = nossa equipe",
    )


class MatchTeam(BaseModel):
    """
    Schema de resposta completo para match_team.
    Campos conforme banco: id, match_id, team_id, is_home, is_our_team
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "aa0e8400-e29b-41d4-a716-446655440001",
                "match_id": "bb0e8400-e29b-41d4-a716-446655440000",
                "team_id": "cc0e8400-e29b-41d4-a716-446655440002",
                "is_home": True,
                "is_our_team": True,
            }
        }
    )

    id: UUID = Field(
        ...,
        description="ID único do match_team",
    )
    match_id: UUID = Field(
        ...,
        description="ID do jogo",
    )
    team_id: UUID = Field(
        ...,
        description="ID da equipe",
    )
    is_home: bool = Field(
        ...,
        description="True = mandante, False = visitante",
    )
    is_our_team: bool = Field(
        ...,
        description="True = nossa equipe",
    )


# =============================================================================
# MATCH ROSTER SCHEMAS
# =============================================================================


class MatchRosterCreate(BaseModel):
    """
    Schema para adicionar atleta ao roster (POST).

    Campos obrigatórios (banco):
    - athlete_id: UUID da atleta
    - jersey_number: smallint > 0
    - is_goalkeeper: boolean
    - is_available: boolean

    Campos opcionais:
    - is_starting: boolean (nullable)
    - notes: text

    Constraints:
    - UNIQUE (match_id, athlete_id)
    - RD18: Máximo 16 atletas por jogo

    Regras:
    - RD4/RD7: Participação exige inscrição na temporada
    - RDB13: Bloquear se jogo finalizado
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "athlete_id": "ee0e8400-e29b-41d4-a716-446655440005",
                "jersey_number": 10,
                "is_goalkeeper": False,
                "is_available": True,
                "is_starting": True,
                "notes": None,
            }
        }
    )

    athlete_id: UUID = Field(
        ...,
        description="ID da atleta (obrigatório)",
    )
    jersey_number: int = Field(
        ...,
        gt=0,
        le=99,
        description="Número da camisa (obrigatório, >0)",
    )
    is_goalkeeper: bool = Field(
        ...,
        description="Indica se é goleira (obrigatório)",
    )
    is_available: bool = Field(
        default=True,
        description="Indica se está disponível para jogar (obrigatório, default true)",
    )
    is_starting: Optional[bool] = Field(
        default=None,
        description="Indica se é titular (opcional)",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Observações (opcional)",
    )


class MatchRosterUpdate(BaseModel):
    """
    Schema para atualizar roster entry (PATCH).

    Campos editáveis:
    - jersey_number: número da camisa
    - is_starting: se é titular
    - is_goalkeeper: se é goleira
    - is_available: se está disponível
    - notes: observações

    Campos NÃO editáveis:
    - athlete_id (imutável)
    - match_id (imutável)
    - team_id (imutável)

    Regras: RDB13/RF15 - Bloquear se jogo finalizado
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "jersey_number": 7,
                "is_starting": False,
                "is_available": True,
            }
        }
    )

    jersey_number: Optional[int] = Field(
        default=None,
        gt=0,
        le=99,
        description="Número da camisa (>0)",
    )
    is_starting: Optional[bool] = Field(
        default=None,
        description="Indica se é titular",
    )
    is_goalkeeper: Optional[bool] = Field(
        default=None,
        description="Indica se é goleira",
    )
    is_available: Optional[bool] = Field(
        default=None,
        description="Indica se está disponível",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Observações",
    )


class MatchRoster(BaseModel):
    """
    Schema de resposta completo para match_roster.
    Campos conforme banco: id, match_id, team_id, athlete_id, jersey_number,
                          is_starting, is_goalkeeper, is_available, notes

    Regras relacionadas:
    - RD4/RD7: Participação oficial exige inscrição na temporada
    - RD18: Limite máximo de 16 atletas por jogo
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "dd0e8400-e29b-41d4-a716-446655440001",
                "match_id": "bb0e8400-e29b-41d4-a716-446655440000",
                "team_id": "cc0e8400-e29b-41d4-a716-446655440002",
                "athlete_id": "ee0e8400-e29b-41d4-a716-446655440005",
                "jersey_number": 10,
                "is_starting": True,
                "is_goalkeeper": False,
                "is_available": True,
                "notes": None,
            }
        }
    )

    id: UUID = Field(
        ...,
        description="ID único do match_roster",
    )
    match_id: UUID = Field(
        ...,
        description="ID do jogo",
    )
    team_id: UUID = Field(
        ...,
        description="ID da equipe",
    )
    athlete_id: UUID = Field(
        ...,
        description="ID da atleta",
    )
    jersey_number: int = Field(
        ...,
        description="Número da camisa",
    )
    is_starting: Optional[bool] = Field(
        default=None,
        description="Indica se é titular",
    )
    is_goalkeeper: bool = Field(
        ...,
        description="Indica se é goleira",
    )
    is_available: bool = Field(
        ...,
        description="Indica se está disponível",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Observações",
    )


# =============================================================================
# MATCH EVENTS SCHEMAS
# =============================================================================


class MatchEventCreate(BaseModel):
    """
    Schema para criar evento do jogo (POST).

    Campos obrigatórios:
    - period: Período do jogo
    - second_in_match: Segundo no jogo
    - event_type: Tipo do evento (TEXT livre)

    Campo event_type (TEXT livre na V1):
    Exemplos: goal, 7m_shot, 2min_exclusion, red_card, assist, blocked_shot,
    goalkeeper_save, turnover, interception, timeout, substitution

    Regras:
    - RDB13: Bloquear se jogo finalizado
    - RF5.2/R37: Temporada interrompida bloqueia criação
    - RD13/RD22: Validar eventos incompatíveis com goleira/goleiro-linha
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "team_id": "cc0e8400-e29b-41d4-a716-446655440002",
                "athlete_id": "ee0e8400-e29b-41d4-a716-446655440005",
                "period": 1,
                "second_in_match": 300,
                "event_type": "goal",
                "points": 1,
                "notes": "Gol de contra-ataque",
            }
        }
    )

    team_id: Optional[UUID] = Field(
        default=None,
        description="ID da equipe (opcional)",
    )
    athlete_id: Optional[UUID] = Field(
        default=None,
        description="ID da atleta (opcional)",
    )
    period: int = Field(
        ...,
        ge=1,
        description="Período do jogo (1, 2, ou prorrogação) - obrigatório",
    )
    second_in_match: int = Field(
        ...,
        ge=0,
        description="Segundo no jogo em que ocorreu o evento - obrigatório",
    )
    event_type: str = Field(
        ...,
        min_length=1,
        description="Tipo do evento (TEXT livre) - obrigatório. Ex: goal, 7m_shot, 2min_exclusion",
    )
    points: Optional[int] = Field(
        default=1,
        description="Pontos associados ao evento (opcional, default 1)",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Observações adicionais (opcional)",
    )


class MatchEventUpdate(BaseModel):
    """
    Schema para atualizar evento do jogo (PATCH).

    Campos editáveis:
    - period: Período do jogo
    - second_in_match: Segundo no jogo
    - event_type: Tipo do evento
    - points: Pontos
    - notes: Observações

    Campos NÃO editáveis:
    - match_id (imutável)
    - team_id (imutável)
    - athlete_id (imutável)

    Regras: RDB13/RF15 - Bloquear se jogo finalizado
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "7m_shot",
                "points": 1,
                "notes": "Convertido",
            }
        }
    )

    period: Optional[int] = Field(
        default=None,
        ge=1,
        description="Período do jogo",
    )
    second_in_match: Optional[int] = Field(
        default=None,
        ge=0,
        description="Segundo no jogo",
    )
    event_type: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Tipo do evento",
    )
    points: Optional[int] = Field(
        default=None,
        description="Pontos",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Observações",
    )


class MatchEvent(BaseModel):
    """
    Schema de resposta completo para match_event.

    Campo event_type (TEXT livre na V1):
    Exemplos: goal, 7m_shot, 2min_exclusion, red_card, assist, blocked_shot,
    goalkeeper_save, turnover, interception, timeout, substitution

    Nota: match_events não possui updated_at no schema atual (apenas created_at).
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "ff0e8400-e29b-41d4-a716-446655440001",
                "match_id": "bb0e8400-e29b-41d4-a716-446655440000",
                "team_id": "cc0e8400-e29b-41d4-a716-446655440002",
                "athlete_id": "ee0e8400-e29b-41d4-a716-446655440005",
                "period": 1,
                "second_in_match": 300,
                "event_type": "goal",
                "points": 1,
                "notes": "Gol de contra-ataque",
                "created_at": "2024-03-15T14:05:00Z",
            }
        }
    )

    id: UUID = Field(
        ...,
        description="ID único do evento",
    )
    match_id: UUID = Field(
        ...,
        description="ID do jogo",
    )
    team_id: Optional[UUID] = Field(
        default=None,
        description="ID da equipe (opcional)",
    )
    athlete_id: Optional[UUID] = Field(
        default=None,
        description="ID da atleta (opcional)",
    )
    period: int = Field(
        ...,
        description="Período do jogo",
    )
    second_in_match: int = Field(
        ...,
        description="Segundo no jogo em que ocorreu o evento",
    )
    event_type: str = Field(
        ...,
        description="Tipo do evento",
    )
    points: int = Field(
        ...,
        description="Pontos associados ao evento",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Observações adicionais",
    )
    created_at: datetime = Field(
        ...,
        description="Data/hora de criação",
    )


class MatchEventPaginatedResponse(BaseModel):
    """
    Resposta paginada para listagem de eventos do jogo.

    Envelope padrão: {items, page, limit, total}
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "ff0e8400-e29b-41d4-a716-446655440001",
                        "match_id": "bb0e8400-e29b-41d4-a716-446655440000",
                        "team_id": "cc0e8400-e29b-41d4-a716-446655440002",
                        "athlete_id": "ee0e8400-e29b-41d4-a716-446655440005",
                        "period": 1,
                        "second_in_match": 300,
                        "event_type": "goal",
                        "points": 1,
                        "notes": "Gol de contra-ataque",
                        "created_at": "2024-03-15T14:05:00Z",
                    }
                ],
                "page": 1,
                "limit": 50,
                "total": 45,
            }
        }
    )

    items: list[MatchEvent] = Field(
        ...,
        description="Lista de eventos na página atual",
    )
    page: int = Field(
        ...,
        ge=1,
        description="Página atual",
    )
    limit: int = Field(
        ...,
        ge=1,
        le=100,
        description="Itens por página",
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total de itens (todas as páginas)",
    )
