"""Add indexes for reports and alerts performance

Revision ID: 2026010101_reports_idx
Revises: 
Create Date: 2026-01-01

Índices otimizados para:
- Relatórios de assiduidade (attendance)
- Relatórios de minutos (match_attendance)
- Relatórios de carga (wellness_post + training_sessions)
- Alertas de ACWR e lesões
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2026010101_reports_idx'
down_revision: Union[str, None] = '015_deprecate_athlete_photo_path'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria índices compostos para acelerar queries de relatórios e alertas.
    
    Ordem dos índices: team → athlete → data (conforme padrões de filtro)
    Índices parciais para estados ativos (reduz custo de storage e manutenção)
    """
    
    # ===========================================================================
    # ATTENDANCE (Assiduidade em treinos)
    # Queries: JOIN training_sessions → filter by team_id, athlete_id, session_at
    # ===========================================================================
    
    # Índice composto para relatórios de assiduidade por atleta
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_attendance_athlete_session_active
        ON attendance (athlete_id, training_session_id)
        WHERE deleted_at IS NULL;
    """)
    
    # ===========================================================================
    # TRAINING_SESSIONS (Sessões de treino)
    # Queries: filter by team_id, season_id, session_at (date range)
    # ===========================================================================
    
    # Índice composto team + data para relatórios por equipe
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_training_sessions_team_date_active
        ON training_sessions (team_id, session_at)
        WHERE deleted_at IS NULL;
    """)
    
    # Índice composto team + season + data para filtros completos
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_training_sessions_team_season_date
        ON training_sessions (team_id, season_id, session_at)
        WHERE deleted_at IS NULL;
    """)
    
    # ===========================================================================
    # MATCH_ATTENDANCE (Presença em jogos)
    # Queries: filter by athlete_id, match_id + join matches for team/date
    # ===========================================================================
    
    # Índice composto para relatórios de minutos por atleta
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_match_attendance_athlete_match_active
        ON match_attendance (athlete_id, match_id)
        WHERE deleted_at IS NULL AND played = true;
    """)
    
    # ===========================================================================
    # WELLNESS_POST (Carga - RPE × minutos)
    # Queries: JOIN training_sessions → filter by athlete_id, training_session_id
    # ===========================================================================
    
    # Índice para queries de carga por atleta (ACWR)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_wellness_post_athlete_session_active
        ON wellness_post (athlete_id, training_session_id, created_at)
        WHERE deleted_at IS NULL;
    """)
    
    # ===========================================================================
    # TEAM_REGISTRATIONS (Vínculos ativos)
    # Queries: filter by team_id, athlete_id WHERE active
    # ===========================================================================
    
    # Índice parcial para vínculos ativos (joins frequentes em todos os relatórios)
    # NOTA: Já existe ux_team_registrations_active, mas vamos criar um composto team→athlete
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_team_registrations_team_athlete_active
        ON team_registrations (team_id, athlete_id)
        WHERE end_at IS NULL AND deleted_at IS NULL;
    """)
    
    # ===========================================================================
    # MATCHES (Jogos - para relatórios de minutos)
    # Queries: filter by season_id, match_date
    # ===========================================================================
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_matches_season_date_active
        ON matches (season_id, match_date)
        WHERE deleted_at IS NULL;
    """)
    
    # ===========================================================================
    # ATHLETES (Alertas de lesão)
    # Queries: filter by state, injured, medical_restriction
    # ===========================================================================
    
    # Índice parcial para atletas com flags médicas (alertas de lesão)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_athletes_medical_flags
        ON athletes (organization_id)
        WHERE deleted_at IS NULL AND (injured = true OR medical_restriction = true OR load_restricted = true);
    """)
    
    # ===========================================================================
    # MEDICAL_CASES (Casos médicos ativos)
    # Queries: filter by athlete_id, status
    # ===========================================================================
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_medical_cases_athlete_status_active
        ON medical_cases (athlete_id, status)
        WHERE deleted_at IS NULL AND status IN ('ativo', 'em_acompanhamento');
    """)


def downgrade() -> None:
    """Remove os índices criados."""
    
    op.execute("DROP INDEX IF EXISTS ix_attendance_athlete_session_active;")
    op.execute("DROP INDEX IF EXISTS ix_training_sessions_team_date_active;")
    op.execute("DROP INDEX IF EXISTS ix_training_sessions_team_season_date;")
    op.execute("DROP INDEX IF EXISTS ix_match_attendance_athlete_match_active;")
    op.execute("DROP INDEX IF EXISTS ix_wellness_post_athlete_session_active;")
    op.execute("DROP INDEX IF EXISTS ix_team_registrations_team_athlete_active;")
    op.execute("DROP INDEX IF EXISTS ix_matches_season_date_active;")
    op.execute("DROP INDEX IF EXISTS ix_athletes_medical_flags;")
    op.execute("DROP INDEX IF EXISTS ix_medical_cases_athlete_status_active;")
