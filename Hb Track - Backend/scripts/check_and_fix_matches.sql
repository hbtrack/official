-- Script para verificar e corrigir matches E2E

-- 1. Ver todos os matches da equipe E2E
SELECT 
    id, 
    match_date, 
    match_time,
    status, 
    phase,
    venue as location,
    final_score_home,
    final_score_away,
    CASE 
        WHEN match_date < CURRENT_DATE THEN 'PASSADO'
        WHEN match_date = CURRENT_DATE THEN 'HOJE'
        ELSE 'FUTURO (' || (match_date - CURRENT_DATE) || ' dias)'
    END as timing
FROM matches 
WHERE our_team_id = '88888888-8888-8888-8884-000000000001'
ORDER BY match_date;

-- 2. Deletar matches E2E antigos para permitir reinserção
DELETE FROM matches 
WHERE our_team_id = '88888888-8888-8888-8884-000000000001';

-- 3. Inserir matches com datas futuras corretas
INSERT INTO matches (
    id, season_id, match_date, match_time, home_team_id, away_team_id,
    our_team_id, phase, status, venue,
    final_score_home, final_score_away,
    created_by_user_id, created_at, updated_at
) VALUES 
-- Match 1: Passado/Finalizado (não deve aparecer)
(
    '88888888-8888-8888-8885-100000000001',
    '88888888-8888-8888-8888-000000000010',
    CURRENT_DATE - INTERVAL '4 days',
    '14:00:00',
    '88888888-8888-8888-8884-000000000001',
    '88888888-8888-8888-8885-000000000011',
    '88888888-8888-8888-8884-000000000001',
    'friendly',
    'finished',
    'Campo E2E',
    3,
    1,
    '88888888-8888-8888-8881-000000000001',
    NOW(),
    NOW()
),
-- Match 2: Futuro +6 dias (deve aparecer)
(
    '88888888-8888-8888-8885-100000000002',
    '88888888-8888-8888-8888-000000000010',
    CURRENT_DATE + INTERVAL '6 days',
    '16:30:00',
    '88888888-8888-8888-8885-000000000012',
    '88888888-8888-8888-8884-000000000001',
    '88888888-8888-8888-8884-000000000001',
    'group',
    'scheduled',
    'Arena Adversário B',
    NULL,
    NULL,
    '88888888-8888-8888-8881-000000000001',
    NOW(),
    NOW()
),
-- Match 3: Futuro +30 dias (deve aparecer)
(
    '88888888-8888-8888-8885-100000000003',
    '88888888-8888-8888-8888-000000000010',
    CURRENT_DATE + INTERVAL '30 days',
    '18:00:00',
    '88888888-8888-8888-8884-000000000001',
    '88888888-8888-8888-8885-000000000013',
    '88888888-8888-8888-8884-000000000001',
    'friendly',
    'scheduled',
    'Campo E2E',
    NULL,
    NULL,
    '88888888-8888-8888-8881-000000000001',
    NOW(),
    NOW()
);

-- 4. Verificar resultado final
SELECT 
    id, 
    match_date, 
    match_time,
    status, 
    phase,
    venue as location,
    CASE 
        WHEN match_date < CURRENT_DATE THEN 'PASSADO'
        WHEN match_date = CURRENT_DATE THEN 'HOJE'
        ELSE 'FUTURO +' || (match_date - CURRENT_DATE) || ' dias'
    END as timing
FROM matches 
WHERE our_team_id = '88888888-8888-8888-8884-000000000001'
ORDER BY match_date;
