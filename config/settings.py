"""
Django settings — HB Track
Stack: Django 5.x + Django Ninja 1.x + PostgreSQL 16 + Celery 5 + Channels 4
Referência: ADR-031-backend-framework.md
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega .env da raiz do projeto (dev/local — não sobrescreve variáveis já definidas)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env", override=False)
except ImportError:
    pass  # python-dotenv opcional em produção (variáveis declaradas externamente)

# Garante que src/ esteja no path independente de como Django é iniciado
# (manage.py, gunicorn, uvicorn, celery, etc.)
_SRC_DIR = str(BASE_DIR / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

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
    "shared.middleware.SecurityHeadersMiddleware",
    "shared.middleware.FlowIDMiddleware",
    "shared.middleware.JWTClaimsMiddleware",
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
AUTH_USER_MODEL = "identity_access.HBTrackUser"

# ── Static files ──────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ── Templates ──────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

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
# Temporarily allow all origins for CI tests
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000",
    ).split(",")
    if o.strip()
]
CORS_ALLOW_CREDENTIALS = True
CORS_PREFLIGHT_MAX_AGE = 86400
CORS_ALLOWED_ORIGINS_REGEXES = [
    r"^http://localhost:\d+$",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# ── Logging estruturado ──────────────────────────────────────────────────────
_LOG_DIR = BASE_DIR / "logs"
_LOG_DIR.mkdir(exist_ok=True)

_handlers: dict = {
    "console": {
        "class": "logging.StreamHandler",
        "formatter": "flow_json",
    },
}

# Rotação de arquivos em produção (não em DEBUG)
if not DEBUG:
    _handlers["file"] = {
        "class": "logging.handlers.TimedRotatingFileHandler",
        "filename": str(_LOG_DIR / "hbtrack.log"),
        "when": "midnight",
        "backupCount": 30,          # 30 dias de retenção
        "encoding": "utf-8",
        "formatter": "flow_json",
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "flow_json": {
            # FlowIDFormatter: injeta flow_id em cada linha de log (FASE 1.7)
            "()": "shared.logging_formatters.FlowIDFormatter",
        },
    },
    "handlers": _handlers,
    "root": {
        "handlers": list(_handlers.keys()),
        "level": os.environ.get("LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {
            "handlers": list(_handlers.keys()),
            "level": "WARNING",
            "propagate": False,
        },
        "celery": {
            "handlers": list(_handlers.keys()),
            "level": "INFO",
            "propagate": False,
        },
    },
}
