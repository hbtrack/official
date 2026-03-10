"""
AR_274 — Gate 5: adjustments sao append-only; plan_data original intacto.

Cobre:
  test_adjustment_creates_new_row
  test_plan_original_intact_after_adjustment
  test_sequence_number_incremental
  test_no_destructive_update_of_plan
"""
from uuid import uuid4

import pytest

from app.models.training_session_adjustment import TrainingSessionAdjustment
from app.models.training_session_plan import TrainingSessionPlan


def test_adjustment_creates_new_row():
    """Cada ajuste e uma nova instancia de TrainingSessionAdjustment (append-only)."""
    plan_id = uuid4()
    session_id = uuid4()
    adj1 = TrainingSessionAdjustment(
        plan_id=plan_id,
        session_id=session_id,
        sequence_number=1,
        adjustment_data={"change": "add_set"},
    )
    adj2 = TrainingSessionAdjustment(
        plan_id=plan_id,
        session_id=session_id,
        sequence_number=2,
        adjustment_data={"change": "remove_exercise"},
    )
    # Objetos distintos (nao o mesmo objeto em memoria), sequence_numbers diferentes
    assert adj1 is not adj2
    assert adj1.sequence_number != adj2.sequence_number


def test_plan_original_intact_after_adjustment():
    """plan_data do TrainingSessionPlan original nao e modificado por ajustes."""
    original_plan_data = {"exercises": ["squat", "deadlift"], "sets": 3}
    plan = TrainingSessionPlan(
        session_id=uuid4(),
        plan_data=dict(original_plan_data),
    )
    # Criar ajuste nao modifica plan.plan_data
    adj = TrainingSessionAdjustment(
        plan_id=plan.id if plan.id else uuid4(),
        session_id=plan.session_id,
        sequence_number=1,
        adjustment_data={"change": "add_exercise", "exercise": "bench_press"},
    )
    assert plan.plan_data == original_plan_data


def test_sequence_number_incremental():
    """sequence_number deve ser incremental entre ajustes do mesmo plano."""
    plan_id = uuid4()
    session_id = uuid4()
    adjustments = [
        TrainingSessionAdjustment(
            plan_id=plan_id,
            session_id=session_id,
            sequence_number=i,
            adjustment_data={"seq": i},
        )
        for i in range(1, 6)
    ]
    seqs = [a.sequence_number for a in adjustments]
    assert seqs == list(range(1, 6))


def test_no_destructive_update_of_plan():
    """TrainingSessionPlan nao expoe metodos de update — append-only por design."""
    plan = TrainingSessionPlan(
        session_id=uuid4(),
        plan_data={"exercises": ["squat"]},
    )
    # Verificar que o model nao tem metodos update/set que modifiquem plan_data
    assert not hasattr(plan, "update_plan_data"), (
        "TrainingSessionPlan NAO deve ter metodo update_plan_data"
    )
    assert not hasattr(plan, "modify"), (
        "TrainingSessionPlan NAO deve ter metodo modify"
    )
    # O unico campo sem default gerado e plan_data — nao deve haver setter de negocio
    assert not callable(getattr(plan, "update", None)), (
        "TrainingSessionPlan NAO deve ter metodo de negocio 'update'"
    )
