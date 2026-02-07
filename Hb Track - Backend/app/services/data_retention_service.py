"""
Service - Data Retention and Anonymization (LGPD Compliance)

Implements LGPD data retention policy:
- Anonymizes training data after 3 years
- Preserves aggregated analytics
- Maintains badge counts without personal identification
- Logs all anonymization operations

LGPD Reference: Art. 16 - Direito à eliminação dos dados pessoais
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.data_retention_log import DataRetentionLog


class DataRetentionService:
    """
    Service for managing data retention and anonymization policies
    
    Handles:
    - Automated anonymization of old training data (>3 years)
    - Manual anonymization triggers
    - Anonymization status reporting
    - LGPD compliance logging
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def anonymize_old_training_data(
        self,
        dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Anonymize training data older than 3 years
        
        Actions:
        - SET athlete_id = NULL in wellness_pre, wellness_post, attendance
        - Preserve: training_analytics_cache (aggregated data)
        - Preserve: Badge counts (remove athlete_id link but keep totals)
        - Log: All operations in data_retention_logs
        
        Args:
            dry_run: If True, only count records without updating
            
        Returns:
            Dict with counts per table:
            {
                'wellness_pre': count,
                'wellness_post': count,
                'attendance': count,
                'athlete_badges': count,
                'total': total_count
            }
        """
        cutoff_date = datetime.now() - timedelta(days=3*365)  # 3 years
        results = {}
        
        # Anonymize wellness_pre
        wellness_pre_count = await self._anonymize_table(
            table_name='wellness_pre',
            date_column='filled_at',
            cutoff_date=cutoff_date,
            dry_run=dry_run
        )
        results['wellness_pre'] = wellness_pre_count
        
        # Anonymize wellness_post
        wellness_post_count = await self._anonymize_table(
            table_name='wellness_post',
            date_column='filled_at',
            cutoff_date=cutoff_date,
            dry_run=dry_run
        )
        results['wellness_post'] = wellness_post_count
        
        # Anonymize attendance
        attendance_count = await self._anonymize_table(
            table_name='attendance',
            date_column='created_at',
            cutoff_date=cutoff_date,
            dry_run=dry_run
        )
        results['attendance'] = attendance_count
        
        # Anonymize athlete_badges (preserve counts)
        badges_count = await self._anonymize_badges(
            cutoff_date=cutoff_date,
            dry_run=dry_run
        )
        results['athlete_badges'] = badges_count
        
        # Calculate total
        results['total'] = (
            wellness_pre_count +
            wellness_post_count +
            attendance_count +
            badges_count
        )
        
        # Log operation (if not dry_run)
        if not dry_run and results['total'] > 0:
            await self._log_anonymization(
                table_name='multiple',
                records_anonymized=results['total'],
                details=results
            )
        
        return results
    
    async def _anonymize_table(
        self,
        table_name: str,
        date_column: str,
        cutoff_date: datetime,
        dry_run: bool
    ) -> int:
        """
        Anonymize records in a specific table
        
        Args:
            table_name: Name of the table to anonymize
            date_column: Column name for date filtering
            cutoff_date: Records before this date will be anonymized
            dry_run: If True, only count records
            
        Returns:
            Number of records anonymized (or counted if dry_run)
        """
        if dry_run:
            # Count records that would be anonymized
            query = text(f"""
                SELECT COUNT(*)
                FROM {table_name}
                WHERE {date_column} < :cutoff_date
                  AND athlete_id IS NOT NULL
                  AND deleted_at IS NULL
            """)
            result = await self.db.execute(query, {"cutoff_date": cutoff_date})
            count = result.scalar()
            return count or 0
        else:
            # Anonymize records
            if table_name in ['wellness_pre', 'wellness_post']:
                # For wellness tables, also anonymize notes field
                query = text(f"""
                    UPDATE {table_name}
                    SET 
                        athlete_id = NULL,
                        notes = '[ANONIMIZADO - LGPD]'
                    WHERE {date_column} < :cutoff_date
                      AND athlete_id IS NOT NULL
                      AND deleted_at IS NULL
                """)
            else:
                # For other tables, only nullify athlete_id
                query = text(f"""
                    UPDATE {table_name}
                    SET athlete_id = NULL
                    WHERE {date_column} < :cutoff_date
                      AND athlete_id IS NOT NULL
                      AND deleted_at IS NULL
                """)
            
            result = await self.db.execute(query, {"cutoff_date": cutoff_date})
            await self.db.commit()
            
            return result.rowcount
    
    async def _anonymize_badges(
        self,
        cutoff_date: datetime,
        dry_run: bool
    ) -> int:
        """
        Anonymize athlete badges older than 3 years
        
        Note: We keep badge records for aggregate statistics,
        but remove the athlete_id link for privacy
        
        Args:
            cutoff_date: Badges before this date will be anonymized
            dry_run: If True, only count records
            
        Returns:
            Number of badges anonymized
        """
        if dry_run:
            query = text("""
                SELECT COUNT(*)
                FROM athlete_badges
                WHERE earned_at < :cutoff_date
                  AND athlete_id IS NOT NULL
            """)
            result = await self.db.execute(query, {"cutoff_date": cutoff_date})
            count = result.scalar()
            return count or 0
        else:
            query = text("""
                UPDATE athlete_badges
                SET athlete_id = NULL
                WHERE earned_at < :cutoff_date
                  AND athlete_id IS NOT NULL
            """)
            result = await self.db.execute(query, {"cutoff_date": cutoff_date})
            await self.db.commit()
            
            return result.rowcount
    
    async def _log_anonymization(
        self,
        table_name: str,
        records_anonymized: int,
        details: Optional[Dict] = None
    ) -> None:
        """
        Log anonymization operation for audit trail
        
        Args:
            table_name: Name of the table (or 'multiple')
            records_anonymized: Total number of records affected
            details: Optional additional details (JSON)
        """
        log = DataRetentionLog(
            table_name=table_name,
            records_anonymized=records_anonymized,
            details=details
        )
        self.db.add(log)
        await self.db.commit()
    
    async def get_anonymization_status(
        self,
        team_id: Optional[UUID] = None
    ) -> Dict[str, any]:
        """
        Get current anonymization status
        
        Shows:
        - Records eligible for anonymization (>3 years)
        - Last anonymization run
        - Total records anonymized to date
        
        Args:
            team_id: Optional team filter
            
        Returns:
            Status dictionary with counts per table
        """
        cutoff_date = datetime.now() - timedelta(days=3*365)
        
        # Count eligible records (dry run)
        eligible = await self.anonymize_old_training_data(dry_run=True)
        
        # Get last anonymization log
        query = select(DataRetentionLog).order_by(
            DataRetentionLog.anonymized_at.desc()
        ).limit(1)
        result = await self.db.execute(query)
        last_run = result.scalar_one_or_none()
        
        # Get total anonymized count
        total_query = text("""
            SELECT SUM(records_anonymized) as total
            FROM data_retention_logs
        """)
        total_result = await self.db.execute(total_query)
        total_anonymized = total_result.scalar() or 0
        
        return {
            'cutoff_date': cutoff_date.isoformat(),
            'eligible_for_anonymization': eligible,
            'last_run': {
                'date': last_run.anonymized_at.isoformat() if last_run else None,
                'records_processed': last_run.records_anonymized if last_run else 0,
                'table': last_run.table_name if last_run else None
            },
            'total_anonymized_to_date': int(total_anonymized),
            'policy': '3 years retention',
            'lgpd_compliance': 'Art. 16 - Direito à eliminação'
        }
    
    async def get_anonymization_history(
        self,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get history of anonymization operations
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of anonymization log entries
        """
        query = select(DataRetentionLog).order_by(
            DataRetentionLog.anonymized_at.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        return [
            {
                'id': str(log.id),
                'table_name': log.table_name,
                'records_anonymized': log.records_anonymized,
                'anonymized_at': log.anonymized_at.isoformat(),
                'details': log.details
            }
            for log in logs
        ]
    
    async def manually_trigger_anonymization(
        self,
        user_id: UUID,
        user_role: str
    ) -> Dict[str, any]:
        """
        Manually trigger anonymization process
        
        Only allowed for admin roles
        
        Args:
            user_id: ID of the user triggering the operation
            user_role: Role of the user (must be 'dirigente' or 'coordenador')
            
        Returns:
            Results of anonymization operation
            
        Raises:
            PermissionError: If user doesn't have permission
        """
        if user_role not in ['dirigente', 'coordenador']:
            raise PermissionError(
                "Apenas dirigentes e coordenadores podem executar anonimização manual"
            )
        
        # Execute anonymization
        results = await self.anonymize_old_training_data(dry_run=False)
        
        # Log the manual trigger with user info
        if results['total'] > 0:
            await self._log_anonymization(
                table_name='multiple',
                records_anonymized=results['total'],
                details={
                    **results,
                    'triggered_by_user_id': str(user_id),
                    'triggered_manually': True
                }
            )
        
        return {
            'success': True,
            'results': results,
            'triggered_by': str(user_id),
            'triggered_at': datetime.now().isoformat()
        }
