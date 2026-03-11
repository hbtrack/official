"""
Utilitários de hash determinístico.

SSOT: docs/hbtrack/modulos/atletas/MOTORES.md
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Calcula SHA-256 do conteúdo binário de um arquivo."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def sha256_jsonable(obj) -> str:
    """Calcula SHA-256 de um objeto JSON serializado de forma determinística."""
    data = json.dumps(
        obj,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()
