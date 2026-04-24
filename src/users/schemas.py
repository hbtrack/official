from __future__ import annotations

# CODEGEN CUTOVER — generated layer linked
from .generated import schemas as _gen_schemas  # noqa: F401


"""
Pydantic schemas para Django Ninja — módulo users.
Derivados de: contracts/schemas/users/user_profile.schema.json
Alinhados com: contracts/openapi/paths/users.yaml
"""

from typing import Optional
from uuid import UUID

from ninja import Schema
from pydantic import Field
from shared.middleware import get_current_flow_id as _get_flow_id

UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"

class UserProfileOut(Schema):
    """Response schema — userProfile (INV-USR-003: sem campos authn)."""
    id: UUID
    displayName: str
    roleLabel: str

    organizationId: Optional[UUID] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    statusLabel: Optional[str] = None
    positionLabel: Optional[str] = None
    preferredLanguage: Optional[str] = None
    avatarUrl: Optional[str] = None
    preferenceTags: list[str] = []
    teamIds: list[UUID] = []
    seasonIds: list[UUID] = []

class CreateUserIn(Schema):
    """Request body para POST /users (createUser)."""
    displayName: str
    roleLabel: str
    organizationId: Optional[UUID] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    positionLabel: Optional[str] = None
    preferredLanguage: Optional[str] = None
    avatarUrl: Optional[str] = None
    preferenceTags: list[str] = []
    teamIds: list[UUID] = []
    seasonIds: list[UUID] = []

class PatchUserIn(Schema):
    """Request body para PATCH /users/{userId} (patchUser). minProperties=1 validado no use case."""
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    displayName: Optional[str] = None
    roleLabel: Optional[str] = None
    statusLabel: Optional[str] = None
    positionLabel: Optional[str] = None
    preferredLanguage: Optional[str] = None
    avatarUrl: Optional[str] = None
    preferenceTags: Optional[list[str]] = None
    teamIds: Optional[list[UUID]] = None
    seasonIds: Optional[list[UUID]] = None

class UserListOut(Schema):
    """Response para GET /users (listUsers)."""
    items: list[UserProfileOut]
    nextPageToken: Optional[str] = None

class ProblemOut(Schema):
    """RFC 9457 Problem Details."""
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    traceId: str = Field(default_factory=_get_flow_id)
