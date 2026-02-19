BEGIN;
SET LOCAL timezone TO 'UTC';
SET CONSTRAINTS ALL DEFERRED;

DO $$
DECLARE
  v_role_dirigente smallint;
  v_category_id int;
  v_team_id uuid := 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee';
  v_season_id uuid := 'dddddddd-dddd-dddd-dddd-dddddddddddd';
BEGIN
  -- Get dirigente role
  SELECT id INTO v_role_dirigente FROM roles WHERE code = 'dirigente';
  IF v_role_dirigente IS NULL THEN
    RAISE EXCEPTION 'Seed abortado: role dirigente ausente';
  END IF;

  -- 1. Person and User (base identity)
  INSERT INTO persons (id, full_name, first_name, last_name, birth_date)
  VALUES ('11111111-1111-1111-1111-111111111111', 'Seed Admin', 'Seed', 'Admin', NULL)
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO users (id, email, person_id, is_superadmin, status)
  VALUES (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'seed.admin@example.com',
    '11111111-1111-1111-1111-111111111111',
    false,
    'ativo'
  )
  ON CONFLICT (id) DO NOTHING;

  -- 2. Organization
  INSERT INTO organizations (id, name)
  VALUES (
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'Seed Org'
  )
  ON CONFLICT (id) DO NOTHING;

  -- 3. Membership (user in organization)
  INSERT INTO org_memberships (id, organization_id, person_id, role_id, start_at)
  VALUES (
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    '11111111-1111-1111-1111-111111111111',
    v_role_dirigente,
    current_timestamp
  )
  ON CONFLICT (id) DO NOTHING;

  -- 4. Category (use existing or create simple one)
  -- Try to get first available category
  SELECT id INTO v_category_id FROM categories WHERE is_active = true LIMIT 1;
  
  -- If no category exists, create one
  IF v_category_id IS NULL THEN
    INSERT INTO categories (name, max_age, is_active)
    VALUES ('Seed Category', 99, true)
    RETURNING id INTO v_category_id;
  END IF;

  -- 5. Team (without season_id first - circular dependency)
  INSERT INTO teams (
    id, 
    organization_id, 
    name, 
    category_id, 
    gender, 
    is_our_team,
    created_by_user_id
  )
  VALUES (
    v_team_id,
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'Seed Team',
    v_category_id,
    'masculino',
    true,
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
  )
  ON CONFLICT (id) DO NOTHING;

  -- 6. Season (belongs to team)
  INSERT INTO seasons (
    id, 
    team_id, 
    name, 
    year, 
    start_date, 
    end_date,
    created_by_user_id
  )
  VALUES (
    v_season_id,
    v_team_id,
    'Temporada Seed 2025',
    2025,
    DATE '2025-01-01',
    DATE '2025-12-31',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
  )
  ON CONFLICT (id) DO NOTHING;

  -- 7. Update team to link to season (circular dependency resolved)
  UPDATE teams 
  SET season_id = v_season_id
  WHERE id = v_team_id AND season_id IS NULL;

  -- 8. Athlete (Person + Athlete)
  INSERT INTO persons (id, full_name, first_name, last_name, birth_date)
  VALUES ('22222222-2222-2222-2222-222222222222', 'Seed Athlete', 'Seed', 'Athlete', DATE '2010-01-01')
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO athletes (
    id, 
    person_id, 
    athlete_name,
    birth_date, 
    state
  )
  VALUES (
    'ffffffff-ffff-ffff-ffff-ffffffffffff',
    '22222222-2222-2222-2222-222222222222',
    'Seed Athlete',
    DATE '2010-01-01',
    'ativa'
  )
  ON CONFLICT (id) DO NOTHING;

  -- 9. Team Registration (athlete in team)
  INSERT INTO team_registrations (
    id, 
    athlete_id, 
    team_id, 
    start_at
  )
  VALUES (
    '99999999-9999-9999-9999-999999999999',
    'ffffffff-ffff-ffff-ffff-ffffffffffff',
    v_team_id,
    current_timestamp
  )
  ON CONFLICT (id) DO NOTHING;

END $$;

COMMIT;
