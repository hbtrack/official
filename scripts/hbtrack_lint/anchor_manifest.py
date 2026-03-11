"""
Geração do anchor manifest a partir dos contratos.

SSOT: docs/hbtrack/modulos/atletas/MOTORES.md
"""
from __future__ import annotations

import hashlib
from pathlib import Path


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_anchor_manifest(
    repo_root: Path,
    module_root: Path,
    contracts: dict,
) -> dict:
    """
    Constrói o anchor manifest mapeando operações → arquivos gerados com âncoras.

    Na versão de bootstrap, deriva das operações declaradas em 08_ATLETAS_TRACEABILITY.yaml.
    Na versão forte, extrairia âncoras dos stubs físicos já gerados.
    """
    traceability = contracts.get("08_ATLETAS_TRACEABILITY.yaml") or {}
    handoff_files = []

    for op in traceability.get("operations", []):
        operation_id = op.get("operation_id", "")
        binding = op.get("implementation_binding") or {}

        backend_handler = binding.get("backend_handler")
        file_path = binding.get("backend_handler_file", f"Hb Track - Backend/app/services/athlete_service.py")

        if not backend_handler:
            backend_handler = _derive_handler_name(operation_id)

        start_marker = f"# <HB-BODY-START:{operation_id}>"
        end_marker = f"# <HB-BODY-END:{operation_id}>"

        handoff_files.append({
            "path": file_path,
            "language": "python",
            "anchors": [
                {
                    "symbol_id": operation_id,
                    "public_symbol": backend_handler,
                    "anchor_type": "function_body",
                    "start_marker": start_marker,
                    "end_marker": end_marker,
                    "anchor_hash": _hash_text(start_marker + end_marker + backend_handler),
                }
            ],
        })

    return {
        "module_id": (traceability.get("meta") or {}).get("module_id", "ATHLETES"),
        "snapshot_hash": "0" * 64,
        "files": handoff_files,
    }


def _derive_handler_name(operation_id: str) -> str:
    """Deriva nome de handler a partir do operation_id (ex: athletes__athlete__create → athlete_create)."""
    parts = operation_id.split("__")
    if len(parts) >= 3:
        return f"athlete_{parts[-1]}"
    return operation_id
