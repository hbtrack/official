"""
Export Rate Limit Model - Step 23

Tracks daily export counts per user to enforce rate limits (5/day for analytics_pdf).
Automatically cleaned up after 30 days.
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ExportRateLimit(Base):
    __tablename__ = "export_rate_limits"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    
    # Foreign Keys
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Rate Limit Tracking
    export_type: Mapped[str] = mapped_column(String(50), nullable=False)
    """Type: analytics_pdf, athlete_data_json, athlete_data_csv"""
    
    date: Mapped[date] = mapped_column(Date, nullable=False)
    """Date for counting (resets daily)"""
    
    count: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    """Number of exports today"""
    
    last_export_at: Mapped[Optional[datetime]]
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="export_rate_limits")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'export_type', 'date', name='uq_export_rate_limits_user_type_date'),
        CheckConstraint(
            "count >= 0 AND count <= 10",
            name='ck_export_rate_limits_reasonable_count'
        ),
        Index('idx_export_rate_limits_user_date', 'user_id', 'date', postgresql_ops={'date': 'DESC'}),
        Index('idx_export_rate_limits_cleanup', 'date', postgresql_where="date < CURRENT_DATE - INTERVAL '30 days'"),
    )
    
    def increment(self) -> None:
        """Increment count and update timestamp"""
        self.count += 1
        self.last_export_at = datetime.utcnow()
