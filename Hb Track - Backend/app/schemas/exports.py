"""
Export Schemas - Step 23

Pydantic schemas for PDF export and LGPD data export functionality.
"""
from datetime import date, datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ========================================
# Export Request Schemas
# ========================================

class AnalyticsPDFExportRequest(BaseModel):
    """Request to export analytics as PDF"""
    team_id: UUID
    start_date: date = Field(..., description="Start date for analytics period")
    end_date: date = Field(..., description="End date for analytics period")
    include_wellness: bool = Field(True, description="Include wellness metrics")
    include_badges: bool = Field(True, description="Include badges and rankings")
    include_prevention: bool = Field(True, description="Include prevention effectiveness")
    
    @field_validator('end_date')
    @classmethod
    def end_date_after_start(cls, v: date, info) -> date:
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "f2971108-2b14-478d-b5af-39aae83749da",
                "start_date": "2026-01-01",
                "end_date": "2026-01-31",
                "include_wellness": True,
                "include_badges": True,
                "include_prevention": True
            }
        }


class AthleteDataExportRequest(BaseModel):
    """Request to export athlete's personal data (LGPD)"""
    export_format: str = Field("json", description="Export format: json or csv")
    
    @field_validator('export_format')
    @classmethod
    def valid_format(cls, v: str) -> str:
        if v not in ['json', 'csv']:
            raise ValueError('export_format must be json or csv')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "export_format": "json"
            }
        }


# ========================================
# Export Job Response Schemas
# ========================================

class ExportJobResponse(BaseModel):
    """Response for export job status"""
    id: UUID
    export_type: str
    status: str  # pending, processing, completed, failed
    params: Dict[str, Any]
    file_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "export_type": "analytics_pdf",
                "status": "completed",
                "params": {
                    "team_id": "f2971108-2b14-478d-b5af-39aae83749da",
                    "start_date": "2026-01-01",
                    "end_date": "2026-01-31"
                },
                "file_url": "https://s3.amazonaws.com/exports/analytics_abc123.pdf",
                "file_size_bytes": 2048576,
                "error_message": None,
                "started_at": "2026-01-17T23:00:00Z",
                "completed_at": "2026-01-17T23:01:30Z",
                "created_at": "2026-01-17T23:00:00Z",
                "expires_at": "2026-01-24T23:01:30Z"
            }
        }


class ExportJobListResponse(BaseModel):
    """Response for list of export jobs"""
    jobs: list[ExportJobResponse]
    total: int
    page: int
    per_page: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "jobs": [],
                "total": 15,
                "page": 1,
                "per_page": 10
            }
        }


# ========================================
# Rate Limit Response
# ========================================

class ExportRateLimitResponse(BaseModel):
    """Response for rate limit status"""
    export_type: str
    remaining_today: int
    total_limit: int
    resets_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "export_type": "analytics_pdf",
                "remaining_today": 3,
                "total_limit": 5,
                "resets_at": "2026-01-18T00:00:00Z"
            }
        }
