"""
Router FastAPI para Users.

V1.2 - Atualizado para novo modelo de vínculos.

Conforme definido em:
- docs/openapi/rbac.yaml (OpenAPI 3.1)
- backend/REGRAS.md (V1.2)

Endpoints:
- GET    /v1/users              - Listar usuários (paginado)
- POST   /v1/users              - Criar usuário
- GET    /v1/users/{user_id}    - Obter usuário por ID
- PATCH  /v1/users/{user_id}    - Atualizar usuário

Regras de negócio V1.2:
- RF1: Super Admin pode criar todos os papéis
- RF1.1: Vínculos automáticos por papel:
  - Dirigente: NÃO cria vínculo automático (vincula ao fundar/solicitar org)
  - Coordenador/Treinador: Cria vínculo automático com org do criador
  - Atleta: NÃO cria user automático (opcional)
- R25/R26: Permissões por papel e escopo
- R29/R33: Exclusão lógica e histórico com rastro
- R31/R32: Ações críticas auditadas

Erros mapeados:
- 401 unauthorized: Token inválido ou ausente
- 403 permission_denied: Permissão insuficiente
- 404 not_found: Usuário não encontrado
- 409 conflict_unique: Email já cadastrado
- 422 validation_error: Payload inválido
"""

from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.auth import get_current_user, require_role
from app.core.context import ExecutionContext
from app.core.db import get_async_db
from app.models.person import Person
from app.models.user import User as UserModel
from app.models.membership import OrgMembership
from app.models.athlete import Athlete
from app.models.team_registration import TeamRegistration
from app.schemas.error import ErrorResponse
from app.schemas.rbac import (
    OrderDirection,
    User as UserSchema,
    UserCreate,
    UserOrderBy,
    UserPaginatedResponse,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(
    tags=["users"],
)


# =============================================================================
# GET /v1/users - Listar usuários (paginado)
# =============================================================================

@router.get(
    "",
    response_model=UserPaginatedResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
    },
    summary="Listar usuários (paginado)",
    description="""
Lista paginada de usuários do sistema.

**Regras aplicáveis:** R25/R26 (permissões), R42 (vínculo ativo), R29/R33 (histórico)

**Comportamento:**
- Retorna usuários ativos por padrão
- Filtrar por search (full_name/email) quando necessário
- Escopo organizacional aplicado automaticamente via JWT (R34)
""",
)
async def list_users(
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    order_by: UserOrderBy = Query(
        UserOrderBy.CREATED_AT,
        description="Campo para ordenação"
    ),
    order_dir: OrderDirection = Query(
        OrderDirection.DESC,
        description="Direção da ordenação"
    ),
    search: Optional[str] = Query(None, description="Busca por full_name ou email"),
):
    """
    Lista usuários (paginado).
    
    Regras:
    - R25/R26: Verificar permissões do ator
    - R42: Ator deve ter vínculo ativo
    """
    service = UserService(db)
    items, total = await service.list_users(page=page, limit=limit)
    
    return UserPaginatedResponse(
        items=[UserSchema.model_validate(u) for u in items],
        page=page,
        limit=limit,
        total=total,
    )


# =============================================================================
# POST /v1/users - Criar usuário
# =============================================================================

@router.post(
    "",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        409: {"model": ErrorResponse, "description": "Email já cadastrado"},
        422: {"model": ErrorResponse, "description": "Payload inválido"},
    },
    summary="Criar usuário",
    description="""
Cria um novo usuário no sistema.

**Regras V1.2 aplicáveis:**
- RF1: Cadeia hierárquica de criação (Super Admin > Dirigente > Coordenador > Treinador)
- RF1.1: Vínculos automáticos por papel:
  - Dirigente: NÃO cria vínculo organizacional automático
  - Coordenador/Treinador: Cria vínculo automático (org_membership) com organização do criador
  - Atleta: Usado endpoint específico de atletas
- R25/R26: Permissões por papel e escopo
- R31/R32: Auditoria de criação
""",
)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
):
    """
    Cria usuário (V1.2).

    Regras:
    - RF1: Super Admin pode criar todos os papéis
    - RF1.1: Vínculos automáticos conforme papel:
      - Dirigente: NÃO cria org_membership (vincula ao fundar/solicitar org)
      - Coordenador/Treinador: Cria org_membership com org do criador
    - R1: Person deve existir antes (person_id obrigatório)
    - R3: Email único
    - R31/R32: Auditoria
    """
    service = UserService(db)

    role_code = payload.role.lower().strip()
    
    # Validação: superadmin não pode ser criado via API
    if role_code in ("superadmin", "super_administrador"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "invalid_role", "message": "Superadmin não pode ser criado via API"},
        )

    # RF1: Validar cadeia hierárquica de criação
    if not current_user.is_superadmin:
        # Super Admin pode criar qualquer papel
        # Outros papéis têm restrições
        allowed = {
            "dirigente": {"coordenador", "treinador", "atleta"},
            "coordenador": {"treinador", "atleta"},
            "treinador": {"atleta"},
        }
        allowed_roles = allowed.get(current_user.role_code, set())
        if role_code not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "permission_denied", "message": f"Papel '{current_user.role_code}' não pode criar '{role_code}'"},
            )

    try:
        # R1: Person deve existir (person_id é obrigatório no V1.2)
        person_id = payload.person_id
        person = db.get(Person, str(person_id))
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "person_not_found", "message": f"Person {person_id} não encontrada"},
            )
        
        # Verificar se person já tem user
        existing_user = db.scalar(
            select(UserModel).where(
                UserModel.person_id == str(person_id),
                UserModel.deleted_at.is_(None),
            )
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "user_exists", "message": "Esta pessoa já possui um usuário no sistema"},
            )

        # Hash da senha
        from app.core.security import hash_password
        if payload.password:
            password_hash = hash_password(payload.password)
        else:
            # Senha temporária (usuário definirá via email)
            import secrets
            temp_password = secrets.token_urlsafe(32)
            password_hash = hash_password(temp_password)

        # Criar usuário
        user = await service.create(
            payload,
            person_id=person_id,
            password_hash=password_hash,
        )
        await db.flush()

        # RF1.1: Criar vínculo organizacional automático (apenas para coordenador/treinador)
        # Dirigente NÃO cria vínculo automático - vincula ao fundar ou solicitar org
        if role_code in ("coordenador", "treinador"):
            # Precisa de organização do criador
            if not current_user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": "no_organization", "message": "Criador não possui organização para vincular o novo usuário"},
                )
            
            # Resolver role_id
            from app.models.role import Role
            role = db.scalar(
                select(Role).where(Role.code == role_code)
            )
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"code": "invalid_role", "message": f"Papel '{role_code}' não encontrado"},
                )

            # Verificar se já existe vínculo ativo
            existing_membership = db.scalar(
                select(OrgMembership).where(
                    OrgMembership.organization_id == str(current_user.organization_id),
                    OrgMembership.person_id == str(person_id),
                    OrgMembership.role_id == role.id,
                    OrgMembership.end_at.is_(None),
                    OrgMembership.deleted_at.is_(None),
                )
            )

            if existing_membership:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"code": "membership_exists", "message": "Pessoa já possui vínculo ativo nesta organização com este papel"},
                )

            # Criar org_membership (V1.2 - sem season_id)
            org_membership = OrgMembership(
                organization_id=str(current_user.organization_id),
                person_id=str(person_id),
                role_id=role.id,
                start_at=datetime.now(timezone.utc),
            )
            db.add(org_membership)

        # Atleta: não criar vínculo aqui - usar endpoint específico /athletes
        if role_code == "atleta":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "use_athlete_endpoint", "message": "Para criar atleta com usuário, use o endpoint /athletes com checkbox 'criar acesso'"},
            )

        db.commit()
        
        # Enviar email de boas-vindas com link para criar senha
        if payload.send_welcome_email:
            try:
                from app.services.email_service import email_service
                from app.services.password_reset_service import PasswordResetService
                from app.core.config import settings
                
                reset_service = PasswordResetService(db)
                reset = await reset_service.create_reset_token(
                    user_id=user.id,
                    token_type="welcome",
                    expires_in_hours=48,
                )
                
                reset_link = f"{settings.FRONTEND_URL}/new-password?token={reset.token}"
                
                # Buscar nome da pessoa
                person = db.get(Person, str(person_id))
                user_name = person.full_name if person else None
                
                await email_service.send_welcome_email(
                    user_email=user.email,
                    reset_link=reset_link,
                    user_name=user_name,
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send welcome email for user {user.id}: {str(e)}")
        
        return UserSchema.model_validate(user)
    
    except HTTPException:
        raise
    except ValueError as e:
        error_code = str(e)
        if error_code == "email_already_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "email_already_exists", "message": "Email ja cadastrado"}
            )
        if error_code in {"organization_not_found", "multiple_organizations"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": error_code, "message": "Organizacao invalida"},
            )
        if error_code == "season_not_found":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "no_active_season", "message": "Nao ha temporada disponivel"}
            )
        if error_code == "role_not_found":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "invalid_role", "message": "Papel invalido"}
            )
        if error_code in {"institutional_team_missing", "institutional_team_mismatch", "category_not_found"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": error_code, "message": "Equipe institucional nao configurada"}
            )
        raise


# =============================================================================
# GET /v1/users/me - Obter usuário atual (DEVE VIR ANTES DE /{user_id})
# =============================================================================

@router.get(
    "/me",
    response_model=UserSchema,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
    },
    summary="Obter usuário atual",
    description="""
Retorna os dados do usuário autenticado.

Útil para obter informações do perfil do usuário logado.
""",
)
async def get_current_user_profile(
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
):
    """
    Obtém dados do usuário atual (logado).
    """
    service = UserService(db)
    user = await service.get_by_id(current_user.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Usuário não encontrado"}
        )
    
    return UserSchema.model_validate(user)


# =============================================================================
# GET /v1/users/{user_id} - Obter usuário por ID
# =============================================================================

@router.get(
    "/{user_id}",
    response_model=UserSchema,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        404: {"model": ErrorResponse, "description": "Usuário não encontrado"},
    },
    summary="Obter usuário por ID",
    description="""
Retorna os dados de um usuário específico.

**Regras aplicáveis:** R25/R26 (permissões)
""",
)
async def get_user_by_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
):
    """
    Obtém usuário por ID.
    
    Regras:
    - R25/R26: Verificar permissões do ator
    """
    service = UserService(db)
    user = await service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Usuário não encontrado"}
        )
    
    return UserSchema.model_validate(user)


# =============================================================================
# PATCH /v1/users/{user_id} - Atualizar usuário
# =============================================================================

@router.patch(
    "/{user_id}",
    response_model=UserSchema,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        409: {"model": ErrorResponse, "description": "Email já cadastrado"},
        422: {"model": ErrorResponse, "description": "Payload inválido"},
    },
    summary="Atualizar usuário",
    description="""
Atualiza dados de um usuário existente.

**Regras aplicáveis:** R25/R26 (permissões), R31/R32 (auditoria)

**Comportamento:**
- Valida unicidade de email (se alterado)
- Registra auditoria da alteração (R31/R32)
""",
)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
):
    """
    Atualiza usuário.
    
    Regras:
    - R25/R26: Verificar permissões do ator
    - R31/R32: Registrar auditoria
    """
    service = UserService(db)
    user = await service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Usuário não encontrado"}
        )
    
    try:
        updated = await service.update(user, payload)
        await db.commit()
        return UserSchema.model_validate(updated)
    except ValueError as e:
        error_code = str(e)
        if error_code == "email_already_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "email_already_exists", "message": "Email já cadastrado"}
            )
        elif error_code == "user_deleted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "user_deleted", "message": "Usuário já foi deletado"}
            )
        raise


# =============================================================================
# DELETE /v1/users/{user_id} - Excluir usuário (soft delete)
# =============================================================================

class DeleteRequest(BaseModel):
    """Payload para exclusão."""
    reason: Optional[str] = None


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        404: {"model": ErrorResponse, "description": "Usuário não encontrado"},
    },
    summary="Excluir usuário (soft delete)",
    description="""
Exclui um usuário do sistema (soft delete).

**Regras aplicáveis:** R25/R26 (permissões), R29/R33 (soft delete)

**Comportamento:**
- Soft delete: marca deleted_at e deleted_reason
- Não remove fisicamente do banco
""",
)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(require_role(["dirigente"])),
):
    """
    Exclui usuário (soft delete).
    
    Regras:
    - R25/R26: Verificar permissões do ator
    - R29: Soft delete obrigatório
    """
    service = UserService(db)
    user = await service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Usuário não encontrado"}
        )

    if not current_user.is_superadmin:
        membership = db.scalar(
            select(OrgMembership).where(
                OrgMembership.person_id == str(user.person_id),
                OrgMembership.organization_id == str(current_user.organization_id),
                OrgMembership.end_at.is_(None),
                OrgMembership.deleted_at.is_(None),
            )
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "permission_denied", "message": "Usuário fora da organização"},
            )
    
    try:
        await service.soft_delete(user, reason="Exclusão administrativa")
        await db.commit()
        return None
    except ValueError as e:
        if str(e) == "already_deleted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "already_deleted", "message": "Usuário já foi excluído"}
            )
        raise


# =============================================================================
# POST /v1/users/{user_id}/reset-password - Resetar senha
# =============================================================================

class ResetPasswordRequest(BaseModel):
    """Payload para reset de senha."""
    new_password: str


@router.post(
    "/{user_id}/reset-password",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido ou ausente"},
        403: {"model": ErrorResponse, "description": "Permissão insuficiente"},
        404: {"model": ErrorResponse, "description": "Usuário não encontrado"},
    },
    summary="Resetar senha do usuário",
)
async def reset_user_password(
    user_id: UUID,
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(require_role(["dirigente", "coordenador"])),
):
    """Reseta a senha de um usuário."""
    service = UserService(db)
    user = await service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Usuário não encontrado"}
        )

    if not current_user.is_superadmin:
        membership = db.scalar(
            select(OrgMembership).where(
                OrgMembership.person_id == str(user.person_id),
                OrgMembership.organization_id == str(current_user.organization_id),
                OrgMembership.end_at.is_(None),
                OrgMembership.deleted_at.is_(None),
            )
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "permission_denied", "message": "Usuário fora da organização"},
            )
    
    from app.core.security import hash_password
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    
    return {"message": "Senha alterada com sucesso"}
