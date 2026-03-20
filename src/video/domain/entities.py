"""
Entidades de domínio do módulo video.
Contratos: contracts/schemas/video/
Regras: DOMAIN_RULES_VIDEO.md | Invariantes: INVARIANTS_VIDEO.md
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID


class SessionState(StrEnum):
    DRAFT = "DRAFT"
    CAPTURING = "CAPTURING"
    SYNCING = "SYNCING"
    TRANSCODING = "TRANSCODING"
    PUBLISHED = "PUBLISHED"


class CaptureMode(StrEnum):
    PANORAMIC = "PANORAMIC"
    AUTO_FOLLOW = "AUTO_FOLLOW"
    MULTI_ANGLE = "MULTI_ANGLE"


class RetentionPolicy(StrEnum):
    KEEP_7_DAYS = "KEEP_7_DAYS"
    KEEP_30_DAYS = "KEEP_30_DAYS"
    KEEP_90_DAYS = "KEEP_90_DAYS"
    ARCHIVE_S3 = "ARCHIVE_S3"
    PUBLIC_FOREVER = "PUBLIC_FOREVER"


class SegmentState(StrEnum):
    OPEN = "OPEN"
    FINALIZED = "FINALIZED"


class TargetType(StrEnum):
    TECHNICAL_INTERNAL = "TECHNICAL_INTERNAL"
    PUBLIC_CDN = "PUBLIC_CDN"
    BROADCAST_PARTNER = "BROADCAST_PARTNER"


@dataclass
class MatchMediaSession:
    """
    Agregado raiz do módulo video.
    Orquestra: captura → ingestão → sincronização → transcodificação → distribuição.
    Schema: contracts/schemas/video/match_media_session.schema.json
    """
    id: UUID
    match_id: UUID
    state: SessionState
    capture_mode: CaptureMode
    retention_policy: RetentionPolicy
    created_at: datetime
    created_by_user_id: UUID
    last_timecode: int = 0
    technical_contact_user_id: Optional[UUID] = None

    def validate_invariants(self) -> None:
        """INV-VID-007: Toda sessão deve ter retentionPolicy explícita (padrão = KEEP_7_DAYS)."""
        assert self.retention_policy is not None, "INV-VID-007: retentionPolicy obrigatória"

    def can_be_edited(self) -> bool:
        """INV-VID-002: PUBLISHED é imutável."""
        return self.state != SessionState.PUBLISHED


@dataclass
class MediaSegment:
    """
    Segmento imutável de mídia capturado pelo edge node.
    Schema: contracts/schemas/video/media_segment.schema.json
    DR-VID-001: timecodeLogical único por sessão.
    DR-VID-005: imutável após FINALIZED.
    """
    id: UUID
    session_id: UUID
    timecode_logical: int
    timecode_label: str
    state: SegmentState
    codec_label: Optional[str] = None
    bitrate: Optional[int] = None
    duration_ms: Optional[int] = None
    source_edge_node_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    finalized_at: Optional[datetime] = None

    def validate_invariants(self) -> None:
        """INV-VID-003: timecodeLogical >= 0; DR-VID-001: deve ter timecode único."""
        assert self.timecode_logical >= 0, "INV-VID-001: timecodeLogical deve ser >= 0"

    def is_mutable(self) -> bool:
        """DR-VID-005: Segments são imutáveis após FINALIZED."""
        return self.state == SegmentState.OPEN


@dataclass
class ClipDefinition:
    """
    Recorte semântico de vídeo com contexto de negócio.
    Schema: contracts/schemas/video/clip_definition.schema.json
    INV-VID-005: Exige ao menos um contexto semântico.
    DR-VID-004: Clipping é sempre semântico.
    """
    id: UUID
    session_id: UUID
    from_timecode: int
    to_timecode: int
    scout_event_id: Optional[UUID] = None
    zone_label: Optional[str] = None
    athlete_ids: list[UUID] = field(default_factory=list)
    context_label: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by_user_id: Optional[UUID] = None

    def validate_invariants(self) -> None:
        """INV-VID-005: Clip sem contexto semântico é inválido."""
        if not self.scout_event_id and not self.zone_label and not self.athlete_ids:
            raise ValueError(
                "INV-VID-005: ClipDefinition exige ao menos um de: "
                "scout_event_id, zone_label ou athlete_ids"
            )
        if self.from_timecode >= self.to_timecode:
            raise ValueError("from_timecode deve ser menor que to_timecode")


@dataclass
class DistributionProfile:
    """
    Perfil de transcodificação e distribuição.
    Schema: contracts/schemas/video/distribution_profile.schema.json
    DR-VID-002: Dual pipeline (técnico + público).
    DR-VID-006: Transcodificação lazy (on-demand).
    """
    id: UUID
    profile_label: str
    target_type: TargetType
    codec_label: str
    bitrate: int
    session_id: Optional[UUID] = None
    published_at: Optional[datetime] = None
    published_by_user_id: Optional[UUID] = None
