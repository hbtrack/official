from __future__ import annotations

# CODEGEN CUTOVER — generated layer linked
from .generated import schemas as _gen_schemas  # noqa: F401


"""
Pydantic schemas (Django Ninja) do módulo video.
Derivados dos contratos em contracts/openapi/paths/video.yaml e contracts/schemas/video/.
REGRA: Router implementa EXATAMENTE o contrato — sem campos extras, sem omissões.
"""
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID

from ninja import Schema
from pydantic import Field
from shared.middleware import get_current_flow_id as _get_flow_id

# ── Enums (alinhados com contracts/schemas/video/) ────────────────────────────

class SessionStateSchema(StrEnum):
    DRAFT = "DRAFT"
    CAPTURING = "CAPTURING"
    SYNCING = "SYNCING"
    TRANSCODING = "TRANSCODING"
    PUBLISHED = "PUBLISHED"

class CaptureModeSchema(StrEnum):
    PANORAMIC = "PANORAMIC"
    AUTO_FOLLOW = "AUTO_FOLLOW"
    MULTI_ANGLE = "MULTI_ANGLE"

class RetentionPolicySchema(StrEnum):
    KEEP_7_DAYS = "KEEP_7_DAYS"
    KEEP_30_DAYS = "KEEP_30_DAYS"
    KEEP_90_DAYS = "KEEP_90_DAYS"
    ARCHIVE_S3 = "ARCHIVE_S3"
    PUBLIC_FOREVER = "PUBLIC_FOREVER"

class SegmentStateSchema(StrEnum):
    OPEN = "OPEN"
    FINALIZED = "FINALIZED"

class TargetTypeSchema(StrEnum):
    TECHNICAL_INTERNAL = "TECHNICAL_INTERNAL"
    PUBLIC_CDN = "PUBLIC_CDN"
    BROADCAST_PARTNER = "BROADCAST_PARTNER"

# ── MatchMediaSession ─────────────────────────────────────────────────────────

class CreateSessionIn(Schema):
    matchId: UUID
    captureMode: CaptureModeSchema
    retentionPolicy: RetentionPolicySchema
    technicalContactUserId: Optional[UUID] = None

class PatchSessionIn(Schema):
    state: Optional[SessionStateSchema] = None
    retentionPolicy: Optional[RetentionPolicySchema] = None
    technicalContactUserId: Optional[UUID] = None

class MatchMediaSessionOut(Schema):
    id: UUID
    matchId: UUID
    state: SessionStateSchema
    captureMode: CaptureModeSchema
    retentionPolicy: RetentionPolicySchema
    lastTimecode: int
    technicalContactUserId: Optional[UUID]
    createdAt: datetime
    createdByUserId: UUID

# ── MediaSegment ──────────────────────────────────────────────────────────────

class CreateSegmentIn(Schema):
    sessionId: UUID
    timecodeLogical: int
    timecodeLabel: str
    codecLabel: Optional[str] = None
    bitrate: Optional[int] = None
    durationMs: Optional[int] = None
    sourceEdgeNodeId: Optional[UUID] = None

class MediaSegmentOut(Schema):
    id: UUID
    sessionId: UUID
    timecodeLogical: int
    timecodeLabel: str
    state: SegmentStateSchema
    codecLabel: Optional[str]
    bitrate: Optional[int]
    durationMs: Optional[int]
    sourceEdgeNodeId: Optional[UUID]
    createdAt: Optional[datetime]
    finalizedAt: Optional[datetime]

# ── ClipDefinition ────────────────────────────────────────────────────────────

class CreateClipIn(Schema):
    sessionId: UUID
    fromTimecode: int
    toTimecode: int
    scoutEventId: Optional[UUID] = None
    zoneLabel: Optional[str] = None
    athleteIds: Optional[list[UUID]] = None
    contextLabel: Optional[str] = None

class ClipDefinitionOut(Schema):
    id: UUID
    sessionId: UUID
    fromTimecode: int
    toTimecode: int
    scoutEventId: Optional[UUID]
    zoneLabel: Optional[str]
    athleteIds: list[UUID]
    contextLabel: Optional[str]
    createdAt: Optional[datetime]
    createdByUserId: Optional[UUID]

# ── DistributionProfile ───────────────────────────────────────────────────────

class PublishDistributionIn(Schema):
    sessionId: UUID
    distributionProfileId: UUID
    targetLabel: TargetTypeSchema
    profileLabel: str = "default"
    codecLabel: str = "H264"
    bitrate: int = 2500

class DistributionProfileOut(Schema):
    id: UUID
    sessionId: Optional[UUID]
    profileLabel: str
    targetType: TargetTypeSchema
    codecLabel: str
    bitrate: int
    publishedAt: Optional[datetime]
    publishedByUserId: Optional[UUID]

# ── Paginação (conforme api_rules.yaml) ───────────────────────────────────────

class PaginatedSessionsOut(Schema):
    data: list[MatchMediaSessionOut]
    total: int
    page: int
    pageSize: int

class PaginatedSegmentsOut(Schema):
    data: list[MediaSegmentOut]
    total: int
    page: int
    pageSize: int

class PaginatedClipsOut(Schema):
    data: list[ClipDefinitionOut]
    total: int
    page: int
    pageSize: int

class PaginatedDistributionsOut(Schema):
    data: list[DistributionProfileOut]
    total: int
    page: int
    pageSize: int

# ── Error (problem+json conforme api_rules.yaml) ──────────────────────────────

class ProblemOut(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    traceId: str = Field(default_factory=_get_flow_id)
