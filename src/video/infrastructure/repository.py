"""
Repository do módulo video — queries Django ORM sem lógica de negócio.
Padrão: ADR-031 (Django ORM), CODE_ARCHITECTURE.md
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from .models import (
    ClipDefinitionModel,
    DistributionProfileModel,
    MatchMediaSessionModel,
    MediaSegmentModel,
)
from ..domain.entities import (
    CaptureMode,
    ClipDefinition,
    DistributionProfile,
    MatchMediaSession,
    MediaSegment,
    RetentionPolicy,
    SegmentState,
    SessionState,
    TargetType,
)


def _session_to_domain(m: MatchMediaSessionModel) -> MatchMediaSession:
    return MatchMediaSession(
        id=m.id,
        match_id=m.match_id,
        state=SessionState(m.state),
        capture_mode=CaptureMode(m.capture_mode),
        retention_policy=RetentionPolicy(m.retention_policy),
        created_at=m.created_at,
        created_by_user_id=m.created_by_user_id,
        last_timecode=m.last_timecode,
        technical_contact_user_id=m.technical_contact_user_id,
    )


def _segment_to_domain(m: MediaSegmentModel) -> MediaSegment:
    return MediaSegment(
        id=m.id,
        session_id=m.session_id,
        timecode_logical=m.timecode_logical,
        timecode_label=m.timecode_label,
        state=SegmentState(m.state),
        codec_label=m.codec_label,
        bitrate=m.bitrate,
        duration_ms=m.duration_ms,
        source_edge_node_id=m.source_edge_node_id,
        created_at=m.created_at,
        finalized_at=m.finalized_at,
    )


def _clip_to_domain(m: ClipDefinitionModel) -> ClipDefinition:
    return ClipDefinition(
        id=m.id,
        session_id=m.session_id,
        from_timecode=m.from_timecode,
        to_timecode=m.to_timecode,
        scout_event_id=m.scout_event_id,
        zone_label=m.zone_label,
        athlete_ids=list(m.athlete_ids) if m.athlete_ids else [],
        context_label=m.context_label,
        created_at=m.created_at,
        created_by_user_id=m.created_by_user_id,
    )


def _distribution_to_domain(m: DistributionProfileModel) -> DistributionProfile:
    return DistributionProfile(
        id=m.id,
        profile_label=m.profile_label,
        target_type=TargetType(m.target_type),
        codec_label=m.codec_label,
        bitrate=m.bitrate,
        session_id=m.session_id,
        published_at=m.published_at,
        published_by_user_id=m.published_by_user_id,
    )


class VideoRepository:
    # ── Sessions ──────────────────────────────────────────────────────────────

    def create_session(self, session: MatchMediaSession) -> MatchMediaSession:
        m = MatchMediaSessionModel.objects.create(
            id=session.id,
            match_id=session.match_id,
            state=session.state.value,
            capture_mode=session.capture_mode.value,
            retention_policy=session.retention_policy.value,
            last_timecode=session.last_timecode,
            technical_contact_user_id=session.technical_contact_user_id,
            created_by_user_id=session.created_by_user_id,
        )
        return _session_to_domain(m)

    def get_session_by_id(self, session_id: UUID) -> Optional[MatchMediaSession]:
        try:
            return _session_to_domain(MatchMediaSessionModel.objects.get(pk=session_id))
        except MatchMediaSessionModel.DoesNotExist:
            return None

    def list_sessions(
        self,
        match_id: Optional[UUID] = None,
        state: Optional[str] = None,
        created_at_from: Optional[datetime] = None,
        created_at_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[MatchMediaSession], int]:
        qs = MatchMediaSessionModel.objects.all()
        if match_id:
            qs = qs.filter(match_id=match_id)
        if state:
            qs = qs.filter(state=state)
        if created_at_from:
            qs = qs.filter(created_at__gte=created_at_from)
        if created_at_to:
            qs = qs.filter(created_at__lte=created_at_to)
        total = qs.count()
        offset = (page - 1) * page_size
        sessions = [_session_to_domain(m) for m in qs[offset : offset + page_size]]
        return sessions, total

    def update_session(self, session: MatchMediaSession) -> MatchMediaSession:
        m = MatchMediaSessionModel.objects.get(pk=session.id)
        m.state = session.state.value
        m.retention_policy = session.retention_policy.value
        m.technical_contact_user_id = session.technical_contact_user_id
        m.last_timecode = session.last_timecode
        m.save(update_fields=["state", "retention_policy", "technical_contact_user_id", "last_timecode", "updated_at"])
        return _session_to_domain(m)

    # ── Segments ─────────────────────────────────────────────────────────────

    def create_segment(self, segment: MediaSegment) -> MediaSegment:
        m = MediaSegmentModel.objects.create(
            id=segment.id,
            session_id=segment.session_id,
            timecode_logical=segment.timecode_logical,
            timecode_label=segment.timecode_label,
            state=segment.state.value,
            codec_label=segment.codec_label,
            bitrate=segment.bitrate,
            duration_ms=segment.duration_ms,
            source_edge_node_id=segment.source_edge_node_id,
        )
        return _segment_to_domain(m)

    def list_segments(
        self,
        session_id: UUID,
        state: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[MediaSegment], int]:
        qs = MediaSegmentModel.objects.filter(session_id=session_id).order_by("timecode_logical")
        if state:
            qs = qs.filter(state=state)
        total = qs.count()
        offset = (page - 1) * page_size
        segments = [_segment_to_domain(m) for m in qs[offset : offset + page_size]]
        return segments, total

    def timecode_exists_in_session(self, session_id: UUID, timecode_logical: int) -> bool:
        return MediaSegmentModel.objects.filter(session_id=session_id, timecode_logical=timecode_logical).exists()

    # ── Clips ─────────────────────────────────────────────────────────────────

    def create_clip(self, clip: ClipDefinition) -> ClipDefinition:
        m = ClipDefinitionModel.objects.create(
            id=clip.id,
            session_id=clip.session_id,
            from_timecode=clip.from_timecode,
            to_timecode=clip.to_timecode,
            scout_event_id=clip.scout_event_id,
            zone_label=clip.zone_label,
            athlete_ids=clip.athlete_ids,
            context_label=clip.context_label,
            created_by_user_id=clip.created_by_user_id,
        )
        return _clip_to_domain(m)

    def list_clips(
        self,
        session_id: UUID,
        scout_event_id: Optional[UUID] = None,
        zone_label: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ClipDefinition], int]:
        qs = ClipDefinitionModel.objects.filter(session_id=session_id).order_by("from_timecode")
        if scout_event_id:
            qs = qs.filter(scout_event_id=scout_event_id)
        if zone_label:
            qs = qs.filter(zone_label=zone_label)
        total = qs.count()
        offset = (page - 1) * page_size
        clips = [_clip_to_domain(m) for m in qs[offset : offset + page_size]]
        return clips, total

    # ── Distributions ─────────────────────────────────────────────────────────

    def create_distribution(self, dist: DistributionProfile) -> DistributionProfile:
        m = DistributionProfileModel.objects.create(
            id=dist.id,
            session_id=dist.session_id,
            profile_label=dist.profile_label,
            target_type=dist.target_type.value,
            codec_label=dist.codec_label,
            bitrate=dist.bitrate,
            published_at=dist.published_at,
            published_by_user_id=dist.published_by_user_id,
        )
        return _distribution_to_domain(m)

    def list_distributions(
        self,
        session_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[DistributionProfile], int]:
        qs = DistributionProfileModel.objects.filter(session_id=session_id).order_by("-created_at")
        total = qs.count()
        offset = (page - 1) * page_size
        dists = [_distribution_to_domain(m) for m in qs[offset : offset + page_size]]
        return dists, total

    def distribution_exists(self, dist_id: UUID) -> bool:
        """INV-VID-012: Idempotência — verifica se distribution_id já existe."""
        return DistributionProfileModel.objects.filter(pk=dist_id).exists()
