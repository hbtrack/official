"""
Migration: Create v_anonymization_status view

View provides real-time anonymization status for LGPD compliance dashboard
"""

from alembic import op


# revision identifiers
revision = '0045'
down_revision = '0044'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create v_anonymization_status view
    
    Shows records eligible for anonymization (>3 years old) per table
    """
    op.execute("""
        CREATE OR REPLACE VIEW v_anonymization_status AS
        WITH cutoff AS (
            SELECT NOW() - INTERVAL '3 years' AS cutoff_date
        ),
        wellness_pre_eligible AS (
            SELECT 
                'wellness_pre' AS table_name,
                COUNT(*) AS eligible_count,
                MIN(filled_at) AS oldest_record_date,
                MAX(filled_at) AS newest_eligible_date
            FROM wellness_pre, cutoff
            WHERE filled_at < cutoff.cutoff_date
              AND athlete_id IS NOT NULL
              AND deleted_at IS NULL
        ),
        wellness_post_eligible AS (
            SELECT 
                'wellness_post' AS table_name,
                COUNT(*) AS eligible_count,
                MIN(filled_at) AS oldest_record_date,
                MAX(filled_at) AS newest_eligible_date
            FROM wellness_post, cutoff
            WHERE filled_at < cutoff.cutoff_date
              AND athlete_id IS NOT NULL
              AND deleted_at IS NULL
        ),
        attendance_eligible AS (
            SELECT 
                'attendance' AS table_name,
                COUNT(*) AS eligible_count,
                MIN(created_at) AS oldest_record_date,
                MAX(created_at) AS newest_eligible_date
            FROM attendance, cutoff
            WHERE created_at < cutoff.cutoff_date
              AND athlete_id IS NOT NULL
              AND deleted_at IS NULL
        ),
        badges_eligible AS (
            SELECT 
                'athlete_badges' AS table_name,
                COUNT(*) AS eligible_count,
                MIN(earned_at) AS oldest_record_date,
                MAX(earned_at) AS newest_eligible_date
            FROM athlete_badges, cutoff
            WHERE earned_at < cutoff.cutoff_date
              AND athlete_id IS NOT NULL
        ),
        last_run AS (
            SELECT 
                table_name AS last_run_table,
                records_anonymized AS last_run_count,
                anonymized_at AS last_run_date
            FROM data_retention_logs
            ORDER BY anonymized_at DESC
            LIMIT 1
        ),
        all_eligible AS (
            SELECT * FROM wellness_pre_eligible
            UNION ALL
            SELECT * FROM wellness_post_eligible
            UNION ALL
            SELECT * FROM attendance_eligible
            UNION ALL
            SELECT * FROM badges_eligible
        )
        SELECT 
            e.table_name,
            e.eligible_count,
            e.oldest_record_date,
            e.newest_eligible_date,
            (SELECT cutoff_date FROM cutoff) AS cutoff_date,
            (SELECT last_run_date FROM last_run) AS last_anonymization_run,
            (SELECT last_run_count FROM last_run) AS last_run_records,
            CASE 
                WHEN e.eligible_count = 0 THEN 'compliant'
                WHEN e.eligible_count < 100 THEN 'attention'
                WHEN e.eligible_count < 1000 THEN 'warning'
                ELSE 'critical'
            END AS status_severity
        FROM all_eligible e
        WHERE e.eligible_count > 0
        
        UNION ALL
        
        -- Summary row
        SELECT 
            'TOTAL' AS table_name,
            SUM(eligible_count) AS eligible_count,
            MIN(oldest_record_date) AS oldest_record_date,
            MAX(newest_eligible_date) AS newest_eligible_date,
            (SELECT cutoff_date FROM cutoff) AS cutoff_date,
            (SELECT last_run_date FROM last_run) AS last_anonymization_run,
            (SELECT last_run_count FROM last_run) AS last_run_records,
            CASE 
                WHEN SUM(eligible_count) = 0 THEN 'compliant'
                WHEN SUM(eligible_count) < 500 THEN 'attention'
                WHEN SUM(eligible_count) < 5000 THEN 'warning'
                ELSE 'critical'
            END AS status_severity
        FROM all_eligible;
    """)
    
    # Add comment for documentation
    op.execute("""
        COMMENT ON VIEW v_anonymization_status IS 
        'Real-time status of records eligible for anonymization (LGPD Art. 16).
        Shows counts per table and severity levels for compliance dashboard.';
    """)


def downgrade():
    """Drop v_anonymization_status view"""
    op.execute("DROP VIEW IF EXISTS v_anonymization_status;")
