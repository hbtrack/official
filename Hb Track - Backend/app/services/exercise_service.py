from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.exercise_tag import ExerciseTag
from app.models.exercise import Exercise
from app.models.exercise_favorite import ExerciseFavorite
from uuid import UUID
from typing import List, Optional
from datetime import datetime


class ExerciseService:
    """
    Serviço para gerenciamento de exercícios e tags.

    Validações implementadas:
    - Anti-ciclo: Impede que uma tag seja ancestral de si mesma
    - tag_ids: Valida que todos os UUIDs existem e estão ativos
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================================
    # VALIDAÇÕES
    # =========================================================================

    async def _validate_no_cycle(self, tag_id: UUID, new_parent_id: Optional[UUID]) -> None:
        """
        Valida que atribuir new_parent_id a tag_id não cria ciclo.

        Algoritmo: Percorre a árvore de ancestrais de new_parent_id.
        Se encontrar tag_id, haveria ciclo.

        Args:
            tag_id: UUID da tag sendo atualizada
            new_parent_id: UUID do novo parent proposto

        Raises:
            HTTPException 400: Se criaria ciclo
        """
        if new_parent_id is None:
            return  # Mover para raiz nunca cria ciclo

        if tag_id == new_parent_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag cannot be its own parent"
            )

        # Percorrer ancestrais de new_parent_id
        current_id = new_parent_id
        visited = set()

        while current_id is not None:
            if current_id in visited:
                # Ciclo pré-existente (não deveria acontecer)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Existing cycle detected in tag hierarchy"
                )

            if current_id == tag_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot set parent: would create a cycle in the hierarchy"
                )

            visited.add(current_id)

            # Buscar parent do current
            result = await self.db.execute(
                select(ExerciseTag.parent_tag_id)
                .where(ExerciseTag.id == current_id)
            )
            row = result.first()
            current_id = row[0] if row else None

    async def _validate_tag_ids(
        self,
        tag_ids: List[UUID],
        require_active: bool = True
    ) -> None:
        """
        Valida que todos tag_ids existem em exercise_tags.

        Args:
            tag_ids: Lista de UUIDs de tags
            require_active: Se True, exige que tags sejam is_active=True

        Raises:
            HTTPException 400: Se alguma tag não existe ou está inativa
        """
        if not tag_ids:
            return  # Lista vazia é válida

        # Buscar tags existentes
        stmt = select(ExerciseTag.id, ExerciseTag.is_active).where(
            ExerciseTag.id.in_(tag_ids)
        )
        result = await self.db.execute(stmt)
        existing_tags = {row.id: row.is_active for row in result}

        # Verificar existência
        missing_ids = set(tag_ids) - set(existing_tags.keys())
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_TAG_IDS",
                    "message": f"Tags not found: {[str(t) for t in missing_ids]}"
                }
            )

        # Verificar ativas (se requerido)
        if require_active:
            inactive_ids = [tid for tid, is_active in existing_tags.items() if not is_active]
            if inactive_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_code": "INACTIVE_TAGS",
                        "message": f"Tags are inactive: {[str(t) for t in inactive_ids]}"
                    }
                )

    # =========================================================================
    # TAGS CRUD
    # =========================================================================

    async def list_tags(self, active_only: bool = False) -> List[ExerciseTag]:
        """Lista todas as tags, ordenadas por display_order e nome."""
        stmt = (
            select(ExerciseTag)
            .options(selectinload(ExerciseTag.children))
            .order_by(ExerciseTag.display_order, ExerciseTag.name)
        )
        if active_only:
            stmt = stmt.where(ExerciseTag.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_tag(
        self,
        data: dict,
        suggested_by_user_id: Optional[UUID] = None,
        auto_approve: bool = True
    ) -> ExerciseTag:
        """
        Cria nova tag.

        Args:
            data: Dados da tag (name, parent_tag_id, description, display_order)
            suggested_by_user_id: UUID do usuário que sugeriu
            auto_approve: Se True, marca como ativa e aprovada automaticamente
        """
        tag_data = {**data}
        if suggested_by_user_id:
            tag_data['suggested_by_user_id'] = suggested_by_user_id

        if auto_approve:
            tag_data['is_active'] = True
            tag_data['approved_at'] = datetime.utcnow()
            tag_data['approved_by_admin_id'] = suggested_by_user_id

        tag = ExerciseTag(**tag_data)
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        return tag

    async def update_tag(self, tag_id: UUID, data: dict) -> ExerciseTag:
        """
        Atualiza tag existente com validação anti-ciclo.

        Raises:
            HTTPException 404: Tag não encontrada
            HTTPException 400: Mudança de parent criaria ciclo
        """
        tag = await self.db.get(ExerciseTag, tag_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        # Validação anti-ciclo se parent_tag_id está sendo alterado
        if 'parent_tag_id' in data:
            await self._validate_no_cycle(tag_id, data['parent_tag_id'])

        for k, v in data.items():
            setattr(tag, k, v)

        await self.db.commit()
        await self.db.refresh(tag)
        return tag

    # =========================================================================
    # EXERCISES CRUD
    # =========================================================================

    async def list_exercises(
        self,
        organization_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        tag_ids: Optional[List[UUID]] = None,
        favorites_only: bool = False
    ) -> dict:
        """
        Lista exercícios com paginação e filtros.

        Args:
            organization_id: Filtrar por organização
            user_id: UUID do usuário (para filtro de favoritos)
            page: Número da página (1-indexed)
            per_page: Itens por página
            search: Buscar por nome ou descrição
            category: Filtrar por categoria
            tag_ids: Filtrar por tags (AND - exercício deve ter todas)
            favorites_only: Filtrar apenas favoritos do usuário

        Returns:
            Dict com exercises, total, page, per_page
        """
        from sqlalchemy import func, or_

        # Query base
        stmt = (
            select(Exercise)
            .options(
                selectinload(Exercise.creator),
                selectinload(Exercise.organization)
            )
        )

        # Filtro por organização
        if organization_id:
            stmt = stmt.where(Exercise.organization_id == organization_id)

        # Filtro por favoritos
        if favorites_only and user_id:
            stmt = stmt.join(
                ExerciseFavorite,
                (ExerciseFavorite.exercise_id == Exercise.id) &
                (ExerciseFavorite.user_id == user_id)
            )

        # Filtro de busca (nome ou descrição)
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Exercise.name.ilike(search_pattern),
                    Exercise.description.ilike(search_pattern)
                )
            )

        # Filtro por categoria
        if category:
            stmt = stmt.where(Exercise.category == category)

        # Filtro por tags
        if tag_ids:
            stmt = stmt.where(Exercise.tag_ids.contains(tag_ids))

        # Contar total (antes de paginação)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Aplicar ordenação e paginação
        stmt = stmt.order_by(Exercise.name)
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)

        # Executar query
        result = await self.db.execute(stmt)
        exercises = result.scalars().all()

        return {
            "exercises": exercises,
            "total": total,
            "page": page,
            "per_page": per_page
        }

    async def get_exercise(self, exercise_id: UUID) -> Optional[Exercise]:
        """Busca exercício por ID."""
        return await self.db.get(Exercise, exercise_id)

    async def create_exercise(
        self,
        data: dict,
        user_id: UUID,
        organization_id: UUID
    ) -> Exercise:
        """
        Cria novo exercício com validação de tag_ids.

        Args:
            data: Dados do exercício (name, description, tag_ids, category, media_url)
            user_id: UUID do usuário criador
            organization_id: UUID da organização

        Raises:
            HTTPException 400: tag_ids inválidos ou inativos
        """
        # Validar tag_ids
        if data.get('tag_ids'):
            await self._validate_tag_ids(data['tag_ids'])

        exercise = Exercise(
            **data,
            created_by_user_id=user_id,
            organization_id=organization_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(exercise)
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def update_exercise(
        self,
        exercise_id: UUID,
        data: dict,
        organization_id: Optional[UUID] = None
    ) -> Exercise:
        """
        Atualiza exercício existente com validação de tag_ids.

        Args:
            exercise_id: UUID do exercício
            data: Campos a atualizar
            organization_id: Se fornecido, valida que exercício pertence à org

        Raises:
            HTTPException 404: Exercício não encontrado
            HTTPException 403: Exercício não pertence à organização
            HTTPException 400: tag_ids inválidos
        """
        exercise = await self.db.get(Exercise, exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )

        # Validar escopo de organização
        if organization_id and exercise.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Exercise does not belong to your organization"
            )

        # Validar tag_ids se estão sendo atualizados
        if 'tag_ids' in data and data['tag_ids']:
            await self._validate_tag_ids(data['tag_ids'])

        for k, v in data.items():
            setattr(exercise, k, v)

        exercise.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    # =========================================================================
    # FAVORITES
    # =========================================================================

    async def favorite_exercise(self, user_id: UUID, exercise_id: UUID) -> ExerciseFavorite:
        """
        Marca exercício como favorito do usuário.

        Raises:
            HTTPException 404: Exercício não encontrado
            HTTPException 409: Já é favorito (PK composta impede duplicatas)
        """
        # Verificar se exercício existe
        exercise = await self.db.get(Exercise, exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )

        # Verificar se já é favorito
        existing = await self.db.get(ExerciseFavorite, {'user_id': user_id, 'exercise_id': exercise_id})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Exercise is already a favorite"
            )

        fav = ExerciseFavorite(
            user_id=user_id,
            exercise_id=exercise_id,
            created_at=datetime.utcnow()
        )
        self.db.add(fav)
        await self.db.commit()
        await self.db.refresh(fav)
        return fav

    async def unfavorite_exercise(self, user_id: UUID, exercise_id: UUID) -> bool:
        """
        Remove exercício dos favoritos do usuário.

        Returns:
            True se removido, False se não era favorito
        """
        fav = await self.db.get(ExerciseFavorite, {'user_id': user_id, 'exercise_id': exercise_id})
        if fav:
            await self.db.delete(fav)
            await self.db.commit()
            return True
        return False

    async def list_favorites(self, user_id: UUID) -> List[ExerciseFavorite]:
        """Lista todos os exercícios favoritos de um usuário."""
        stmt = select(ExerciseFavorite).where(
            ExerciseFavorite.user_id == user_id
        ).order_by(ExerciseFavorite.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()
