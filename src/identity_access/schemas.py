"""
Pydantic schemas (Django Ninja) do módulo identity_access.
Derivados do contrato: contracts/openapi/paths/identity_access.yaml
                        contracts/schemas/identity_access/auth_session.schema.json
REGRA: Router implementa EXATAMENTE o contrato — sem campos extras, sem omissões.
OWASP API3:2023: password nunca aparece em schemas de saída.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ninja import Schema


# ── AuthSession (contrato: auth_session.schema.json) ─────────────────────────

class AuthSessionOut(Schema):
    """Projeção HTTP de AuthSession — alinhada com auth_session.schema.json."""
    id: UUID
    principalUserId: UUID
    sessionScopeLabel: str
    roleLabels: List[str] = []
    authMethodLabel: Optional[str] = None
    mfaRequired: Optional[bool] = None
    mfaSatisfied: Optional[bool] = None
    issuedAt: Optional[datetime] = None
    expiresAt: Optional[datetime] = None
    revokedAt: Optional[datetime] = None


class PaginatedSessionsOut(Schema):
    items: List[AuthSessionOut]
    nextPageToken: Optional[str] = None


# ── Login ─────────────────────────────────────────────────────────────────────

class LoginIn(Schema):
    """POST /auth/login — credenciais de acesso."""
    email: str
    password: str  # writeOnly — nunca retornado em nenhum schema de saída


class LoginOut(Schema):
    """200 em POST /auth/login."""
    accessToken: str
    refreshToken: str
    session: AuthSessionOut


# ── Refresh ───────────────────────────────────────────────────────────────────

class RefreshIn(Schema):
    """POST /auth/refresh."""
    refreshToken: str


class RefreshOut(Schema):
    """200 em POST /auth/refresh."""
    accessToken: str
    refreshToken: str


# ── Role management ───────────────────────────────────────────────────────────

class UserRolesOut(Schema):
    """200 em GET/POST /auth/users/{userId}/roles."""
    userId: UUID
    roles: List[str]


class AssignRoleIn(Schema):
    """POST /auth/users/{userId}/roles."""
    roleLabel: str


# ── Erro (application/problem+json) ──────────────────────────────────────────

class ProblemOut(Schema):
    """RFC 9457 Problem Details — application/problem+json."""
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
