"""
Fixtures para replay packs de staging.

Dois modos:
- Estrutural (padrão): testa imports, describe() e estrutura — sem Django nem rede.
- Live staging: ativado quando HB_STAGING_URL está definida — executa replay completo.
"""
from __future__ import annotations

import os
import pytest


STAGING_URL = os.environ.get("HB_STAGING_URL", "").strip().rstrip("/")


@pytest.fixture(scope="session")
def staging_url() -> str:
    return STAGING_URL


@pytest.fixture(scope="session")
def live_staging() -> bool:
    return bool(STAGING_URL)


@pytest.fixture(scope="session")
def http_client(live_staging):
    """Cliente HTTP para live staging. Yields None se não estiver em modo live."""
    if not live_staging:
        yield None
        return
    import httpx
    with httpx.Client(timeout=30.0) as client:
        yield client
