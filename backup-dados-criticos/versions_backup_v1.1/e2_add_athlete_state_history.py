"""Add athlete_state_history table for state tracking

Revision ID: e2_athlete_state_history
Revises: e1_audit_logs
Create Date: 2025-12-27 15:45:00

Implementa RDB7, R13:
- Tabela athlete_state_history para rastrear mudanças de estado (ativa, lesionada, dispensada)
- Campos: athlete_id, state, changed_at, changed_by_membership_id, reason
- Trigger para registrar mudanças automáticas
- Soft delete de team_registrations ao dispensar atleta (R13)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP

# revision identifiers, used by Alembic.
revision: str = 'e2_athlete_state_history'
down_revision: Union[str, None] = 'e1_audit_logs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Criar tabela athlete_state_history
    op.create_table(
        'athlete_state_history',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('athlete_id', UUID(as_uuid=True), sa.ForeignKey('athletes.id'), nullable=False),

        # Estado e timestamps
        sa.Column('state', sa.String(20), nullable=False),  # ativa, lesionada, dispensada
        sa.Column('changed_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('effective_from', TIMESTAMP(timezone=True), nullable=False),  # Início da vigência
        sa.Column('effective_until', TIMESTAMP(timezone=True), nullable=True),  # Fim (NULL = atual)

        # Contexto da mudança
        sa.Column('changed_by_membership_id', UUID(as_uuid=True), sa.ForeignKey('membership.id'), nullable=True),
        sa.Column('reason', sa.Text, nullable=True),  # Motivo da mudança

        # Metadados
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),

        # CHECK constraint para estado válido
        sa.CheckConstraint(
            "state IN ('ativa', 'lesionada', 'dispensada')",
            name='ck_athlete_state_history_state'
        ),
    )

    # 2. Índices
    op.create_index('ix_athlete_state_history_athlete_id', 'athlete_state_history', ['athlete_id'])
    op.create_index('ix_athlete_state_history_changed_at', 'athlete_state_history', ['changed_at'])
    op.create_index('ix_athlete_state_history_state', 'athlete_state_history', ['state'])

    # Índice para buscar estado atual (effective_until IS NULL)
    op.create_index(
        'ix_athlete_state_history_current',
        'athlete_state_history',
        ['athlete_id', 'effective_until'],
        postgresql_where=sa.text('effective_until IS NULL')
    )

    # 3. Migrar dados existentes: criar histórico inicial para todas as atletas
    op.execute("""
        INSERT INTO athlete_state_history (athlete_id, state, changed_at, effective_from, effective_until, reason)
        SELECT
            id,
            state,
            created_at,
            created_at,
            NULL,
            'Estado inicial (migração)'
        FROM athletes
        WHERE deleted_at IS NULL
    """)

    # 4. Trigger para registrar mudanças de estado automáticas
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_athlete_state_change()
        RETURNS TRIGGER AS $$
        DECLARE
            v_membership_id UUID;
            v_reason TEXT;
        BEGIN
            -- Detectar mudança de estado
            IF (TG_OP = 'UPDATE' AND OLD.state IS DISTINCT FROM NEW.state) THEN
                -- Obter contexto
                BEGIN
                    v_membership_id := current_setting('app.current_membership_id', true)::UUID;
                EXCEPTION WHEN OTHERS THEN
                    v_membership_id := NULL;
                END;

                -- Fechar registro anterior
                UPDATE athlete_state_history
                SET effective_until = now()
                WHERE athlete_id = NEW.id
                  AND effective_until IS NULL;

                -- Criar novo registro
                INSERT INTO athlete_state_history (
                    athlete_id, state, changed_at, effective_from, effective_until,
                    changed_by_membership_id, reason
                ) VALUES (
                    NEW.id,
                    NEW.state,
                    now(),
                    now(),
                    NULL,
                    v_membership_id,
                    'Mudança de estado: ' || OLD.state || ' → ' || NEW.state
                );

                -- Se mudou para "dispensada", fazer soft delete das participações ativas (R13)
                IF NEW.state = 'dispensada' THEN
                    UPDATE team_registrations
                    SET deleted_at = now(),
                        deleted_reason = 'Atleta dispensada (R13)'
                    WHERE athlete_id = NEW.id
                      AND deleted_at IS NULL;
                END IF;

                -- Registrar auditoria
                PERFORM log_audit(
                    'athletes',
                    NEW.id,
                    'STATE_CHANGE',
                    jsonb_build_object('state', OLD.state),
                    jsonb_build_object('state', NEW.state),
                    'Mudança de estado: ' || OLD.state || ' → ' || NEW.state
                );
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_after_athlete_state_change
        AFTER UPDATE ON athletes
        FOR EACH ROW
        EXECUTE FUNCTION trg_athlete_state_change();
    """)


def downgrade() -> None:
    # Remover trigger
    op.execute("DROP TRIGGER IF EXISTS trg_after_athlete_state_change ON athletes")
    op.execute("DROP FUNCTION IF EXISTS trg_athlete_state_change()")

    # Remover índices
    op.drop_index('ix_athlete_state_history_current', table_name='athlete_state_history')
    op.drop_index('ix_athlete_state_history_state', table_name='athlete_state_history')
    op.drop_index('ix_athlete_state_history_changed_at', table_name='athlete_state_history')
    op.drop_index('ix_athlete_state_history_athlete_id', table_name='athlete_state_history')

    # Remover tabela
    op.drop_table('athlete_state_history')
