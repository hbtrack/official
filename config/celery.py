"""
Celery 5.x — HB Track
Broker: Redis (CELERY_BROKER_URL)
Backend: django-celery-results (CELERY_RESULT_BACKEND)
"""
import os

from celery import Celery
from celery.signals import before_task_publish, task_prerun

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("hbtrack")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@before_task_publish.connect
def inject_flow_id_into_task_headers(headers: dict, **kwargs) -> None:
    """Propaga X-Flow-ID do request atual para o header da task Celery (FASE 1.4)."""
    from shared.middleware import get_current_flow_id  # noqa: PLC0415

    headers.setdefault("X-Flow-ID", get_current_flow_id())


@task_prerun.connect
def restore_flow_id_from_task_headers(task, **kwargs) -> None:
    """Restaura flow_id no thread-local do worker a partir do header da task."""
    from shared.middleware import set_flow_id  # noqa: PLC0415

    flow_id = (task.request.headers or {}).get("X-Flow-ID")
    if flow_id:
        set_flow_id(flow_id)
