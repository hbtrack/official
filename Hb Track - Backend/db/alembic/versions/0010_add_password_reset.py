"""V1.2 - Add password reset tokens table

Revision ID: 009_v1_2_password_reset
Revises: 008_v1_2_update_categories
Create Date: 2025-12-28

Adds password_resets table for email-based password recovery flow.

REGRAS: R29 (sem delete físico), RDB4 (soft delete)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None


def upgrade():
    # ========================================
    # PASSWORD_RESETS table
    # ========================================
    op.create_table(
        'password_resets',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.Text(), nullable=False, unique=True),
        sa.Column('token_type', sa.Text(), nullable=False, server_default='reset'),
        sa.Column('used', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('used_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deleted_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_password_resets_user_id'),
        sa.PrimaryKeyConstraint('id', name='pk_password_resets'),
        sa.CheckConstraint(
            "token_type IN ('reset', 'welcome')",
            name='ck_password_resets_token_type'
        ),
        sa.CheckConstraint(
            "(deleted_at IS NULL AND deleted_reason IS NULL) OR (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)",
            name='ck_password_resets_deleted_reason'
        ),
        comment='Email-based password reset tokens. R29: soft delete. Token expires in 24h.'
    )

    # Indexes
    op.create_index('ix_password_resets_user_id', 'password_resets', ['user_id'])
    op.create_index('ix_password_resets_token', 'password_resets', ['token'])
    op.create_index('ix_password_resets_expires_at', 'password_resets', ['expires_at'])


def downgrade():
    op.drop_index('ix_password_resets_expires_at', table_name='password_resets')
    op.drop_index('ix_password_resets_token', table_name='password_resets')
    op.drop_index('ix_password_resets_user_id', table_name='password_resets')
    op.drop_table('password_resets')
