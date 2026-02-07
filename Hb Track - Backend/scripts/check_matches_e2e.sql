-- Query para verificar matches da equipe E2E
SELECT 
    id, 
    match_date,
    TO_CHAR(start_time, 'HH24:MI:SS') as match_time,
    notes as opponent_name,
    status,
    venue as location,
    CASE 
        WHEN match_date < CURRENT_DATE THEN 'PASSADO (' || (CURRENT_DATE - match_date) || ' dias atrás)'
        WHEN match_date = CURRENT_DATE THEN 'HOJE'
        ELSE 'FUTURO (+' || (match_date - CURRENT_DATE) || ' dias)'
    END as timing,
    deleted_at
FROM matches 
WHERE our_team_id = '88888888-8888-8888-8884-000000000001'
ORDER BY match_date;
