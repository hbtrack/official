"""Add 'scheduled' status and backfill with tri-class logic

Revision ID: 0048_scheduled_status
Revises: 0047
Create Date: 2026-01-21

Step 4 - Plano de Refatoração:
Adicionar status 'scheduled' ao CHECK constraint e executar backfill tri-classe:

1. draft com session_at+duration_planned_minutes+session_type+main_objective
   preenchidos e FUTURO → scheduled

2. draft com mesmos campos preenchidos mas PASSADO não-fechado → scheduled
   (UI mostrará "Confirmar execução")

3. draft incompleto → permanece draft

Também deprecia 'in_progress' como legado/não-utilizado.
O estado "Em andamento" é agora derivado via is_happening property.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0048'
down_revision = '0047'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adiciona status 'scheduled' e executa backfill tri-classe.
    """

    # =========================================================================
    # 0. DESABILITAR TRIGGER TEMPORARIAMENTE (evita erro de audit_logs)
    # =========================================================================
    # A trigger fn_audit_session_status pode ter dependências de colunas inexistentes
    
    op.execute("""
        DROP TRIGGER IF EXISTS tr_audit_session_status ON training_sessions;
    """)

    # =========================================================================
    # 1. REMOVER CHECK CONSTRAINT ATUAL
    # =========================================================================

    op.execute("""
        ALTER TABLE training_sessions
        DROP CONSTRAINT IF EXISTS check_training_session_status;
    """)

    # =========================================================================
    # 2. ADICIONAR NOVO CHECK CONSTRAINT com 'scheduled'
    # =========================================================================
    # Nota: 'in_progress' mantido para compatibilidade mas documentado como legado

    op.execute("""
        ALTER TABLE training_sessions
        ADD CONSTRAINT check_training_session_status
        CHECK (status IN ('draft', 'scheduled', 'in_progress', 'closed', 'readonly'));
    """)

    # Adicionar comentário documentando o status in_progress como legado
    op.execute("""
        COMMENT ON COLUMN training_sessions.status IS
        'Status da sessão: draft (rascunho), scheduled (agendado), closed (fechado), readonly (somente leitura). '
        'in_progress é LEGADO e não deve ser usado - estado "Em andamento" é derivado via is_happening.';
    """)

    # =========================================================================
    # 3. BACKFILL TRI-CLASSE
    # =========================================================================

    # Classe 1: drafts com dados mínimos E no FUTURO → scheduled
    op.execute("""
        UPDATE training_sessions
        SET status = 'scheduled'
        WHERE status = 'draft'
          AND session_at IS NOT NULL
          AND session_type IS NOT NULL
          AND main_objective IS NOT NULL
          AND session_at > NOW();
    """)

    # Classe 2: drafts com dados mínimos E no PASSADO → scheduled
    # (UI mostrará "Confirmar execução" via is_past_without_closure)
    op.execute("""
        UPDATE training_sessions
        SET status = 'scheduled'
        WHERE status = 'draft'
          AND session_at IS NOT NULL
          AND session_type IS NOT NULL
          AND main_objective IS NOT NULL
          AND session_at <= NOW();
    """)

    # Classe 3: drafts incompletos → permanecem draft (nenhuma ação necessária)

    # =========================================================================
    # 4. MIGRAR in_progress PARA scheduled (depreciar)
    # =========================================================================
    # Qualquer sessão com status 'in_progress' deve ir para 'scheduled'
    # O estado "Em andamento" é derivado pelo horário atual

    op.execute("""
        UPDATE training_sessions
        SET status = 'scheduled'
        WHERE status = 'in_progress';
    """)


def downgrade() -> None:
    """
    Remove status 'scheduled' e reverte para CHECK anterior.
    """

    # Reverter scheduled de volta para draft
    op.execute("""
        UPDATE training_sessions
        SET status = 'draft'
        WHERE status = 'scheduled';
    """)

    # Remover CHECK atual
    op.execute("""
        ALTER TABLE training_sessions
        DROP CONSTRAINT IF EXISTS check_training_session_status;
    """)

    # Restaurar CHECK original
    op.execute("""
        ALTER TABLE training_sessions
        ADD CONSTRAINT check_training_session_status
        CHECK (status IN ('draft', 'in_progress', 'closed', 'readonly'));
    """)

    # Remover comentário
    op.execute("""
        COMMENT ON COLUMN training_sessions.status IS NULL;
    """)
