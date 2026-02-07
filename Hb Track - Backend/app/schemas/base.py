"""
Base schemas comuns (FASE 3)
"""
from typing import Optional, Generic, TypeVar, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# === Mixins para herança ===

class TimestampMixin(BaseModel):
    """
    Mixin para campos de timestamp (created_at, updated_at)
    """
    created_at: datetime = Field(..., description="Data de criação (UTC)")
    updated_at: datetime = Field(..., description="Data da última atualização (UTC)")

    model_config = ConfigDict(from_attributes=True)


class SoftDeleteMixin(BaseModel):
    """
    Mixin para soft delete (deleted_at, deleted_reason)
    """
    deleted_at: Optional[datetime] = Field(None, description="Data de exclusão lógica (UTC)")
    deleted_reason: Optional[str] = Field(None, description="Motivo da exclusão (RDB4)")

    model_config = ConfigDict(from_attributes=True)


# === Base Schemas ===

class BaseSchema(BaseModel):
    """
    Schema base para todos os modelos
    """
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {}
        }
    )


class BaseResponseSchema(BaseSchema, TimestampMixin):
    """
    Schema base para respostas da API (inclui timestamps)
    """
    id: UUID = Field(..., description="ID único do recurso (UUID v4)")


class BaseResponseWithSoftDelete(BaseResponseSchema, SoftDeleteMixin):
    """
    Schema base para respostas com soft delete
    """
    pass


# === Paginação ===

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Resposta paginada genérica

    Usage:
        PaginatedResponse[PersonOut](items=[...], total=100, skip=0, limit=10)
    """
    items: list[T] = Field(..., description="Lista de itens da página atual")
    total: int = Field(..., description="Total de itens (sem paginação)")
    skip: int = Field(0, description="Número de itens pulados")
    limit: int = Field(100, description="Limite de itens por página")

    @property
    def has_next(self) -> bool:
        """Verifica se há próxima página"""
        return (self.skip + self.limit) < self.total

    @property
    def has_previous(self) -> bool:
        """Verifica se há página anterior"""
        return self.skip > 0

    @property
    def page_count(self) -> int:
        """Calcula número total de páginas"""
        if self.limit == 0:
            return 0
        return (self.total + self.limit - 1) // self.limit

    @property
    def current_page(self) -> int:
        """Calcula página atual (1-indexed)"""
        if self.limit == 0:
            return 1
        return (self.skip // self.limit) + 1

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 100,
                "skip": 0,
                "limit": 10
            }
        }
    )
