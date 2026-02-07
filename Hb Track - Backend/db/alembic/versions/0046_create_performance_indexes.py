"""
Migration: Create Performance Indexes (Step 26)

8 strategic indexes to optimize query performance:
1. idx_wellness_athlete_date - Wellness history by athlete
2. idx_wellness_session_athlete - Wellness by session and athlete
3. idx_wellness_reminders_pending - Pending reminders lookup
4. idx_badges_athlete_month - Badge leaderboard queries
5. idx_rankings_team_month - Team rankings by month
6. idx_sessions_team_date - Session listing by team
7. idx_analytics_lookup - Analytics cache queries
8. idx_notifications_unread - Unread notifications

Target: All queries <50ms
"""

from alembic import op


# revision identifiers
revision = '0046'
down_revision = '0045'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create 8 strategic indexes for performance optimization
    
    Each index targets specific query patterns with high frequency:
    - Wellness queries: athlete history, session status
    - Gamification: badges, rankings
    - Notifications: unread count, listing
    - Analytics: cache lookup
    """
    
    # 1. Wellness Post - Athlete History (athlete profile, wellness history page)
    # Query pattern: SELECT * FROM wellness_post WHERE athlete_id = ? ORDER BY filled_at DESC
    # Estimated improvement: 200ms → 15ms for 500+ records
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_wellness_athlete_date 
        ON wellness_post(athlete_id, filled_at DESC)
        WHERE athlete_id IS NOT NULL;
    """)
    
    op.execute("""
        COMMENT ON INDEX idx_wellness_athlete_date IS 
        'Optimizes wellness history queries by athlete. Used in athlete profile and history pages.
        WHERE clause excludes anonymized records (athlete_id IS NULL).';
    """)
    
    # 2. Wellness Pre - Session Status (wellness status dashboard)
    # Query pattern: SELECT * FROM wellness_pre WHERE training_session_id = ? AND athlete_id IN (...)
    # Estimated improvement: 100ms → 10ms for 30 athletes
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_wellness_session_athlete 
        ON wellness_pre(training_session_id, athlete_id);
    """)
    
    op.execute("""
        COMMENT ON INDEX idx_wellness_session_athlete IS 
        'Optimizes wellness status queries per session. Used in wellness dashboard and session modal.';
    """)
    
    # 3. Wellness Reminders - Pending Lookup (scheduled jobs)
    # Query pattern: SELECT * FROM wellness_reminders WHERE responded_at IS NULL
    # Estimated improvement: 80ms → 5ms for 1000+ reminders
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_wellness_reminders_pending 
        ON wellness_reminders(training_session_id, athlete_id)
        WHERE responded_at IS NULL;
    """)
    
    op.execute("""
        COMMENT ON INDEX idx_wellness_reminders_pending IS 
        'Optimizes pending reminder lookups. Used by scheduled jobs (send_pre_wellness_reminders_daily).
        Partial index: only indexes unresponded reminders.';
    """)
    
    # 4. Athlete Badges - Leaderboard (gamification)
    # Query pattern: SELECT * FROM athlete_badges WHERE athlete_id = ? ORDER BY month_reference DESC
    # Estimated improvement: 50ms → 8ms for 50+ badges
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_badges_athlete_month 
        ON athlete_badges(athlete_id, month_reference DESC);
    """)
    
    op.execute("""
        COMMENT ON INDEX idx_badges_athlete_month IS 
        'Optimizes badge queries by athlete and month. Used in athlete profile badges section.';
    """)
    
    # 5. Team Wellness Rankings - Monthly Rankings (analytics)
    # Query pattern: SELECT * FROM team_wellness_rankings WHERE team_id = ? ORDER BY month_reference DESC
    # Estimated improvement: 40ms → 5ms for 12+ months
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_rankings_team_month 
        ON team_wellness_rankings(team_id, month_reference DESC);
    """)
    
    op.execute("""
        COMMENT ON INDEX idx_rankings_team_month IS 
        'Optimizes team ranking queries. Used in analytics dashboard and team comparison.';
    """)
    
    # 6. Training Sessions - Agenda View (main training page)
    # Query pattern: SELECT id, status FROM training_sessions 
    #               WHERE team_id = ? ORDER BY session_at DESC
    # Estimated improvement: 150ms → 20ms for 200+ sessions
    # Note: INCLUDE clause for covering index (PostgreSQL 11+)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_team_date 
        ON training_sessions(team_id, session_at DESC)
        INCLUDE (status);
    """)
    
    op.execute("""
        COMMENT ON INDEX idx_sessions_team_date IS 
        'Covering index for session listing. Includes frequently accessed columns (status).
        Used in agenda view and session calendar.';
    """)
    
    # 7. Training Analytics Cache - Cache Lookup (analytics queries)
    # Query pattern: SELECT * FROM training_analytics_cache 
    #               WHERE team_id = ? AND granularity = ? AND cache_dirty = false
    # Estimated improvement: 60ms → 10ms
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_analytics_lookup 
        ON training_analytics_cache(team_id, granularity, cache_dirty)
        WHERE cache_dirty = false;
    """)
    
    op.execute("""
        COMMENT ON INDEX idx_analytics_lookup IS 
        'Optimizes analytics cache queries. Partial index: only valid (non-dirty) cache entries.
        Used by TrainingAnalyticsService for summary and load queries.';
    """)
    
    # 8. Notifications - Unread Count (navbar badge)
    # Query pattern: SELECT COUNT(*) FROM notifications WHERE user_id = ? AND read_at IS NULL
    # Estimated improvement: 70ms → 5ms for 500+ notifications
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_notifications_unread 
        ON notifications(user_id, created_at DESC)
        WHERE read_at IS NULL;
    """)
    
    op.execute("""
        COMMENT ON INDEX idx_notifications_unread IS 
        'Optimizes unread notification count and listing. Partial index: only unread notifications.
        Used in navbar badge and notifications dropdown.';
    """)
    
    # Run ANALYZE to update statistics
    op.execute("ANALYZE wellness_post;")
    op.execute("ANALYZE wellness_pre;")
    op.execute("ANALYZE wellness_reminders;")
    op.execute("ANALYZE athlete_badges;")
    op.execute("ANALYZE team_wellness_rankings;")
    op.execute("ANALYZE training_sessions;")
    op.execute("ANALYZE training_analytics_cache;")
    op.execute("ANALYZE notifications;")


def downgrade():
    """Drop all performance indexes"""
    op.execute("DROP INDEX IF EXISTS idx_wellness_athlete_date;")
    op.execute("DROP INDEX IF EXISTS idx_wellness_session_athlete;")
    op.execute("DROP INDEX IF EXISTS idx_wellness_reminders_pending;")
    op.execute("DROP INDEX IF EXISTS idx_badges_athlete_month;")
    op.execute("DROP INDEX IF EXISTS idx_rankings_team_month;")
    op.execute("DROP INDEX IF EXISTS idx_sessions_team_date;")
    op.execute("DROP INDEX IF EXISTS idx_analytics_lookup;")
    op.execute("DROP INDEX IF EXISTS idx_notifications_unread;")
