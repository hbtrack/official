"""
JSON report writer — CONNECTIVITY_DIAGNOSTIC_CONTRACT v1.1.0
Writes _reports/connectivity_diagnostic_report.json
"""
from __future__ import annotations

import json
import pathlib

from tools.diagnostics.models.diagnostic_result import DiagnosticResult


def write_json_report(result: DiagnosticResult, path: str) -> None:
    """Persist the diagnostic result as a structured JSON report."""
    output_path = pathlib.Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(result.to_dict(), fh, indent=2, ensure_ascii=False)
