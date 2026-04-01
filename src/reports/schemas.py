from __future__ import annotations

# Canonical runtime adapter: reports now composes the generated contract layer.
from .generated.schemas import (
    CreateReportJobIn,
    ErrorOut,
    ReportJobListOut,
    ReportJobOut,
    UpdateReportJobIn,
)

__all__ = [
    "ReportJobOut",
    "ReportJobListOut",
    "CreateReportJobIn",
    "UpdateReportJobIn",
    "ErrorOut",
]
