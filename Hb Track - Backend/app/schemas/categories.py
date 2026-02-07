"""
Schemas: Category (REGRAS.md RDB11)

Referências RAG:
- R14: Categorias globais definidas por idade máxima (max_age)
- RDB11: Categorias apenas com max_age (sem min_age)
- RD2: Categoria natural derivada pela idade
"""
from pydantic import BaseModel, Field
from typing import Optional


class CategoryBase(BaseModel):
    """Campos comuns de Category (REGRAS.md RDB11)"""
    name: str = Field(..., min_length=2, max_length=50, description="Nome da categoria (ex: Mirim, Infantil)")
    max_age: int = Field(..., ge=1, le=100, description="Idade máxima para a categoria")
    is_active: bool = Field(True, description="Se a categoria está ativa")


class CategoryCreate(CategoryBase):
    """Schema para criação de Category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema para atualização parcial de Category"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    max_age: Optional[int] = Field(None, ge=1, le=100)
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema de resposta com todos os campos"""
    id: int = Field(..., description="ID da categoria")

    model_config = {"from_attributes": True}


class CategoryList(BaseModel):
    """Lista paginada de categorias"""
    items: list[CategoryResponse]
    total: int
    page: int = 1
    limit: int = 50
