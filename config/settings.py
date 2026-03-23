"""
Django settings — HB Track
Stack: Django 5.x + Django Ninja 1.x + PostgreSQL 16
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
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

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

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "UTC"
USE_TZ = True
