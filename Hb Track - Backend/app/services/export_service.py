"""
Export Service - Step 23

Handles PDF export jobs with rate limiting, caching via params_hash,
and async job creation using Celery.
"""
import hashlib
import json
from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export_job import ExportJob
from app.models.export_rate_limit import ExportRateLimit
from app.schemas.exports import (
    AnalyticsPDFExportRequest,
    AthleteDataExportRequest,
    ExportJobResponse,
    ExportRateLimitResponse,
)


class ExportService:
    """Service for managing export jobs and rate limits"""
    
    # Rate limit constants
    ANALYTICS_PDF_DAILY_LIMIT = 5
    ATHLETE_DATA_DAILY_LIMIT = 3
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_rate_limit(
        self,
        user_id: UUID,
        export_type: str
    ) -> ExportRateLimitResponse:
        """
        Check if user has exceeded rate limit for today
        
        Returns:
            ExportRateLimitResponse with remaining_today count
        
        Raises:
            Exception if limit exceeded
        """
        today = date.today()
        
        # Get or create rate limit record
        stmt = select(ExportRateLimit).where(
            and_(
                ExportRateLimit.user_id == user_id,
                ExportRateLimit.export_type == export_type,
                ExportRateLimit.date == today
            )
        )
        result = await self.db.execute(stmt)
        rate_limit = result.scalar_one_or_none()
        
        if rate_limit is None:
            # Create new record
            rate_limit = ExportRateLimit(
                user_id=user_id,
                export_type=export_type,
                date=today,
                count=0
            )
            self.db.add(rate_limit)
            await self.db.flush()
        
        # Determine limit
        limit = self._get_daily_limit(export_type)
        remaining = max(0, limit - rate_limit.count)
        
        if remaining == 0:
            raise Exception(
                f"Daily export limit exceeded. You can export {limit} times per day. "
                f"Limit resets at midnight."
            )
        
        tomorrow = datetime.combine(today + timedelta(days=1), datetime.min.time())
        
        return ExportRateLimitResponse(
            export_type=export_type,
            remaining_today=remaining,
            total_limit=limit,
            resets_at=tomorrow
        )
    
    async def increment_rate_limit(
        self,
        user_id: UUID,
        export_type: str
    ) -> None:
        """Increment rate limit counter after successful job creation"""
        today = date.today()
        
        stmt = select(ExportRateLimit).where(
            and_(
                ExportRateLimit.user_id == user_id,
                ExportRateLimit.export_type == export_type,
                ExportRateLimit.date == today
            )
        )
        result = await self.db.execute(stmt)
        rate_limit = result.scalar_one_or_none()
        
        if rate_limit:
            rate_limit.increment()
        else:
            # Should not happen if check_rate_limit was called first
            rate_limit = ExportRateLimit(
                user_id=user_id,
                export_type=export_type,
                date=today,
                count=1,
                last_export_at=datetime.utcnow()
            )
            self.db.add(rate_limit)
        
        await self.db.commit()
    
    async def check_cache(
        self,
        export_type: str,
        params_hash: str
    ) -> Optional[ExportJob]:
        """
        Check if identical export already exists and is still valid
        
        Returns:
            ExportJob if cached result found, None otherwise
        """
        stmt = select(ExportJob).where(
            and_(
                ExportJob.export_type == export_type,
                ExportJob.params_hash == params_hash,
                ExportJob.status == 'completed',
                ExportJob.expires_at > datetime.utcnow()
            )
        ).order_by(ExportJob.completed_at.desc())
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_export_job(
        self,
        user_id: UUID,
        export_type: str,
        params: dict
    ) -> ExportJob:
        """
        Create a new export job
        
        Steps:
        1. Check rate limit
        2. Calculate params_hash
        3. Check cache
        4. Create job record
        5. Increment rate limit
        6. Trigger Celery task (async)
        
        Returns:
            ExportJob instance
        """
        # 1. Check rate limit
        await self.check_rate_limit(user_id, export_type)
        
        # 2. Calculate params_hash (SHA256 of sorted JSON)
        params_json = json.dumps(params, sort_keys=True, default=str)
        params_hash = hashlib.sha256(params_json.encode()).hexdigest()
        
        # 3. Check cache
        cached_job = await self.check_cache(export_type, params_hash)
        if cached_job:
            # Return cached job without incrementing rate limit
            return cached_job
        
        # 4. Create job record
        job = ExportJob(
            user_id=user_id,
            export_type=export_type,
            params=params,
            params_hash=params_hash,
            status='pending'
        )
        self.db.add(job)
        await self.db.flush()
        
        # 5. Increment rate limit
        await self.increment_rate_limit(user_id, export_type)
        
        # 6. Trigger Celery task (async)
        from app.core.celery_tasks import generate_analytics_pdf_task
        generate_analytics_pdf_task.delay(str(job.id))
        
        await self.db.commit()
        await self.db.refresh(job)
        
        return job
    
    async def get_job_status(
        self,
        job_id: UUID,
        user_id: UUID
    ) -> ExportJob:
        """
        Get status of an export job
        
        Raises:
            Exception if job not found or not owned by user
        """
        stmt = select(ExportJob).where(
            and_(
                ExportJob.id == job_id,
                ExportJob.user_id == user_id
            )
        )
        result = await self.db.execute(stmt)
        job = result.scalar_one_or_none()
        
        if not job:
            raise Exception("Export job not found or access denied")
        
        return job
    
    async def list_user_jobs(
        self,
        user_id: UUID,
        page: int = 1,
        per_page: int = 10
    ) -> tuple[list[ExportJob], int]:
        """
        List export jobs for a user
        
        Returns:
            (jobs, total_count)
        """
        offset = (page - 1) * per_page
        
        # Get total count
        count_stmt = select(func.count(ExportJob.id)).where(
            ExportJob.user_id == user_id
        )
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()
        
        # Get jobs
        stmt = select(ExportJob).where(
            ExportJob.user_id == user_id
        ).order_by(
            ExportJob.created_at.desc()
        ).limit(per_page).offset(offset)
        
        result = await self.db.execute(stmt)
        jobs = result.scalars().all()
        
        return list(jobs), total
    
    async def cleanup_expired_jobs(self) -> int:
        """
        Delete expired export jobs (Celery scheduled task)
        
        Returns:
            Number of jobs deleted
        """
        stmt = select(ExportJob).where(
            and_(
                ExportJob.status == 'completed',
                ExportJob.expires_at < datetime.utcnow()
            )
        )
        result = await self.db.execute(stmt)
        expired_jobs = result.scalars().all()
        
        count = len(expired_jobs)
        for job in expired_jobs:
            await self.db.delete(job)
        
        await self.db.commit()
        return count
    
    async def cleanup_old_rate_limits(self) -> int:
        """
        Delete rate limit records older than 30 days (Celery scheduled task)
        
        Returns:
            Number of records deleted
        """
        cutoff_date = date.today() - timedelta(days=30)
        
        stmt = select(ExportRateLimit).where(
            ExportRateLimit.date < cutoff_date
        )
        result = await self.db.execute(stmt)
        old_limits = result.scalars().all()
        
        count = len(old_limits)
        for limit in old_limits:
            await self.db.delete(limit)
        
        await self.db.commit()
        return count
    
    def _get_daily_limit(self, export_type: str) -> int:
        """Get daily limit for export type"""
        if export_type == 'analytics_pdf':
            return self.ANALYTICS_PDF_DAILY_LIMIT
        elif export_type in ['athlete_data_json', 'athlete_data_csv']:
            return self.ATHLETE_DATA_DAILY_LIMIT
        else:
            return 5  # Default
