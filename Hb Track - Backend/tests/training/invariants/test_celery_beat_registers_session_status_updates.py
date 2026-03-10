"""
AR_274 — Gates 7 & 8: beat_schedule registra update_training_session_statuses_task
com crontab(minute='*').

Cobre:
  test_beat_schedule_has_update_task
  test_update_task_has_valid_schedule
"""
import pytest
from celery.schedules import crontab

from app.core.celery_app import app as celery_app

_TARGET_TASK = "app.core.celery_tasks.update_training_session_statuses_task"


def test_beat_schedule_has_update_task():
    """beat_schedule deve conter update_training_session_statuses_task."""
    beat = celery_app.conf.beat_schedule
    registered_tasks = [entry.get("task", "") for entry in beat.values()]
    assert _TARGET_TASK in registered_tasks, (
        f"'{_TARGET_TASK}' nao encontrado em beat_schedule. "
        f"Tasks registradas: {registered_tasks}"
    )


def test_update_task_has_valid_schedule():
    """update_training_session_statuses_task deve usar crontab(minute='*')."""
    beat = celery_app.conf.beat_schedule
    for entry in beat.values():
        if entry.get("task") == _TARGET_TASK:
            schedule = entry.get("schedule")
            assert isinstance(schedule, crontab), (
                f"schedule deve ser crontab, recebeu {type(schedule)}"
            )
            # crontab(minute='*') → _orig_minute_expr == '*'
            minute_expr = str(schedule._orig_minute)
            assert minute_expr == "*", (
                f"crontab.minute deve ser '*' (every minute), recebeu '{minute_expr}'"
            )
            return
    pytest.fail(f"Task '{_TARGET_TASK}' nao encontrada no beat_schedule")
