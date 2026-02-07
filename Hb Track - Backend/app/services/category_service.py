"""
Service: Category (REGRAS.md RDB11)

Camada de lógica de negócio

Referências RAG:
- R14: Categorias globais definidas por idade máxima (max_age)
- RDB11: Categorias apenas com max_age (sem min_age)
- RD2: Categoria natural derivada pela idade
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import date

from app.models.category import Category
from app.schemas.categories import CategoryCreate, CategoryUpdate
from app.schemas.error import ErrorResponse, ErrorCode, ErrorDetail
from fastapi import HTTPException, status


class CategoryService:
    """Service para operações de Category"""

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Category]:
        """
        Lista todas as categorias

        Args:
            db: Sessão do banco
            skip: Offset de paginação
            limit: Limite de resultados

        Returns:
            Lista de Category ordenada por max_age

        Referências RAG:
            - R14: Categorias globais
            - RDB11: Ordenação por max_age ASC
        """
        stmt = select(Category).order_by(Category.max_age.asc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def count_all(db: AsyncSession) -> int:
        """Conta todas as categorias"""
        stmt = select(func.count()).select_from(Category)
        result = await db.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: int) -> Category:
        """
        Busca categoria por ID

        Args:
            db: Sessão do banco
            category_id: ID da categoria (int)

        Returns:
            Category

        Raises:
            HTTPException 404: Se categoria não encontrada
        """
        stmt = select(Category).filter(Category.id == category_id)
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error_code=ErrorCode.RESOURCE_NOT_FOUND,
                    message=f"Categoria {category_id} não encontrada",
                    request_id="",
                    details=ErrorDetail(field="category_id")
                ).model_dump()
            )

        return category

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Category]:
        """Busca categoria por nome"""
        stmt = select(Category).filter(Category.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, category_data: CategoryCreate) -> Category:
        """
        Cria nova categoria

        Args:
            db: Sessão do banco
            category_data: Dados da categoria

        Returns:
            Category criada

        Raises:
            HTTPException 409: Se nome já existe

        Referências RAG:
            - R14: Categorias globais
            - RDB11: Apenas max_age (sem min_age)
        """
        # Verificar se nome já existe
        existing = await CategoryService.get_by_name(db, category_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error_code=ErrorCode.VALIDATION_ERROR,
                    message=f"Categoria com nome '{category_data.name}' já existe",
                    request_id="",
                    details=ErrorDetail(field="name", existing_id=str(existing.id))
                ).model_dump()
            )

        category = Category(**category_data.model_dump())
        db.add(category)
        await db.flush()

        return category

    @staticmethod
    async def update(db: AsyncSession, category_id: int, category_data: CategoryUpdate) -> Category:
        """
        Atualiza categoria

        Args:
            db: Sessão do banco
            category_id: ID da categoria
            category_data: Dados para atualizar

        Returns:
            Category atualizada
        """
        category = await CategoryService.get_by_id(db, category_id)

        # Verificar nome duplicado se está sendo alterado
        if category_data.name and category_data.name != category.name:
            existing = await CategoryService.get_by_name(db, category_data.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=ErrorResponse(
                        error_code=ErrorCode.VALIDATION_ERROR,
                        message=f"Categoria com nome '{category_data.name}' já existe",
                        request_id="",
                        details=ErrorDetail(field="name", existing_id=str(existing.id))
                    ).model_dump()
                )

        # Atualizar apenas campos fornecidos
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        await db.flush()
        return category

    @staticmethod
    async def get_category_for_age(db: AsyncSession, birth_date: date, reference_date: date) -> Optional[Category]:
        """
        Retorna a categoria apropriada para uma idade

        Conforme REGRAS.md RD2:
        SELECT id, name FROM categories 
        WHERE idade <= max_age AND is_active = true 
        ORDER BY max_age ASC LIMIT 1

        Args:
            db: Sessão do banco
            birth_date: Data de nascimento
            reference_date: Data de referência (ex: ano da temporada)

        Returns:
            Category apropriada ou None

        Referências RAG:
            - RD1: Idade esportiva = ano_temporada - ano_nascimento
            - RD2: Categoria natural baseada em max_age
        """
        # Calcular idade conforme RD1: ano_temporada - ano_nascimento
        age = reference_date.year - birth_date.year

        # Buscar categoria conforme RD2: idade <= max_age ORDER BY max_age ASC LIMIT 1
        stmt = select(Category).filter(
            Category.max_age >= age,
            Category.is_active == True
        ).order_by(Category.max_age.asc())
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()

        return category

    @staticmethod
    async def validate_athlete_category(
        db: AsyncSession, 
        athlete_birth_date: date, 
        category_id: int, 
        season_year: int
    ) -> bool:
        """
        Valida se atleta pode atuar na categoria

        Conforme REGRAS.md R15:
        Atleta pode atuar na sua categoria natural ou em categorias acima (superior),
        nunca em categorias abaixo (inferior).

        Args:
            db: Sessão do banco
            athlete_birth_date: Data de nascimento do atleta
            category_id: ID da categoria desejada
            season_year: Ano da temporada (seasons.year)

        Returns:
            True se pode atuar, False caso contrário

        Referências RAG:
            - R15: Regra etária obrigatória
            - RD1/RD2: Idade e categoria natural
        """
        # Calcular idade conforme RD1: ano_temporada - ano_nascimento
        age = season_year - athlete_birth_date.year

        # Buscar categoria desejada
        category = await CategoryService.get_by_id(db, category_id)

        # Atleta pode atuar se sua idade <= max_age da categoria (R15)
        # Ou seja, pode jogar na sua categoria ou em categorias superiores (max_age maior)
        return age <= category.max_age
