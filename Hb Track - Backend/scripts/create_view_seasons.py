"""
Script para criar VIEW v_seasons_with_status
"""
from sqlalchemy import create_engine, text
from app.core.config import settings
import os

os.environ.setdefault('ENV', 'test')

SQL = """
DROP VIEW IF EXISTS v_seasons_with_status;

CREATE VIEW v_seasons_with_status AS
SELECT 
    s.id,
    s.team_id,
    s.name,
    s.year,
    s.competition_type,
    s.start_date,
    s.end_date,
    s.canceled_at,
    s.interrupted_at,
    s.created_by_user_id,
    s.created_at,
    s.updated_at,
    s.deleted_at,
    s.deleted_reason,
    CASE
        WHEN s.canceled_at IS NOT NULL THEN 'cancelada'
        WHEN s.interrupted_at IS NOT NULL THEN 'interrompida'
        WHEN s.end_date < CURRENT_DATE THEN 'encerrada'
        WHEN s.start_date <= CURRENT_DATE AND CURRENT_DATE <= s.end_date THEN 'ativa'
        ELSE 'planejada'
    END AS status
FROM seasons s
WHERE s.deleted_at IS NULL;

COMMENT ON VIEW v_seasons_with_status IS 'VIEW de temporadas com status derivado calculado (6.1.1)';
"""

if __name__ == "__main__":
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Executar cada statement separadamente
        for stmt in SQL.strip().split(';'):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
        print("✅ VIEW v_seasons_with_status criada com sucesso!")
        
        # Verificar
        result = conn.execute(text("SELECT COUNT(*) FROM pg_views WHERE viewname = 'v_seasons_with_status'"))
        count = result.scalar()
        print(f"   Verificação: {count} view(s) encontrada(s)")
