"""
Service para gerenciar exercícios vinculados a sessões de treino.
Suporta CRUD, reordenação e bulk operations para drag-and-drop.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import select, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from fastapi import HTTPException, status

from app.models.session_exercise import SessionExercise
from app.models.training_session import TrainingSession
from app.models.exercise import Exercise
from app.schemas.session_exercises import (
    SessionExerciseCreate,
    SessionExerciseBulkCreate,
    SessionExerciseUpdate,
    SessionExerciseReorder,
    SessionExerciseResponse,
    SessionExerciseListResponse,
    ExerciseNested
)


class SessionExerciseService:
    """Service para operações de session-exercises"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== VERIFICAÇÕES ====================
    
    async def _verify_session_exists(self, session_id: UUID) -> TrainingSession:
        """Verifica se sessão existe e não está deletada"""
        result = await self.db.execute(
            select(TrainingSession)
            .where(
                and_(
                    TrainingSession.id == session_id,
                    TrainingSession.deleted_at.is_(None)
                )
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training session not found: {session_id}"
            )
        
        return session
    
    async def _verify_exercise_exists(self, exercise_id: UUID) -> Exercise:
        """Verifica se exercício existe"""
        result = await self.db.execute(
            select(Exercise).where(Exercise.id == exercise_id)
        )
        exercise = result.scalar_one_or_none()
        
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise not found: {exercise_id}"
            )
        
        return exercise
    
    async def _verify_session_exercise_exists(self, session_exercise_id: UUID) -> SessionExercise:
        """Verifica se vínculo existe e não está deletado"""
        result = await self.db.execute(
            select(SessionExercise)
            .options(
                selectinload(SessionExercise.exercise),
                selectinload(SessionExercise.session)
            )
            .where(
                and_(
                    SessionExercise.id == session_exercise_id,
                    SessionExercise.deleted_at.is_(None)
                )
            )
        )
        session_exercise = result.scalar_one_or_none()
        
        if not session_exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session exercise link not found: {session_exercise_id}"
            )
        
        return session_exercise
    
    # ==================== ADD (CREATE) ====================
    
    async def add_exercise(
        self,
        session_id: UUID,
        data: SessionExerciseCreate,
        user_id: UUID
    ) -> SessionExerciseResponse:
        """
        Adiciona um exercício à sessão de treino.
        
        Args:
            session_id: UUID da sessão
            data: Dados do exercício a adicionar (exercise_id, order_index, duration, notes)
            user_id: UUID do usuário (para auditoria)
        
        Returns:
            SessionExerciseResponse com dados do exercício aninhados
        
        Raises:
            404: Sessão ou exercício não encontrado
            400: Conflict de order_index (já existe exercício naquela posição)
        """
        # Verificar existência
        await self._verify_session_exists(session_id)
        await self._verify_exercise_exists(data.exercise_id)
        
        # Criar vínculo
        session_exercise = SessionExercise(
            session_id=session_id,
            exercise_id=data.exercise_id,
            order_index=data.order_index,
            duration_minutes=data.duration_minutes,
            notes=data.notes
        )
        
        self.db.add(session_exercise)
        
        try:
            await self.db.commit()
            await self.db.refresh(session_exercise)
        except Exception as e:
            await self.db.rollback()
            # Conflict de UNIQUE index (session_id, order_index)
            if "idx_session_exercises_session_order_unique" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order index {data.order_index} already exists for this session. Please use a different order or reorder existing exercises."
                )
            raise
        
        # Carregar exercise relacionado para response
        await self.db.refresh(session_exercise, ['exercise'])
        
        return self._to_response(session_exercise)
    
    async def bulk_add_exercises(
        self,
        session_id: UUID,
        data: SessionExerciseBulkCreate,
        user_id: UUID
    ) -> list[SessionExerciseResponse]:
        """
        Adiciona múltiplos exercícios de uma vez (bulk insert).
        Útil para drag-and-drop de seleção múltipla.
        
        Args:
            session_id: UUID da sessão
            data: Lista de exercícios a adicionar
            user_id: UUID do usuário (para auditoria)
        
        Returns:
            Lista de SessionExerciseResponse
        
        Raises:
            404: Sessão não encontrada
            400: Algum exercise_id inválido ou conflict de order_index
        """
        # Verificar sessão existe
        await self._verify_session_exists(session_id)
        
        # Verificar todos exercícios existem
        exercise_ids = [ex.exercise_id for ex in data.exercises]
        result = await self.db.execute(
            select(Exercise).where(Exercise.id.in_(exercise_ids))
        )
        existing_exercises = {ex.id for ex in result.scalars().all()}
        
        invalid_ids = set(exercise_ids) - existing_exercises
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid exercise IDs: {list(invalid_ids)}"
            )
        
        # Criar vínculos em batch
        session_exercises = [
            SessionExercise(
                session_id=session_id,
                exercise_id=ex.exercise_id,
                order_index=ex.order_index,
                duration_minutes=ex.duration_minutes,
                notes=ex.notes
            )
            for ex in data.exercises
        ]
        
        self.db.add_all(session_exercises)
        
        try:
            await self.db.commit()
            
            # Refresh all com relationships
            for se in session_exercises:
                await self.db.refresh(se, ['exercise'])
        
        except Exception as e:
            await self.db.rollback()
            if "idx_session_exercises_session_order_unique" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Conflict: One or more order_index values already exist. Please check ordering."
                )
            raise
        
        return [self._to_response(se) for se in session_exercises]
    
    # ==================== GET (READ) ====================
    
    async def get_session_exercises(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> SessionExerciseListResponse:
        """
        Retorna todos exercícios de uma sessão ordenados por order_index.
        
        Args:
            session_id: UUID da sessão
            user_id: UUID do usuário (para auditoria)
        
        Returns:
            SessionExerciseListResponse com lista ordenada + metadados (total, duração)
        
        Raises:
            404: Sessão não encontrada
        """
        # Verificar sessão existe
        await self._verify_session_exists(session_id)
        
        # Buscar todos exercícios com eager loading
        result = await self.db.execute(
            select(SessionExercise)
            .options(selectinload(SessionExercise.exercise))
            .where(
                and_(
                    SessionExercise.session_id == session_id,
                    SessionExercise.deleted_at.is_(None)
                )
            )
            .order_by(SessionExercise.order_index.asc())
        )
        session_exercises = result.scalars().all()
        
        # Calcular metadados
        total_exercises = len(session_exercises)
        total_duration = sum(
            (se.duration_minutes or 0) for se in session_exercises
        )
        
        return SessionExerciseListResponse(
            session_id=session_id,
            total_exercises=total_exercises,
            total_duration_minutes=total_duration if total_duration > 0 else None,
            exercises=[self._to_response(se) for se in session_exercises]
        )
    
    # ==================== UPDATE ====================
    
    async def update_exercise(
        self,
        session_exercise_id: UUID,
        data: SessionExerciseUpdate,
        user_id: UUID
    ) -> SessionExerciseResponse:
        """
        Atualiza metadados de um exercício já adicionado (order, duration, notes).
        
        Args:
            session_exercise_id: UUID do vínculo
            data: Campos a atualizar
            user_id: UUID do usuário (para auditoria)
        
        Returns:
            SessionExerciseResponse atualizado
        
        Raises:
            404: Vínculo não encontrado
            400: Conflict de order_index se alterado
        """
        # Verificar existência
        session_exercise = await self._verify_session_exercise_exists(session_exercise_id)
        
        # Aplicar updates
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session_exercise, field, value)
        
        session_exercise.updated_at = datetime.utcnow()
        
        try:
            await self.db.commit()
            await self.db.refresh(session_exercise, ['exercise'])
        except Exception as e:
            await self.db.rollback()
            if "idx_session_exercises_session_order_unique" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order index {data.order_index} already exists. Use reorder endpoint for reordering."
                )
            raise
        
        return self._to_response(session_exercise)
    
    async def reorder_exercises(
        self,
        session_id: UUID,
        data: SessionExerciseReorder,
        user_id: UUID
    ) -> dict:
        """
        Reordena múltiplos exercícios de uma vez (bulk update de order_index).
        Usado após drag-and-drop de reordenação.
        
        Args:
            session_id: UUID da sessão (validação)
            data: Lista de {id, order_index} para atualizar
            user_id: UUID do usuário (para auditoria)
        
        Returns:
            {"success": True, "updated_count": N}
        
        Raises:
            404: Sessão ou algum vínculo não encontrado
            400: Algum ID não pertence à sessão especificada
        """
        # Verificar sessão existe
        await self._verify_session_exists(session_id)
        
        # Buscar todos vínculos a atualizar
        ids_to_update = [item.id for item in data.reorders]
        result = await self.db.execute(
            select(SessionExercise)
            .where(
                and_(
                    SessionExercise.id.in_(ids_to_update),
                    SessionExercise.deleted_at.is_(None)
                )
            )
        )
        session_exercises = result.scalars().all()
        
        # Verificar todos IDs são válidos
        found_ids = {se.id for se in session_exercises}
        invalid_ids = set(ids_to_update) - found_ids
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invalid session_exercise IDs: {list(invalid_ids)}"
            )
        
        # Verificar todos pertencem à mesma sessão
        sessions_ids = {se.session_id for se in session_exercises}
        if len(sessions_ids) > 1 or session_id not in sessions_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All exercises must belong to the specified session"
            )
        
        # Criar mapeamento id → novo order_index
        reorder_map = {item.id: item.order_index for item in data.reorders}

        # Validar que não há índices duplicados no payload
        if len(set(reorder_map.values())) != len(reorder_map):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order index duplicado no payload de reordenação"
            )

        # Evitar violação de índice UNIQUE (session_id, order_index) em swaps
        max_order_result = await self.db.execute(
            select(func.max(SessionExercise.order_index)).where(
                and_(
                    SessionExercise.session_id == session_id,
                    SessionExercise.deleted_at.is_(None)
                )
            )
        )
        max_order = max_order_result.scalar() or 0
        offset = max_order + 1000

        try:
            # 1) Mover temporariamente para liberar conflitos
            await self.db.execute(
                update(SessionExercise)
                .where(
                    and_(
                        SessionExercise.id.in_(ids_to_update),
                        SessionExercise.deleted_at.is_(None)
                    )
                )
                .values(
                    order_index=SessionExercise.order_index + offset,
                    updated_at=datetime.utcnow()
                )
            )

            # 2) Aplicar índices finais
            mappings = [
                {"id": se.id, "order_index": reorder_map[se.id], "updated_at": datetime.utcnow()}
                for se in session_exercises
            ]
            await self.db.execute(update(SessionExercise), mappings)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            if "idx_session_exercises_session_order_unique" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order index já existe para esta sessão"
                )
            raise

        return {
            "success": True,
            "updated_count": len(mappings)
        }
    
    # ==================== DELETE ====================
    
    async def remove_exercise(
        self,
        session_exercise_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Remove exercício da sessão (soft delete).
        
        Args:
            session_exercise_id: UUID do vínculo a remover
            user_id: UUID do usuário (para auditoria)
        
        Raises:
            404: Vínculo não encontrado
        """
        # Verificar existência
        session_exercise = await self._verify_session_exercise_exists(session_exercise_id)
        
        # Soft delete
        session_exercise.deleted_at = datetime.utcnow()
        
        await self.db.commit()
    
    # ==================== HELPERS ====================
    
    def _to_response(self, se: SessionExercise) -> SessionExerciseResponse:
        """Converte model para response schema com dados aninhados"""
        exercise_nested = ExerciseNested(
            id=se.exercise.id,
            name=se.exercise.name,
            description=se.exercise.description,
            category=se.exercise.category,
            media_url=se.exercise.media_url,
            tag_ids=se.exercise.tag_ids
        )
        
        return SessionExerciseResponse(
            id=se.id,
            session_id=se.session_id,
            exercise_id=se.exercise_id,
            order_index=se.order_index,
            duration_minutes=se.duration_minutes,
            notes=se.notes,
            exercise=exercise_nested,
            created_at=se.created_at,
            updated_at=se.updated_at
        )
