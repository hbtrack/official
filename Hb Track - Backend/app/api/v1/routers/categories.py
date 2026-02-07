"""
Router: Categories (R15, RDB11)

Referências RAG:
- R15: Categorias globais definidas por idade
- R16: Atleta pode atuar na sua categoria ou acima
- RDB11: min_age <= max_age (CHECK constraint)
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.core.context import ExecutionContext
from app.api.v1.deps.auth import get_current_context, require_role
from app.services.category_service import CategoryService
from app.schemas.categories import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryList
)

router = APIRouter(tags=["Categories"])


@router.get("", response_model=CategoryList)
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Lista todas as categorias

    Endpoint público - catálogo fixo para uso em formulários.

    Referências RAG:
    - R15: Categorias globais
    """
    categories = await CategoryService.get_all(db, skip, limit)
    total = await CategoryService.count_all(db)

    return CategoryList(
        items=[CategoryResponse.model_validate(c) for c in categories],
        total=total
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente", "treinador"]))
):
    """
    Busca categoria por ID

    Permissões: coordenador, dirigente, treinador (R26)

    Referências RAG:
    - R15: Categorias globais
    """
    category = await CategoryService.get_by_id(db, category_id)
    return CategoryResponse.model_validate(category)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """
    Cria nova categoria

    Permissões: coordenador, dirigente (R26)

    Referências RAG:
    - R15: Categorias globais definidas por idade
    - RDB11: Validação min_age <= max_age
    """
    category = await CategoryService.create(db, category_data)
    await db.commit()
    await db.refresh(category)
    return CategoryResponse.model_validate(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "dirigente"]))
):
    """
    Atualiza categoria

    Permissões: coordenador, dirigente (R26)

    Referências RAG:
    - R15: Categorias globais
    - RDB11: Validação min_age <= max_age
    """
    category = await CategoryService.update(db, category_id, category_data)
    await db.commit()
    await db.refresh(category)
    return CategoryResponse.model_validate(category)
