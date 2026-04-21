"""
Políticas de domínio para FeedbackThread.

Helpers que determinam context_type e context_ref_id a partir de um FeedbackThread.
Consolidado aqui para evitar duplicação entre application/use_cases.py e api/mappers.py.
"""
from __future__ import annotations

import uuid

from ..entities import FeedbackThread


def feedback_context_type(thread: FeedbackThread) -> str:
    """Retorna o tipo de contexto canônico do thread."""
    if thread.subject in {"SESSION", "BLOCK", "OBJECTIVE", "ATHLETE", "EVIDENCE", "GROUP"}:
        return thread.subject
    if thread.block_id is not None:
        return "BLOCK"
    if thread.objective_id is not None:
        return "OBJECTIVE"
    if thread.athlete_id is not None:
        return "ATHLETE"
    return "SESSION"


def feedback_context_ref_id(thread: FeedbackThread) -> uuid.UUID:
    """Retorna o UUID de referência correspondente ao context_type."""
    context_type = feedback_context_type(thread)
    if context_type == "BLOCK" and thread.block_id is not None:
        return thread.block_id
    if context_type == "OBJECTIVE" and thread.objective_id is not None:
        return thread.objective_id
    if context_type == "ATHLETE" and thread.athlete_id is not None:
        return thread.athlete_id
    return thread.session_id
