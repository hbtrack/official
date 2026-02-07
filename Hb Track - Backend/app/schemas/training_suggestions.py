"""Schemas para Training Suggestions"""

from typing import List, Optional, Dict, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class SuggestionEvidence(BaseModel):
    """Evidência/base de uma sugestão."""
    avg_deviation: float
    direction: Literal["above", "below"]
    consistency: float = Field(..., ge=0, le=1)
    occurrences: int
    total_analyzed: int


class FocusSuggestion(BaseModel):
    """Sugestão de ajuste de foco."""
    focus_field: str
    focus_label: str
    suggested_adjustment: int  # Positivo ou negativo
    reason: str
    evidence: SuggestionEvidence
    type: Literal["focus_adjustment"]
    confidence: Literal["high", "medium", "low"]


class SuggestionContext(BaseModel):
    """Contexto da análise de sugestões."""
    period_analyzed: str
    microcycle_type: Optional[str] = None


class TrainingSuggestionsResponse(BaseModel):
    """Resposta de sugestões para novo microciclo."""
    has_suggestions: bool
    microcycles_analyzed: int
    suggestions: Optional[List[FocusSuggestion]] = None
    context: Optional[SuggestionContext] = None
    reason: Optional[str] = None  # Se não houver sugestões
    message: Optional[str] = None  # Mensagem explicativa


class ApplySuggestionRequest(BaseModel):
    """Request para aplicar uma sugestão."""
    microcycle_id: UUID
    suggestion: FocusSuggestion
