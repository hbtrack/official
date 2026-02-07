-- ============================================================================
-- SCRIPT: Reset do Banco para Ambiente de Produção Simulado (Soft Delete)
-- Objetivo: Manter apenas 1 organização e o superadmin admin@hbtracking.com
-- Data: 2026-01-06
-- ATENÇÃO: Este script faz soft delete em massa. Revise antes de rodar.
-- ============================================================================

BEGIN;

-- Identificar o superadmin
SELECT id, email, is_superadmin, person_id FROM users WHERE email = 'admin@hbtracking.com';

-- ---------------------------------------------------------------------------
-- Soft delete de dados relacionados (ordem importa)
-- ---------------------------------------------------------------------------

-- Treinos
UPDATE training_sessions
SET deleted_at = NOW(), deleted_reason = 'reset_to_production'
WHERE deleted_at IS NULL;

-- Focos de treino (se existir)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'training_focus') THEN
        EXECUTE 'UPDATE training_focus SET deleted_at = NOW(), deleted_reason = ''reset_to_production'' WHERE deleted_at IS NULL';
    END IF;
END $$;

-- Registros e memberships de equipe
UPDATE team_registrations
SET deleted_at = NOW(), deleted_reason = 'reset_to_production'
WHERE deleted_at IS NULL;

UPDATE team_memberships
SET deleted_at = NOW(), deleted_reason = 'reset_to_production'
WHERE deleted_at IS NULL;

-- Password resets (delete físico se permitido)
DELETE FROM password_resets;

-- Atletas e equipes
UPDATE athletes
SET deleted_at = NOW(), deleted_reason = 'reset_to_production'
WHERE deleted_at IS NULL;

UPDATE teams
SET deleted_at = NOW(), deleted_reason = 'reset_to_production'
WHERE deleted_at IS NULL;

-- Org memberships (exceto do superadmin)
UPDATE org_memberships
SET deleted_at = NOW(), deleted_reason = 'reset_to_production'
WHERE person_id NOT IN (
    SELECT person_id FROM users WHERE email = 'admin@hbtracking.com' AND person_id IS NOT NULL
)
AND deleted_at IS NULL;

-- Contatos de pessoas (exceto do superadmin)
UPDATE person_contacts
SET deleted_at = NOW(), deleted_reason = 'reset_to_production'
WHERE person_id NOT IN (
    SELECT person_id FROM users WHERE email = 'admin@hbtracking.com' AND person_id IS NOT NULL
)
AND deleted_at IS NULL;

-- Usuários (exceto superadmin)
UPDATE users
SET deleted_at = NOW(), deleted_reason = 'reset_to_production'
WHERE email != 'admin@hbtracking.com' AND deleted_at IS NULL;

-- Pessoas (exceto superadmin)
UPDATE persons
SET deleted_at = NOW(), deleted_reason = 'reset_to_production'
WHERE id NOT IN (
    SELECT person_id FROM users WHERE email = 'admin@hbtracking.com' AND person_id IS NOT NULL
)
AND deleted_at IS NULL;

-- ---------------------------------------------------------------------------
-- Organização principal: cria se não existir, atualiza se existir, soft delete demais
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    main_org_id UUID;
    admin_person_id UUID;
BEGIN
    SELECT person_id INTO admin_person_id FROM users WHERE email = 'admin@hbtracking.com';

    -- Buscar uma organização ativa
    SELECT id INTO main_org_id FROM organizations WHERE deleted_at IS NULL LIMIT 1;

    IF main_org_id IS NULL THEN
        INSERT INTO organizations (name)
        VALUES ('HB Track Clube')
        RETURNING id INTO main_org_id;
    ELSE
        UPDATE organizations
        SET name = 'HB Track Clube'
        WHERE id = main_org_id;
    END IF;

    -- Soft delete das demais organizações
    UPDATE organizations
    SET deleted_at = NOW(), deleted_reason = 'reset_to_production'
    WHERE id != main_org_id AND deleted_at IS NULL;

    -- Garantir membership do admin
    IF admin_person_id IS NOT NULL THEN
        INSERT INTO org_memberships (person_id, organization_id, role_id, start_at)
        SELECT admin_person_id, main_org_id, 1, NOW()
        WHERE NOT EXISTS (
            SELECT 1 FROM org_memberships
            WHERE person_id = admin_person_id AND organization_id = main_org_id AND deleted_at IS NULL
        );
    END IF;

    RAISE NOTICE 'Organização principal: %', main_org_id;
END $$;

-- ---------------------------------------------------------------------------
-- Verificações
-- ---------------------------------------------------------------------------

SELECT 'Organizacoes' as tabela, COUNT(*) as total FROM organizations WHERE deleted_at IS NULL
UNION ALL
SELECT 'Usuarios', COUNT(*) FROM users WHERE deleted_at IS NULL
UNION ALL
SELECT 'Pessoas', COUNT(*) FROM persons WHERE deleted_at IS NULL
UNION ALL
SELECT 'Equipes', COUNT(*) FROM teams WHERE deleted_at IS NULL
UNION ALL
SELECT 'Atletas', COUNT(*) FROM athletes WHERE deleted_at IS NULL
UNION ALL
SELECT 'Treinos', COUNT(*) FROM training_sessions WHERE deleted_at IS NULL;

SELECT 
    u.email,
    u.is_superadmin,
    p.full_name,
    o.name as organizacao
FROM users u
LEFT JOIN persons p ON u.person_id = p.id
LEFT JOIN org_memberships om ON p.id = om.person_id AND om.deleted_at IS NULL
LEFT JOIN organizations o ON om.organization_id = o.id AND o.deleted_at IS NULL
WHERE u.deleted_at IS NULL;

COMMIT;

-- Para reverter (antes do COMMIT): ROLLBACK;
