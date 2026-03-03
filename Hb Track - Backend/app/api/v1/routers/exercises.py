"""
Router para operações de exercises e exercise_tags.

RBAC:
- Tags (leitura): Qualquer usuário autenticado
- Tags (escrita): dirigente, coordenador
- Exercícios (leitura): Qualquer usuário autenticado da mesma org
- Exercícios (escrita): treinador, coordenador, dirigente
- Favoritos: Próprio usuário autenticado
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional

from app.schemas.exercise_tags import ExerciseTagCreate, ExerciseTagUpdate, ExerciseTagResponse
from app.schemas.exercises import (
    ExerciseCreate, ExerciseUpdate, ExerciseResponse, ExerciseListResponse,
    ExerciseACLResponse, ExerciseACLGrantRequest, VisibilityUpdateRequest
)
from app.schemas.exercise_favorites import ExerciseFavoriteCreate, ExerciseFavoriteResponse
from app.services.exercise_service import ExerciseService
from app.services.exercise_acl_service import ExerciseAclService
from app.core.db import get_async_db
from app.api.v1.deps.auth import permission_dep, get_current_context
from app.core.context import ExecutionContext


router = APIRouter()


# =============================================================================
# TAGS
# =============================================================================

@router.get(
    "/exercise-tags",
    response_model=List[ExerciseTagResponse],
    summary="Listar tags de exercícios",
    description="Lista todas as tags hierárquicas. Requer autenticação.",
    tags=["exercise-tags"]
)
async def list_tags(
    active_only: bool = True,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Lista todas as tags de exercícios em formato hierárquico.

    **Permissões:** Qualquer usuário autenticado

    **Query params:**
    - active_only: Se True (default), retorna apenas tags is_active=True
    """
    service = ExerciseService(db)
    tags = await service.list_tags(active_only=active_only)
    return tags


@router.post(
    "/exercise-tags",
    response_model=ExerciseTagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tag de exercício",
    description="Cria nova tag. Requer role dirigente ou coordenador.",
    tags=["exercise-tags"]
)
async def create_tag(
    data: ExerciseTagCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador"])
    ),
):
    """
    Cria uma nova tag de exercício.

    **Permissões:** dirigente, coordenador

    Tags criadas por esses roles são auto-aprovadas (is_active=True).
    """
    service = ExerciseService(db)
    tag = await service.create_tag(
        data.model_dump(exclude_unset=True),
        suggested_by_user_id=ctx.user_id,
        auto_approve=True
    )
    return tag


@router.patch(
    "/exercise-tags/{tag_id}",
    response_model=ExerciseTagResponse,
    summary="Atualizar tag de exercício",
    description="Atualiza tag existente. Inclui validação anti-ciclo.",
    tags=["exercise-tags"]
)
async def update_tag(
    tag_id: UUID,
    data: ExerciseTagUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador"])
    ),
):
    """
    Atualiza uma tag existente.

    **Permissões:** dirigente, coordenador

    **Validações:**
    - Anti-ciclo: Impede que uma tag seja definida como filha de si mesma ou de seus descendentes

    **Errors:**
    - 404: Tag não encontrada
    - 400: Mudança de parent_tag_id criaria ciclo
    """
    service = ExerciseService(db)
    tag = await service.update_tag(tag_id, data.model_dump(exclude_unset=True))
    return tag


# =============================================================================
# EXERCISES
# =============================================================================

@router.get(
    "/exercises",
    response_model=ExerciseListResponse,
    summary="Listar exercícios",
    description="Lista exercícios da organização do usuário com paginação.",
    tags=["exercises"]
)
async def list_exercises(
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
    tag_ids: Optional[List[UUID]] = None,
    favorites_only: bool = False,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Lista exercícios da organização do usuário autenticado com paginação.

    **Permissões:** Qualquer usuário autenticado

    **Query params:**
    - page: Número da página (padrão: 1)
    - per_page: Itens por página (padrão: 20)
    - search: Busca por nome ou descrição
    - category: Filtrar por categoria
    - tag_ids: Filtrar por tags (exercício deve conter todas as tags)
    - favorites_only: Filtrar apenas favoritos do usuário
    """
    service = ExerciseService(db)
    result = await service.list_exercises(
        organization_id=ctx.organization_id,
        user_id=ctx.user_id if favorites_only else None,
        page=page,
        per_page=per_page,
        search=search,
        category=category,
        tag_ids=tag_ids,
        favorites_only=favorites_only
    )
    return result


@router.get(
    "/exercises/{exercise_id}",
    response_model=ExerciseResponse,
    summary="Buscar exercício por ID",
    description="Retorna um exercício específico.",
    tags=["exercises"]
)
async def get_exercise(
    exercise_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Busca exercício por ID.

    **Permissões:** Qualquer usuário autenticado

    **Errors:**
    - 404: Exercício não encontrado
    - 403: Exercício não pertence à organização do usuário
    """
    service = ExerciseService(db)
    exercise = await service.get_exercise(exercise_id)

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    # Validar escopo de organização
    if exercise.organization_id != ctx.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Exercise does not belong to your organization"
        )

    return exercise


@router.post(
    "/exercises",
    response_model=ExerciseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar exercício",
    description="Cria novo exercício. Valida tag_ids.",
    tags=["exercises"]
)
async def create_exercise(
    data: ExerciseCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"])
    ),
):
    """
    Cria um novo exercício.

    **Permissões:** treinador, coordenador, dirigente

    **Validações:**
    - tag_ids: Todos os UUIDs devem existir e estar ativos em exercise_tags

    **Errors:**
    - 400: tag_ids inválidos ou inativos
    """
    service = ExerciseService(db)
    exercise = await service.create_exercise(
        data.model_dump(exclude_unset=True),
        user_id=ctx.user_id,
        organization_id=ctx.organization_id
    )
    return exercise


@router.patch(
    "/exercises/{exercise_id}",
    response_model=ExerciseResponse,
    summary="Atualizar exercício",
    description="Atualiza exercício existente. Valida tag_ids e escopo de organização.",
    tags=["exercises"]
)
async def update_exercise(
    exercise_id: UUID,
    data: ExerciseUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"])
    ),
):
    """
    Atualiza um exercício existente.

    **Permissões:** treinador, coordenador, dirigente

    **Validações:**
    - Exercício deve pertencer à organização do usuário
    - tag_ids: Se fornecidos, devem existir e estar ativos

    **Errors:**
    - 404: Exercício não encontrado
    - 403: Exercício não pertence à organização
    - 400: tag_ids inválidos
    """
    service = ExerciseService(db)
    exercise = await service.update_exercise(
        exercise_id,
        data.model_dump(exclude_unset=True),
        organization_id=ctx.organization_id
    )
    return exercise


# =============================================================================
# ACL / VISIBILITY / COPY-TO-ORG
# =============================================================================

@router.get(
    "/exercises/{exercise_id}/acl",
    response_model=List[ExerciseACLResponse],
    summary="Listar ACL do exercício",
    description="Lista usuários com acesso ao exercício restricted. Apenas o criador pode ver.",
    tags=["exercises"]
)
async def list_exercise_acl(
    exercise_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Lista entradas de ACL do exercício.

    **Permissões:** Qualquer usuário autenticado (apenas criador vê a lista)

    **Errors:**
    - 404: Exercício não encontrado
    - 403: Usuário não é o criador do exercício
    """
    exercise_svc = ExerciseService(db)
    exercise = await exercise_svc.get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    if exercise.created_by_user_id != ctx.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator can view ACL")

    acl_svc = ExerciseAclService(db)
    return await acl_svc.list_access(exercise_id)


@router.post(
    "/exercises/{exercise_id}/acl",
    response_model=ExerciseACLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Conceder acesso ao exercício",
    description="Adiciona usuário à ACL do exercício restricted. Apenas o criador pode conceder.",
    tags=["exercises"]
)
async def grant_exercise_acl(
    exercise_id: UUID,
    data: ExerciseACLGrantRequest,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"])
    ),
):
    """
    Concede acesso ao exercício para um usuário.

    **Permissões:** treinador, coordenador, dirigente (apenas criador do exercício)

    **Errors:**
    - 404: Exercício ou usuário não encontrado
    - 403: Exercício não é restricted ou acting_user não é o criador
    - 409: Usuário já tem acesso (ACL duplicada)
    """
    acl_svc = ExerciseAclService(db)
    return await acl_svc.grant_access(
        exercise_id=exercise_id,
        target_user_id=data.target_user_id,
        acting_user_id=ctx.user_id
    )


@router.delete(
    "/exercises/{exercise_id}/acl/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revogar acesso ao exercício",
    description="Remove usuário da ACL do exercício. Apenas o criador pode revogar.",
    tags=["exercises"]
)
async def revoke_exercise_acl(
    exercise_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"])
    ),
):
    """
    Revoga acesso ao exercício de um usuário.

    **Permissões:** treinador, coordenador, dirigente (apenas criador do exercício)

    **Returns:** 204 No Content (sucesso mesmo se o usuário não tinha ACL)

    **Errors:**
    - 404: Exercício não encontrado
    - 403: acting_user não é o criador
    """
    acl_svc = ExerciseAclService(db)
    await acl_svc.revoke_access(
        exercise_id=exercise_id,
        target_user_id=user_id,
        acting_user_id=ctx.user_id
    )
    return None


@router.patch(
    "/exercises/{exercise_id}/visibility",
    response_model=ExerciseResponse,
    summary="Alterar visibilidade do exercício",
    description="Altera visibility_mode entre org_wide e restricted. Apenas o criador pode alterar.",
    tags=["exercises"]
)
async def update_exercise_visibility(
    exercise_id: UUID,
    data: VisibilityUpdateRequest,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"])
    ),
):
    """
    Altera o visibility_mode do exercício.

    **Permissões:** treinador, coordenador, dirigente (apenas criador do exercício)

    **Body:** { "visibility_mode": "org_wide" | "restricted" }

    **Errors:**
    - 404: Exercício não encontrado
    - 403: Usuário não é o criador
    """
    acl_svc = ExerciseAclService(db)
    exercise_svc = ExerciseService(db)

    if data.visibility_mode == "org_wide":
        return await acl_svc.change_visibility_to_org_wide(exercise_id, acting_user_id=ctx.user_id)
    else:
        # Para restricted: validar criador inline e usar update_exercise
        exercise = await exercise_svc.get_exercise(exercise_id)
        if not exercise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
        if exercise.created_by_user_id != ctx.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator can modify visibility")
        return await exercise_svc.update_exercise(
            exercise_id,
            {"visibility_mode": data.visibility_mode},
            organization_id=ctx.organization_id
        )


@router.post(
    "/exercises/{exercise_id}/copy-to-org",
    response_model=ExerciseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Copiar exercício SYSTEM para ORG",
    description="Cria cópia editável de um exercício SYSTEM na organização do usuário.",
    tags=["exercises"]
)
async def copy_exercise_to_org(
    exercise_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["treinador", "coordenador", "dirigente"])
    ),
):
    """
    Copia exercício SYSTEM para a organização do usuário autenticado.

    **Permissões:** treinador, coordenador, dirigente

    **Returns:** Novo exercício ORG com scope='ORG' e organization_id da org do usuário

    **Errors:**
    - 404: Exercício não encontrado
    - 400: Exercício não é SYSTEM (copy-to-org só para SYSTEM)
    """
    service = ExerciseService(db)
    return await service.copy_system_exercise_to_org(
        exercise_id=exercise_id,
        organization_id=ctx.organization_id,
        user_id=ctx.user_id
    )


# =============================================================================
# FAVORITES
# =============================================================================

@router.post(
    "/exercise-favorites",
    response_model=ExerciseFavoriteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Favoritar exercício",
    description="Marca exercício como favorito do usuário atual.",
    tags=["exercise-favorites"]
)
async def favorite_exercise(
    data: ExerciseFavoriteCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Marca exercício como favorito do usuário autenticado.

    **Permissões:** Qualquer usuário autenticado
    
    **Body:** { "exercise_id": "uuid" }

    **Errors:**
    - 404: Exercício não encontrado
    - 409: Já é favorito (PK composta impede duplicatas)
    """
    service = ExerciseService(db)
    fav = await service.favorite_exercise(ctx.user_id, data.exercise_id)
    return fav


@router.delete(
    "/exercise-favorites/{exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover dos favoritos",
    description="Remove exercício dos favoritos do usuário atual.",
    tags=["exercise-favorites"]
)
async def unfavorite_exercise(
    exercise_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Remove exercício dos favoritos do usuário autenticado.

    **Permissões:** Qualquer usuário autenticado

    **Returns:** 204 No Content (sucesso mesmo se não era favorito)
    """
    service = ExerciseService(db)
    await service.unfavorite_exercise(ctx.user_id, exercise_id)
    return None


@router.get(
    "/exercise-favorites",
    response_model=List[ExerciseFavoriteResponse],
    summary="Listar meus favoritos",
    description="Lista exercícios favoritos do usuário atual.",
    tags=["exercise-favorites"]
)
async def list_my_favorites(
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Lista todos os exercícios favoritos do usuário autenticado.

    **Permissões:** Qualquer usuário autenticado
    """
    service = ExerciseService(db)
    favorites = await service.list_favorites(ctx.user_id)
    return favorites
