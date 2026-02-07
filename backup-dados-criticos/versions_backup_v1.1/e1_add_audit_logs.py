"""Add audit_logs table for immutable audit trail

Revision ID: e1_audit_logs
Revises: d5_athlete_triggers
Create Date: 2025-12-27 15:40:00

Implementa RDB5, R31, R32, R35:
- Tabela append-only audit_logs para rastreamento imutável
- Campos: user_id, membership_id, table_name, record_id, operation, old_values, new_values
- Trigger para prevenir UPDATE/DELETE (somente INSERT permitido)
- Índices para consulta eficiente por tabela, usuário e timestamp
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP

# revision identifiers, used by Alembic.
revision: str = 'e1_audit_logs'
down_revision: Union[str, None] = 'd5_athlete_triggers'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTA: tabela audit_logs já existe (schema: entity, entity_id, action, justification, context, actor_user_id)
    # Vamos apenas adicionar triggers de proteção (RDB5 - append-only)

    #  Índices para a tabela existente (IF NOT EXISTS)
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_created_at ON audit_logs(created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_entity ON audit_logs(entity)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_entity_id ON audit_logs(entity_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_actor_user_id ON audit_logs(actor_user_id)")

    # 3. Trigger para tornar audit_logs APPEND-ONLY (bloquear UPDATE/DELETE)
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_audit_logs_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_logs é append-only: UPDATE e DELETE não permitidos (RDB5)';
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_prevent_audit_logs_update
        BEFORE UPDATE ON audit_logs
        FOR EACH ROW
        EXECUTE FUNCTION prevent_audit_logs_modification();
    """)

    op.execute("""
        CREATE TRIGGER trg_prevent_audit_logs_delete
        BEFORE DELETE ON audit_logs
        FOR EACH ROW
        EXECUTE FUNCTION prevent_audit_logs_modification();
    """)

    # 4. Função helper para registrar auditoria usando o schema existente (entity, entity_id, action, justification, context)
    op.execute("""
        CREATE OR REPLACE FUNCTION log_audit(
            p_entity VARCHAR,
            p_entity_id UUID,
            p_action VARCHAR,
            p_old_values JSONB DEFAULT NULL,
            p_new_values JSONB DEFAULT NULL,
            p_justification TEXT DEFAULT NULL
        ) RETURNS VOID AS $$
        DECLARE
            v_actor_user_id UUID;
            v_context JSONB;
        BEGIN
            -- Obter contexto do usuário (se disponível)
            BEGIN
                v_actor_user_id := current_setting('app.current_user_id', true)::UUID;
            EXCEPTION WHEN OTHERS THEN
                v_actor_user_id := NULL;
            END;

            -- Montar contexto JSON
            v_context := jsonb_build_object(
                'old_values', p_old_values,
                'new_values', p_new_values
            );

            -- Inserir no audit_logs
            INSERT INTO audit_logs (
                entity,
                entity_id,
                action,
                justification,
                context,
                actor_user_id
            ) VALUES (
                p_entity,
                p_entity_id,
                p_action,
                p_justification,
                v_context,
                v_actor_user_id
            );
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)


def downgrade() -> None:
    # Remover triggers e função helper
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_audit_logs_delete ON audit_logs")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_audit_logs_update ON audit_logs")
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_logs_modification()")
    op.execute("DROP FUNCTION IF EXISTS log_audit(VARCHAR, UUID, VARCHAR, JSONB, JSONB, TEXT)")

    # Remover índices (IF EXISTS)
    op.execute("DROP INDEX IF EXISTS ix_audit_logs_actor_user_id")
    op.execute("DROP INDEX IF EXISTS ix_audit_logs_entity_id")
    op.execute("DROP INDEX IF EXISTS ix_audit_logs_entity")
    op.execute("DROP INDEX IF EXISTS ix_audit_logs_created_at")

    # Não remover a tabela (já existia antes desta migration)
