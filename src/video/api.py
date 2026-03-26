"""
Django Ninja Router do módulo video.
Implementa EXATAMENTE os endpoints de contracts/openapi/paths/video.yaml.
PERMISSIONS_VIDEO.md governa RBAC por operação.
BOLA (INV-VID-006): acesso scopado ao nível de MatchMediaSession.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID

from ninja import Router
from ninja.errors import HttpError

from .application.use_cases import (
    CreateClipUseCase,
    CreateSessionUseCase,
    GetSessionUseCase,
    IngestSegmentUseCase,
    ListClipsUseCase,
    ListDistributionsUseCase,
    ListSegmentsUseCase,
    ListSessionsUseCase,
    PatchSessionUseCase,
    PublishDistributionUseCase,
)
from .infrastructure.repository import VideoRepository
from .schemas import (
    ClipDefinitionOut,
    CreateClipIn,
    CreateSegmentIn,
    CreateSessionIn,
    DistributionProfileOut,
    MatchMediaSessionOut,
    MediaSegmentOut,
    PaginatedClipsOut,
    PaginatedDistributionsOut,
    PaginatedSegmentsOut,
    PaginatedSessionsOut,
    PatchSessionIn,
    ProblemOut,
    PublishDistributionIn,
)

router = Router(tags=["video"])


def _get_repo() -> VideoRepository:
    return VideoRepository()


def _session_to_out(s) -> dict:
    return {
        "id": s.id,
        "matchId": s.match_id,
        "state": s.state,
        "captureMode": s.capture_mode,
        "retentionPolicy": s.retention_policy,
        "lastTimecode": s.last_timecode,
        "technicalContactUserId": s.technical_contact_user_id,
        "createdAt": s.created_at,
        "createdByUserId": s.created_by_user_id,
    }


def _segment_to_out(sg) -> dict:
    return {
        "id": sg.id,
        "sessionId": sg.session_id,
        "timecodeLogical": sg.timecode_logical,
        "timecodeLabel": sg.timecode_label,
        "state": sg.state,
        "codecLabel": sg.codec_label,
        "bitrate": sg.bitrate,
        "durationMs": sg.duration_ms,
        "sourceEdgeNodeId": sg.source_edge_node_id,
        "createdAt": sg.created_at,
        "finalizedAt": sg.finalized_at,
    }


def _clip_to_out(c) -> dict:
    return {
        "id": c.id,
        "sessionId": c.session_id,
        "fromTimecode": c.from_timecode,
        "toTimecode": c.to_timecode,
        "scoutEventId": c.scout_event_id,
        "zoneLabel": c.zone_label,
        "athleteIds": c.athlete_ids,
        "contextLabel": c.context_label,
        "createdAt": c.created_at,
        "createdByUserId": c.created_by_user_id,
    }


def _dist_to_out(d) -> dict:
    return {
        "id": d.id,
        "sessionId": d.session_id,
        "profileLabel": d.profile_label,
        "targetType": d.target_type,
        "codecLabel": d.codec_label,
        "bitrate": d.bitrate,
        "publishedAt": d.published_at,
        "publishedByUserId": d.published_by_user_id,
    }


# ── POST /video/sessions — createSession ──────────────────────────────────────

@router.post(
    "/sessions",
    response={201: MatchMediaSessionOut, 400: ProblemOut, 401: ProblemOut, 403: ProblemOut, 422: ProblemOut, 500: ProblemOut},
    auth=None,  # TODO: plugar JWT auth do módulo identity_access (ADR-007)
)
def create_session(request, body: CreateSessionIn):
    """
    operationId: createSession
    POST /video/sessions
    PERMISSIONS: admin, coordinator, coach (PERMISSIONS_VIDEO.md)
    """
    # TODO: extrair user_id do JWT quando identity_access estiver implementado
    created_by = getattr(request, "auth", None)
    if created_by is None:
        import uuid as _uuid
        created_by = _uuid.uuid4()  # placeholder até integração JWT

    try:
        session = CreateSessionUseCase(_get_repo()).execute(
            match_id=body.matchId,
            capture_mode=body.captureMode,
            retention_policy=body.retentionPolicy,
            created_by_user_id=created_by,
            technical_contact_user_id=body.technicalContactUserId,
        )
        return 201, _session_to_out(session)
    except ValueError as exc:
        raise HttpError(422, str(exc))


# ── GET /video/sessions — listSessions ────────────────────────────────────────

@router.get(
    "/sessions",
    response={200: PaginatedSessionsOut, 500: ProblemOut},
    auth=None,
)
def list_sessions(
    request,
    matchId: Optional[UUID] = None,
    state: Optional[str] = None,
    createdAtFrom: Optional[datetime] = None,
    createdAtTo: Optional[datetime] = None,
    page: int = 1,
    pageSize: int = 20,
):
    """
    operationId: listSessions
    GET /video/sessions
    PERMISSIONS: admin, coordinator, coach, athlete (filtered), member (filtered)
    """
    sessions, total = ListSessionsUseCase(_get_repo()).execute(
        match_id=matchId,
        state=state,
        created_at_from=createdAtFrom,
        created_at_to=createdAtTo,
        page=page,
        page_size=min(pageSize, 100),
    )
    return 200, {
        "data": [_session_to_out(s) for s in sessions],
        "total": total,
        "page": page,
        "pageSize": pageSize,
    }


# ── GET /video/sessions/{sessionId} — getSession ──────────────────────────────

@router.get(
    "/sessions/{session_id}",
    response={200: MatchMediaSessionOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut, 500: ProblemOut},
    auth=None,
)
def get_session(request, session_id: UUID):
    """
    operationId: getSession
    GET /video/sessions/{sessionId}
    PERMISSIONS: todos autenticados conforme escopo da partida (BOLA — INV-VID-006)
    """
    session = GetSessionUseCase(_get_repo()).execute(session_id)
    if session is None:
        raise HttpError(404, f"Sessão {session_id} não encontrada")
    return 200, _session_to_out(session)


# ── PATCH /video/sessions/{sessionId} — patchSession ─────────────────────────

@router.patch(
    "/sessions/{session_id}",
    response={200: MatchMediaSessionOut, 409: ProblemOut, 500: ProblemOut},
    auth=None,
)
def patch_session(request, session_id: UUID, body: PatchSessionIn):
    """
    operationId: patchSession
    PATCH /video/sessions/{sessionId}
    PERMISSIONS: admin, coordinator, coach (antes de SYNCING)
    """
    try:
        session = PatchSessionUseCase(_get_repo()).execute(
            session_id=session_id,
            state=body.state,
            retention_policy=body.retentionPolicy,
            technical_contact_user_id=body.technicalContactUserId,
        )
        return 200, _session_to_out(session)
    except ValueError as exc:
        raise HttpError(409, str(exc))


# ── POST /video/segments — createSegment ──────────────────────────────────────

@router.post(
    "/segments",
    response={201: MediaSegmentOut, 409: ProblemOut, 500: ProblemOut},
    auth=None,
)
def create_segment(request, body: CreateSegmentIn):
    """
    operationId: createSegment
    POST /video/segments
    PERMISSIONS: admin, coordinator, coach (edge service account — DR-VID-003)
    """
    try:
        segment = IngestSegmentUseCase(_get_repo()).execute(
            session_id=body.sessionId,
            timecode_logical=body.timecodeLogical,
            timecode_label=body.timecodeLabel,
            codec_label=body.codecLabel,
            bitrate=body.bitrate,
            duration_ms=body.durationMs,
            source_edge_node_id=body.sourceEdgeNodeId,
        )
        return 201, _segment_to_out(segment)
    except ValueError as exc:
        raise HttpError(409, str(exc))


# ── GET /video/segments — listSegments ────────────────────────────────────────

@router.get(
    "/segments",
    response={200: PaginatedSegmentsOut, 500: ProblemOut},
    auth=None,
)
def list_segments(
    request,
    sessionId: UUID,
    state: Optional[str] = None,
    page: int = 1,
    pageSize: int = 20,
):
    """
    operationId: listSegments
    GET /video/segments
    PERMISSIONS: visibilidade herdada da MatchMediaSession pai (INV-VID-006)
    """
    segments, total = ListSegmentsUseCase(_get_repo()).execute(
        session_id=sessionId,
        state=state,
        page=page,
        page_size=min(pageSize, 100),
    )
    return 200, {
        "data": [_segment_to_out(s) for s in segments],
        "total": total,
        "page": page,
        "pageSize": pageSize,
    }


# ── POST /video/clips — createClip ────────────────────────────────────────────

@router.post(
    "/clips",
    response={201: ClipDefinitionOut, 409: ProblemOut, 422: ProblemOut, 500: ProblemOut},
    auth=None,
)
def create_clip(request, body: CreateClipIn):
    """
    operationId: createClip
    POST /video/clips
    PERMISSIONS: admin, coordinator, coach, athlete (INV-VID-005)
    """
    user_id = getattr(request, "auth", None)
    if user_id is None:
        import uuid as _uuid
        user_id = _uuid.uuid4()

    try:
        clip = CreateClipUseCase(_get_repo()).execute(
            session_id=body.sessionId,
            from_timecode=body.fromTimecode,
            to_timecode=body.toTimecode,
            created_by_user_id=user_id,
            scout_event_id=body.scoutEventId,
            zone_label=body.zoneLabel,
            athlete_ids=body.athleteIds,
            context_label=body.contextLabel,
        )
        return 201, _clip_to_out(clip)
    except ValueError as exc:
        raise HttpError(422, str(exc))


# ── GET /video/clips — listClips ──────────────────────────────────────────────

@router.get(
    "/clips",
    response={200: PaginatedClipsOut, 500: ProblemOut},
    auth=None,
)
def list_clips(
    request,
    sessionId: UUID,
    scoutEventId: Optional[UUID] = None,
    zoneLabel: Optional[str] = None,
    page: int = 1,
    pageSize: int = 20,
):
    """
    operationId: listClips
    GET /video/clips
    PERMISSIONS: visibilidade herdada da MatchMediaSession pai (INV-VID-006)
    """
    clips, total = ListClipsUseCase(_get_repo()).execute(
        session_id=sessionId,
        scout_event_id=scoutEventId,
        zone_label=zoneLabel,
        page=page,
        page_size=min(pageSize, 100),
    )
    return 200, {
        "data": [_clip_to_out(c) for c in clips],
        "total": total,
        "page": page,
        "pageSize": pageSize,
    }


# ── POST /video/distribution — publishDistribution ───────────────────────────

@router.post(
    "/distribution",
    response={201: DistributionProfileOut, 409: ProblemOut, 422: ProblemOut, 500: ProblemOut},
    auth=None,
)
def publish_distribution(request, body: PublishDistributionIn):
    """
    operationId: publishDistribution
    POST /video/distribution
    PERMISSIONS: admin, coordinator, coach (DR-VID-009, PERM-VID-007)
    INV-VID-012: Idempotente por distributionProfileId
    """
    user_id = getattr(request, "auth", None)
    if user_id is None:
        import uuid as _uuid
        user_id = _uuid.uuid4()

    try:
        dist = PublishDistributionUseCase(_get_repo()).execute(
            session_id=body.sessionId,
            distribution_profile_id=body.distributionProfileId,
            target_label=body.targetLabel,
            profile_label=body.profileLabel,
            codec_label=body.codecLabel,
            bitrate=body.bitrate,
            published_by_user_id=user_id,
        )
        return 201, _dist_to_out(dist)
    except ValueError as exc:
        raise HttpError(422, str(exc))


# ── GET /video/distribution — listDistributions ───────────────────────────────

@router.get(
    "/distribution",
    response={200: PaginatedDistributionsOut, 500: ProblemOut},
    auth=None,
)
def list_distributions(
    request,
    sessionId: UUID,
    page: int = 1,
    pageSize: int = 20,
):
    """
    operationId: listDistributions
    GET /video/distribution
    PERMISSIONS: visibilidade herdada da MatchMediaSession pai (INV-VID-006)
    """
    dists, total = ListDistributionsUseCase(_get_repo()).execute(
        session_id=sessionId,
        page=page,
        page_size=min(pageSize, 100),
    )
    return 200, {
        "data": [_dist_to_out(d) for d in dists],
        "total": total,
        "page": page,
        "pageSize": pageSize,
    }
