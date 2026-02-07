"""
Export Job Model - Step 23

Tracks asynchronous export jobs (PDF analytics, athlete data JSON/CSV)
with status tracking, cache via params_hash, and automatic cleanup.
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ExportJob(Base):
    __tablename__ = "export_jobs"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    
    # Foreign Keys
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Export Details
    export_type: Mapped[str] = mapped_column(String(50), nullable=False)
    """Type: analytics_pdf, athlete_data_json, athlete_data_csv"""
    
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    """Status: pending, processing, completed, failed"""
    
    params: Mapped[dict] = mapped_column(JSONB, nullable=False)
    """Export parameters (team_id, start_date, end_date, include_wellness, etc)"""
    
    params_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    """SHA256 hash of params for cache lookup"""
    
    # Result
    file_url: Mapped[Optional[str]] = mapped_column(String(500))
    """S3/local URL when completed"""
    
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    started_at: Mapped[Optional[datetime]]
    completed_at: Mapped[Optional[datetime]]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    expires_at: Mapped[Optional[datetime]]
    """Auto-delete file after 7 days (set on completion)"""
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="export_jobs")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "export_type IN ('analytics_pdf', 'athlete_data_json', 'athlete_data_csv')",
            name='ck_export_jobs_valid_type'
        ),
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name='ck_export_jobs_valid_status'
        ),
        CheckConstraint(
            "file_size_bytes IS NULL OR file_size_bytes > 0",
            name='ck_export_jobs_positive_file_size'
        ),
        Index('idx_export_jobs_user', 'user_id', 'created_at', postgresql_ops={'created_at': 'DESC'}),
        Index('idx_export_jobs_status', 'status', 'created_at', postgresql_where="status IN ('pending', 'processing')"),
        Index('idx_export_jobs_cache_lookup', 'export_type', 'params_hash', 'status', postgresql_where="status = 'completed' AND expires_at > NOW()"),
        Index('idx_export_jobs_cleanup', 'expires_at', postgresql_where="expires_at IS NOT NULL AND status = 'completed'"),
    )
    
    def mark_processing(self) -> None:
        """Mark job as processing"""
        self.status = "processing"
        self.started_at = datetime.utcnow()
    
    def mark_completed(self, file_url: str, file_size: int) -> None:
        """Mark job as completed"""
        self.status = "completed"
        self.file_url = file_url
        self.file_size_bytes = file_size
        self.completed_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(days=7)
    
    def mark_failed(self, error: str) -> None:
        """Mark job as failed"""
        self.status = "failed"
        self.error_message = error
        self.completed_at = datetime.utcnow()
