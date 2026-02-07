\set ON_ERROR_STOP 1

\echo ==== SMOKE START
\echo INFO: session_timezone will be forced to UTC for deterministic tests
SET TIME ZONE 'UTC';

-- CHK-0001: versao do Postgres
DO $$
BEGIN
  IF current_setting('server_version_num')::int < 130000 THEN
    RAISE EXCEPTION 'CHK-0001: PostgreSQL >= 13 exigido; atual %', current_setting('server_version');
  END IF;
  RAISE NOTICE 'CHK-0001: OK (server_version=%)', current_setting('server_version');
END $$;

-- CHK-0002A: sessao em UTC (deterministico)
DO $$
BEGIN
  IF current_setting('TimeZone') <> 'UTC' THEN
    RAISE EXCEPTION 'CHK-0002A: session TimeZone deve ser UTC; atual %', current_setting('TimeZone');
  END IF;
  RAISE NOTICE 'CHK-0002A: OK (session TimeZone=UTC)';
END $$;

-- CHK-0002B: default do servidor/banco (informativo)
DO $$
DECLARE v_setting text; v_source text;
BEGIN
  SELECT setting, source INTO v_setting, v_source
  FROM pg_settings WHERE name='TimeZone';

  IF v_setting <> 'UTC' THEN
    RAISE NOTICE 'CHK-0002B: ATENCAO (pg_settings TimeZone=% source=%). Smoke usa sessao UTC mesmo assim.', v_setting, v_source;
  ELSE
    RAISE NOTICE 'CHK-0002B: OK (pg_settings TimeZone=UTC source=%)', v_source;
  END IF;
END $$;

-- CHK-0003: extensoes
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname='pgcrypto') THEN
    RAISE EXCEPTION 'CHK-0003: extensao pgcrypto ausente';
  END IF;
  RAISE NOTICE 'CHK-0003: OK (pgcrypto presente)';
END $$;

-- CHK-0004: alembic_version existe e tem 1 linha; opcional EXPECTED_HEAD
DO $$
DECLARE v_total int; v_head text;
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema='public' AND table_name='alembic_version'
  ) THEN
    RAISE EXCEPTION 'CHK-0004: tabela alembic_version ausente';
  END IF;

  SELECT count(*) INTO v_total FROM public.alembic_version;
  IF v_total <> 1 THEN
    RAISE EXCEPTION 'CHK-0004: alembic_version deve ter exatamente 1 linha; atual %', v_total;
  END IF;

  SELECT version_num INTO v_head FROM public.alembic_version LIMIT 1;
  RAISE NOTICE 'CHK-0004: OK (single row, head=%)', v_head;
END $$;

\if :{?EXPECTED_HEAD}
SELECT set_config('smoke.expected_head', :'EXPECTED_HEAD', false) \gset
DO $$
DECLARE
  v_expected text := current_setting('smoke.expected_head', true);
  v_current  text;
BEGIN
  SELECT version_num INTO v_current FROM alembic_version;
  IF v_current IS DISTINCT FROM v_expected THEN
    RAISE EXCEPTION 'CHK-0004B: head esperado %, atual %', v_expected, v_current;
  END IF;
  RAISE NOTICE 'CHK-0004B: OK (expected=%)', v_expected;
END $$;
\endif
-- CHK-0005: tabelas essenciais
DO $$
DECLARE v_missing text[];
BEGIN
  SELECT array_agg(name) INTO v_missing
  FROM (VALUES
    ('audit_logs'),
    ('persons'),
    ('users'),
    ('roles'),
    ('permissions'),
    ('role_permissions'),
    ('organizations'),
    ('membership'),
    ('athletes'),
    ('athlete_states'),
    ('medical_cases'),
    ('training_sessions'),
    ('attendance'),
    ('wellness_pre'),
    ('wellness_post'),
    ('seasons'),
    ('categories'),
    ('teams'),
    ('team_registrations'),
    ('competitions'),
    ('competition_seasons'),
    ('matches'),
    ('match_teams'),
    ('match_roster'),
    ('match_events')
  ) AS expected(name)
  WHERE NOT EXISTS (
    SELECT 1
    FROM information_schema.tables t
    WHERE t.table_schema='public' AND t.table_name=expected.name
  );

  IF v_missing IS NOT NULL THEN
    RAISE EXCEPTION 'CHK-0005: tabelas ausentes %', v_missing;
  END IF;
  RAISE NOTICE 'CHK-0005: OK';
END $$;

-- CHK-0006: views essenciais
DO $$
DECLARE v_missing text[];
BEGIN
  SELECT array_agg(name) INTO v_missing
  FROM (VALUES
    ('v_session_athlete_dashboard'),
    ('v_training_session_summary')
  ) AS expected(name)
  WHERE NOT EXISTS (
    SELECT 1
    FROM information_schema.views v
    WHERE v.table_schema='public' AND v.table_name=expected.name
  );

  IF v_missing IS NOT NULL THEN
    RAISE EXCEPTION 'CHK-0006: views ausentes %', v_missing;
  END IF;
  RAISE NOTICE 'CHK-0006: OK';
END $$;

-- CHK-0007: funcoes essenciais (existencia)
DO $$
DECLARE v_missing text[];
BEGIN
  SELECT array_agg(proname) INTO v_missing
  FROM (VALUES
    ('set_updated_at'),
    ('set_internal_load_wellness_post'),
    ('age_in_years'),
    ('log_audit_event'),
    ('block_delete'),
    ('ensure_active_membership'),
    ('ensure_user_active_membership')
  ) AS expected(proname)
  WHERE NOT EXISTS (
    SELECT 1
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid=p.pronamespace
    WHERE n.nspname='public' AND p.proname=expected.proname
  );

  IF v_missing IS NOT NULL THEN
    RAISE EXCEPTION 'CHK-0007: funcoes ausentes %', v_missing;
  END IF;
  RAISE NOTICE 'CHK-0007: OK';
END $$;

-- CHK-0008: triggers updated_at (existencia)
DO $$
DECLARE v_missing text[];
BEGIN
  SELECT array_agg(format('%s.%s', tbl, trg)) INTO v_missing
  FROM (VALUES
    ('users', 'trg_users_updated_at'),
    ('organizations', 'trg_organizations_updated_at'),
    ('membership', 'trg_membership_updated_at'),
    ('athletes', 'trg_athletes_updated_at'),
    ('training_sessions', 'trg_training_sessions_updated_at'),
    ('attendance', 'trg_attendance_updated_at'),
    ('wellness_pre', 'trg_wellness_pre_updated_at'),
    ('wellness_post', 'trg_wellness_post_updated_at'),
    ('seasons', 'trg_seasons_updated_at'),
    ('categories', 'trg_categories_updated_at'),
    ('teams', 'trg_teams_updated_at'),
    ('matches', 'trg_matches_updated_at')
  ) AS expected(tbl, trg)
  WHERE NOT EXISTS (
    SELECT 1
    FROM pg_trigger tg
    JOIN pg_class c ON c.oid=tg.tgrelid
    JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='public'
      AND c.relname=expected.tbl
      AND tg.tgname=expected.trg
      AND NOT tg.tgisinternal
  );

  IF v_missing IS NOT NULL THEN
    RAISE EXCEPTION 'CHK-0008: triggers updated_at ausentes %', v_missing;
  END IF;
  RAISE NOTICE 'CHK-0008: OK';
END $$;

-- CHK-0009: triggers soft delete + imutabilidade audit_logs (existencia)
DO $$
DECLARE v_missing text[];
BEGIN
  SELECT array_agg(format('%s.%s', tbl, trg)) INTO v_missing
  FROM (VALUES
    ('audit_logs', 'trg_audit_logs_immutable'),
    ('matches', 'trg_soft_delete_matches'),
    ('training_sessions', 'trg_soft_delete_training'),
    ('persons', 'trg_soft_delete_persons'),
    ('athletes', 'trg_soft_delete_athletes'),
    ('membership', 'trg_soft_delete_membership')
  ) AS expected(tbl, trg)
  WHERE NOT EXISTS (
    SELECT 1
    FROM pg_trigger tg
    JOIN pg_class c ON c.oid=tg.tgrelid
    JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='public'
      AND c.relname=expected.tbl
      AND tg.tgname=expected.trg
      AND NOT tg.tgisinternal
  );

  IF v_missing IS NOT NULL THEN
    RAISE EXCEPTION 'CHK-0009: triggers soft delete/imutabilidade ausentes %', v_missing;
  END IF;
  RAISE NOTICE 'CHK-0009: OK';
END $$;

-- CHK-0010: sem constraints NOT VALID
DO $$
DECLARE v_not_valid text[];
BEGIN
  SELECT array_agg(conname) INTO v_not_valid
  FROM pg_constraint c
  JOIN pg_namespace n ON n.oid=c.connamespace
  WHERE n.nspname='public' AND NOT c.convalidated;

  IF v_not_valid IS NOT NULL THEN
    RAISE EXCEPTION 'CHK-0010: constraints NOT VALID %', v_not_valid;
  END IF;
  RAISE NOTICE 'CHK-0010: OK';
END $$;

-- CHK-0011: sanity gen_random_uuid()
DO $$
DECLARE v_ok boolean;
BEGIN
  SELECT (gen_random_uuid() IS NOT NULL) INTO v_ok;
  IF NOT v_ok THEN
    RAISE EXCEPTION 'CHK-0011: gen_random_uuid() falhou';
  END IF;
  RAISE NOTICE 'CHK-0011: OK';
END $$;

\echo ==== SMOKE OK


