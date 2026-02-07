"""add_email_queue_table

Revision ID: f62ede3bab26
Revises: 41e6ff9bc859
Create Date: 2026-01-01 17:03:55.282756

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0020'
down_revision: Union[str, Sequence[str], None] = '0019'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria tabela email_queue para fila de emails com retry automático."""
    
    # Criar função update_updated_at_column se não existir
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Criar tabela email_queue
    op.create_table(
        'email_queue',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('template_type', sa.String(50), nullable=False, comment='invite, welcome, reset_password'),
        sa.Column('to_email', sa.String(255), nullable=False),
        sa.Column('template_data', postgresql.JSONB, nullable=False, comment='Dados dinâmicos do template'),
        sa.Column('status', sa.String(20), nullable=False, default='pending', comment='pending, sent, failed, cancelled'),
        sa.Column('attempts', sa.Integer, nullable=False, default=0, comment='Número de tentativas'),
        sa.Column('max_attempts', sa.Integer, nullable=False, default=3, comment='Máximo de tentativas'),
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True, comment='Próxima tentativa'),
        sa.Column('last_error', sa.Text, nullable=True, comment='Última mensagem de erro'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True, comment='Quando foi enviado'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_email_queue_created_by_user'),
        comment='Fila de emails com retry automático'
    )
    
    # Índices para performance
    op.create_index('ix_email_queue_status', 'email_queue', ['status'])
    op.create_index('ix_email_queue_next_retry', 'email_queue', ['next_retry_at'], postgresql_where=sa.text("status = 'pending'"))
    op.create_index('ix_email_queue_created_at', 'email_queue', ['created_at'])
    op.create_index('ix_email_queue_to_email', 'email_queue', ['to_email'])
    
    # Trigger updated_at
    op.execute("""
        CREATE TRIGGER trg_email_queue_updated_at
        BEFORE UPDATE ON email_queue
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Remove tabela email_queue."""
    op.drop_table('email_queue')
