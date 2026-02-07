"""
Migration: Criar índices compostos para otimização do Dashboard

Índices críticos para performance:
- (team_id, deleted_at) - filtro mais comum
- (team_id, date) - queries por data
- (organization_id, deleted_at) - queries por organização

NOTA: Usa CREATE INDEX sem CONCURRENTLY para compatibilidade com transações Alembic.
Em produção, pode-se rodar manualmente com CONCURRENTLY fora de transação.
"""

from alembic import op
import sqlalchemy as sa


revision = '20260101_dashboard_indexes'
down_revision = '018_ficha_perf_idx'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria índices compostos para otimização do dashboard"""
    
    # ==========================================================================
    # TABELA: athletes
    # ==========================================================================
    
    # Índice principal para listagem de atletas por organização
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_athletes_org_deleted
        ON athletes (organization_id, deleted_at)
        WHERE deleted_at IS NULL
    """)
    
    # ==========================================================================
    # TABELA: team_registrations
    # ==========================================================================
    
    # Índice para busca de atletas por time
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_team_registrations_team_active
        ON team_registrations (team_id, deleted_at)
        WHERE deleted_at IS NULL
    """)
    
    # Índice para busca por atleta
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_team_registrations_athlete_active
        ON team_registrations (athlete_id, deleted_at)
        WHERE deleted_at IS NULL
    """)
    
    # ==========================================================================
    # TABELA: training_sessions
    # ==========================================================================
    
    # Índice para listagem por time e data
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_training_sessions_team_date
        ON training_sessions (team_id, session_at DESC, deleted_at)
        WHERE deleted_at IS NULL
    """)
    
    # Índice para listagem por organização
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_training_sessions_org
        ON training_sessions (organization_id, deleted_at)
        WHERE deleted_at IS NULL
    """)
    
    # ==========================================================================
    # TABELA: attendance (presença em treinos)
    # ==========================================================================
    
    # Índice para busca por sessão (apenas training_session_id)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_attendance_session
        ON attendance (training_session_id)
    """)


def downgrade() -> None:
    """Remove os índices criados"""
    
    op.execute("DROP INDEX IF EXISTS idx_athletes_org_deleted")
    op.execute("DROP INDEX IF EXISTS idx_team_registrations_team_active")
    op.execute("DROP INDEX IF EXISTS idx_team_registrations_athlete_active")
    op.execute("DROP INDEX IF EXISTS idx_training_sessions_team_date")
    op.execute("DROP INDEX IF EXISTS idx_training_sessions_org")
    op.execute("DROP INDEX IF EXISTS idx_attendance_session")
