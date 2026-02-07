"""create session exercises table

Revision ID: 0043
Revises: 0042
Create Date: 2026-01-17 06:00:00

⚠️ PERMITE DUPLICATAS - Mesmo exercício pode aparecer múltiplas vezes (circuitos/repetições)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '0043'
down_revision = '0042'
down_revision = '0042'
branch_labels = None
depends_on = None


def upgrade():
    """
    Cria tabela training_session_exercises para vincular exercícios às sessões de treino.
    
    Features:
    - Permite DUPLICATAS (mesmo exercise_id múltiplas vezes)
    - Ordenação via order_index
    - Soft delete (deleted_at)
    - Duração e notas por exercício
    """
    
    # Criar tabela training_session_exercises
    op.create_table(
        'training_session_exercises',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', UUID(as_uuid=True), sa.ForeignKey('training_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('exercise_id', UUID(as_uuid=True), sa.ForeignKey('exercises.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('order_index', sa.Integer, nullable=False, server_default='0'),
        sa.Column('duration_minutes', sa.SmallInteger, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        
        # Constraints
        sa.CheckConstraint('order_index >= 0', name='ck_session_exercises_order_positive'),
        sa.CheckConstraint('duration_minutes IS NULL OR duration_minutes >= 0', name='ck_session_exercises_duration_positive'),
        
        # Comments
        comment='Vínculo entre sessões de treino e exercícios. ⚠️ Permite DUPLICATAS do mesmo exercício (circuitos/repetições).'
    )
    
    # Índices otimizados
    # Índice principal para ordenação e filtragem de soft delete
    op.create_index(
        'idx_session_exercises_session_order',
        'training_session_exercises',
        ['session_id', 'order_index', 'deleted_at'],
        postgresql_where=sa.text('deleted_at IS NULL'),
        unique=False
    )
    
    # Índice para reverse lookup (exercício → sessões)
    op.create_index(
        'idx_session_exercises_exercise',
        'training_session_exercises',
        ['exercise_id'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )
    
    # Índice UNIQUE para evitar conflitos de order_index na mesma sessão
    op.create_index(
        'idx_session_exercises_session_order_unique',
        'training_session_exercises',
        ['session_id', 'order_index'],
        postgresql_where=sa.text('deleted_at IS NULL'),
        unique=True
    )
    
    # Trigger para atualizar updated_at automaticamente
    op.execute("""
        CREATE OR REPLACE FUNCTION tr_update_session_exercises_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE TRIGGER tr_session_exercises_updated_at
        BEFORE UPDATE ON training_session_exercises
        FOR EACH ROW
        EXECUTE FUNCTION tr_update_session_exercises_updated_at();
    """)


def downgrade():
    """Remove tabela training_session_exercises"""
    
    # Drop trigger primeiro
    op.execute('DROP TRIGGER IF EXISTS tr_session_exercises_updated_at ON training_session_exercises;')
    op.execute('DROP FUNCTION IF EXISTS tr_update_session_exercises_updated_at();')
    
    # Drop índices
    op.drop_index('idx_session_exercises_session_order_unique', table_name='training_session_exercises')
    op.drop_index('idx_session_exercises_exercise', table_name='training_session_exercises')
    op.drop_index('idx_session_exercises_session_order', table_name='training_session_exercises')
    
    # Drop tabela (CASCADE remove FKs automaticamente)
    op.drop_table('training_session_exercises')
