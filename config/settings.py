"""
Django settings — HB Track
Stack: Django 5.x + Django Ninja 1.x + PostgreSQL 16 + Celery 5 + Channels 4
Referência: ADR-031-backend-framework.md
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-hbtrack-dev-key-not-for-production-change-before-deploy",
)

DEBUG = os.environ.get("DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    # Django core
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    # Channels (WebSocket)
    "channels",
    # Celery results/beat
    "django_celery_results",
    "django_celery_beat",
    # CORS
    "corsheaders",
    # HB Track shared (management commands, middleware)
    "shared",
    # HB Track modules
    "identity_access",
    "users",
    "teams",
    "seasons",
    "video",
    "training",
    "competitions",
    "wellness",
    "medical",
    "matches",
    "scout",
    "exercises",
    "analytics",
    "reports",
    "ai_ingestion",
    "audit",
    "notifications",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "shared.middleware.FlowIDMiddleware",
]

ROOT_URLCONF = "config.urls"

ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "hb_track_dev"),
        "USER": os.environ.get("DB_USER", "hbtrack_dev"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "hbtrack_dev_pwd"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5433"),
        "TEST": {
            "NAME": os.environ.get("DB_TEST_NAME", "hb_track_test"),
        },
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Static files ──────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "UTC"
USE_TZ = True

# ── Redis ────────────────────────────────────────────────────────────────────
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# ── Celery ───────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "default"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True

# ── Django Channels ──────────────────────────────────────────────────────────
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_URL", "redis://localhost:6379/0")],
        },
    }
}

# ── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000",
    ).split(",")
    if o.strip()
]
CORS_ALLOW_CREDENTIALS = True

# ── Logging estruturado ──────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "logging.Formatter",
            "fmt": '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "celery": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
