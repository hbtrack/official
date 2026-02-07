"""Add trigger for automatic phase_focus_* derivation

Revision ID: 0047_phase_focus_trigger
Revises: 0046
Create Date: 2026-01-21

Step 3 - Plano de Refatoração:
Criar trigger SQL BEFORE INSERT OR UPDATE para recalcular automaticamente:
- phase_focus_attack = (focus_attack_positional_pct + focus_attack_technical_pct) >= 5
- phase_focus_defense = (focus_defense_positional_pct + focus_defense_technical_pct) >= 5
- phase_focus_transition_offense = focus_transition_offense_pct >= 5
- phase_focus_transition_defense = focus_transition_defense_pct >= 5
- phase_focus_physical = focus_physical_pct >= 5 (se existir)

Também adiciona:
1. NOT NULL constraints nos campos phase_focus_*
2. CHECK constraints para consistência
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0047'
down_revision = '0046'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Threshold para considerar fase como ativa (5%)
PHASE_THRESHOLD = 5


def upgrade() -> None:
    """
    Cria trigger e constraints para derivação automática de phase_focus_*.

    Ordem de execução (3 blocos):
    1. Backfill de dados existentes
    2. ALTER COLUMN para NOT NULL com defaults
    3. Criar trigger + CHECKs de consistência
    """

    # =========================================================================
    # BLOCO 1: BACKFILL de dados existentes
    # =========================================================================
    # Atualiza registros existentes com valores derivados

    op.execute(f"""
        UPDATE training_sessions
        SET
            phase_focus_attack = (
                COALESCE(focus_attack_positional_pct, 0) +
                COALESCE(focus_attack_technical_pct, 0)
            ) >= {PHASE_THRESHOLD},
            phase_focus_defense = (
                COALESCE(focus_defense_positional_pct, 0) +
                COALESCE(focus_defense_technical_pct, 0)
            ) >= {PHASE_THRESHOLD},
            phase_focus_transition_offense = (
                COALESCE(focus_transition_offense_pct, 0)
            ) >= {PHASE_THRESHOLD},
            phase_focus_transition_defense = (
                COALESCE(focus_transition_defense_pct, 0)
            ) >= {PHASE_THRESHOLD}
        WHERE phase_focus_attack IS NULL
           OR phase_focus_defense IS NULL
           OR phase_focus_transition_offense IS NULL
           OR phase_focus_transition_defense IS NULL;
    """)

    # =========================================================================
    # BLOCO 2: ALTER COLUMN para NOT NULL com defaults
    # =========================================================================

    op.execute("""
        ALTER TABLE training_sessions
        ALTER COLUMN phase_focus_attack SET DEFAULT false,
        ALTER COLUMN phase_focus_attack SET NOT NULL;
    """)

    op.execute("""
        ALTER TABLE training_sessions
        ALTER COLUMN phase_focus_defense SET DEFAULT false,
        ALTER COLUMN phase_focus_defense SET NOT NULL;
    """)

    op.execute("""
        ALTER TABLE training_sessions
        ALTER COLUMN phase_focus_transition_offense SET DEFAULT false,
        ALTER COLUMN phase_focus_transition_offense SET NOT NULL;
    """)

    op.execute("""
        ALTER TABLE training_sessions
        ALTER COLUMN phase_focus_transition_defense SET DEFAULT false,
        ALTER COLUMN phase_focus_transition_defense SET NOT NULL;
    """)

    # =========================================================================
    # BLOCO 3: TRIGGER + CHECKs de consistência
    # =========================================================================

    # Criar função para recalcular phase_focus_*
    op.execute(f"""
        CREATE OR REPLACE FUNCTION fn_derive_phase_focus()
        RETURNS TRIGGER AS $$
        DECLARE
            v_threshold CONSTANT NUMERIC := {PHASE_THRESHOLD};
        BEGIN
            -- Derivar phase_focus_attack (ataque posicional + técnico)
            NEW.phase_focus_attack := (
                COALESCE(NEW.focus_attack_positional_pct, 0) +
                COALESCE(NEW.focus_attack_technical_pct, 0)
            ) >= v_threshold;

            -- Derivar phase_focus_defense (defesa posicional + técnico)
            NEW.phase_focus_defense := (
                COALESCE(NEW.focus_defense_positional_pct, 0) +
                COALESCE(NEW.focus_defense_technical_pct, 0)
            ) >= v_threshold;

            -- Derivar phase_focus_transition_offense
            NEW.phase_focus_transition_offense := (
                COALESCE(NEW.focus_transition_offense_pct, 0)
            ) >= v_threshold;

            -- Derivar phase_focus_transition_defense
            NEW.phase_focus_transition_defense := (
                COALESCE(NEW.focus_transition_defense_pct, 0)
            ) >= v_threshold;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Adicionar comentário
    op.execute("""
        COMMENT ON FUNCTION fn_derive_phase_focus() IS
        'Step 3: Deriva automaticamente phase_focus_* baseado no threshold de 5%';
    """)

    # Criar trigger BEFORE INSERT OR UPDATE
    op.execute("""
        CREATE TRIGGER tr_derive_phase_focus
        BEFORE INSERT OR UPDATE OF
            focus_attack_positional_pct,
            focus_attack_technical_pct,
            focus_defense_positional_pct,
            focus_defense_technical_pct,
            focus_transition_offense_pct,
            focus_transition_defense_pct,
            focus_physical_pct
        ON training_sessions
        FOR EACH ROW
        EXECUTE FUNCTION fn_derive_phase_focus();
    """)

    # =========================================================================
    # CHECK CONSTRAINTS para consistência
    # =========================================================================
    # Garante que phase_focus_* é consistente com os focos percentuais
    # Nota: Usar >= para threshold pois o trigger já garantiu o cálculo

    op.execute(f"""
        ALTER TABLE training_sessions
        ADD CONSTRAINT ck_phase_focus_attack_consistency
        CHECK (
            phase_focus_attack = (
                (COALESCE(focus_attack_positional_pct, 0) + COALESCE(focus_attack_technical_pct, 0)) >= {PHASE_THRESHOLD}
            )
        );
    """)

    op.execute(f"""
        ALTER TABLE training_sessions
        ADD CONSTRAINT ck_phase_focus_defense_consistency
        CHECK (
            phase_focus_defense = (
                (COALESCE(focus_defense_positional_pct, 0) + COALESCE(focus_defense_technical_pct, 0)) >= {PHASE_THRESHOLD}
            )
        );
    """)

    op.execute(f"""
        ALTER TABLE training_sessions
        ADD CONSTRAINT ck_phase_focus_transition_offense_consistency
        CHECK (
            phase_focus_transition_offense = (
                COALESCE(focus_transition_offense_pct, 0) >= {PHASE_THRESHOLD}
            )
        );
    """)

    op.execute(f"""
        ALTER TABLE training_sessions
        ADD CONSTRAINT ck_phase_focus_transition_defense_consistency
        CHECK (
            phase_focus_transition_defense = (
                COALESCE(focus_transition_defense_pct, 0) >= {PHASE_THRESHOLD}
            )
        );
    """)


def downgrade() -> None:
    """
    Remove trigger, função e constraints na ordem inversa.
    """

    # Remover CHECK constraints
    op.execute("""
        ALTER TABLE training_sessions
        DROP CONSTRAINT IF EXISTS ck_phase_focus_attack_consistency;
    """)

    op.execute("""
        ALTER TABLE training_sessions
        DROP CONSTRAINT IF EXISTS ck_phase_focus_defense_consistency;
    """)

    op.execute("""
        ALTER TABLE training_sessions
        DROP CONSTRAINT IF EXISTS ck_phase_focus_transition_offense_consistency;
    """)

    op.execute("""
        ALTER TABLE training_sessions
        DROP CONSTRAINT IF EXISTS ck_phase_focus_transition_defense_consistency;
    """)

    # Remover trigger
    op.execute("DROP TRIGGER IF EXISTS tr_derive_phase_focus ON training_sessions;")

    # Remover função
    op.execute("DROP FUNCTION IF EXISTS fn_derive_phase_focus();")

    # Reverter NOT NULL (tornar nullable novamente)
    op.execute("""
        ALTER TABLE training_sessions
        ALTER COLUMN phase_focus_attack DROP NOT NULL,
        ALTER COLUMN phase_focus_attack DROP DEFAULT;
    """)

    op.execute("""
        ALTER TABLE training_sessions
        ALTER COLUMN phase_focus_defense DROP NOT NULL,
        ALTER COLUMN phase_focus_defense DROP DEFAULT;
    """)

    op.execute("""
        ALTER TABLE training_sessions
        ALTER COLUMN phase_focus_transition_offense DROP NOT NULL,
        ALTER COLUMN phase_focus_transition_offense DROP DEFAULT;
    """)

    op.execute("""
        ALTER TABLE training_sessions
        ALTER COLUMN phase_focus_transition_defense DROP NOT NULL,
        ALTER COLUMN phase_focus_transition_defense DROP DEFAULT;
    """)
