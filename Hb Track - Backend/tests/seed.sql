BEGIN;
SET LOCAL timezone TO 'UTC';
SET CONSTRAINTS ALL DEFERRED;

DO $$
DECLARE
  v_role_dirigente smallint;
  v_category_id int;
BEGIN
  SELECT id INTO v_role_dirigente FROM roles WHERE code = 'dirigente';
  IF v_role_dirigente IS NULL THEN
    RAISE EXCEPTION 'Seed abortado: role dirigente ausente';
  END IF;

  -- Pessoa e usuaria base
  INSERT INTO persons (id, full_name, birth_date)
  VALUES ('11111111-1111-1111-1111-111111111111', 'Seed Admin', NULL)
  ON CONFLICT DO NOTHING;

  INSERT INTO users (id, email, full_name, person_id, is_superadmin, status)
  VALUES (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'seed.admin@example.com',
    'Seed Admin',
    '11111111-1111-1111-1111-111111111111',
    false,
    'ativo'
  )
  ON CONFLICT DO NOTHING;

  -- Organizacao e temporada base
  INSERT INTO organizations (id, name, owner_user_id)
  VALUES (
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'Seed Org',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
  )
  ON CONFLICT DO NOTHING;

  INSERT INTO seasons (id, organization_id, created_by_membership_id, year, name, starts_at, ends_at, is_active)
  VALUES (
    'dddddddd-dddd-dddd-dddd-dddddddddddd',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    2025,
    'Temporada Seed 2025',
    DATE '2025-01-01',
    DATE '2025-12-31',
    true
  )
  ON CONFLICT DO NOTHING;

  INSERT INTO membership (id, organization_id, user_id, person_id, role_id, season_id, status, start_date)
  VALUES (
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '11111111-1111-1111-1111-111111111111',
    v_role_dirigente,
    'dddddddd-dddd-dddd-dddd-dddddddddddd',
    'ativo',
    current_date
  )
  ON CONFLICT DO NOTHING;

  -- Categoria e time base
  INSERT INTO categories (code, label, min_age, max_age)
  VALUES ('U99', 'Seed Categoria', 0, 99)
  ON CONFLICT DO NOTHING;

  SELECT id INTO v_category_id FROM categories WHERE code = 'U99';
  IF v_category_id IS NULL THEN
    RAISE EXCEPTION 'Seed abortado: categoria U99 nao encontrada';
  END IF;

  INSERT INTO teams (id, organization_id, created_by_membership_id, season_id, category_id, name)
  VALUES (
    'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    'dddddddd-dddd-dddd-dddd-dddddddddddd',
    v_category_id,
    'Seed Team'
  )
  ON CONFLICT DO NOTHING;

  -- Atleta base e vinculacao
  INSERT INTO persons (id, full_name, birth_date)
  VALUES ('22222222-2222-2222-2222-222222222222', 'Seed Athlete', DATE '2010-01-01')
  ON CONFLICT DO NOTHING;

  INSERT INTO athletes (id, organization_id, created_by_membership_id, person_id, full_name, birth_date, position, state)
  VALUES (
    'ffffffff-ffff-ffff-ffff-ffffffffffff',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    '22222222-2222-2222-2222-222222222222',
    'Seed Athlete',
    DATE '2010-01-01',
    'pivo',
    'ativa'
  )
  ON CONFLICT DO NOTHING;

  INSERT INTO team_registrations (id, athlete_id, season_id, category_id, team_id, organization_id, created_by_membership_id, role)
  VALUES (
    '99999999-9999-9999-9999-999999999999',
    'ffffffff-ffff-ffff-ffff-ffffffffffff',
    'dddddddd-dddd-dddd-dddd-dddddddddddd',
    v_category_id,
    'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    'atleta'
  )
  ON CONFLICT DO NOTHING;
END $$;

COMMIT;
