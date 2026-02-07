"""add_season_team_to_training_sessions_phase1

Revision ID: 5c90cfd7e291
Revises: 8fba6a22b58c
Create Date: 2025-12-25 14:41:00.605645

FASE 1: Adiciona season_id e team_id como NULLABLE (minimiza locks).
Referências RAG: R8, R39, RDB4, RDB5

IMPORTANTE: Esta é a FASE 1 de uma migração em 2 fases.
- FASE 1: Adiciona colunas NULL, backfill, índices CONCURRENTLY, FKs NOT VALID
- FASE 2: Altera para NOT NULL após validação

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c90cfd7e291'
down_revision: Union[str, Sequence[str], None] = '4af09f9d46a0'  # ANTES de R1
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    FASE 1: Adiciona season_id e team_id como NULLABLE a training_sessions.

    Estratégia:
    1. Adiciona colunas como NULL (sem bloquear longamente - R8, R39)
    2. Backfill será executado em script separado
    3. Índices CONCURRENTLY (RD85, RF29)
    4. FKs como NOT VALID depois VALIDATE (minimiza lock)
    """

    # ============================================================================
    # 1. ADICIONAR COLUNAS COMO NULL
    # ============================================================================
    op.execute(sa.text("""
        -- Adiciona season_id (R8: vínculo obrigatório por temporada)
        ALTER TABLE training_sessions
        ADD COLUMN IF NOT EXISTS season_id uuid;

        -- Adiciona team_id (R39: atividades vinculadas a equipe)
        ALTER TABLE training_sessions
        ADD COLUMN IF NOT EXISTS team_id uuid;

        -- Documentação (RDB5: audit trail)
        COMMENT ON COLUMN training_sessions.season_id IS
        'Temporada do treino. R8: Todas atletas vinculadas a uma temporada. FASE 1: NULL permitido para backfill.';

        COMMENT ON COLUMN training_sessions.team_id IS
        'Equipe do treino. R39: Atividades vinculadas a equipe. FASE 1: NULL permitido para backfill.';
    """))

    # ============================================================================
    # 2. CRIAR ÍNDICES (RD85, RF29 - performance de relatórios)
    # ============================================================================
    # NOTA: Índices criados SEM CONCURRENTLY (dentro da transação alembic)
    # Em produção com muitos dados, pode-se criar CONCURRENTLY manualmente após migration
    op.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS idx_training_sessions_season
        ON training_sessions(season_id)
        WHERE season_id IS NOT NULL;

        CREATE INDEX IF NOT EXISTS idx_training_sessions_team
        ON training_sessions(team_id)
        WHERE team_id IS NOT NULL;

        -- Índice composto para queries de relatórios (R18, R22)
        CREATE INDEX IF NOT EXISTS idx_training_sessions_org_season_date
        ON training_sessions(organization_id, season_id, session_at DESC)
        WHERE season_id IS NOT NULL;
    """))

    # ============================================================================
    # 3. ADICIONAR FKs COMO NOT VALID (validação posterior - minimiza lock)
    # ============================================================================
    op.execute(sa.text("""
        -- FK para seasons (R8)
        ALTER TABLE training_sessions
        ADD CONSTRAINT fk_training_sessions_season
        FOREIGN KEY (season_id) REFERENCES seasons(id)
        ON DELETE RESTRICT
        NOT VALID;

        -- FK para teams (R39)
        ALTER TABLE training_sessions
        ADD CONSTRAINT fk_training_sessions_team
        FOREIGN KEY (team_id) REFERENCES teams(id)
        ON DELETE RESTRICT
        NOT VALID;
    """))

    # ============================================================================
    # 4. VALIDAR FKs (em transação separada, pode ser demorado)
    # ============================================================================
    # IMPORTANTE: VALIDATE CONSTRAINT faz scan completo mas permite leituras
    op.execute(sa.text("""
        -- Valida FK de season (verifica integridade referencial)
        ALTER TABLE training_sessions
        VALIDATE CONSTRAINT fk_training_sessions_season;

        -- Valida FK de team (verifica integridade referencial)
        ALTER TABLE training_sessions
        VALIDATE CONSTRAINT fk_training_sessions_team;
    """))


def downgrade() -> None:
    """
    Reverte FASE 1: Remove colunas season_id e team_id.

    ATENÇÃO: Isso remove dados! Usar apenas em desenvolvimento/staging.
    """

    # Remove FKs
    op.execute(sa.text("""
        ALTER TABLE training_sessions
        DROP CONSTRAINT IF EXISTS fk_training_sessions_season;

        ALTER TABLE training_sessions
        DROP CONSTRAINT IF EXISTS fk_training_sessions_team;
    """))

    # Remove índices
    op.execute(sa.text("""
        DROP INDEX IF EXISTS idx_training_sessions_season;
        DROP INDEX IF EXISTS idx_training_sessions_team;
        DROP INDEX IF EXISTS idx_training_sessions_org_season_date;
    """))

    # Remove colunas
    op.execute(sa.text("""
        ALTER TABLE training_sessions
        DROP COLUMN IF EXISTS season_id;

        ALTER TABLE training_sessions
        DROP COLUMN IF EXISTS team_id;
    """))
