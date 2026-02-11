"""
Export Job Model - Step 23

Tracks asynchronous export jobs (PDF analytics, athlete data JSON/CSV)
with status tracking, cache via params_hash, and automatic cleanup.
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END


from app.models.base import Base


class ExportJob(Base):
    __tablename__ = "export_jobs"
    

# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.export_jobs
    __table_args__ = (
        CheckConstraint("status::text = ANY (ARRAY['pending'::character varying, 'processing'::character varying, 'completed'::character varying, 'failed'::character varying]::text[])", name='ck_export_jobs_status'),
        Index('idx_export_cache', 'params_hash', 'status', unique=False, postgresql_where=sa.text("((status)::text = 'completed'::text)")),
    )

    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='export_jobs_user_id_fkey', ondelete='CASCADE'), nullable=False)
    export_type: Mapped[str] = mapped_column(sa.String(length=50), nullable=False)
    params: Mapped[object] = mapped_column(PG_JSONB(), nullable=False)
    params_hash: Mapped[str] = mapped_column(sa.String(length=64), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(length=20), nullable=False, server_default=sa.text("'pending'::character varying"))
    file_url: Mapped[Optional[str]] = mapped_column(sa.String(length=500), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(sa.Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    completed_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    # HB-AUTOGEN:END
    # Primary Key
    
    # Foreign Keys
    
    # Export Details
    """Type: analytics_pdf, athlete_data_json, athlete_data_csv"""
    
    """Status: pending, processing, completed, failed"""
    
    """Export parameters (team_id, start_date, end_date, include_wellness, etc)"""
    
    """SHA256 hash of params for cache lookup"""
    
    # Result
    """S3/local URL when completed"""
    
    
    
    # Timestamps
    """Auto-delete file after 7 days (set on completion)"""
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="export_jobs")
    
    # Constraints
    
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
