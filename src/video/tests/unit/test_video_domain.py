"""
Testes unitários do módulo video.
Testam entidades, state machine e use cases isolados (mock repository).
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest

from video.domain.entities import (
    CaptureMode,
    ClipDefinition,
    MatchMediaSession,
    MediaSegment,
    RetentionPolicy,
    SegmentState,
    SessionState,
)
from video.domain.state_machine import MatchMediaSessionStateMachine
from video.domain.rules import (
    assert_session_capturing,
    assert_timecode_monotonic,
    assert_session_published_for_distribution,
)
from video.application.use_cases import (
    CreateSessionUseCase,
    IngestSegmentUseCase,
    PatchSessionUseCase,
    CreateClipUseCase,
)


def make_session(state=SessionState.DRAFT, last_timecode=0) -> MatchMediaSession:
    return MatchMediaSession(
        id=uuid.uuid4(),
        match_id=uuid.uuid4(),
        state=state,
        capture_mode=CaptureMode.PANORAMIC,
        retention_policy=RetentionPolicy.KEEP_7_DAYS,
        created_at=datetime.now(tz=timezone.utc),
        created_by_user_id=uuid.uuid4(),
        last_timecode=last_timecode,
    )


class TestMatchMediaSessionStateMachine:
    def test_draft_to_capturing_allowed(self):
        assert MatchMediaSessionStateMachine.can_transition(SessionState.DRAFT, SessionState.CAPTURING)

    def test_capturing_to_syncing_allowed(self):
        assert MatchMediaSessionStateMachine.can_transition(SessionState.CAPTURING, SessionState.SYNCING)

    def test_syncing_to_transcoding_allowed(self):
        assert MatchMediaSessionStateMachine.can_transition(SessionState.SYNCING, SessionState.TRANSCODING)

    def test_transcoding_to_published_allowed(self):
        assert MatchMediaSessionStateMachine.can_transition(SessionState.TRANSCODING, SessionState.PUBLISHED)

    def test_draft_to_published_not_allowed(self):
        assert not MatchMediaSessionStateMachine.can_transition(SessionState.DRAFT, SessionState.PUBLISHED)

    def test_published_is_terminal(self):
        for target in SessionState:
            assert not MatchMediaSessionStateMachine.can_transition(SessionState.PUBLISHED, target)

    def test_assert_transition_raises_on_invalid(self):
        with pytest.raises(ValueError):
            MatchMediaSessionStateMachine.assert_transition(SessionState.DRAFT, SessionState.PUBLISHED)


class TestDomainRules:
    def test_assert_session_capturing_raises_if_not_capturing(self):
        session = make_session(state=SessionState.DRAFT)
        with pytest.raises(ValueError, match="DR-VID-003"):
            assert_session_capturing(session)

    def test_assert_session_capturing_ok_when_capturing(self):
        session = make_session(state=SessionState.CAPTURING)
        assert_session_capturing(session)  # no exception

    def test_timecode_monotonic_raises_when_lower(self):
        session = make_session(last_timecode=1000)
        with pytest.raises(ValueError, match="DR-VID-001"):
            assert_timecode_monotonic(session, 500)

    def test_timecode_monotonic_ok_when_equal_or_greater(self):
        session = make_session(last_timecode=1000)
        assert_timecode_monotonic(session, 1000)
        assert_timecode_monotonic(session, 2000)

    def test_assert_published_raises_when_not_published(self):
        session = make_session(state=SessionState.CAPTURING)
        with pytest.raises(ValueError, match="DR-VID-009"):
            assert_session_published_for_distribution(session)


class TestClipDefinitionInvariant:
    def test_clip_without_context_raises(self):
        clip = ClipDefinition(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            from_timecode=0,
            to_timecode=1000,
        )
        with pytest.raises(ValueError, match="INV-VID-005"):
            clip.validate_invariants()

    def test_clip_with_zone_label_is_valid(self):
        clip = ClipDefinition(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            from_timecode=0,
            to_timecode=1000,
            zone_label="LEFT_WING",
        )
        clip.validate_invariants()  # no exception

    def test_clip_from_gte_to_raises(self):
        clip = ClipDefinition(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            from_timecode=1000,
            to_timecode=1000,
            zone_label="CENTER",
        )
        with pytest.raises(ValueError):
            clip.validate_invariants()


class TestCreateSessionUseCase:
    def test_creates_session_in_draft(self):
        repo = MagicMock()
        repo.create_session.side_effect = lambda s: s
        session = CreateSessionUseCase(repo).execute(
            match_id=uuid.uuid4(),
            capture_mode="PANORAMIC",
            retention_policy="KEEP_7_DAYS",
            created_by_user_id=uuid.uuid4(),
        )
        assert session.state == SessionState.DRAFT
        repo.create_session.assert_called_once()


class TestPatchSessionUseCaseInvariant:
    def test_patch_published_session_raises(self):
        repo = MagicMock()
        session = make_session(state=SessionState.PUBLISHED)
        repo.get_session_by_id.return_value = session
        with pytest.raises(ValueError, match="INV-VID-002"):
            PatchSessionUseCase(repo).execute(
                session_id=session.id,
                state="CAPTURING",
            )


class TestIngestSegmentUseCase:
    def test_ingest_raises_when_not_capturing(self):
        repo = MagicMock()
        session = make_session(state=SessionState.DRAFT)
        repo.get_session_by_id.return_value = session
        with pytest.raises(ValueError, match="DR-VID-003"):
            IngestSegmentUseCase(repo).execute(
                session_id=session.id,
                timecode_logical=100,
                timecode_label="00:00:00.100",
            )

    def test_ingest_raises_on_duplicate_timecode(self):
        repo = MagicMock()
        session = make_session(state=SessionState.CAPTURING, last_timecode=0)
        repo.get_session_by_id.return_value = session
        repo.timecode_exists_in_session.return_value = True
        with pytest.raises(ValueError, match="INV-VID-001"):
            IngestSegmentUseCase(repo).execute(
                session_id=session.id,
                timecode_logical=100,
                timecode_label="00:00:00.100",
            )

    def test_ingest_succeeds_with_valid_data(self):
        repo = MagicMock()
        session = make_session(state=SessionState.CAPTURING, last_timecode=0)
        repo.get_session_by_id.return_value = session
        repo.timecode_exists_in_session.return_value = False
        segment = MediaSegment(
            id=uuid.uuid4(),
            session_id=session.id,
            timecode_logical=500,
            timecode_label="00:00:00.500",
            state=SegmentState.OPEN,
        )
        repo.create_segment.return_value = segment
        result = IngestSegmentUseCase(repo).execute(
            session_id=session.id,
            timecode_logical=500,
            timecode_label="00:00:00.500",
        )
        assert result.timecode_logical == 500
