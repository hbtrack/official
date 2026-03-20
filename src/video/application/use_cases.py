"""
Use cases do módulo video.
Um use case por feature — orquestra domínio sem conhecer ORM.
PERMISSIONS_VIDEO.md governa quem pode chamar cada use case.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

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
from ..domain.rules import (
    assert_session_capturing,
    assert_session_published_for_distribution,
    assert_timecode_monotonic,
)
from ..domain.state_machine import MatchMediaSessionStateMachine
from ..infrastructure.repository import VideoRepository


class CreateSessionUseCase:
    """
    Criar MatchMediaSession — POST /video/sessions (operationId: createSession).
    PERMISSIONS: admin, coordinator, coach.
    """

    def __init__(self, repository: VideoRepository):
        self._repo = repository

    def execute(
        self,
        match_id: UUID,
        capture_mode: str,
        retention_policy: str,
        created_by_user_id: UUID,
        technical_contact_user_id: Optional[UUID] = None,
    ) -> MatchMediaSession:
        session = MatchMediaSession(
            id=uuid.uuid4(),
            match_id=match_id,
            state=SessionState.DRAFT,
            capture_mode=CaptureMode(capture_mode),
            retention_policy=RetentionPolicy(retention_policy),
            created_at=datetime.now(tz=timezone.utc),
            created_by_user_id=created_by_user_id,
            technical_contact_user_id=technical_contact_user_id,
        )
        session.validate_invariants()
        return self._repo.create_session(session)


class ListSessionsUseCase:
    """
    Listar MatchMediaSessions — GET /video/sessions (operationId: listSessions).
    PERMISSIONS: filtrado por role no router (INV-VID-006).
    """

    def __init__(self, repository: VideoRepository):
        self._repo = repository

    def execute(
        self,
        match_id: Optional[UUID] = None,
        state: Optional[str] = None,
        created_at_from: Optional[datetime] = None,
        created_at_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[MatchMediaSession], int]:
        return self._repo.list_sessions(
            match_id=match_id,
            state=state,
            created_at_from=created_at_from,
            created_at_to=created_at_to,
            page=page,
            page_size=page_size,
        )


class GetSessionUseCase:
    """
    Obter MatchMediaSession — GET /video/sessions/{sessionId} (operationId: getSession).
    PERMISSIONS: verificada no router (BOLA — INV-VID-006).
    """

    def __init__(self, repository: VideoRepository):
        self._repo = repository

    def execute(self, session_id: UUID) -> Optional[MatchMediaSession]:
        return self._repo.get_session_by_id(session_id)


class PatchSessionUseCase:
    """
    Atualizar MatchMediaSession — PATCH /video/sessions/{sessionId} (operationId: patchSession).
    Aceita transições de estado e atualização de metadados.
    INV-VID-002: PUBLISHED é imutável — validado aqui.
    """

    def __init__(self, repository: VideoRepository):
        self._repo = repository

    def execute(
        self,
        session_id: UUID,
        state: Optional[str] = None,
        retention_policy: Optional[str] = None,
        technical_contact_user_id: Optional[UUID] = None,
    ) -> MatchMediaSession:
        session = self._repo.get_session_by_id(session_id)
        if session is None:
            raise ValueError(f"Sessão {session_id} não encontrada")

        if not session.can_be_edited() and (state or retention_policy or technical_contact_user_id):
            raise ValueError("INV-VID-002: Sessão PUBLISHED é imutável")

        if state:
            new_state = SessionState(state)
            MatchMediaSessionStateMachine.assert_transition(session.state, new_state)
            session.state = new_state

        if retention_policy:
            session.retention_policy = RetentionPolicy(retention_policy)

        if technical_contact_user_id is not None:
            session.technical_contact_user_id = technical_contact_user_id

        return self._repo.update_session(session)


class IngestSegmentUseCase:
    """
    Ingerir MediaSegment — POST /video/segments (operationId: createSegment).
    DR-VID-003: Apenas durante CAPTURING.
    DR-VID-001: Timecode monotônico e único.
    PERMISSIONS: admin, coordinator, coach (edge service account).
    """

    def __init__(self, repository: VideoRepository):
        self._repo = repository

    def execute(
        self,
        session_id: UUID,
        timecode_logical: int,
        timecode_label: str,
        codec_label: Optional[str] = None,
        bitrate: Optional[int] = None,
        duration_ms: Optional[int] = None,
        source_edge_node_id: Optional[UUID] = None,
    ) -> MediaSegment:
        session = self._repo.get_session_by_id(session_id)
        if session is None:
            raise ValueError(f"Sessão {session_id} não encontrada")

        assert_session_capturing(session)
        assert_timecode_monotonic(session, timecode_logical)

        if self._repo.timecode_exists_in_session(session_id, timecode_logical):
            raise ValueError(
                f"INV-VID-001: timecodeLogical {timecode_logical} já existe na sessão {session_id}"
            )

        segment = MediaSegment(
            id=uuid.uuid4(),
            session_id=session_id,
            timecode_logical=timecode_logical,
            timecode_label=timecode_label,
            state=SegmentState.OPEN,
            codec_label=codec_label,
            bitrate=bitrate,
            duration_ms=duration_ms,
            source_edge_node_id=source_edge_node_id,
        )
        segment.validate_invariants()

        session.last_timecode = timecode_logical
        self._repo.update_session(session)

        return self._repo.create_segment(segment)


class ListSegmentsUseCase:
    """
    Listar MediaSegments — GET /video/segments (operationId: listSegments).
    PERMISSIONS: acesso herdado da MatchMediaSession pai (INV-VID-006).
    """

    def __init__(self, repository: VideoRepository):
        self._repo = repository

    def execute(
        self,
        session_id: UUID,
        state: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[MediaSegment], int]:
        return self._repo.list_segments(session_id=session_id, state=state, page=page, page_size=page_size)


class CreateClipUseCase:
    """
    Criar ClipDefinition — POST /video/clips (operationId: createClip).
    INV-VID-005: Contexto semântico obrigatório.
    DR-VID-004: Clipping é sempre semântico.
    PERMISSIONS: admin, coordinator, coach, athlete.
    """

    def __init__(self, repository: VideoRepository):
        self._repo = repository

    def execute(
        self,
        session_id: UUID,
        from_timecode: int,
        to_timecode: int,
        created_by_user_id: UUID,
        scout_event_id: Optional[UUID] = None,
        zone_label: Optional[str] = None,
        athlete_ids: Optional[list[UUID]] = None,
        context_label: Optional[str] = None,
    ) -> ClipDefinition:
        session = self._repo.get_session_by_id(session_id)
        if session is None:
            raise ValueError(f"Sessão {session_id} não encontrada")

        clip = ClipDefinition(
            id=uuid.uuid4(),
            session_id=session_id,
            from_timecode=from_timecode,
            to_timecode=to_timecode,
            scout_event_id=scout_event_id,
            zone_label=zone_label,
            athlete_ids=athlete_ids or [],
            context_label=context_label,
            created_at=datetime.now(tz=timezone.utc),
            created_by_user_id=created_by_user_id,
        )
        clip.validate_invariants()
        return self._repo.create_clip(clip)


class ListClipsUseCase:
    """
    Listar ClipDefinitions — GET /video/clips (operationId: listClips).
    PERMISSIONS: visibilidade herdada da MatchMediaSession pai (INV-VID-006).
    """

    def __init__(self, repository: VideoRepository):
        self._repo = repository

    def execute(
        self,
        session_id: UUID,
        scout_event_id: Optional[UUID] = None,
        zone_label: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ClipDefinition], int]:
        return self._repo.list_clips(
            session_id=session_id,
            scout_event_id=scout_event_id,
            zone_label=zone_label,
            page=page,
            page_size=page_size,
        )


class PublishDistributionUseCase:
    """
    Publicar distribuição — POST /video/distribution (operationId: publishDistribution).
    DR-VID-009: Toda distribuição é auditada.
    INV-VID-012: Idempotência por distribution_id.
    PERMISSIONS: admin, coordinator, coach.
    """

    def __init__(self, repository: VideoRepository):
        self._repo = repository

    def execute(
        self,
        session_id: UUID,
        distribution_profile_id: UUID,
        target_label: str,
        profile_label: str,
        codec_label: str,
        bitrate: int,
        published_by_user_id: UUID,
    ) -> DistributionProfile:
        session = self._repo.get_session_by_id(session_id)
        if session is None:
            raise ValueError(f"Sessão {session_id} não encontrada")

        assert_session_published_for_distribution(session)

        # INV-VID-012: Idempotência — se já existe, não criar duplicata
        if self._repo.distribution_exists(distribution_profile_id):
            existing, _ = self._repo.list_distributions(session_id=session_id)
            match = next((d for d in existing if d.id == distribution_profile_id), None)
            if match:
                return match

        dist = DistributionProfile(
            id=distribution_profile_id,
            profile_label=profile_label,
            target_type=TargetType(target_label),
            codec_label=codec_label,
            bitrate=bitrate,
            session_id=session_id,
            published_at=datetime.now(tz=timezone.utc),
            published_by_user_id=published_by_user_id,
        )
        return self._repo.create_distribution(dist)


class ListDistributionsUseCase:
    """
    Listar distribuições — GET /video/distribution (operationId: listDistributions).
    PERMISSIONS: visibilidade herdada da MatchMediaSession pai (INV-VID-006).
    """

    def __init__(self, repository: VideoRepository):
        self._repo = repository

    def execute(
        self,
        session_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[DistributionProfile], int]:
        return self._repo.list_distributions(session_id=session_id, page=page, page_size=page_size)
