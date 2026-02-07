"""
Model - Data Retention Log (LGPD Compliance)

Records all anonymization operations for audit trail
"""

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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String(100), nullable=False, index=True)
    records_anonymized = Column(Integer, nullable=False)
    anonymized_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    details = Column(JSON, nullable=True)
    
    def __repr__(self):
        return (
            f"<DataRetentionLog("
            f"table={self.table_name}, "
            f"records={self.records_anonymized}, "
            f"at={self.anonymized_at}"
            f")>"
        )
