"""create export system tables

Revision ID: 0044_create_export_system
Revises: 0043_create_session_exercises
Create Date: 2026-01-17 23:00:00.000000

Step 23: Export PDF Assíncrono com Wellness Metrics
- Tabela export_jobs: tracking de jobs de export assíncronos
- Tabela export_rate_limits: controle de rate limit (5/dia por user)
- Índices para performance de queries
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0044'
down_revision: Union[str, None] = '0043'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========================================
    # 1. Tabela export_jobs
    # ========================================
    # Verificar se já existe antes de criar
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'export_jobs' not in inspector.get_table_names():
        op.create_table(
            'export_jobs',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('export_type', sa.String(50), nullable=False),
            sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
            sa.Column('params', postgresql.JSONB, nullable=False),
            sa.Column('params_hash', sa.String(64), nullable=False),
            sa.Column('file_url', sa.String(500), nullable=True),
            sa.Column('file_size_bytes', sa.BigInteger, nullable=True),
            sa.Column('error_message', sa.Text, nullable=True),
            sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
            sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
            
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            
            sa.CheckConstraint(
                "export_type IN ('analytics_pdf', 'athlete_data_json', 'athlete_data_csv')",
                name='ck_export_jobs_valid_type'
            ),
            sa.CheckConstraint(
                "status IN ('pending', 'processing', 'completed', 'failed')",
                name='ck_export_jobs_valid_status'
            ),
            sa.CheckConstraint(
                "file_size_bytes IS NULL OR file_size_bytes > 0",
                name='ck_export_jobs_positive_file_size'
            ),
        )
        
        # Índices export_jobs
        op.create_index('idx_export_jobs_user', 'export_jobs', ['user_id', 'created_at'], postgresql_ops={'created_at': 'DESC'})
        op.create_index('idx_export_jobs_status', 'export_jobs', ['status', 'created_at'], postgresql_where=sa.text("status IN ('pending', 'processing')"))
        op.create_index('idx_export_jobs_cache_lookup', 'export_jobs', ['export_type', 'params_hash', 'status'], postgresql_where=sa.text("status = 'completed' AND expires_at > NOW()"))
        op.create_index('idx_export_jobs_cleanup', 'export_jobs', ['expires_at'], postgresql_where=sa.text("expires_at IS NOT NULL AND status = 'completed'"))
    
    # ========================================
    # 2. Tabela export_rate_limits
    # ========================================
    if 'export_rate_limits' not in inspector.get_table_names():
        op.create_table(
            'export_rate_limits',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('export_type', sa.String(50), nullable=False),
            sa.Column('date', sa.Date, nullable=False),
            sa.Column('count', sa.SmallInteger, nullable=False, server_default='0'),
            sa.Column('last_export_at', sa.TIMESTAMP(timezone=True), nullable=True),
            
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            
            sa.UniqueConstraint('user_id', 'export_type', 'date', name='uq_export_rate_limits_user_type_date'),
            
            sa.CheckConstraint(
                "count >= 0 AND count <= 10",
                name='ck_export_rate_limits_reasonable_count'
            ),
        )
        
        # Índices export_rate_limits
        op.create_index('idx_export_rate_limits_user_date', 'export_rate_limits', ['user_id', 'date'], postgresql_ops={'date': 'DESC'})
        op.create_index('idx_export_rate_limits_cleanup', 'export_rate_limits', ['date'], postgresql_where=sa.text("date < CURRENT_DATE - INTERVAL '30 days'"))


def downgrade() -> None:
    op.drop_table('export_rate_limits')
    op.drop_table('export_jobs')
