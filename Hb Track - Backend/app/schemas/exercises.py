from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ExerciseBase(BaseModel):
    """Campos comuns de exercício."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    tag_ids: List[UUID] = Field(default_factory=list)
    category: Optional[str] = Field(None, max_length=100)
    media_url: Optional[str] = Field(None, max_length=500)


class ExerciseCreate(ExerciseBase):
    """
    Schema para criação de exercício.

    organization_id e created_by_user_id são obtidos do contexto.
    """
    pass


class ExerciseUpdate(BaseModel):
    """
    Schema para atualização de exercício.

    Todos os campos são opcionais.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    tag_ids: Optional[List[UUID]] = None
    category: Optional[str] = Field(None, max_length=100)
    media_url: Optional[str] = Field(None, max_length=500)


class ExerciseResponse(ExerciseBase):
    """Schema de resposta com todos os campos do exercício."""
    id: UUID
    organization_id: UUID
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (substitui orm_mode)


class ExerciseListResponse(BaseModel):
    """Schema de resposta paginada para listagem de exercícios."""
    exercises: List[ExerciseResponse]
    total: int
    page: int
    per_page: int


class ExerciseACLResponse(BaseModel):
    """Schema de resposta para entrada de ACL de exercício."""
    id: UUID
    exercise_id: UUID
    user_id: UUID
    granted_by_user_id: UUID
    granted_at: datetime

    class Config:
        from_attributes = True


class ExerciseACLGrantRequest(BaseModel):
    """Schema de request para conceder acesso (POST /exercises/{id}/acl)."""
    target_user_id: UUID


class VisibilityUpdateRequest(BaseModel):
    """Schema de request para alterar visibilidade (PATCH /exercises/{id}/visibility)."""
    visibility_mode: str = Field(..., pattern="^(org_wide|restricted)$")
