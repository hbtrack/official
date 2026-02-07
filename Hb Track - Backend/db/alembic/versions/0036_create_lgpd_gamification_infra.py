"""Create LGPD, notifications, gamification, and analytics infrastructure

Revision ID: 0036_lgpd_gamif_infra
Revises: 0035_training_triggers
Create Date: 2026-01-16

Step 3: Criar infraestrutura completa para:
- LGPD: data_access_logs, export_jobs, export_rate_limits, data_retention_logs
- Wellness: wellness_reminders
- Gamificação: athlete_badges, team_wellness_rankings
- Alertas: training_alerts, training_suggestions
- Exercícios: exercises, exercise_tags, exercise_favorites
- Analytics: training_analytics_cache
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET


# revision identifiers, used by Alembic.
revision: str = '0036'
down_revision: Union[str, None] = '0035'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria todas as tabelas de infraestrutura necessárias para o módulo Training.
    Total: 13 tabelas novas.
    """
    
    # =========================================================================
    # 1. WELLNESS_REMINDERS - Tracking de lembretes wellness
    # =========================================================================
    op.create_table(
        'wellness_reminders',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('training_session_id', UUID(as_uuid=True), sa.ForeignKey('training_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('athlete_id', UUID(as_uuid=True), sa.ForeignKey('athletes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reminder_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('training_session_id', 'athlete_id', name='uq_wellness_reminders_session_athlete'),
    )
    
    op.create_index('idx_wellness_reminders_pending', 'wellness_reminders', 
                    ['training_session_id', 'athlete_id'],
                    postgresql_where=sa.text('responded_at IS NULL'))
    
    op.execute("""
        COMMENT ON TABLE wellness_reminders IS 
        'Step 3: Tracking de lembretes wellness enviados aos atletas';
    """)
    
    # =========================================================================
    # 2. ATHLETE_BADGES - Sistema de gamificação
    # =========================================================================
    op.create_table(
        'athlete_badges',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('athlete_id', UUID(as_uuid=True), sa.ForeignKey('athletes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('badge_type', sa.String(50), nullable=False),
        sa.Column('month_reference', sa.Date, nullable=True),
        sa.Column('earned_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint(
            "badge_type IN ('wellness_champion_monthly', 'wellness_streak_3months')",
            name='ck_athlete_badges_type'
        ),
    )
    
    op.create_index('idx_badges_athlete_month', 'athlete_badges', ['athlete_id', 'month_reference'])
    
    op.execute("""
        COMMENT ON TABLE athlete_badges IS 
        'Step 3: Badges de gamificação para atletas (wellness_champion_monthly 90%+, wellness_streak_3months)';
    """)
    
    # =========================================================================
    # 3. TEAM_WELLNESS_RANKINGS - Rankings mensais de equipes
    # =========================================================================
    op.create_table(
        'team_wellness_rankings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('team_id', UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('month_reference', sa.Date, nullable=False),
        sa.Column('response_rate_pre', sa.Numeric(5, 2), nullable=True),
        sa.Column('response_rate_post', sa.Numeric(5, 2), nullable=True),
        sa.Column('avg_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('rank', sa.Integer, nullable=True),
        sa.Column('athletes_90plus', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.UniqueConstraint('team_id', 'month_reference', name='uq_team_wellness_rankings_team_month'),
    )
    
    op.create_index('idx_rankings_team_month', 'team_wellness_rankings', ['team_id', 'month_reference'])
    op.create_index('idx_rankings_month_rank', 'team_wellness_rankings', ['month_reference', 'rank'])
    
    op.execute("""
        COMMENT ON TABLE team_wellness_rankings IS 
        'Step 3: Rankings mensais de equipes por taxa de resposta wellness';
    """)
    
    # =========================================================================
    # 4. TRAINING_ALERTS - Sistema de alertas
    # =========================================================================
    op.create_table(
        'training_alerts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('team_id', UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('metadata', JSONB, nullable=True),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('dismissed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dismissed_by_user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.CheckConstraint(
            "alert_type IN ('weekly_overload', 'low_wellness_response')",
            name='ck_training_alerts_type'
        ),
        sa.CheckConstraint(
            "severity IN ('warning', 'critical')",
            name='ck_training_alerts_severity'
        ),
    )
    
    op.create_index('idx_alerts_active', 'training_alerts', ['team_id', 'triggered_at'],
                    postgresql_where=sa.text('dismissed_at IS NULL'))
    
    op.execute("""
        COMMENT ON TABLE training_alerts IS 
        'Step 3: Alertas automáticos de sobrecarga semanal e baixa taxa de resposta wellness';
    """)
    
    # =========================================================================
    # 5. TRAINING_SUGGESTIONS - Sugestões automáticas
    # =========================================================================
    op.create_table(
        'training_suggestions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('team_id', UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('origin_session_id', UUID(as_uuid=True), sa.ForeignKey('training_sessions.id', ondelete='CASCADE'), nullable=True),
        sa.Column('target_session_ids', sa.ARRAY(UUID(as_uuid=True)), nullable=True),
        sa.Column('recommended_adjustment_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dismissed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dismissal_reason', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint(
            "type IN ('compensation', 'reduce_next_week')",
            name='ck_training_suggestions_type'
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'applied', 'dismissed')",
            name='ck_training_suggestions_status'
        ),
    )
    
    op.execute("""
        COMMENT ON TABLE training_suggestions IS 
        'Step 3: Sugestões automáticas de compensação de carga e redução de intensidade';
    """)
    
    # =========================================================================
    # 6. EXERCISES - Banco de exercícios
    # =========================================================================
    op.create_table(
        'exercises',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('tag_ids', sa.ARRAY(UUID(as_uuid=True)), nullable=False, server_default='{}'),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('media_url', sa.String(500), nullable=True),
        sa.Column('created_by_user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # GIN index para busca eficiente por tags
    op.execute("CREATE INDEX idx_exercises_tags ON exercises USING GIN (tag_ids);")
    
    op.execute("""
        COMMENT ON TABLE exercises IS 
        'Step 3: Banco de exercícios com tags hierárquicas e busca GIN';
    """)
    
    # =========================================================================
    # 7. EXERCISE_TAGS - Tags hierárquicas de exercícios
    # =========================================================================
    op.create_table(
        'exercise_tags',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('parent_tag_id', UUID(as_uuid=True), sa.ForeignKey('exercise_tags.id', ondelete='CASCADE'), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('display_order', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('suggested_by_user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_by_admin_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    op.create_index('idx_tags_parent', 'exercise_tags', ['parent_tag_id'],
                    postgresql_where=sa.text('parent_tag_id IS NOT NULL'))
    
    op.execute("""
        COMMENT ON TABLE exercise_tags IS 
        'Step 3: Tags hierárquicas de exercícios (Tático → Ataque Posicional, etc)';
    """)
    
    # =========================================================================
    # 8. EXERCISE_FAVORITES - Favoritos de exercícios por usuário
    # =========================================================================
    op.create_table(
        'exercise_favorites',
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('exercise_id', UUID(as_uuid=True), sa.ForeignKey('exercises.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('user_id', 'exercise_id'),
    )
    
    op.execute("""
        COMMENT ON TABLE exercise_favorites IS 
        'Step 3: Exercícios favoritados por usuário';
    """)
    
    # =========================================================================
    # 9. TRAINING_ANALYTICS_CACHE - Cache híbrido de analytics
    # =========================================================================
    op.create_table(
        'training_analytics_cache',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('team_id', UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('microcycle_id', UUID(as_uuid=True), sa.ForeignKey('training_microcycles.id', ondelete='CASCADE'), nullable=True),
        sa.Column('month', sa.Date, nullable=True),
        sa.Column('granularity', sa.String(20), nullable=False),
        
        # Métricas agregadas
        sa.Column('total_sessions', sa.Integer, nullable=True),
        sa.Column('avg_focus_attack_positional_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('avg_focus_defense_positional_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('avg_focus_transition_offense_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('avg_focus_transition_defense_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('avg_focus_attack_technical_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('avg_focus_defense_technical_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('avg_focus_physical_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('avg_rpe', sa.Numeric(5, 2), nullable=True),
        sa.Column('avg_internal_load', sa.Numeric(10, 2), nullable=True),
        sa.Column('total_internal_load', sa.Numeric(12, 2), nullable=True),
        sa.Column('attendance_rate', sa.Numeric(5, 2), nullable=True),
        
        # Métricas wellness
        sa.Column('wellness_response_rate_pre', sa.Numeric(5, 2), nullable=True),
        sa.Column('wellness_response_rate_post', sa.Numeric(5, 2), nullable=True),
        sa.Column('athletes_with_badges_count', sa.Integer, nullable=True),
        
        # Métricas threshold
        sa.Column('deviation_count', sa.Integer, nullable=True),
        sa.Column('threshold_mean', sa.Numeric(10, 2), nullable=True),
        sa.Column('threshold_stddev', sa.Numeric(10, 2), nullable=True),
        
        # Controle de cache
        sa.Column('cache_dirty', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.CheckConstraint(
            "granularity IN ('weekly', 'monthly')",
            name='ck_training_analytics_cache_granularity'
        ),
        sa.UniqueConstraint('team_id', 'microcycle_id', 'month', 'granularity', 
                            name='uq_training_analytics_cache_lookup'),
    )
    
    op.create_index('idx_analytics_lookup', 'training_analytics_cache', 
                    ['team_id', 'granularity', 'cache_dirty'],
                    postgresql_where=sa.text('cache_dirty = false'))
    
    op.execute("""
        COMMENT ON TABLE training_analytics_cache IS 
        'Step 3: Cache híbrido de analytics - weekly (granular) para mês corrente, monthly (agregado) para histórico';
    """)
    
    # =========================================================================
    # 10. DATA_ACCESS_LOGS - Auditoria LGPD
    # =========================================================================
    op.create_table(
        'data_access_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', UUID(as_uuid=True), nullable=False),
        sa.Column('athlete_id', UUID(as_uuid=True), sa.ForeignKey('athletes.id', ondelete='SET NULL'), nullable=True),
        sa.Column('accessed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('ip_address', INET, nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
    )
    
    op.create_index('idx_access_logs_user', 'data_access_logs', ['user_id', 'accessed_at'])
    op.create_index('idx_access_logs_athlete', 'data_access_logs', ['athlete_id', 'accessed_at'])
    op.create_index('idx_access_logs_accessed_at', 'data_access_logs', ['accessed_at'])
    
    op.execute("""
        COMMENT ON TABLE data_access_logs IS 
        'Step 3: Log de auditoria LGPD - registra acesso de staff a dados de atletas (não self-access)';
    """)
    
    # =========================================================================
    # 11. EXPORT_JOBS - Jobs de exportação PDF
    # =========================================================================
    op.create_table(
        'export_jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('export_type', sa.String(50), nullable=False),
        sa.Column('params', JSONB, nullable=False),
        sa.Column('params_hash', sa.String(64), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('file_url', sa.String(500), nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name='ck_export_jobs_status'
        ),
    )
    
    op.create_index('idx_export_cache', 'export_jobs', ['params_hash', 'status'],
                    postgresql_where=sa.text("status = 'completed'"))
    
    op.execute("""
        COMMENT ON TABLE export_jobs IS 
        'Step 3: Jobs assíncronos de exportação PDF com cache por params_hash';
    """)
    
    # =========================================================================
    # 12. EXPORT_RATE_LIMITS - Rate limiting de exports
    # =========================================================================
    op.create_table(
        'export_rate_limits',
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('count', sa.Integer, nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('user_id', 'date'),
    )
    
    op.execute("""
        COMMENT ON TABLE export_rate_limits IS 
        'Step 3: Rate limiting de exportações - máximo 5 exports por dia por usuário';
    """)
    
    # =========================================================================
    # 13. DATA_RETENTION_LOGS - Log de anonimização
    # =========================================================================
    op.create_table(
        'data_retention_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('table_name', sa.String(100), nullable=False),
        sa.Column('records_anonymized', sa.Integer, nullable=False),
        sa.Column('anonymized_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    op.execute("""
        COMMENT ON TABLE data_retention_logs IS 
        'Step 3: Log de anonimização automática após 3 anos (política LGPD)';
    """)
    
    # =========================================================================
    # ADICIONAR COLUNA alert_threshold_multiplier em TEAMS
    # =========================================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'teams' 
                AND column_name = 'alert_threshold_multiplier'
            ) THEN
                ALTER TABLE teams 
                ADD COLUMN alert_threshold_multiplier NUMERIC(3, 1) DEFAULT 2.0 
                CHECK (alert_threshold_multiplier BETWEEN 1.0 AND 3.0);
                
                COMMENT ON COLUMN teams.alert_threshold_multiplier IS 
                'Step 3: Multiplicador para threshold de alertas (1.5 juvenis, 2.0 padrão, 2.5 adultos)';
            END IF;
        END $$;
    """)
    
    # =========================================================================
    # ADICIONAR COLUNAS locked_at em WELLNESS_PRE e WELLNESS_POST
    # =========================================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'wellness_pre' 
                AND column_name = 'locked_at'
            ) THEN
                ALTER TABLE wellness_pre 
                ADD COLUMN locked_at TIMESTAMP WITH TIME ZONE;
                
                COMMENT ON COLUMN wellness_pre.locked_at IS 
                'Step 3: Timestamp de lock - pré editável até 2h antes da sessão';
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'wellness_post' 
                AND column_name = 'locked_at'
            ) THEN
                ALTER TABLE wellness_post 
                ADD COLUMN locked_at TIMESTAMP WITH TIME ZONE;
                
                COMMENT ON COLUMN wellness_post.locked_at IS 
                'Step 3: Timestamp de lock - post editável até 24h após submission';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """
    Remove todas as tabelas na ordem inversa.
    """
    
    # Remover colunas adicionadas
    op.execute("ALTER TABLE wellness_post DROP COLUMN IF EXISTS locked_at;")
    op.execute("ALTER TABLE wellness_pre DROP COLUMN IF EXISTS locked_at;")
    op.execute("ALTER TABLE teams DROP COLUMN IF EXISTS alert_threshold_multiplier;")
    
    # Remover tabelas
    op.drop_table('data_retention_logs')
    op.drop_table('export_rate_limits')
    op.drop_table('export_jobs')
    op.drop_table('data_access_logs')
    op.drop_table('training_analytics_cache')
    op.drop_table('exercise_favorites')
    op.drop_table('exercise_tags')
    op.drop_table('exercises')
    op.drop_table('training_suggestions')
    op.drop_table('training_alerts')
    op.drop_table('team_wellness_rankings')
    op.drop_table('athlete_badges')
    op.drop_table('wellness_reminders')
