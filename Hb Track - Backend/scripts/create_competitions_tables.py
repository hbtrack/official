"""
Script de migração para criar tabelas de Competitions e Competition Seasons

Este script cria as tabelas necessárias para o módulo de competições:
- competitions: Tabela principal de competições
- competition_seasons: Tabela de ligação competição-temporada

Execute: python scripts/create_competitions_tables.py
"""

from app.core.db import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_competitions_tables():
    """Cria as tabelas de competitions e competition_seasons"""
    
    with engine.begin() as conn:
        # 1. Verificar se a tabela competitions já existe
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'competitions'
            );
        """))
        competitions_exists = result.scalar()
        
        if competitions_exists:
            logger.info("✅ Tabela 'competitions' já existe")
        else:
            logger.info("📦 Criando tabela 'competitions'...")
            conn.execute(text("""
                CREATE TABLE competitions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    organization_id UUID NOT NULL REFERENCES organizations(id),
                    name VARCHAR(200) NOT NULL,
                    kind VARCHAR(50),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(organization_id, name)
                );
            """))
            logger.info("✅ Tabela 'competitions' criada")
            
            # Criar índice para organization_id
            conn.execute(text("""
                CREATE INDEX idx_competitions_organization_id 
                ON competitions(organization_id);
            """))
            logger.info("✅ Índice 'idx_competitions_organization_id' criado")
        
        # 2. Verificar se a tabela competition_seasons já existe
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'competition_seasons'
            );
        """))
        comp_seasons_exists = result.scalar()
        
        if comp_seasons_exists:
            logger.info("✅ Tabela 'competition_seasons' já existe")
        else:
            logger.info("📦 Criando tabela 'competition_seasons'...")
            conn.execute(text("""
                CREATE TABLE competition_seasons (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
                    season_id UUID NOT NULL REFERENCES seasons(id),
                    name VARCHAR(200),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(competition_id, season_id)
                );
            """))
            logger.info("✅ Tabela 'competition_seasons' criada")
            
            # Criar índices
            conn.execute(text("""
                CREATE INDEX idx_competition_seasons_competition_id 
                ON competition_seasons(competition_id);
            """))
            conn.execute(text("""
                CREATE INDEX idx_competition_seasons_season_id 
                ON competition_seasons(season_id);
            """))
            logger.info("✅ Índices para 'competition_seasons' criados")
        
        logger.info("\n🎉 Migração concluída com sucesso!")


if __name__ == "__main__":
    create_competitions_tables()
