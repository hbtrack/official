"""
Utilitários comuns para replay packs de staging.

Dois modos:
- WSGI local (padrão): usa Django test client em memória.
- Live staging: ativado quando HB_STAGING_URL está definida.
"""
from __future__ import annotations

import json
import os
from typing import Any


STAGING_URL = os.environ.get("HB_STAGING_URL", "").strip().rstrip("/")


def is_live_staging() -> bool:
    return bool(STAGING_URL)


def _assert_status(response: Any, expected: int, label: str) -> None:
    got = getattr(response, "status_code", None)
    assert got == expected, (
        f"{label}: esperado HTTP {expected}, obteve {got}. "
        f"Body: {getattr(response, 'content', b'')[:500]}"
    )


def _json(response: Any) -> dict:
    content = getattr(response, "content", b"")
    return json.loads(content)


SEED_ADMIN_EMAIL = "admin@hbtrack.test"
SEED_ADMIN_PASSWORD = "hbtrack_test_2024!"

SEED_USER_EMAIL = "atleta@hbtrack.test"
SEED_USER_PASSWORD = "hbtrack_test_2024!"
