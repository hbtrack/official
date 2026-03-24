"""
Celery 5.x — HB Track
Broker: Redis (CELERY_BROKER_URL)
Backend: django-celery-results (CELERY_RESULT_BACKEND)
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("hbtrack")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
