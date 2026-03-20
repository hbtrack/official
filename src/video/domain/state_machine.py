"""
FSM da MatchMediaSession.
Fonte: STATE_MODEL_VIDEO.md
INV-VID-002: PUBLISHED é estado terminal (nenhuma transição a partir dele).
"""
from .entities import SessionState


class MatchMediaSessionStateMachine:
    """
    Transições válidas conforme STATE_MODEL_VIDEO.md §Diagrama de Estados.
    """
    TRANSITIONS: dict[SessionState, set[SessionState]] = {
        SessionState.DRAFT: {SessionState.CAPTURING},
        SessionState.CAPTURING: {SessionState.SYNCING},
        SessionState.SYNCING: {SessionState.TRANSCODING},
        SessionState.TRANSCODING: {SessionState.PUBLISHED},
        SessionState.PUBLISHED: set(),  # INV-VID-002: terminal
    }

    @classmethod
    def can_transition(cls, from_state: SessionState, to_state: SessionState) -> bool:
        return to_state in cls.TRANSITIONS.get(from_state, set())

    @classmethod
    def assert_transition(cls, from_state: SessionState, to_state: SessionState) -> None:
        if not cls.can_transition(from_state, to_state):
            raise ValueError(
                f"Transição inválida: {from_state} → {to_state}. "
                f"Permitidas: {cls.TRANSITIONS.get(from_state, set())}"
            )
