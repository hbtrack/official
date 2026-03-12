"""
CheckResult model — CONNECTIVITY_DIAGNOSTIC_CONTRACT v1.1.0
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CheckResult:
    """Represents the output of a single diagnostic check."""

    name: str
    status: str  # pass | fail | skip | warn
    evidence: Any
    root_cause_candidate: Optional[str] = None

    def to_dict(self) -> dict:
        d: dict = {
            "name": self.name,
            "status": self.status,
            "evidence": self.evidence,
        }
        if self.root_cause_candidate:
            d["root_cause_candidate"] = self.root_cause_candidate
        return d
