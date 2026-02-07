-- Migration: Criar VIEW v_seasons_with_status
-- Data: 2026-01-08
-- Descrição: VIEW que calcula status derivado das temporadas conforme 6.1.1
-- Referência: app/models/season.py (property status)

-- Drop se existir (para idempotência)
DROP VIEW IF EXISTS v_seasons_with_status;

-- Criar a VIEW
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
    -- Status derivado conforme regra 6.1.1
    -- Prioridade: cancelada > interrompida > encerrada > ativa > planejada
    CASE
        WHEN s.canceled_at IS NOT NULL THEN 'cancelada'
        WHEN s.interrupted_at IS NOT NULL THEN 'interrompida'
        WHEN s.end_date < CURRENT_DATE THEN 'encerrada'
        WHEN s.start_date <= CURRENT_DATE AND CURRENT_DATE <= s.end_date THEN 'ativa'
        ELSE 'planejada'
    END AS status
FROM seasons s
WHERE s.deleted_at IS NULL;

-- Comentário da VIEW
COMMENT ON VIEW v_seasons_with_status IS 'VIEW de temporadas com status derivado calculado (6.1.1). Status: planejada, ativa, interrompida, cancelada, encerrada';
