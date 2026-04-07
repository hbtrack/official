
# CODEGEN CUTOVER — generated use cases linked
from .generated.application import use_cases as _gen_use_cases  # noqa: F401
from .generated.infrastructure import repository as _gen_repository  # noqa: F401


"""
Django Ninja Router do módulo identity_access.
Implementa EXATAMENTE os endpoints de contracts/openapi/paths/identity_access.yaml.
PERMISSIONS_IDENTITY_ACCESS.md governa RBAC por operação.

9 operações:
  authLogin, authLogout, authRefreshToken, authGetCurrentSession,
  listActiveSessions, revokeSession,
  listUserRoles, assignRole, revokeRole

OWASP API Security Top 10 (2023):
  API1/BOLA: session filtrada ao principalUserId do token
  API2/Broken Auth: JWT RS256 + rotação de refresh token
  API3/BOPLA: password nunca no response
  API4/Resource Consumption: pageSize máximo 100
  API5/BFLA: role verificado server-side em cada operação sensível
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from ninja import Router
from ninja.errors import HttpError

from .application.use_cases import (
    AssignRoleUseCase,
    GetCurrentSessionUseCase,
    ListActiveSessionsUseCase,
    ListUserRolesUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
    RevokeRoleUseCase,
    RevokeSessionUseCase,
)
from .domain.rules import (
    AuthError,
    InsufficientPrivilege,
    LastAdminProtection,
    SessionExpired,
    SessionRevoked,
)
from .infrastructure.repository import IdentityAccessRepository
from .schemas import (
    AssignRoleIn,
    AuthSessionOut,
    LoginIn,
    LoginOut,
    PaginatedSessionsOut,
    ProblemOut,
    RefreshIn,
    RefreshOut,
    UserRolesOut,
)

router = Router(tags=["identity_access"])

def _get_repo() -> IdentityAccessRepository:
    from .infrastructure.jwt_adapter import JWTAdapter
    return IdentityAccessRepository(jwt_port=JWTAdapter())

def _session_to_out(s) -> dict:
    return {
        "id": s.id,
        "principalUserId": s.principal_user_id,
        "sessionScopeLabel": s.session_scope_label,
        "roleLabels": s.role_labels or [],
        "authMethodLabel": s.auth_method_label,
        "mfaRequired": s.mfa_required,
        "mfaSatisfied": s.mfa_satisfied,
        "issuedAt": s.issued_at,
        "expiresAt": s.expires_at,
        "revokedAt": s.revoked_at,
    }

def _problem(status: int, title: str, detail: str = "") -> dict:
    return {"type": "about:blank", "title": title, "status": status, "detail": detail or None}

# ── FT-011: Autenticação ──────────────────────────────────────────────────────

@router.post(
    "/login",
    response={200: LoginOut, 400: ProblemOut, 401: ProblemOut, 429: ProblemOut},
    auth=None,
    operation_id="authLogin",
    summary="Authenticate user",
)
def auth_login(request, body: LoginIn):
    """POST /auth/login — authLogin. security: []"""
    if not body.email or not body.password:
        return 400, _problem(400, "Bad Request", "email e password são obrigatórios.")
    try:
        session, access_token, refresh_token = LoginUseCase(_get_repo()).execute(
            email=body.email,
            password=body.password,
        )
    except ValueError as exc:
        return 401, _problem(401, "Unauthorized", str(exc))
    return 200, {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "session": _session_to_out(session),
    }

@router.post(
    "/logout",
    response={204: None, 401: ProblemOut, 500: ProblemOut},
    operation_id="authLogout",
    summary="Revoke current session",
)
def auth_logout(request):
    """POST /auth/logout — authLogout. Revoga a sessão do Bearer token."""
    session_id = _extract_session_id(request)
    if session_id is None:
        return 401, _problem(401, "Unauthorized", "Token ausente ou inválido.")
    try:
        LogoutUseCase(_get_repo()).execute(session_id)
    except Exception as exc:
        return 500, _problem(500, "Internal Server Error", str(exc))
    return 204, None

@router.post(
    "/refresh",
    response={200: RefreshOut, 401: ProblemOut},
    auth=None,
    operation_id="authRefreshToken",
    summary="Refresh access token",
)
def auth_refresh(request, body: RefreshIn):
    """POST /auth/refresh — authRefreshToken. security: []"""
    if not body.refreshToken:
        return 401, _problem(401, "Unauthorized", "refreshToken ausente.")
    try:
        access_token, refresh_token = RefreshTokenUseCase(_get_repo()).execute(
            body.refreshToken
        )
    except (ValueError, SessionRevoked, SessionExpired) as exc:
        return 401, _problem(401, "Unauthorized", str(exc))
    return 200, {"accessToken": access_token, "refreshToken": refresh_token}

# ── FT-012: Gestão de Sessões ─────────────────────────────────────────────────

@router.get(
    "/me",
    response={200: AuthSessionOut, 401: ProblemOut, 500: ProblemOut},
    operation_id="authGetCurrentSession",
    summary="Get current session",
)
def auth_me(request):
    """GET /auth/me — authGetCurrentSession. BOLA: escopo ao token do caller."""
    session_id = _extract_session_id(request)
    if session_id is None:
        return 401, _problem(401, "Unauthorized", "Token ausente ou inválido.")
    try:
        session = GetCurrentSessionUseCase(_get_repo()).execute(session_id)
    except (ValueError, SessionRevoked, SessionExpired) as exc:
        return 401, _problem(401, "Unauthorized", str(exc))
    except Exception as exc:
        return 500, _problem(500, "Internal Server Error", str(exc))
    return 200, _session_to_out(session)

@router.get(
    "/sessions",
    response={200: PaginatedSessionsOut, 401: ProblemOut, 403: ProblemOut, 500: ProblemOut},
    operation_id="listActiveSessions",
    summary="List active sessions",
)
def list_active_sessions(
    request,
    pageSize: int = 20,
    pageToken: Optional[str] = None,
    principalUserId: Optional[UUID] = None,
):
    """GET /auth/sessions — listActiveSessions. BFLA: admin apenas."""
    caller_roles = _extract_roles(request)
    if not caller_roles:
        return 401, _problem(401, "Unauthorized", "Token ausente ou inválido.")
    try:
        sessions, next_token = ListActiveSessionsUseCase(_get_repo()).execute(
            caller_roles=caller_roles,
            page_size=pageSize,
            page_token=pageToken,
            principal_user_id=principalUserId,
        )
    except InsufficientPrivilege as exc:
        return 403, _problem(403, "Forbidden", str(exc))
    except Exception as exc:
        return 500, _problem(500, "Internal Server Error", str(exc))
    return 200, {
        "items": [_session_to_out(s) for s in sessions],
        "nextPageToken": next_token,
    }

@router.delete(
    "/sessions/{session_id}",
    response={204: None, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut, 409: ProblemOut, 500: ProblemOut},
    operation_id="revokeSession",
    summary="Revoke session by ID",
)
def revoke_session(request, session_id: UUID):
    """DELETE /auth/sessions/{sessionId} — revokeSession. BOLA + BFLA."""
    caller_user_id = _extract_user_id(request)
    caller_roles = _extract_roles(request)
    if caller_user_id is None:
        return 401, _problem(401, "Unauthorized", "Token ausente ou inválido.")
    try:
        RevokeSessionUseCase(_get_repo()).execute(
            session_id=session_id,
            caller_user_id=caller_user_id,
            caller_roles=caller_roles,
        )
    except InsufficientPrivilege as exc:
        return 403, _problem(403, "Forbidden", str(exc))
    except LookupError as exc:
        return 404, _problem(404, "Not Found", str(exc))
    except Exception as exc:
        return 500, _problem(500, "Internal Server Error", str(exc))
    return 204, None

# ── FT-013: Gestão de Roles RBAC ─────────────────────────────────────────────

@router.get(
    "/users/{user_id}/roles",
    response={200: UserRolesOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut, 500: ProblemOut},
    operation_id="listUserRoles",
    summary="List roles for user",
)
def list_user_roles(request, user_id: UUID):
    """GET /auth/users/{userId}/roles — listUserRoles. BFLA: admin ou coordinator."""
    caller_user_id = _extract_user_id(request)
    caller_roles = _extract_roles(request)
    if caller_user_id is None:
        return 401, _problem(401, "Unauthorized", "Token ausente ou inválido.")
    try:
        roles = ListUserRolesUseCase(_get_repo()).execute(
            user_id=user_id,
            caller_user_id=caller_user_id,
            caller_roles=caller_roles,
        )
    except InsufficientPrivilege as exc:
        return 403, _problem(403, "Forbidden", str(exc))
    except LookupError as exc:
        return 404, _problem(404, "Not Found", str(exc))
    except Exception as exc:
        return 500, _problem(500, "Internal Server Error", str(exc))
    return 200, {"userId": user_id, "roles": roles}

@router.post(
    "/users/{user_id}/roles",
    response={200: UserRolesOut, 400: ProblemOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut, 409: ProblemOut, 500: ProblemOut},
    operation_id="assignRole",
    summary="Assign role to user",
)
def assign_role(request, user_id: UUID, body: AssignRoleIn):
    """POST /auth/users/{userId}/roles — assignRole. BFLA: admin apenas."""
    caller_roles = _extract_roles(request)
    if not caller_roles:
        return 401, _problem(401, "Unauthorized", "Token ausente ou inválido.")
    try:
        roles = AssignRoleUseCase(_get_repo()).execute(
            user_id=user_id,
            role_label=body.roleLabel,
            caller_roles=caller_roles,
        )
    except InsufficientPrivilege as exc:
        return 403, _problem(403, "Forbidden", str(exc))
    except LookupError as exc:
        return 404, _problem(404, "Not Found", str(exc))
    except ValueError as exc:
        title = str(exc)
        if "já atribuído" in title:
            return 409, _problem(409, "Conflict", title)
        return 400, _problem(400, "Bad Request", title)
    except Exception as exc:
        return 500, _problem(500, "Internal Server Error", str(exc))
    return 200, {"userId": user_id, "roles": roles}

@router.delete(
    "/users/{user_id}/roles/{role_label}",
    response={204: None, 400: ProblemOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut, 409: ProblemOut, 500: ProblemOut},
    operation_id="revokeRole",
    summary="Revoke role from user",
)
def revoke_role(request, user_id: UUID, role_label: str):
    """DELETE /auth/users/{userId}/roles/{roleLabel} — revokeRole. BFLA: admin."""
    caller_roles = _extract_roles(request)
    if not caller_roles:
        return 401, _problem(401, "Unauthorized", "Token ausente ou inválido.")
    try:
        RevokeRoleUseCase(_get_repo()).execute(
            user_id=user_id,
            role_label=role_label,
            caller_roles=caller_roles,
        )
    except InsufficientPrivilege as exc:
        return 403, _problem(403, "Forbidden", str(exc))
    except LookupError as exc:
        return 404, _problem(404, "Not Found", str(exc))
    except LastAdminProtection as exc:
        return 409, _problem(409, "Conflict", str(exc))
    except Exception as exc:
        return 500, _problem(500, "Internal Server Error", str(exc))
    return 204, None

# ── Helpers de extração de claims do JWT ─────────────────────────────────────
# Stubs — serão substituídos pela integração real com JwtPort (ADR-007).
# Em produção: extrair sub e roleLabels do JWT RS256 decodificado no request.

def _extract_session_id(request) -> Optional[UUID]:
    """Extrai session_id dos claims do JWT Bearer."""
    session_id = getattr(request, "_session_id", None)
    if session_id:
        return session_id
    return None

def _extract_user_id(request) -> Optional[UUID]:
    """Extrai sub (principalUserId) do JWT Bearer."""
    user_id = getattr(request, "_principal_user_id", None)
    if user_id:
        return user_id
    return None

def _extract_roles(request) -> list[str]:
    """Extrai roleLabels do JWT Bearer."""
    return getattr(request, "_role_labels", [])
