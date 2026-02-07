-- ============================================================================
-- MIGRATION: Módulo Completo de Competições com IA
-- Data: 2026-01-08
-- Descrição: Altera tabela competitions existente e cria novas tabelas para
--            suportar cadastro completo de competições via importação PDF/IA
-- ============================================================================

-- ============================================================================
-- 1. ALTERAR TABELA competitions EXISTENTE
-- Adiciona novos campos mantendo compatibilidade com dados existentes
-- ============================================================================

-- Adicionar campo team_id (FK para teams - qual equipe NOSSA participa)
ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS team_id UUID REFERENCES teams(id) ON DELETE SET NULL;

-- Adicionar campos de informações básicas
ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS season VARCHAR(50);

ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS modality VARCHAR(50) DEFAULT 'masculino';

-- Adicionar campos de forma de disputa
ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS competition_type VARCHAR(50);

ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS format_details JSONB DEFAULT '{}';

-- Critérios de desempate (ordenados por prioridade)
ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS tiebreaker_criteria JSONB DEFAULT '["pontos", "saldo_gols", "gols_pro", "confronto_direto"]';

-- Pontuação (padrão handebol: 2 pontos por vitória)
ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS points_per_win INTEGER DEFAULT 2;

-- Status e controle
ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'draft';

ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS current_phase_id UUID;

-- Regulamento
ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS regulation_file_url VARCHAR(500);

ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS regulation_notes TEXT;

-- Auditoria
ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id);

ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE competitions 
    ADD COLUMN IF NOT EXISTS deleted_reason TEXT;

-- Adicionar constraints de validação
DO $$ 
BEGIN
    -- Constraint para competition_type
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_competition_type'
    ) THEN
        ALTER TABLE competitions ADD CONSTRAINT chk_competition_type CHECK (
            competition_type IS NULL OR competition_type IN (
                'turno_unico',
                'turno_returno', 
                'grupos',
                'grupos_mata_mata',
                'mata_mata',
                'triangular',
                'quadrangular',
                'custom'
            )
        );
    END IF;
    
    -- Constraint para modality
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_comp_modality'
    ) THEN
        ALTER TABLE competitions ADD CONSTRAINT chk_comp_modality CHECK (
            modality IS NULL OR modality IN ('masculino', 'feminino', 'misto')
        );
    END IF;
    
    -- Constraint para status
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_comp_status'
    ) THEN
        ALTER TABLE competitions ADD CONSTRAINT chk_comp_status CHECK (
            status IS NULL OR status IN ('draft', 'active', 'finished', 'cancelled')
        );
    END IF;
END $$;

-- Índices para competitions
CREATE INDEX IF NOT EXISTS idx_competitions_team_id ON competitions(team_id);
CREATE INDEX IF NOT EXISTS idx_competitions_season ON competitions(season);
CREATE INDEX IF NOT EXISTS idx_competitions_status ON competitions(status);
CREATE INDEX IF NOT EXISTS idx_competitions_org ON competitions(organization_id);

-- ============================================================================
-- 2. TABELA: competition_phases (Fases da competição)
-- ============================================================================
CREATE TABLE IF NOT EXISTS competition_phases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    
    name VARCHAR(100) NOT NULL,
    phase_type VARCHAR(50) NOT NULL,
    order_index INT NOT NULL DEFAULT 0,
    
    -- Cruzamento olímpico (1ºA x 2ºB)
    is_olympic_cross BOOLEAN DEFAULT false,
    
    -- Configurações específicas da fase
    config JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_phase_type CHECK (
        phase_type IN (
            'group',           -- Fase de grupos
            'knockout',        -- Mata-mata genérico
            'round_robin',     -- Todos contra todos
            'semifinal',
            'final',
            'third_place',     -- Disputa 3º lugar
            'quarterfinal',
            'round_of_16',
            'custom'
        )
    ),
    CONSTRAINT chk_phase_status CHECK (
        status IN ('pending', 'in_progress', 'finished')
    )
);

CREATE INDEX IF NOT EXISTS idx_phases_competition ON competition_phases(competition_id);
CREATE INDEX IF NOT EXISTS idx_phases_order ON competition_phases(competition_id, order_index);

-- Adicionar FK de current_phase_id após criar a tabela
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_current_phase'
    ) THEN
        ALTER TABLE competitions 
            ADD CONSTRAINT fk_current_phase 
            FOREIGN KEY (current_phase_id) REFERENCES competition_phases(id) ON DELETE SET NULL;
    END IF;
END $$;

-- ============================================================================
-- 3. TABELA: competition_opponent_teams (Equipes adversárias na competição)
-- ============================================================================
CREATE TABLE IF NOT EXISTS competition_opponent_teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    
    -- Informações da equipe adversária
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50),
    category VARCHAR(50),
    city VARCHAR(100),
    logo_url VARCHAR(500),
    
    -- Vínculo com equipe existente no sistema (fuzzy match)
    linked_team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
    
    -- Grupo (se houver fase de grupos)
    group_name VARCHAR(50),
    
    -- Estatísticas calculadas (atualizadas após cada jogo)
    stats JSONB DEFAULT '{
        "points": 0,
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0
    }',
    
    -- Status na competição
    status VARCHAR(50) DEFAULT 'active',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_opponent_status CHECK (
        status IN ('active', 'eliminated', 'qualified', 'withdrawn')
    )
);

CREATE INDEX IF NOT EXISTS idx_opponent_teams_competition ON competition_opponent_teams(competition_id);
CREATE INDEX IF NOT EXISTS idx_opponent_teams_group ON competition_opponent_teams(competition_id, group_name);
CREATE INDEX IF NOT EXISTS idx_opponent_teams_linked ON competition_opponent_teams(linked_team_id);

-- ============================================================================
-- 4. TABELA: competition_matches (Jogos da competição - separado de matches)
-- Esta tabela armazena TODOS os jogos da competição, não apenas os nossos
-- ============================================================================
CREATE TABLE IF NOT EXISTS competition_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    phase_id UUID REFERENCES competition_phases(id) ON DELETE SET NULL,
    
    -- ID externo para upsert (evita duplicação ao reimportar PDF)
    external_reference_id VARCHAR(100),
    
    -- Equipes do jogo (da tabela competition_opponent_teams)
    home_team_id UUID REFERENCES competition_opponent_teams(id) ON DELETE SET NULL,
    away_team_id UUID REFERENCES competition_opponent_teams(id) ON DELETE SET NULL,
    
    -- Flag para identificar se é jogo da NOSSA equipe
    is_our_match BOOLEAN DEFAULT false,
    our_team_is_home BOOLEAN,
    
    -- Vínculo com tabela matches (se for nosso jogo e tiver detalhes)
    linked_match_id UUID REFERENCES matches(id) ON DELETE SET NULL,
    
    -- Data e local
    match_date DATE,
    match_time TIME,
    match_datetime TIMESTAMP WITH TIME ZONE,
    location VARCHAR(255),
    
    -- Rodada/Round
    round_number INT,
    round_name VARCHAR(100),
    
    -- Resultado
    home_score INT,
    away_score INT,
    
    -- Resultado em caso de prorrogação/pênaltis
    home_score_extra INT,
    away_score_extra INT,
    home_score_penalties INT,
    away_score_penalties INT,
    
    -- Status do jogo
    status VARCHAR(50) DEFAULT 'scheduled',
    
    -- Observações
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_comp_match_status CHECK (
        status IN ('scheduled', 'in_progress', 'finished', 'postponed', 'cancelled')
    ),
    CONSTRAINT chk_different_teams CHECK (home_team_id IS NULL OR away_team_id IS NULL OR home_team_id != away_team_id)
);

CREATE INDEX IF NOT EXISTS idx_comp_matches_competition ON competition_matches(competition_id);
CREATE INDEX IF NOT EXISTS idx_comp_matches_phase ON competition_matches(phase_id);
CREATE INDEX IF NOT EXISTS idx_comp_matches_date ON competition_matches(match_date);
CREATE INDEX IF NOT EXISTS idx_comp_matches_our ON competition_matches(competition_id, is_our_match);
CREATE INDEX IF NOT EXISTS idx_comp_matches_status ON competition_matches(status);
CREATE INDEX IF NOT EXISTS idx_comp_matches_linked ON competition_matches(linked_match_id);

-- Índice único para external_reference_id (permite upsert)
CREATE UNIQUE INDEX IF NOT EXISTS idx_comp_matches_external_ref 
    ON competition_matches(competition_id, external_reference_id) 
    WHERE external_reference_id IS NOT NULL;

-- ============================================================================
-- 5. TABELA: competition_standings (Classificação - cache para performance)
-- ============================================================================
CREATE TABLE IF NOT EXISTS competition_standings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    phase_id UUID REFERENCES competition_phases(id) ON DELETE CASCADE,
    opponent_team_id UUID NOT NULL REFERENCES competition_opponent_teams(id) ON DELETE CASCADE,
    
    -- Posição e grupo
    position INT NOT NULL,
    group_name VARCHAR(50),
    
    -- Estatísticas
    points INT DEFAULT 0,
    played INT DEFAULT 0,
    wins INT DEFAULT 0,
    draws INT DEFAULT 0,
    losses INT DEFAULT 0,
    goals_for INT DEFAULT 0,
    goals_against INT DEFAULT 0,
    goal_difference INT DEFAULT 0,
    
    -- Forma recente (últimos 5 jogos: W, D, L)
    recent_form VARCHAR(10),
    
    -- Status de classificação
    qualification_status VARCHAR(50),
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_qualification_status CHECK (
        qualification_status IS NULL OR qualification_status IN ('qualified', 'playoffs', 'relegation', 'eliminated')
    ),
    
    UNIQUE(competition_id, phase_id, opponent_team_id)
);

CREATE INDEX IF NOT EXISTS idx_standings_competition ON competition_standings(competition_id);
CREATE INDEX IF NOT EXISTS idx_standings_position ON competition_standings(competition_id, phase_id, position);

-- ============================================================================
-- 6. FUNÇÃO: Atualizar estatísticas após resultado de jogo
-- Usa points_per_win da competição (padrão 2 para handebol)
-- ============================================================================
CREATE OR REPLACE FUNCTION update_competition_team_stats_after_match()
RETURNS TRIGGER AS $$
DECLARE
    home_points INT;
    away_points INT;
    win_points INT;
BEGIN
    -- Só atualiza se o jogo foi finalizado
    IF NEW.status = 'finished' AND NEW.home_score IS NOT NULL AND NEW.away_score IS NOT NULL THEN
        
        -- Busca pontos por vitória da competição (padrão 2 para handebol)
        SELECT COALESCE(points_per_win, 2) INTO win_points
        FROM competitions WHERE id = NEW.competition_id;
        
        -- Calcula pontos
        IF NEW.home_score > NEW.away_score THEN
            home_points := win_points;
            away_points := 0;
        ELSIF NEW.home_score < NEW.away_score THEN
            home_points := 0;
            away_points := win_points;
        ELSE
            home_points := 1;
            away_points := 1;
        END IF;
        
        -- Atualiza estatísticas do time da casa
        IF NEW.home_team_id IS NOT NULL THEN
            UPDATE competition_opponent_teams
            SET stats = jsonb_set(
                jsonb_set(
                    jsonb_set(
                        jsonb_set(
                            jsonb_set(
                                jsonb_set(
                                    jsonb_set(
                                        jsonb_set(
                                            stats,
                                            '{points}', to_jsonb(COALESCE((stats->>'points')::int, 0) + home_points)
                                        ),
                                        '{played}', to_jsonb(COALESCE((stats->>'played')::int, 0) + 1)
                                    ),
                                    '{wins}', to_jsonb(COALESCE((stats->>'wins')::int, 0) + CASE WHEN NEW.home_score > NEW.away_score THEN 1 ELSE 0 END)
                                ),
                                '{draws}', to_jsonb(COALESCE((stats->>'draws')::int, 0) + CASE WHEN NEW.home_score = NEW.away_score THEN 1 ELSE 0 END)
                            ),
                            '{losses}', to_jsonb(COALESCE((stats->>'losses')::int, 0) + CASE WHEN NEW.home_score < NEW.away_score THEN 1 ELSE 0 END)
                        ),
                        '{goals_for}', to_jsonb(COALESCE((stats->>'goals_for')::int, 0) + NEW.home_score)
                    ),
                    '{goals_against}', to_jsonb(COALESCE((stats->>'goals_against')::int, 0) + NEW.away_score)
                ),
                '{goal_difference}', to_jsonb(
                    COALESCE((stats->>'goals_for')::int, 0) + NEW.home_score - 
                    COALESCE((stats->>'goals_against')::int, 0) - NEW.away_score
                )
            ),
            updated_at = NOW()
            WHERE id = NEW.home_team_id;
        END IF;
        
        -- Atualiza estatísticas do time visitante
        IF NEW.away_team_id IS NOT NULL THEN
            UPDATE competition_opponent_teams
            SET stats = jsonb_set(
                jsonb_set(
                    jsonb_set(
                        jsonb_set(
                            jsonb_set(
                                jsonb_set(
                                    jsonb_set(
                                        jsonb_set(
                                            stats,
                                            '{points}', to_jsonb(COALESCE((stats->>'points')::int, 0) + away_points)
                                        ),
                                        '{played}', to_jsonb(COALESCE((stats->>'played')::int, 0) + 1)
                                    ),
                                    '{wins}', to_jsonb(COALESCE((stats->>'wins')::int, 0) + CASE WHEN NEW.away_score > NEW.home_score THEN 1 ELSE 0 END)
                                ),
                                '{draws}', to_jsonb(COALESCE((stats->>'draws')::int, 0) + CASE WHEN NEW.home_score = NEW.away_score THEN 1 ELSE 0 END)
                            ),
                            '{losses}', to_jsonb(COALESCE((stats->>'losses')::int, 0) + CASE WHEN NEW.away_score < NEW.home_score THEN 1 ELSE 0 END)
                        ),
                        '{goals_for}', to_jsonb(COALESCE((stats->>'goals_for')::int, 0) + NEW.away_score)
                    ),
                    '{goals_against}', to_jsonb(COALESCE((stats->>'goals_against')::int, 0) + NEW.home_score)
                ),
                '{goal_difference}', to_jsonb(
                    COALESCE((stats->>'goals_for')::int, 0) + NEW.away_score - 
                    COALESCE((stats->>'goals_against')::int, 0) - NEW.home_score
                )
            ),
            updated_at = NOW()
            WHERE id = NEW.away_team_id;
        END IF;
        
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar estatísticas
DROP TRIGGER IF EXISTS trigger_update_comp_stats_after_match ON competition_matches;
CREATE TRIGGER trigger_update_comp_stats_after_match
    AFTER INSERT OR UPDATE ON competition_matches
    FOR EACH ROW
    EXECUTE FUNCTION update_competition_team_stats_after_match();

-- ============================================================================
-- 7. COMENTÁRIOS NAS TABELAS
-- ============================================================================
COMMENT ON TABLE competitions IS 'Competições que a equipe participa. V2: suporta importação via IA.';
COMMENT ON TABLE competition_phases IS 'Fases de cada competição (grupos, mata-mata, etc)';
COMMENT ON TABLE competition_opponent_teams IS 'Equipes adversárias em cada competição (cadastro via IA)';
COMMENT ON TABLE competition_matches IS 'Todos os jogos da competição (não apenas os nossos)';
COMMENT ON TABLE competition_standings IS 'Classificação/tabela de cada fase (cache)';

COMMENT ON COLUMN competitions.competition_type IS 'Tipo: turno_unico, turno_returno, grupos, grupos_mata_mata, mata_mata, triangular, quadrangular, custom';
COMMENT ON COLUMN competitions.tiebreaker_criteria IS 'Array JSON com critérios de desempate em ordem de prioridade';
COMMENT ON COLUMN competitions.format_details IS 'Detalhes específicos do formato (num_grupos, classificados_por_grupo, etc)';
COMMENT ON COLUMN competitions.points_per_win IS 'Pontos por vitória. Padrão handebol: 2. Algumas ligas usam 3.';
COMMENT ON COLUMN competition_matches.external_reference_id IS 'ID do PDF/IA para permitir upsert sem duplicação';
COMMENT ON COLUMN competition_phases.is_olympic_cross IS 'Se é cruzamento olímpico (1ºA x 2ºB)';

-- ============================================================================
-- 8. Migrar dados existentes (se houver) - Definir valores padrão
-- ============================================================================
UPDATE competitions 
SET 
    status = 'active',
    competition_type = 'custom',
    season = EXTRACT(YEAR FROM created_at)::VARCHAR
WHERE status IS NULL;

-- ============================================================================
-- FIM DA MIGRATION
-- ============================================================================
