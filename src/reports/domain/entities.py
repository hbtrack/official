from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

VALID_FORMATS = frozenset(["pdf", "excel", "csv", "json"])
VALID_STATUSES = frozenset(["queued", "processing", "completed", "failed", "cancelled"])
CANCELLABLE_STATUSES = frozenset(["queued", "processing"])


@dataclass
class ReportJob:
    id: UUID
    owner_user_id: UUID
    report_type: str
    requested_at: datetime
    format_label: Optional[str] = None
    parameter_summary: Optional[str] = None
    source_metric_names: List[str] = field(default_factory=list)
    generated_artifact_ref: Optional[str] = None
    retention_label: Optional[str] = None
    status_label: str = "queued"
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def validate_invariants(self) -> None:
        # INV-RPT-001: id, ownerUserId, reportType required
        if not self.id:
            raise ValueError("INV-RPT-001: id is required")
        if not self.owner_user_id:
            raise ValueError("INV-RPT-001: ownerUserId is required")
        if not self.report_type:
            raise ValueError("INV-RPT-001: reportType is required")
        # INV-RPT-003: requestedAt required
        if not self.requested_at:
            raise ValueError("INV-RPT-003: requestedAt is required")
        # INV-RPT-002: sourceMetricNames unique
        if len(self.source_metric_names) != len(set(self.source_metric_names)):
            raise ValueError("INV-RPT-002: sourceMetricNames must be unique")
        # INV-RPT-004: generatedArtifactRef -> retentionLabel required
        if self.generated_artifact_ref and not self.retention_label:
            raise ValueError("INV-RPT-004: retentionLabel required when generatedArtifactRef is set")

    def can_be_cancelled(self) -> bool:
        return self.status_label in CANCELLABLE_STATUSES

    def can_be_updated(self) -> bool:
        # PERM-REP-003: only QUEUED jobs can be updated
        return self.status_label == "queued"
