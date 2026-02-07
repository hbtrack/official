"""
Celery Application Configuration - Step 18

Configuração do Celery para tasks assíncronas e scheduled jobs:
- Alertas automáticos de sobrecarga semanal
- Verificação de taxa de resposta wellness
- Sugestões automáticas de ajuste de carga
- Cleanup de dados antigos

Usage (Windows PowerShell):
    # Worker
    celery -A app.core.celery_app worker --loglevel=info --pool=solo

    # Beat (scheduler)
    celery -A app.core.celery_app beat --loglevel=info

    # Flower (monitoring UI)
    celery -A app.core.celery_app flower --port=5555 --basic_auth=admin:hbtrack2026
"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Criar aplicação Celery
app = Celery(
    "hbtrack_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configuração geral
app.conf.update(
    # Timezone
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=True,
    
    # Task tracking
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    
    # Worker
    worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
    worker_prefetch_multiplier=4,
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Result backend
    result_expires=3600,  # 1 hora
    result_persistent=False,
    
    # Task routes (opcional - para múltiplas queues)
    task_routes={
        "app.core.celery_tasks.check_weekly_overload_task": {"queue": "alerts"},
        "app.core.celery_tasks.check_wellness_response_rates_task": {"queue": "alerts"},
        "app.core.celery_tasks.cleanup_old_alerts_task": {"queue": "maintenance"},
        "app.core.celery_tasks.update_training_session_statuses_task": {"queue": "maintenance"},
        "app.core.celery_tasks.refresh_training_rankings_task": {"queue": "maintenance"},
    },
)

# Beat schedule (Scheduled Jobs)
app.conf.beat_schedule = {
    # Verificar sobrecarga semanal - Domingo 23h
    "check-weekly-overload": {
        "task": "app.core.celery_tasks.check_weekly_overload_task",
        "schedule": crontab(hour=23, minute=0, day_of_week=0),  # Domingo 23:00
        "args": (),
        "options": {"queue": "alerts"},
    },
    
    # Verificar taxas de resposta wellness - Diário 8h
    "check-wellness-response-rates": {
        "task": "app.core.celery_tasks.check_wellness_response_rates_task",
        "schedule": crontab(hour=8, minute=0),  # Todos os dias 08:00
        "args": (),
        "options": {"queue": "alerts"},
    },
    
    # Cleanup de alertas antigos - Semanal (Domingo 2h)
    "cleanup-old-alerts": {
        "task": "app.core.celery_tasks.cleanup_old_alerts_task",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),  # Domingo 02:00
        "args": (),
        "options": {"queue": "maintenance"},
    },
    
    # Cleanup de exports expirados - Diário 3h (Step 23)
    "cleanup-expired-exports": {
        "task": "app.core.celery_tasks.cleanup_expired_export_jobs_task",
        "schedule": crontab(hour=3, minute=0),  # Todos os dias 03:00
        "args": (),
        "options": {"queue": "maintenance"},
    },

    # Transições automáticas de sessões de treino - a cada 1 minuto
    "update-training-session-statuses": {
        "task": "app.core.celery_tasks.update_training_session_statuses_task",
        "schedule": crontab(minute="*"),
        "args": (),
        "options": {"queue": "maintenance"},
    },
    
    # Anonimizar dados antigos - Diário 4h (Step 25 - LGPD)
    "anonymize-old-training-data": {
        "task": "app.core.celery_tasks.anonymize_old_training_data_task",
        "schedule": crontab(hour=4, minute=0),  # Todos os dias 04:00
        "args": (),
        "options": {"queue": "maintenance"},
    },

    # Refresh diário de caches de analytics - Diário 5h (INV-TRAIN-027)
    "refresh-analytics-cache": {
        "task": "app.core.celery_tasks.refresh_training_rankings_task",
        "schedule": crontab(hour=5, minute=0),  # Todos os dias 05:00 UTC
        "args": (),
        "options": {"queue": "maintenance"},
    },
    
    # Jobs de wellness existentes (Steps anteriores - migrar aqui)
    # Descomentar quando APScheduler for removido:
    
    # "send-pre-wellness-reminders": {
    #     "task": "app.core.celery_tasks.send_pre_wellness_reminders_task",
    #     "schedule": crontab(hour=8, minute=0),  # Diário 08:00
    #     "args": (),
    # },
    
    # "send-post-wellness-reminders": {
    #     "task": "app.core.celery_tasks.send_post_wellness_reminders_task",
    #     "schedule": crontab(hour=10, minute=0),  # Diário 10:00
    #     "args": (),
    # },
    
    # "lock-expired-wellness": {
    #     "task": "app.core.celery_tasks.lock_expired_wellness_task",
    #     "schedule": crontab(hour=3, minute=0),  # Diário 03:00
    #     "args": (),
    # },
    
    # "calculate-monthly-badges": {
    #     "task": "app.core.celery_tasks.calculate_monthly_badges_task",
    #     "schedule": crontab(hour=1, minute=0, day_of_month=1),  # 1º dia do mês 01:00
    #     "args": (),
    # },
    
    # "calculate-monthly-rankings": {
    #     "task": "app.core.celery_tasks.calculate_monthly_rankings_task",
    #     "schedule": crontab(hour=2, minute=0, day_of_month=1),  # 1º dia do mês 02:00
    #     "args": (),
    # },
    
    # "generate-top-performers-report": {
    #     "task": "app.core.celery_tasks.generate_top_performers_task",
    #     "schedule": crontab(hour=8, minute=0, day_of_month=5),  # Dia 5 do mês 08:00
    #     "args": (),
    # },
}

# Auto-discover tasks (busca automaticamente tasks no módulo)
app.autodiscover_tasks(["app.core"])

# Import explícito das tasks para garantir registro
# Necessário porque o arquivo é celery_tasks.py, não tasks.py
from app.core import celery_tasks  # noqa: F401

if __name__ == "__main__":
    app.start()
