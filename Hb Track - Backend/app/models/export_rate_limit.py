"""
Export Rate Limit Model - Step 23

Tracks daily export counts per user to enforce rate limits (5/day for analytics_pdf).
Automatically cleaned up after 30 days.
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


class ExportRateLimit(Base):
    __tablename__ = "export_rate_limits"
    

# HB-AUTOGEN:BEGIN
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    # Table: public.export_rate_limits
    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id', name='export_rate_limits_user_id_fkey', ondelete='CASCADE'), primary_key=True)
    date: Mapped[date] = mapped_column(sa.Date(), primary_key=True)
    count: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default=sa.text('0'))
    # HB-AUTOGEN:END
    # Primary Key
    
    # Foreign Keys
    
    # Rate Limit Tracking
    """Type: analytics_pdf, athlete_data_json, athlete_data_csv"""
    
    """Date for counting (resets daily)"""
    
    """Number of exports today"""
    
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="export_rate_limits")
    
    # Constraints
    
    def increment(self) -> None:
        """Increment count and update timestamp"""
        self.count += 1
        self.last_export_at = datetime.utcnow()
