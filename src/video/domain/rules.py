"""
Regras de domínio do módulo video — DOMAIN_RULES_VIDEO.md.
DR-VID-001..010 são enforçadas aqui e nas entidades.
"""
from .entities import MatchMediaSession, MediaSegment, SessionState


def assert_session_capturing(session: MatchMediaSession) -> None:
    """DR-VID-003: Ingestão de segmentos só é permitida no estado CAPTURING."""
    if session.state != SessionState.CAPTURING:
        raise ValueError(
            f"DR-VID-003: Ingestão de segmentos exige state=CAPTURING "
            f"(atual: {session.state})"
        )


def assert_timecode_monotonic(session: MatchMediaSession, new_timecode: int) -> None:
    """DR-VID-001: Timecode deve ser monotonicamente crescente."""
    if new_timecode < session.last_timecode:
        raise ValueError(
            f"DR-VID-001: timecodeLogical {new_timecode} é menor que "
            f"lastTimecode da sessão {session.last_timecode}"
        )


def assert_session_published_for_distribution(session: MatchMediaSession) -> None:
    """DR-VID-009: Distribuição exige state=PUBLISHED."""
    if session.state != SessionState.PUBLISHED:
        raise ValueError(
            f"DR-VID-009: Distribuição exige state=PUBLISHED (atual: {session.state})"
        )


def assert_segment_is_mutable(segment: MediaSegment) -> None:
    """DR-VID-005: Segments FINALIZED não podem ser alterados."""
    if not segment.is_mutable():
        raise ValueError(
            f"DR-VID-005: MediaSegment {segment.id} está FINALIZED e é imutável"
        )
