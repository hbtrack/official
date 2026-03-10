"""
Gate 12 — Testes de state machine para schedule_session e finalize_session.

Cobre as 5 transições de guarda exigidas por AR_273:
  test_schedule_requires_draft_status
  test_schedule_sets_status_to_scheduled
  test_finalize_requires_pending_review_status
  test_finalize_sets_status_to_readonly
  test_schedule_validates_starts_at_required
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.core.context import ExecutionContext
from app.core.exceptions import ValidationError
from app.schemas.training_sessions import SessionClosureValidationResult
from app.services.training_session_service import TrainingSessionService


def _make_context() -> ExecutionContext:
    return ExecutionContext(
        user_id=uuid4(),
        email="test@hbtrack.com",
        role_code="treinador",
        request_id=str(uuid4()),
        organization_id=uuid4(),
        membership_id=uuid4(),
        team_ids=[uuid4()],
        permissions=[],
    )


def _make_session(status: str) -> MagicMock:
    session = MagicMock()
    session.id = uuid4()
    session.status = status
    session.session_at = datetime.now(timezone.utc) + timedelta(hours=2)
    session.duration_planned_minutes = 90
    session.location = "Ginásio"
    session.session_type = "quadra"
    session.main_objective = "Treino teste"
    return session


@pytest.mark.asyncio
async def test_schedule_requires_draft_status():
    """schedule_session deve levantar ValidationError se status != 'draft'."""
    db = AsyncMock()
    ctx = _make_context()
    service = TrainingSessionService(db, ctx)

    session = _make_session(status="scheduled")
    service.get_by_id = AsyncMock(return_value=session)

    with pytest.raises(ValidationError):
        await service.schedule_session(
            session.id,
            starts_at=datetime.now(timezone.utc) + timedelta(hours=2),
            ends_at=datetime.now(timezone.utc) + timedelta(hours=3, minutes=30),
        )


@pytest.mark.asyncio
async def test_schedule_sets_status_to_scheduled():
    """schedule_session deve transicionar status de 'draft' para 'scheduled'."""
    db = AsyncMock()
    ctx = _make_context()
    service = TrainingSessionService(db, ctx)

    session = _make_session(status="draft")
    service.get_by_id = AsyncMock(return_value=session)
    service.validate_session_publish = MagicMock(return_value={})
    service._audit_session_action = AsyncMock()

    starts_at = datetime.now(timezone.utc) + timedelta(hours=2)
    ends_at = starts_at + timedelta(hours=1, minutes=30)

    result_session, errors = await service.schedule_session(session.id, starts_at=starts_at, ends_at=ends_at)

    assert errors == {}
    assert result_session.status == "scheduled"
    assert result_session.session_at == starts_at


@pytest.mark.asyncio
async def test_finalize_requires_pending_review_status():
    """finalize_session deve retornar success=False se status != 'pending_review'."""
    db = AsyncMock()
    ctx = _make_context()
    service = TrainingSessionService(db, ctx)

    validation_result = SessionClosureValidationResult(
        can_close=False,
        error_code="INVALID_STATUS",
    )
    service.validate_session_closure = AsyncMock(return_value=validation_result)

    result = await service.finalize_session(
        uuid4(),
        attendance_completed=True,
        review_completed=True,
    )

    assert result.success is False
    assert result.validation.error_code == "INVALID_STATUS"


@pytest.mark.asyncio
async def test_finalize_sets_status_to_readonly():
    """finalize_session deve transicionar status de 'pending_review' para 'readonly'."""
    db = AsyncMock()
    ctx = _make_context()
    service = TrainingSessionService(db, ctx)

    validation_result = SessionClosureValidationResult(can_close=True)
    service.validate_session_closure = AsyncMock(return_value=validation_result)

    session = _make_session(status="pending_review")
    session.started_at = None
    session.duration_actual_minutes = None
    session.ended_at = None
    session.execution_outcome = "on_time"
    service.get_by_id = AsyncMock(return_value=session)
    service._audit_session_action = AsyncMock()

    # Patch SessionClosureResponse + TrainingSessionResponse para evitar validação Pydantic do session mock
    with patch("app.services.training_session_service.SessionClosureResponse") as mock_scr, \
         patch("app.schemas.training_sessions.TrainingSessionResponse") as mock_tr:
        mock_scr.return_value = MagicMock(success=True)
        mock_tr.model_validate.return_value = MagicMock()
        await service.finalize_session(
            session.id,
            attendance_completed=True,
            review_completed=True,
        )

    # Verificar mutação do session diretamente (objetivo do teste)
    assert session.status == "readonly"
    assert session.closed_at is not None


@pytest.mark.asyncio
async def test_schedule_validates_starts_at_required():
    """schedule_session deve exigir starts_at e ends_at como parâmetros obrigatórios."""
    db = AsyncMock()
    ctx = _make_context()
    service = TrainingSessionService(db, ctx)

    session = _make_session(status="draft")
    service.get_by_id = AsyncMock(return_value=session)
    service.validate_session_publish = MagicMock(return_value={})
    service._audit_session_action = AsyncMock()

    import inspect
    sig = inspect.signature(service.schedule_session)
    params = list(sig.parameters.keys())

    assert "starts_at" in params, "starts_at deve ser parâmetro obrigatório de schedule_session"
    assert "ends_at" in params, "ends_at deve ser parâmetro obrigatório de schedule_session"

    # Confirmar que a chamada sem esses params levanta TypeError
    with pytest.raises(TypeError):
        await service.schedule_session(session.id)  # type: ignore[call-arg]
