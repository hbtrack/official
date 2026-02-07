"""
Schemas Pydantic para SessionExercise (vínculo training_sessions ↔ exercises).
Suporta drag-and-drop de exercícios para sessões com ordenação, duração e notas.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# ==================== BASE ====================

class SessionExerciseBase(BaseModel):
    """Base schema com campos comuns"""
    model_config = ConfigDict(from_attributes=True)
    
    order_index: int = Field(..., ge=0, description="Ordem do exercício na sessão (0-based)")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Duração planejada em minutos (opcional)")
    notes: Optional[str] = Field(None, max_length=1000, description="Notas específicas desta instância")


# ==================== CREATE ====================

class SessionExerciseCreate(SessionExerciseBase):
    """
    Schema para criar vínculo exercise → session.
    Usado ao arrastar exercício do banco para a sessão.
    """
    exercise_id: UUID = Field(..., description="UUID do exercício a adicionar")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "exercise_id": "550e8400-e29b-41d4-a716-446655440000",
                "order_index": 0,
                "duration_minutes": 15,
                "notes": "3 séries de 10 repetições com descanso de 1min"
            }
        }
    )


class SessionExerciseBulkCreate(BaseModel):
    """
    Schema para adicionar múltiplos exercícios de uma vez.
    Útil para drag-and-drop de múltiplos itens selecionados.
    """
    exercises: list[SessionExerciseCreate] = Field(..., min_length=1, max_length=50)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "exercises": [
                    {
                        "exercise_id": "550e8400-e29b-41d4-a716-446655440000",
                        "order_index": 0,
                        "duration_minutes": 15,
                        "notes": "Aquecimento"
                    },
                    {
                        "exercise_id": "550e8400-e29b-41d4-a716-446655440001",
                        "order_index": 1,
                        "duration_minutes": 30,
                        "notes": "Parte principal"
                    }
                ]
            }
        }
    )


# ==================== UPDATE ====================

class SessionExerciseUpdate(BaseModel):
    """
    Schema para atualizar metadados de um exercício já adicionado.
    Permite editar apenas order_index, duration_minutes e notes.
    """
    order_index: Optional[int] = Field(None, ge=0)
    duration_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "duration_minutes": 20,
                "notes": "Aumentado para 20min devido à baixa intensidade"
            }
        }
    )


class SessionExerciseReorderItem(BaseModel):
    """Item individual para reordenação"""
    id: UUID = Field(..., description="UUID do session_exercise")
    order_index: int = Field(..., ge=0, description="Nova posição na ordenação")


class SessionExerciseReorder(BaseModel):
    """
    Schema para reordenar múltiplos exercícios de uma vez.
    Usado após drag-and-drop de reordenação.
    """
    reorders: list[SessionExerciseReorderItem] = Field(..., min_length=1)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reorders": [
                    {"id": "550e8400-e29b-41d4-a716-446655440000", "order_index": 2},
                    {"id": "550e8400-e29b-41d4-a716-446655440001", "order_index": 0},
                    {"id": "550e8400-e29b-41d4-a716-446655440002", "order_index": 1}
                ]
            }
        }
    )


# ==================== RESPONSE ====================

class ExerciseNested(BaseModel):
    """Dados aninhados do exercício para response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    media_url: Optional[str] = None
    tag_ids: Optional[list[UUID]] = None


class SessionExerciseResponse(SessionExerciseBase):
    """
    Schema de resposta completo com dados do exercício aninhados.
    Inclui timestamps e dados do exercício relacionado.
    """
    id: UUID
    session_id: UUID
    exercise_id: UUID
    exercise: ExerciseNested = Field(..., description="Dados completos do exercício")
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "session_id": "660e8400-e29b-41d4-a716-446655440000",
                "exercise_id": "770e8400-e29b-41d4-a716-446655440000",
                "order_index": 0,
                "duration_minutes": 15,
                "notes": "Aquecimento com ênfase em mobilidade",
                "exercise": {
                    "id": "770e8400-e29b-41d4-a716-446655440000",
                    "name": "Aquecimento Dinâmico",
                    "description": "Sequência de movimentos para preparação corporal",
                    "category": "Físico",
                    "media_url": "https://youtube.com/watch?v=abc123",
                    "tag_ids": ["880e8400-e29b-41d4-a716-446655440000"]
                },
                "created_at": "2026-01-17T10:00:00Z",
                "updated_at": "2026-01-17T10:00:00Z"
            }
        }
    )


class SessionExerciseListResponse(BaseModel):
    """Response para listagem de exercícios de uma sessão"""
    session_id: UUID
    total_exercises: int = Field(..., ge=0, description="Total de exercícios na sessão")
    total_duration_minutes: Optional[int] = Field(None, ge=0, description="Soma das durações planejadas")
    exercises: list[SessionExerciseResponse] = Field(..., description="Lista ordenada por order_index")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "660e8400-e29b-41d4-a716-446655440000",
                "total_exercises": 3,
                "total_duration_minutes": 60,
                "exercises": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "session_id": "660e8400-e29b-41d4-a716-446655440000",
                        "exercise_id": "770e8400-e29b-41d4-a716-446655440000",
                        "order_index": 0,
                        "duration_minutes": 15,
                        "notes": "Aquecimento",
                        "exercise": {
                            "id": "770e8400-e29b-41d4-a716-446655440000",
                            "name": "Aquecimento Dinâmico",
                            "description": "Mobilidade articular",
                            "category": "Físico",
                            "media_url": None,
                            "tag_ids": []
                        },
                        "created_at": "2026-01-17T10:00:00Z",
                        "updated_at": "2026-01-17T10:00:00Z"
                    }
                ]
            }
        }
    )
