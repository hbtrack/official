"""
Router - Data Retention and Anonymization (LGPD Compliance)

Endpoints for LGPD compliance:
- GET /data-retention/status - Current anonymization status
- GET /data-retention/history - History of anonymization operations
- POST /data-retention/anonymize - Manually trigger anonymization
- GET /data-retention/preview - Preview records that would be anonymized

LGPD Reference: Art. 16, Art. 18 (transparency), Art. 37 (audit logs)
"""

from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.data_retention_service import DataRetentionService
from pydantic import BaseModel


router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class AnonymizationStatusResponse(BaseModel):
    """Response for anonymization status"""
    cutoff_date: str
    eligible_for_anonymization: Dict[str, int]
    last_run: Dict[str, any]
    total_anonymized_to_date: int
    policy: str
    lgpd_compliance: str


class AnonymizationHistoryItem(BaseModel):
    """Single anonymization log entry"""
    id: str
    table_name: str
    records_anonymized: int
    anonymized_at: str
    details: Dict | None = None


class AnonymizationHistoryResponse(BaseModel):
    """Response with history of anonymization operations"""
    items: List[AnonymizationHistoryItem]
    total: int


class TriggerAnonymizationResponse(BaseModel):
    """Response after manually triggering anonymization"""
    success: bool
    results: Dict[str, int]
    triggered_by: str
    triggered_at: str


class PreviewAnonymizationResponse(BaseModel):
    """Preview of records that would be anonymized"""
    cutoff_date: str
    would_anonymize: Dict[str, int]
    total: int
    estimated_duration_seconds: int


# =============================================================================
# Endpoints
# =============================================================================

@router.get(
    "/status",
    response_model=AnonymizationStatusResponse,
    summary="Get anonymization status",
    description="""
    Get current anonymization status for LGPD compliance dashboard.
    
    Shows:
    - Number of records eligible for anonymization (>3 years)
    - Date of last anonymization run
    - Total records anonymized to date
    - Policy details (3 years retention)
    
    **Permissions:** Dirigente, Coordenador
    
    **LGPD:** Art. 18 (transparency of processing)
    """,
    tags=["lgpd"]
)
async def get_anonymization_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get current anonymization status"""
    
    # Permission check: only dirigente and coordenador
    if not current_user.has_permission('manage_data_retention'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente. Apenas dirigentes e coordenadores."
        )
    
    service = DataRetentionService(db)
    status_data = await service.get_anonymization_status()
    
    return status_data


@router.get(
    "/history",
    response_model=AnonymizationHistoryResponse,
    summary="Get anonymization history",
    description="""
    Get history of anonymization operations.
    
    Returns audit trail of all anonymization runs with:
    - Tables affected
    - Number of records anonymized
    - Timestamp of operation
    - Additional details (user, trigger type)
    
    **Permissions:** Dirigente, Coordenador
    
    **LGPD:** Art. 37 (audit logs of processing)
    """,
    tags=["lgpd"]
)
async def get_anonymization_history(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of records"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get history of anonymization operations"""
    
    # Permission check
    if not current_user.has_permission('manage_data_retention'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente"
        )
    
    service = DataRetentionService(db)
    history = await service.get_anonymization_history(limit=limit)
    
    return {
        "items": history,
        "total": len(history)
    }


@router.post(
    "/anonymize",
    response_model=TriggerAnonymizationResponse,
    summary="Manually trigger anonymization",
    description="""
    Manually trigger the anonymization process.
    
    This will:
    1. Find all records older than 3 years
    2. SET athlete_id = NULL (wellness_pre, wellness_post, attendance, badges)
    3. Preserve aggregated analytics data
    4. Log the operation in data_retention_logs
    
    **Warning:** This operation cannot be undone!
    
    **Permissions:** Dirigente only
    
    **LGPD:** Art. 16 (right to deletion/anonymization)
    """,
    tags=["lgpd"]
)
async def manually_trigger_anonymization(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Manually trigger anonymization process"""
    
    # Permission check: only dirigente
    if not current_user.has_permission('manage_data_retention'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas dirigentes podem executar anonimização manual"
        )
    
    service = DataRetentionService(db)
    
    try:
        result = await service.manually_trigger_anonymization(
            user_id=current_user.id,
            user_role='dirigente'  # Validated by permission above
        )
        
        return result
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar anonimização: {str(e)}"
        )


@router.get(
    "/preview",
    response_model=PreviewAnonymizationResponse,
    summary="Preview anonymization",
    description="""
    Preview how many records would be anonymized without actually doing it.
    
    Performs a dry-run to count:
    - wellness_pre records >3 years
    - wellness_post records >3 years
    - attendance records >3 years
    - athlete_badges >3 years
    
    **Permissions:** Dirigente, Coordenador
    
    **Use case:** Check impact before running manual anonymization
    """,
    tags=["lgpd"]
)
async def preview_anonymization(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Preview records that would be anonymized (dry-run)"""
    
    # Permission check
    if not current_user.has_permission('manage_data_retention'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente"
        )
    
    service = DataRetentionService(db)
    
    # Run dry-run
    results = await service.anonymize_old_training_data(dry_run=True)
    
    # Estimate duration (rough: 1000 records per second)
    estimated_duration = max(1, results['total'] // 1000)
    
    from datetime import datetime, timedelta
    cutoff_date = (datetime.now() - timedelta(days=3*365)).isoformat()
    
    return {
        "cutoff_date": cutoff_date,
        "would_anonymize": results,
        "total": results['total'],
        "estimated_duration_seconds": estimated_duration
    }
