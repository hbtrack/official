-- Migration: Criar tabela team_memberships
-- Data: 2026-01-06
-- Objetivo: Vincular staff (coordenadores/treinadores) a equipes específicas

-- Criar tabela team_memberships
CREATE TABLE IF NOT EXISTS team_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    org_membership_id UUID REFERENCES org_memberships(id) ON DELETE SET NULL,
    start_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    end_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'pendente' CHECK (status IN ('pendente', 'ativo', 'inativo')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ,
    deleted_reason TEXT
);

-- Índices para performance
CREATE INDEX idx_team_memberships_person_id ON team_memberships(person_id);
CREATE INDEX idx_team_memberships_team_id ON team_memberships(team_id);
CREATE INDEX idx_team_memberships_org_membership_id ON team_memberships(org_membership_id);
CREATE INDEX idx_team_memberships_status ON team_memberships(status);

-- Índice para buscar vínculos ativos de uma equipe
CREATE INDEX idx_team_memberships_team_active ON team_memberships(team_id, status) 
WHERE deleted_at IS NULL AND end_at IS NULL;

-- Índice único para evitar duplicatas (pessoa+equipe ativo)
CREATE UNIQUE INDEX idx_team_memberships_person_team_active 
ON team_memberships(person_id, team_id) 
WHERE deleted_at IS NULL AND end_at IS NULL AND status IN ('pendente', 'ativo');

-- Comentários
COMMENT ON TABLE team_memberships IS 'Vínculo de staff (coordenadores/treinadores) com equipes específicas';
COMMENT ON COLUMN team_memberships.status IS 'Status do vínculo: pendente (aguardando aceitação), ativo, inativo';
COMMENT ON COLUMN team_memberships.org_membership_id IS 'Referência ao cargo organizacional (OrgMembership)';
