"""Create notifications table

Revision ID: 0033_create_notifications
Revises: 0032_add_resend_count
Create Date: 2026-01-14

Step 8: Criar tabela notifications para sistema de notificações em tempo real
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = '0033'
down_revision: Union[str, None] = '0032'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria tabela notifications e índices para queries eficientes.
    """
    op.create_table(
        'notifications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_data', JSONB, nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    
    # Índice composto para buscar notificações não lidas de um usuário
    op.create_index(
        'idx_notifications_user_read',
        'notifications',
        ['user_id', 'read_at'],
    )
    
    # Índice para limpeza de notificações antigas (read_at não nulo + created_at)
    op.create_index(
        'idx_notifications_cleanup',
        'notifications',
        ['read_at', 'created_at'],
    )
    
    # Índice para ordenação por data de criação (mais recentes primeiro)
    op.create_index(
        'idx_notifications_created',
        'notifications',
        [sa.text('created_at DESC')],
    )


def downgrade() -> None:
    """Remove tabela notifications e índices."""
    op.drop_index('idx_notifications_created', table_name='notifications')
    op.drop_index('idx_notifications_cleanup', table_name='notifications')
    op.drop_index('idx_notifications_user_read', table_name='notifications')
    op.drop_table('notifications')
