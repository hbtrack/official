"""
DiagnosticResult model — CONNECTIVITY_DIAGNOSTIC_CONTRACT v1.1.0
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class DiagnosticResult:
    """Aggregated result of the full diagnostic run."""

    status: str            # pass | fail
    exit_code: int
    root_cause_code: str
    root_cause_summary: str
    checks: List[Any]
    inputs: dict
    recommended_action: str
    contract: str = "CONNECTIVITY_DIAGNOSTIC_CONTRACT"
    version: str = "1.1.0"

    def to_dict(self) -> dict:
        return {
            "contract": self.contract,
            "version": self.version,
            "status": self.status,
            "exit_code": self.exit_code,
            "root_cause_code": self.root_cause_code,
            "root_cause_summary": self.root_cause_summary,
            "inputs": self.inputs,
            "checks": [
                c.to_dict() if hasattr(c, "to_dict") else c
                for c in self.checks
            ],
            "recommended_action": self.recommended_action,
        }
