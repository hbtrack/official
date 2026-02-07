-- Índices para otimização de performance na tabela teams
-- Melhoram drasticamente queries de listagem e filtros

-- Índice para filtro por organização (filtro mais comum)
CREATE INDEX IF NOT EXISTS idx_teams_organization_id 
ON teams(organization_id);

-- Índice para ordenação por data de atualização
CREATE INDEX IF NOT EXISTS idx_teams_updated_at 
ON teams(updated_at DESC);

-- Índice para filtro de equipes ativas/arquivadas
CREATE INDEX IF NOT EXISTS idx_teams_is_active 
ON teams(is_active);

-- Índice composto para queries que filtram por organização e ordenam por data
CREATE INDEX IF NOT EXISTS idx_teams_org_updated 
ON teams(organization_id, updated_at DESC);

-- Índice composto para filtrar por organização e status ativo
CREATE INDEX IF NOT EXISTS idx_teams_org_active 
ON teams(organization_id, is_active, updated_at DESC);

-- Comentários para documentação
COMMENT ON INDEX idx_teams_organization_id IS 'Acelera filtros por organização';
COMMENT ON INDEX idx_teams_updated_at IS 'Acelera ordenação por data de atualização';
COMMENT ON INDEX idx_teams_is_active IS 'Acelera filtros de equipes ativas/arquivadas';
COMMENT ON INDEX idx_teams_org_updated IS 'Otimiza listagem paginada por organização';
COMMENT ON INDEX idx_teams_org_active IS 'Otimiza filtros combinados (org + status)';
