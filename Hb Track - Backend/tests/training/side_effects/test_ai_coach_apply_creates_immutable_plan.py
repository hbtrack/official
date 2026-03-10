"""
AR_274 — Gate 4: apply_draft cria registro imutavel em training_session_plans.

Cobre:
  test_apply_creates_plan_record
  test_plan_linked_to_session
  test_plan_preserves_draft_id
  test_plan_not_overwritten_by_second_apply
"""
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models.training_session_plan import TrainingSessionPlan
from app.services.ai_coach_service import AICoachService


def _make_db_mock():
    db = MagicMock()
    db.add = MagicMock()
    return db


def test_apply_creates_plan_record():
    """apply_draft com db e session_id deve criar um TrainingSessionPlan via db.add."""
    svc = AICoachService()
    db = _make_db_mock()
    session_id = str(uuid4())
    draft_id = str(uuid4())

    result = svc.apply_draft(draft_id=draft_id, session_id=session_id, db=db)

    assert result["applied"] is True
    db.add.assert_called_once()
    added_obj = db.add.call_args[0][0]
    assert isinstance(added_obj, TrainingSessionPlan)


def test_plan_linked_to_session():
    """O TrainingSessionPlan criado deve ter session_id igual ao passado."""
    svc = AICoachService()
    db = _make_db_mock()
    session_id = uuid4()
    draft_id = str(uuid4())

    svc.apply_draft(draft_id=draft_id, session_id=str(session_id), db=db)

    added_obj = db.add.call_args[0][0]
    assert isinstance(added_obj, TrainingSessionPlan)
    assert added_obj.session_id == session_id


def test_plan_preserves_draft_id():
    """O TrainingSessionPlan criado deve ter draft_id rastreavel."""
    svc = AICoachService()
    db = _make_db_mock()
    session_id = str(uuid4())
    draft_id = uuid4()

    svc.apply_draft(draft_id=str(draft_id), session_id=session_id, db=db)

    added_obj = db.add.call_args[0][0]
    assert isinstance(added_obj, TrainingSessionPlan)
    assert added_obj.draft_id == draft_id


def test_plan_not_overwritten_by_second_apply():
    """Segunda chamada a apply_draft deve criar nova linha — nunca sobrescrever."""
    svc = AICoachService()
    db = _make_db_mock()
    session_id = str(uuid4())
    draft_id = str(uuid4())

    svc.apply_draft(draft_id=draft_id, session_id=session_id, db=db)
    svc.apply_draft(draft_id=draft_id, session_id=session_id, db=db)

    # Dois registros criados, nunca um update
    assert db.add.call_count == 2
    first = db.add.call_args_list[0][0][0]
    second = db.add.call_args_list[1][0][0]
    assert isinstance(first, TrainingSessionPlan)
    assert isinstance(second, TrainingSessionPlan)
    # Objetos distintos (nao o mesmo objeto em memoria)
    assert first is not second
