"""
TM-200..TM-230 — Transições proibidas da FSM de TrainingSession.
Fonte: TEST_MATRIX_TRAINING.md (tabela de transições proibidas).
Todas as combinações (from_status, to_status) que NÃO estão em VALID_TRANSITIONS.
"""
import pytest

from training.domain.common.enums import TrainingSessionStatus
from training.domain.rules import (
    VALID_TRANSITIONS,
    InvalidStatusTransition,
    assert_valid_transition,
)

ALL_STATUSES = list(TrainingSessionStatus)

# Derivar FORBIDDEN_TRANSITIONS diretamente do código (VALID_TRANSITIONS)
# para garantir que o teste reflete a implementação real.
FORBIDDEN_TRANSITIONS = [
    (src, dst)
    for src in ALL_STATUSES
    for dst in ALL_STATUSES
    if dst not in VALID_TRANSITIONS.get(src, set()) and src != dst
]


class TestForbiddenTransitions:
    """TM-200..TM-230: todas as transições fora de VALID_TRANSITIONS devem ser rejeitadas."""

    @pytest.mark.parametrize(
        "from_status,to_status",
        FORBIDDEN_TRANSITIONS,
        ids=[f"{s.value}->{d.value}" for s, d in FORBIDDEN_TRANSITIONS],
    )
    def test_forbidden_transition_raises(self, from_status, to_status):
        with pytest.raises(InvalidStatusTransition, match="INV-TRAIN-006"):
            assert_valid_transition(from_status, to_status)

    def test_self_transitions_are_forbidden(self):
        """Nenhum estado pode transicionar para si mesmo."""
        for status in ALL_STATUSES:
            with pytest.raises(InvalidStatusTransition):
                assert_valid_transition(status, status)

    def test_terminal_states_block_all(self):
        """CANCELLED e ARCHIVED não têm transições de saída."""
        for terminal in (TrainingSessionStatus.CANCELLED, TrainingSessionStatus.ARCHIVED):
            for target in ALL_STATUSES:
                if target == terminal:
                    continue
                with pytest.raises(InvalidStatusTransition):
                    assert_valid_transition(terminal, target)
