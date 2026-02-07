BEGIN;

DO $$
BEGIN
    CREATE TYPE training_execution_outcome_enum AS ENUM (
        'on_time',
        'delayed',
        'canceled',
        'shortened',
        'extended'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE training_sessions
    ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ NULL,
    ADD COLUMN IF NOT EXISTS ended_at TIMESTAMPTZ NULL,
    ADD COLUMN IF NOT EXISTS duration_actual_minutes INTEGER NULL,
    ADD COLUMN IF NOT EXISTS execution_outcome training_execution_outcome_enum NOT NULL DEFAULT 'on_time',
    ADD COLUMN IF NOT EXISTS delay_minutes INTEGER NULL,
    ADD COLUMN IF NOT EXISTS cancellation_reason TEXT NULL,
    ADD COLUMN IF NOT EXISTS post_review_completed_at TIMESTAMPTZ NULL,
    ADD COLUMN IF NOT EXISTS post_review_completed_by_user_id UUID NULL REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS post_review_deadline_at TIMESTAMPTZ NULL;

ALTER TABLE training_sessions
    DROP CONSTRAINT IF EXISTS check_training_session_status;

ALTER TABLE training_sessions
    ADD CONSTRAINT check_training_session_status
    CHECK (status IN ('draft', 'scheduled', 'in_progress', 'pending_review', 'readonly'));

ALTER TABLE training_sessions
    ADD CONSTRAINT check_training_sessions_execution_outcome
    CHECK (
        (execution_outcome = 'on_time'
            AND delay_minutes IS NULL
            AND cancellation_reason IS NULL
            AND duration_actual_minutes IS NULL)
        OR (execution_outcome = 'delayed'
            AND delay_minutes IS NOT NULL
            AND delay_minutes > 0
            AND cancellation_reason IS NULL)
        OR (execution_outcome = 'canceled'
            AND cancellation_reason IS NOT NULL
            AND delay_minutes IS NULL
            AND duration_actual_minutes IS NULL)
        OR (execution_outcome IN ('shortened', 'extended')
            AND duration_actual_minutes IS NOT NULL
            AND duration_actual_minutes > 0
            AND delay_minutes IS NULL
            AND cancellation_reason IS NULL)
    );

UPDATE training_sessions
SET status = 'readonly'
WHERE status = 'closed';

UPDATE training_sessions
SET post_review_completed_at = COALESCE(post_review_completed_at, closed_at),
    post_review_completed_by_user_id = COALESCE(post_review_completed_by_user_id, closed_by_user_id)
WHERE status = 'readonly';

UPDATE training_sessions
SET started_at = COALESCE(started_at, session_at),
    ended_at = COALESCE(
        ended_at,
        session_at + (COALESCE(duration_planned_minutes, 120) || ' minutes')::interval
    )
WHERE status = 'readonly'
  AND started_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_training_sessions_scheduled_at
    ON training_sessions (session_at)
    WHERE status = 'scheduled' AND deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_training_sessions_in_progress_at
    ON training_sessions (session_at)
    WHERE status = 'in_progress' AND deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_training_sessions_pending_review_deadline
    ON training_sessions (post_review_deadline_at)
    WHERE status = 'pending_review' AND deleted_at IS NULL;

COMMIT;
