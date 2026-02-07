"""
Script para aplicar migration 0044 manualmente
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.db import engine

def apply_migration():
    """Apply migration 0044 - export_system"""
    print("🔄 Aplicando Migration 0044 - export_system...")
    
    with engine.connect() as conn:
        # Check if tables already exist
        check_sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name IN ('export_jobs', 'export_rate_limits')
        AND table_schema = 'public';
        """
        result = conn.execute(text(check_sql))
        existing_tables = [row[0] for row in result]
        
        if existing_tables:
            print(f"⚠️  Tabelas já existem: {existing_tables}")
            print("Migration provavelmente já foi aplicada.")
            return
        
        # Create export_jobs table
        conn.execute(text("""
        CREATE TABLE export_jobs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            export_type VARCHAR(50) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            params JSONB NOT NULL,
            params_hash VARCHAR(64) NOT NULL,
            file_url VARCHAR(500),
            file_size_bytes BIGINT,
            error_message TEXT,
            started_at TIMESTAMPTZ,
            completed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            expires_at TIMESTAMPTZ,
            CONSTRAINT ck_export_jobs_valid_type CHECK (export_type IN ('analytics_pdf', 'athlete_data_json', 'athlete_data_csv')),
            CONSTRAINT ck_export_jobs_valid_status CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
            CONSTRAINT ck_export_jobs_positive_file_size CHECK (file_size_bytes IS NULL OR file_size_bytes > 0)
        );
        """))
        print("✅ Tabela export_jobs criada")
        
        # Create indexes for export_jobs
        conn.execute(text("""
        CREATE INDEX idx_export_jobs_user ON export_jobs(user_id, created_at DESC);
        """))
        conn.execute(text("""
        CREATE INDEX idx_export_jobs_status ON export_jobs(status, created_at) WHERE status IN ('pending', 'processing');
        """))
        conn.execute(text("""
        CREATE INDEX idx_export_jobs_cache_lookup ON export_jobs(export_type, params_hash, status) WHERE status = 'completed' AND expires_at > NOW();
        """))
        conn.execute(text("""
        CREATE INDEX idx_export_jobs_cleanup ON export_jobs(expires_at) WHERE expires_at IS NOT NULL AND status = 'completed';
        """))
        print("✅ 4 índices criados para export_jobs")
        
        # Create export_rate_limits table
        conn.execute(text("""
        CREATE TABLE export_rate_limits (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            export_type VARCHAR(50) NOT NULL,
            date DATE NOT NULL,
            count SMALLINT NOT NULL DEFAULT 0,
            last_export_at TIMESTAMPTZ,
            CONSTRAINT uq_export_rate_limits_user_type_date UNIQUE (user_id, export_type, date),
            CONSTRAINT ck_export_rate_limits_reasonable_count CHECK (count >= 0 AND count <= 10)
        );
        """))
        print("✅ Tabela export_rate_limits criada")
        
        # Create indexes for export_rate_limits
        conn.execute(text("""
        CREATE INDEX idx_export_rate_limits_user_date ON export_rate_limits(user_id, date DESC);
        """))
        conn.execute(text("""
        CREATE INDEX idx_export_rate_limits_cleanup ON export_rate_limits(date) WHERE date < CURRENT_DATE - INTERVAL '30 days';
        """))
        print("✅ 2 índices criados para export_rate_limits")
        
        # Update alembic_version
        conn.execute(text("""
        UPDATE alembic_version SET version_num = '0044_create_export_system';
        """))
        print("✅ alembic_version atualizado")
        
        conn.commit()
        print("\n🎉 Migration 0044 aplicada com sucesso!")

if __name__ == "__main__":
    try:
        apply_migration()
    except Exception as e:
        print(f"\n❌ Erro ao aplicar migration: {e}")
        sys.exit(1)
