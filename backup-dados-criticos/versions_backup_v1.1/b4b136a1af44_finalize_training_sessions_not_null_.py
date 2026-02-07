"""finalize_training_sessions_not_null_phase2

Revision ID: b4b136a1af44
Revises: 8fba6a22b58c
Create Date: 2025-12-25

FASE 2: Finalizar garantias estruturais conforme RAG (R8, R39, R33)
- Tornar season_id e team_id NOT NULL
- Garantir integridade referencial completa

PRÉ-CONDIÇÃO: Backfill concluído e FKs validados (FASE 1 completa)

Referências RAG: R8, R39, R33, RDB4
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4b136a1af44'
down_revision: Union[str, Sequence[str], None] = '8fba6a22b58c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    FASE 2: Tornar season_id e team_id NOT NULL.

    IMPORTANTE: Só executar após backfill completo em produção.
    Esta migration valida que não há NULLs antes de alterar.
    """

    # ============================================================================
    # 1. VALIDAÇÃO: Verificar se há NULLs (aborta se houver)
    # ============================================================================
    op.execute(sa.text("""
        DO $$
        DECLARE
            null_season_count INTEGER;
            null_team_count INTEGER;
        BEGIN
            -- Conta registros com season_id NULL
            SELECT COUNT(*) INTO null_season_count
            FROM training_sessions
            WHERE season_id IS NULL
              AND deleted_at IS NULL;

            -- Conta registros com team_id NULL
            SELECT COUNT(*) INTO null_team_count
            FROM training_sessions
            WHERE team_id IS NULL
              AND deleted_at IS NULL;

            -- Aborta se houver NULLs
            IF null_season_count > 0 THEN
                RAISE EXCEPTION
                    'FASE 2 abortada: % registros com season_id NULL. Execute backfill primeiro!',
                    null_season_count;
            END IF;

            IF null_team_count > 0 THEN
                RAISE EXCEPTION
                    'FASE 2 abortada: % registros com team_id NULL. Execute backfill primeiro!',
                    null_team_count;
            END IF;

            RAISE NOTICE 'Validação OK: Nenhum NULL encontrado';
        END $$;
    """))

    # ============================================================================
    # 2. ALTERAR COLUNAS PARA NOT NULL (R8, R39, R33)
    # ============================================================================
    op.execute(sa.text("""
        -- Season_id NOT NULL (R8: vínculo obrigatório por temporada)
        ALTER TABLE training_sessions
        ALTER COLUMN season_id SET NOT NULL;

        -- Team_id NOT NULL (R39: atividades vinculadas a equipe)
        ALTER TABLE training_sessions
        ALTER COLUMN team_id SET NOT NULL;

        -- Atualizar comentários
        COMMENT ON COLUMN training_sessions.season_id IS
        'Temporada do treino (NOT NULL). R8: Todas atletas vinculadas a uma temporada.';

        COMMENT ON COLUMN training_sessions.team_id IS
        'Equipe do treino (NOT NULL). R39: Atividades vinculadas a equipe.';
    """))

    # ============================================================================
    # 3. VALIDAR CONSISTÊNCIA (R33: Regras operacionais)
    # ============================================================================
    op.execute(sa.text("""
        DO $$
        BEGIN
            -- Verifica se todas as FKs são válidas
            PERFORM 1
            FROM training_sessions ts
            LEFT JOIN seasons s ON s.id = ts.season_id
            WHERE ts.deleted_at IS NULL
              AND s.id IS NULL
            LIMIT 1;

            IF FOUND THEN
                RAISE EXCEPTION 'FK inconsistente: season_id referencia season inexistente';
            END IF;

            PERFORM 1
            FROM training_sessions ts
            LEFT JOIN teams t ON t.id = ts.team_id
            WHERE ts.deleted_at IS NULL
              AND t.id IS NULL
            LIMIT 1;

            IF FOUND THEN
                RAISE EXCEPTION 'FK inconsistente: team_id referencia team inexistente';
            END IF;

            RAISE NOTICE 'Consistência validada: Todas FKs são válidas';
        END $$;
    """))


def downgrade() -> None:
    """
    Reverte FASE 2: Torna colunas NULLABLE novamente.

    ATENÇÃO: Isso remove garantias estruturais do RAG!
    Usar apenas em desenvolvimento/rollback emergencial.
    """

    op.execute(sa.text("""
        -- Torna colunas nullable novamente
        ALTER TABLE training_sessions
        ALTER COLUMN season_id DROP NOT NULL;

        ALTER TABLE training_sessions
        ALTER COLUMN team_id DROP NOT NULL;

        -- Atualizar comentários
        COMMENT ON COLUMN training_sessions.season_id IS
        'Temporada do treino (NULLABLE - FASE 1). R8: Vínculo obrigatório após FASE 2.';

        COMMENT ON COLUMN training_sessions.team_id IS
        'Equipe do treino (NULLABLE - FASE 1). R39: Vínculo obrigatório após FASE 2.';
    """))
