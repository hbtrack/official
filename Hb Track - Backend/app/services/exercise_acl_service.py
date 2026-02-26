"""
ExerciseAclService — Gerenciamento de ACL de exercícios.

Invariantes implementadas:
- INV-EXB-ACL-002: ACL só para restricted
- INV-EXB-ACL-003: Anti-cross-org
- INV-EXB-ACL-004: Creator authority only
- INV-EXB-ACL-005: Creator bypass
- INV-EXB-ACL-006: Constraint unique (exercise_id, user_id)
- INV-EXB-ACL-007: Sem retrobreak em sessions históricas
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exists
from fastapi import HTTPException, status
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from app.models.exercise import Exercise
from app.models.exercise_acl import ExerciseAcl
from app.models.user import User
from app.core.exceptions import (
    AclNotApplicableError,
    AclCrossOrgError, 
    AclUnauthorizedError,
    AclDuplicateError
)


class ExerciseAclService:
    """
    Serviço para gerenciamento de ACL de exercícios.
    
    Apenas exercises com visibility_mode='restricted' suportam ACL.
    Apenas o criador do exercício pode gerenciar ACL.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_exercise(self, exercise_id: UUID) -> Exercise:
        """Busca exercício por ID ou levanta 404."""
        exercise = await self.db.get(Exercise, exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )
        return exercise

    async def _get_user(self, user_id: UUID) -> User:
        """Busca usuário por ID ou levanta 404."""
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    async def _validate_creator_authority(self, exercise: Exercise, acting_user_id: UUID) -> None:
        """
        INV-EXB-ACL-004: Valida que acting_user_id é o criador do exercício.
        """
        if exercise.created_by_user_id != acting_user_id:
            raise AclUnauthorizedError()

    async def _validate_restricted_visibility(self, exercise: Exercise) -> None:
        """
        INV-EXB-ACL-002: Valida que exercício tem visibility_mode='restricted'.
        """
        visibility_mode = getattr(exercise, 'visibility_mode', None)
        if visibility_mode != 'restricted':
            raise AclNotApplicableError()

    async def _validate_same_org(self, exercise: Exercise, user: User) -> None:
        """
        INV-EXB-ACL-003: Valida que usuário pertence à mesma org do exercício.
        """
        if exercise.organization_id != user.organization_id:
            raise AclCrossOrgError()

    async def has_access(self, exercise_id: UUID, user_id: UUID) -> bool:
        """
        INV-EXB-ACL-005: Verifica se usuário tem acesso ao exercício.
        
        Creator sempre tem acesso (bypass).
        Para outros usuários, verifica ACL entry.
        
        Returns:
            True se usuário tem acesso, False caso contrário
        """
        exercise = await self._get_exercise(exercise_id)
        
        # INV-EXB-ACL-005: Creator bypass
        if exercise.created_by_user_id == user_id:
            return True
        
        # Exercícios org_wide são acessíveis a todos da org
        visibility_mode = getattr(exercise, 'visibility_mode', 'org_wide')
        if visibility_mode == 'org_wide':
            return True
        
        # Verificar ACL entry para restricted
        stmt = select(ExerciseAcl).where(
            ExerciseAcl.exercise_id == exercise_id,
            ExerciseAcl.user_id == user_id
        )
        result = await self.db.execute(stmt)
        acl_entry = result.scalar_one_or_none()
        return acl_entry is not None

    async def grant_access(
        self,
        exercise_id: UUID,
        target_user_id: UUID,
        acting_user_id: UUID
    ) -> ExerciseAcl:
        """
        Concede acesso ao exercício para um usuário.
        
        Args:
            exercise_id: UUID do exercício
            target_user_id: UUID do usuário que receberá acesso
            acting_user_id: UUID do usuário que está concedendo (deve ser o criador)
            
        Returns:
            ExerciseAcl entry criada
            
        Raises:
            AclNotApplicableError: Exercise não é restricted (INV-EXB-ACL-002)
            AclCrossOrgError: Usuário não pertence à mesma org (INV-EXB-ACL-003)
            AclUnauthorizedError: Acting user não é o criador (INV-EXB-ACL-004)
            AclDuplicateError: ACL entry já existe (INV-EXB-ACL-006)
        """
        exercise = await self._get_exercise(exercise_id)
        target_user = await self._get_user(target_user_id)
        
        # INV-EXB-ACL-004: Creator authority
        await self._validate_creator_authority(exercise, acting_user_id)
        
        # INV-EXB-ACL-002: Restricted visibility
        await self._validate_restricted_visibility(exercise)
        
        # INV-EXB-ACL-003: Same org
        await self._validate_same_org(exercise, target_user)
        
        # INV-EXB-ACL-006: Check duplicate
        stmt = select(ExerciseAcl).where(
            ExerciseAcl.exercise_id == exercise_id,
            ExerciseAcl.user_id == target_user_id
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise AclDuplicateError()
        
        # Create ACL entry
        acl_entry = ExerciseAcl(
            exercise_id=exercise_id,
            user_id=target_user_id,
            granted_by_user_id=acting_user_id,
            granted_at=datetime.utcnow()
        )
        self.db.add(acl_entry)
        await self.db.commit()
        await self.db.refresh(acl_entry)
        return acl_entry

    async def revoke_access(
        self,
        exercise_id: UUID,
        target_user_id: UUID,
        acting_user_id: UUID
    ) -> bool:
        """
        Revoga acesso ao exercício de um usuário.
        
        INV-EXB-ACL-007: Não afeta session_exercises históricas.
        
        Args:
            exercise_id: UUID do exercício
            target_user_id: UUID do usuário perderá acesso
            acting_user_id: UUID do usuário que está revogando (deve ser o criador)
            
        Returns:
            True se revogado, False se não existia ACL
            
        Raises:
            AclUnauthorizedError: Acting user não é o criador
        """
        exercise = await self._get_exercise(exercise_id)
        
        # INV-EXB-ACL-004: Creator authority
        await self._validate_creator_authority(exercise, acting_user_id)
        
        # Find and delete ACL entry
        stmt = select(ExerciseAcl).where(
            ExerciseAcl.exercise_id == exercise_id,
            ExerciseAcl.user_id == target_user_id
        )
        result = await self.db.execute(stmt)
        acl_entry = result.scalar_one_or_none()
        
        if acl_entry:
            await self.db.delete(acl_entry)
            await self.db.commit()
            # INV-EXB-ACL-007: Session exercises históricas não são afetadas
            # (exercício permanece vinculado às sessions, apenas novos acessos são bloqueados)
            return True
        return False

    async def list_access(self, exercise_id: UUID) -> List[ExerciseAcl]:
        """
        Lista todos os usuários com acesso ao exercício.
        
        Returns:
            Lista de ACL entries
        """
        exercise = await self._get_exercise(exercise_id)
        
        stmt = select(ExerciseAcl).where(
            ExerciseAcl.exercise_id == exercise_id
        ).order_by(ExerciseAcl.granted_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def change_visibility_to_org_wide(
        self,
        exercise_id: UUID,
        acting_user_id: UUID
    ) -> Exercise:
        """
        Altera visibility_mode para org_wide.
        
        INV-EXB-ACL-007: Não afeta session_exercises históricas.
        ACL entries permanecem mas ficam sem efeito (org_wide ignora ACL).
        
        Args:
            exercise_id: UUID do exercício
            acting_user_id: UUID do usuário (deve ser o criador)
            
        Returns:
            Exercise atualizado
        """
        exercise = await self._get_exercise(exercise_id)
        
        # INV-EXB-ACL-004: Creator authority
        await self._validate_creator_authority(exercise, acting_user_id)
        
        # Update visibility
        if hasattr(exercise, 'visibility_mode'):
            exercise.visibility_mode = 'org_wide'
            exercise.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(exercise)
        
        return exercise
