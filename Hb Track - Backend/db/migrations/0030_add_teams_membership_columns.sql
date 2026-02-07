-- Migration: 0030_add_teams_membership_columns
-- Adiciona season_id, coach_membership_id, created_by_membership_id à tabela teams

BEGIN;

-- Adicionar coluna season_id (nullable - teams podem existir sem temporada definida)
ALTER TABLE teams ADD COLUMN IF NOT EXISTS season_id UUID NULL;

-- Criar FK para seasons
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_teams_season_id'
    ) THEN
        ALTER TABLE teams ADD CONSTRAINT fk_teams_season_id 
        FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE RESTRICT;
    END IF;
END $$;

-- Criar índice para queries por temporada
CREATE INDEX IF NOT EXISTS ix_teams_season_id ON teams(season_id);

-- Adicionar coluna coach_membership_id (nullable - RF7)
ALTER TABLE teams ADD COLUMN IF NOT EXISTS coach_membership_id UUID NULL;

-- Criar FK para org_memberships
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_teams_coach_membership_id'
    ) THEN
        ALTER TABLE teams ADD CONSTRAINT fk_teams_coach_membership_id 
        FOREIGN KEY (coach_membership_id) REFERENCES org_memberships(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Criar índice para queries por treinador
CREATE INDEX IF NOT EXISTS ix_teams_coach_membership_id ON teams(coach_membership_id);

-- Adicionar coluna created_by_membership_id (nullable - auditoria)
ALTER TABLE teams ADD COLUMN IF NOT EXISTS created_by_membership_id UUID NULL;

-- Criar FK para org_memberships
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_teams_created_by_membership_id'
    ) THEN
        ALTER TABLE teams ADD CONSTRAINT fk_teams_created_by_membership_id 
        FOREIGN KEY (created_by_membership_id) REFERENCES org_memberships(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Criar índice para auditoria
CREATE INDEX IF NOT EXISTS ix_teams_created_by_membership_id ON teams(created_by_membership_id);

-- Comentários nas colunas
COMMENT ON COLUMN teams.season_id IS 'FK para seasons - vincula team a temporada específica';
COMMENT ON COLUMN teams.coach_membership_id IS 'RF7 - Treinador principal atribuído à equipe';
COMMENT ON COLUMN teams.created_by_membership_id IS 'Auditoria - membership que criou a equipe';

-- Registrar migration no alembic_version (se necessário)
INSERT INTO alembic_version (version_num) 
VALUES ('0030_add_teams_membership_columns')
ON CONFLICT (version_num) DO NOTHING;

COMMIT;

-- Verificação
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'teams' 
  AND column_name IN ('season_id', 'coach_membership_id', 'created_by_membership_id')
ORDER BY column_name;
