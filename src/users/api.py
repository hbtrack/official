
# CODEGEN CUTOVER — generated use cases linked
from .generated.application import use_cases as _gen_use_cases  # noqa: F401
from .generated.infrastructure import repository as _gen_repository  # noqa: F401


"""
Django Ninja Router — módulo users.
Implementa EXATAMENTE o contrato: contracts/openapi/paths/users.yaml
4 operações: listUsers, createUser, getUser, patchUser
Segurança: HTTPBearer (JWT stub — integração real via identity_access)
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from ninja import Router
from ninja.errors import HttpError

from .application.use_cases import (
    CreateUserInput,
    CreateUserUseCase,
    GetUserInput,
    GetUserUseCase,
    ListUsersInput,
    ListUsersUseCase,
    PatchUserInput,
    PatchUserUseCase,
)
from .domain.entities import RoleLabel, UserProfile, UserStatus
from .domain.rules import (
    AuthnFieldForbidden,
    InsufficientPrivilege,
    UserConflict,
    UserNotFound,
)
from .infrastructure.repository import UsersRepository
from .schemas import (
    CreateUserIn,
    PatchUserIn,
    ProblemOut,
    UserListOut,
    UserProfileOut,
)

router = Router(tags=["users"])

# ---------------------------------------------------------------------------
# Helpers JWT (stubs — substituir por integração real com identity_access)
# ---------------------------------------------------------------------------

def _get_actor_id(request) -> UUID:
    """Extrai sub do JWT — stub retorna UUID fixo para desenvolvimento."""
    actor_id = getattr(request, "_actor_id", None)
    if actor_id:
        return UUID(str(actor_id))
    raise HttpError(401, "Unauthenticated")

def _get_actor_role(request) -> RoleLabel:
    """Extrai role do JWT claims."""
    role = getattr(request, "_actor_role", None)
    if role:
        return RoleLabel(role)
    raise HttpError(401, "Unauthenticated")

def _get_actor_team_ids(request) -> list[UUID]:
    """Extrai teamIds do JWT claims (DR-USR-003)."""
    raw = getattr(request, "_actor_team_ids", [])
    return [UUID(str(t)) for t in (raw or [])]

def _profile_to_out(p: UserProfile) -> UserProfileOut:
    return UserProfileOut(
        id=p.id,
        displayName=p.display_name,
        roleLabel=str(p.role_label),
        organizationId=p.organization_id,
        firstName=p.first_name,
        lastName=p.last_name,
        statusLabel=str(p.status_label) if p.status_label else None,
        positionLabel=p.position_label,
        preferredLanguage=p.preferred_language,
        preferenceTags=p.preference_tags,
        teamIds=p.team_ids,
        seasonIds=p.season_ids,
    )

# ---------------------------------------------------------------------------
# GET /users — listUsers (FT-014)
# ---------------------------------------------------------------------------

@router.get(
    "",
    response={200: UserListOut, 400: ProblemOut, 401: ProblemOut, 403: ProblemOut, 500: ProblemOut},
    summary="List users",
    operation_id="listUsers",
)
def list_users(
    request,
    organizationId: Optional[UUID] = None,
    teamId: Optional[UUID] = None,
    roleLabel: Optional[str] = None,
    pageSize: int = 50,
    pageToken: Optional[str] = None,
):
    """Lista perfis de usuário com paginação cursor-based (OWASP API4:2023)."""
    actor_id = _get_actor_id(request)
    actor_role = _get_actor_role(request)
    actor_team_ids = _get_actor_team_ids(request)

    role_filter: RoleLabel | None = None
    if roleLabel:
        try:
            role_filter = RoleLabel(roleLabel)
        except ValueError:
            raise HttpError(400, f"roleLabel '{roleLabel}' inválido")

    inp = ListUsersInput(
        actor_id=actor_id,
        actor_role=actor_role,
        actor_team_ids=actor_team_ids,
        organization_id=organizationId,
        team_id=teamId,
        role_label=role_filter,
        page_size=pageSize,
        page_token=pageToken,
    )
    try:
        result = ListUsersUseCase(UsersRepository()).execute(inp)
        return 200, UserListOut(
            items=[_profile_to_out(p) for p in result.items],
            nextPageToken=result.next_page_token,
        )
    except InsufficientPrivilege as e:
        raise HttpError(403, str(e))

# ---------------------------------------------------------------------------
# POST /users — createUser (FT-015)
# ---------------------------------------------------------------------------

@router.post(
    "",
    response={201: UserProfileOut, 400: ProblemOut, 401: ProblemOut, 403: ProblemOut, 409: ProblemOut, 500: ProblemOut},
    summary="Create user profile",
    operation_id="createUser",
)
def create_user(request, body: CreateUserIn):
    """Cria novo perfil de usuário (admin/coordinator only — PERM-USR-002)."""
    actor_role = _get_actor_role(request)

    try:
        role_label = RoleLabel(body.roleLabel)
    except ValueError:
        raise HttpError(400, f"roleLabel '{body.roleLabel}' inválido")

    inp = CreateUserInput(
        actor_role=actor_role,
        display_name=body.displayName,
        role_label=role_label,
        organization_id=body.organizationId,
        first_name=body.firstName,
        last_name=body.lastName,
        position_label=body.positionLabel,
        preferred_language=body.preferredLanguage,
        preference_tags=body.preferenceTags,
        team_ids=body.teamIds,
        season_ids=body.seasonIds,
    )
    try:
        profile = CreateUserUseCase(UsersRepository()).execute(inp)
        return 201, _profile_to_out(profile)
    except InsufficientPrivilege as e:
        raise HttpError(403, str(e))
    except UserConflict as e:
        raise HttpError(409, str(e))
    except ValueError as e:
        raise HttpError(400, str(e))

# ---------------------------------------------------------------------------
# GET /users/{userId} — getUser (FT-016)
# ---------------------------------------------------------------------------

@router.get(
    "/{userId}",
    response={200: UserProfileOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut, 500: ProblemOut},
    summary="Get user profile",
    operation_id="getUser",
)
def get_user(request, userId: UUID):
    """Retorna perfil completo de um usuário (BOLA — OWASP API1:2023)."""
    actor_id = _get_actor_id(request)
    actor_role = _get_actor_role(request)
    actor_team_ids = _get_actor_team_ids(request)

    inp = GetUserInput(
        actor_id=actor_id,
        actor_role=actor_role,
        actor_team_ids=actor_team_ids,
        target_user_id=userId,
    )
    try:
        profile = GetUserUseCase(UsersRepository()).execute(inp)
        return 200, _profile_to_out(profile)
    except UserNotFound as e:
        raise HttpError(404, str(e))
    except InsufficientPrivilege as e:
        raise HttpError(403, str(e))

# ---------------------------------------------------------------------------
# PATCH /users/{userId} — patchUser (FT-017)
# ---------------------------------------------------------------------------

@router.patch(
    "/{userId}",
    response={200: UserProfileOut, 400: ProblemOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut, 409: ProblemOut, 500: ProblemOut},
    summary="Update user profile",
    operation_id="patchUser",
)
def patch_user(request, userId: UUID, body: PatchUserIn):
    """Atualiza parcialmente o perfil de um usuário (BOLA + BFLA — PERM-USR-003..009)."""
    actor_id = _get_actor_id(request)
    actor_role = _get_actor_role(request)

    # Validar roleLabel se fornecido
    role_label: RoleLabel | None = None
    if body.roleLabel is not None:
        try:
            role_label = RoleLabel(body.roleLabel)
        except ValueError:
            raise HttpError(400, f"roleLabel '{body.roleLabel}' inválido")

    # Validar statusLabel se fornecido
    status_label: UserStatus | None = None
    if body.statusLabel is not None:
        try:
            status_label = UserStatus(body.statusLabel)
        except ValueError:
            raise HttpError(400, f"statusLabel '{body.statusLabel}' inválido")

    inp = PatchUserInput(
        actor_id=actor_id,
        actor_role=actor_role,
        target_user_id=userId,
        first_name=body.firstName,
        last_name=body.lastName,
        display_name=body.displayName,
        role_label=role_label,
        status_label=status_label,
        position_label=body.positionLabel,
        preferred_language=body.preferredLanguage,
        preference_tags=body.preferenceTags,
        team_ids=body.teamIds,
        season_ids=body.seasonIds,
    )
    try:
        profile = PatchUserUseCase(UsersRepository()).execute(inp)
        return 200, _profile_to_out(profile)
    except UserNotFound as e:
        raise HttpError(404, str(e))
    except InsufficientPrivilege as e:
        raise HttpError(403, str(e))
    except AuthnFieldForbidden as e:
        raise HttpError(400, str(e))
    except ValueError as e:
        raise HttpError(400, str(e))
