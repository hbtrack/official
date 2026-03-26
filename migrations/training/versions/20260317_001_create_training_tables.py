"""Create training module tables

Revision ID: 20260317_001
Revises: None
Create Date: 2026-03-17 12:00:00
Module: training
Contract ref: contracts/schemas/training/

This migration creates the foundational tables for the training module:
- training_sessions (main entity)
- session_blocks (operational units within sessions)
- execution_records (append-only facts)
- session_objectives (objectives with origin tracking)
- feedback_threads (coach-athlete conversation)
- attention_queue_items (technical flags/alerts)

All tables use UUIDs (uuid_v4 format) and timestamps (UTC).
Rows are soft-deleted (deletedAt + deletedReason).
Status machine uses ENUM (DRAFT, SCHEDULED, PUBLISHED, IN_PROGRESS, COMPLETED, CANCELLED, ARCHIVED).
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # ============================================================================
    # 1. CREATE ENUM TYPES
    # ============================================================================
    
    # Status enum for training session (ADR-017)
    op.execute("""
        CREATE TYPE training_session_status AS ENUM (
            'DRAFT',
            'SCHEDULED',
            'PUBLISHED',
            'IN_PROGRESS',
            'COMPLETED',
            'CANCELLED',
            'ARCHIVED'
        )
    """)
    
    # Session block phase enum
    op.execute("""
        CREATE TYPE session_block_phase AS ENUM (
            'WARMUP',
            'ACTIVATION',
            'TECHNICAL',
            'DECISION_MAKING',
            'TACTICAL',
            'REDUCED_GAME',
            'COOLDOWN'
        )
    """)
    
    # Execution type enum
    op.execute("""
        CREATE TYPE execution_type AS ENUM (
            'SESSION_EXECUTION',
            'BLOCK_EXECUTION',
            'LIVE_ADJUSTMENT',
            'CONSTRAINT_OVERRIDE',
            'ALTERNATE_EXERCISE',
            'LOAD_RECALCULATION'
        )
    """)
    
    # Individualization mode enum
    op.execute("""
        CREATE TYPE individualization_mode AS ENUM (
            'COLLECTIVE_UNIFORM',
            'COLLECTIVE_WITH_VARIANTS',
            'INDIVIDUAL_ONLY'
        )
    """)
    
    # Objective origin enum
    op.execute("""
        CREATE TYPE objective_origin AS ENUM (
            'NEED_DETECTED',
            'COMPETITIVE_FOCUS',
            'DEVELOPMENT_GOAL',
            'MANUAL_COACH_RATIONALE'
        )
    """)
    
    # ============================================================================
    # 2. CREATE MAIN TABLES
    # ============================================================================
    
    # Main training session table (SSOT entity)
    op.create_table(
        'training_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('microcycle_id', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Temporal attributes
        sa.Column('session_at', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('duration_planned_minutes', sa.Integer, nullable=True),
        sa.Column('duration_actual_minutes', sa.Integer, nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        
        # Location and type
        sa.Column('location', sa.String(120), nullable=True),
        sa.Column('session_type', sa.String(32), nullable=False),
        sa.Column('session_block', sa.String(32), nullable=True),
        
        # Objectives and notes
        sa.Column('main_objective', sa.String(255), nullable=True),
        sa.Column('secondary_objective', sa.String(255), nullable=True),
        sa.Column('objective_origin', postgresql.ENUM('NEED_DETECTED', 'COMPETITIVE_FOCUS', 'DEVELOPMENT_GOAL', 'MANUAL_COACH_RATIONALE', name='objective_origin'), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('continuation_notes', sa.String(2000), nullable=True),
        
        # Load and intensity
        sa.Column('planned_load', sa.Integer, nullable=True),
        sa.Column('actual_load_recorded', sa.Integer, nullable=True),
        sa.Column('intensity_target', sa.Integer, nullable=True),
        sa.Column('group_climate', sa.Integer, nullable=True),
        
        # Focus areas (7 dimensions, percentages 0-100)
        sa.Column('focus_attack_positional_pct', sa.Integer, nullable=True),
        sa.Column('focus_defense_positional_pct', sa.Integer, nullable=True),
        sa.Column('focus_transition_offense_pct', sa.Integer, nullable=True),
        sa.Column('focus_transition_defense_pct', sa.Integer, nullable=True),
        sa.Column('focus_attack_technical_pct', sa.Integer, nullable=True),
        sa.Column('focus_defense_technical_pct', sa.Integer, nullable=True),
        sa.Column('focus_physical_pct', sa.Integer, nullable=True),
        
        # Handball-specific phase flags
        sa.Column('phase_focus_defense', sa.Boolean, nullable=True),
        sa.Column('phase_focus_attack', sa.Boolean, nullable=True),
        sa.Column('phase_focus_transition_offense', sa.Boolean, nullable=True),
        sa.Column('phase_focus_transition_defense', sa.Boolean, nullable=True),
        
        # Status machine (FSM - 7 states)
        sa.Column('status', postgresql.ENUM('DRAFT', 'SCHEDULED', 'PUBLISHED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'ARCHIVED', name='training_session_status'), nullable=False, server_default='DRAFT'),
        sa.Column('planning_deviation_flag', sa.Boolean, nullable=True),
        sa.Column('deviation_justification', sa.Text, nullable=True),
        sa.Column('execution_outcome', sa.String(32), nullable=True),
        sa.Column('delay_minutes', sa.Integer, nullable=True),
        sa.Column('cancellation_reason', sa.Text, nullable=True),
        
        # Post-review
        sa.Column('post_review_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('post_review_completed_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('post_review_deadline_at', sa.DateTime(timezone=True), nullable=True),
        
        # Individualization (INV-TRAIN-086)
        sa.Column('individualization_mode', postgresql.ENUM('COLLECTIVE_UNIFORM', 'COLLECTIVE_WITH_VARIANTS', 'INDIVIDUAL_ONLY', name='individualization_mode'), nullable=True),
        
        # Content snapshot (TRAIN-DEC-045, immutable after PUBLISHED)
        sa.Column('planned_content_snapshot', postgresql.JSON, nullable=True),
        
        # Standalone flag
        sa.Column('standalone', sa.Boolean, nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('closed_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text, nullable=True),
    )
    
    # Indices for performance
    op.create_index('idx_training_sessions_organization_status', 'training_sessions', ['organization_id', 'status'])
    op.create_index('idx_training_sessions_team_session_at', 'training_sessions', ['team_id', 'session_at'])
    op.create_index('idx_training_sessions_season', 'training_sessions', ['season_id'])
    op.create_index('idx_training_sessions_created_at', 'training_sessions', ['created_at'])
    op.create_index('idx_training_sessions_deleted_at', 'training_sessions', ['deleted_at'])
    
    # ============================================================================
    # 3. SESSION BLOCKS TABLE
    # ============================================================================
    
    op.create_table(
        'session_blocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('phase', postgresql.ENUM('WARMUP', 'ACTIVATION', 'TECHNICAL', 'DECISION_MAKING', 'TACTICAL', 'REDUCED_GAME', 'COOLDOWN', name='session_block_phase'), nullable=False),
        sa.Column('order_index', sa.Integer, nullable=False),
        sa.Column('duration_minutes', sa.Integer, nullable=False),
        sa.Column('block_objective', sa.String(300), nullable=False),
        sa.Column('intensity', sa.Integer, nullable=False),
        sa.Column('is_optional', sa.Boolean, nullable=False, server_default=sa.false()),
        
        # Exercise reference (TRAIN-DEC-047: never embed, only reference)
        sa.Column('exercise_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('exercise_version_id', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Content
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('pedagogy_notes', sa.Text, nullable=True),
        
        # Audit
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        
        # Unique constraint on (session_id, order_index)
        sa.UniqueConstraint('session_id', 'order_index', name='uq_session_block_order'),
    )
    
    # Foreign key to training_sessions
    op.create_foreign_key(
        'fk_session_blocks_session_id',
        'session_blocks', 'training_sessions',
        ['session_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Indices
    op.create_index('idx_session_blocks_session_id', 'session_blocks', ['session_id'])
    op.create_index('idx_session_blocks_exercise_id', 'session_blocks', ['exercise_id'])
    
    # ============================================================================
    # 4. EXECUTION RECORDS TABLE (APPEND-ONLY)
    # ============================================================================
    
    op.create_table(
        'execution_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('block_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('execution_type', postgresql.ENUM('SESSION_EXECUTION', 'BLOCK_EXECUTION', 'LIVE_ADJUSTMENT', 'CONSTRAINT_OVERRIDE', 'ALTERNATE_EXERCISE', 'LOAD_RECALCULATION', name='execution_type'), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('planned_value', sa.Numeric, nullable=True),
        sa.Column('actual_value', sa.Numeric, nullable=True),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    
    # Foreign keys
    op.create_foreign_key(
        'fk_execution_records_session_id',
        'execution_records', 'training_sessions',
        ['session_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_execution_records_block_id',
        'execution_records', 'session_blocks',
        ['block_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Indices
    op.create_index('idx_execution_records_session_id', 'execution_records', ['session_id'])
    op.create_index('idx_execution_records_execution_type', 'execution_records', ['execution_type'])
    op.create_index('idx_execution_records_recorded_at', 'execution_records', ['recorded_at'])
    
    # ============================================================================
    # 5. SESSION OBJECTIVES TABLE
    # ============================================================================
    
    op.create_table(
        'session_objectives',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('objective_text', sa.String(255), nullable=False),
        sa.Column('objective_origin', postgresql.ENUM('NEED_DETECTED', 'COMPETITIVE_FOCUS', 'DEVELOPMENT_GOAL', 'MANUAL_COACH_RATIONALE', name='objective_origin'), nullable=False),
        sa.Column('priority_order', sa.Integer, nullable=False),
        sa.Column('achieved_flag', sa.Boolean, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Foreign key
    op.create_foreign_key(
        'fk_session_objectives_session_id',
        'session_objectives', 'training_sessions',
        ['session_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Indices
    op.create_index('idx_session_objectives_session_id', 'session_objectives', ['session_id'])
    op.create_index('idx_session_objectives_origin', 'session_objectives', ['objective_origin'])
    
    # ============================================================================
    # 6. FEEDBACK THREADS TABLE
    # ============================================================================
    
    op.create_table(
        'feedback_threads',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('subject', sa.String(255), nullable=False),
        sa.Column('thread_context', postgresql.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Foreign key
    op.create_foreign_key(
        'fk_feedback_threads_session_id',
        'feedback_threads', 'training_sessions',
        ['session_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Indices
    op.create_index('idx_feedback_threads_session_id', 'feedback_threads', ['session_id'])
    op.create_index('idx_feedback_threads_athlete_id', 'feedback_threads', ['athlete_id'])
    op.create_index('idx_feedback_threads_is_active', 'feedback_threads', ['is_active'])
    
    # ============================================================================
    # 7. ATTENTION QUEUE ITEMS TABLE
    # ============================================================================
    
    op.create_table(
        'attention_queue_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('item_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('is_resolved', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Foreign key
    op.create_foreign_key(
        'fk_attention_queue_items_session_id',
        'attention_queue_items', 'training_sessions',
        ['session_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Indices
    op.create_index('idx_attention_queue_items_session_id', 'attention_queue_items', ['session_id'])
    op.create_index('idx_attention_queue_items_is_resolved', 'attention_queue_items', ['is_resolved'])
    op.create_index('idx_attention_queue_items_severity', 'attention_queue_items', ['severity'])


def downgrade() -> None:
    """Reverter migration — remove todas as tabelas e ENUMs criados."""
    
    # Drop tables (foreign key constraints handled by CASCADE)
    op.drop_table('attention_queue_items')
    op.drop_table('feedback_threads')
    op.drop_table('session_objectives')
    op.drop_table('execution_records')
    op.drop_table('session_blocks')
    op.drop_table('training_sessions')
    
    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS objective_origin CASCADE')
    op.execute('DROP TYPE IF EXISTS individualization_mode CASCADE')
    op.execute('DROP TYPE IF EXISTS execution_type CASCADE')
    op.execute('DROP TYPE IF EXISTS session_block_phase CASCADE')
    op.execute('DROP TYPE IF EXISTS training_session_status CASCADE')
