"""
Model - Data Retention Log (LGPD Compliance)

Records all anonymization operations for audit trail
"""

# HB-AUTOGEN-IMPORTS:BEGIN
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET, ENUM as PG_ENUM
# HB-AUTOGEN-IMPORTS:END

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.db import Base


class DataRetentionLog(Base):
    """
    Log of data retention and anonymization operations
    
    Tracks:
    - Which tables were anonymized
    - How many records were affected
    - When the operation occurred
    - Additional details (JSON)
    
    LGPD Reference: Art. 16, Art. 37 (logs de processamento)
    """
    
    __tablename__ = "data_retention_logs"
    

# HB-AUTOGEN:BEGIN
    
    # AUTO-GENERATED FROM DB (SSOT). DO NOT EDIT MANUALLY.
    
    # Table: public.data_retention_logs
    
    # NOTE: typing helpers may require: from datetime import date, datetime; from uuid import UUID

    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    
    table_name: Mapped[str] = mapped_column(sa.String(length=100), nullable=False)
    
    records_anonymized: Mapped[int] = mapped_column(sa.Integer(), nullable=False)
    
    anonymized_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    
    # HB-AUTOGEN:END
    
    def __repr__(self):
        return (
            f"<DataRetentionLog("
            f"table={self.table_name}, "
            f"records={self.records_anonymized}, "
            f"at={self.anonymized_at}"
            f")>"
        )
