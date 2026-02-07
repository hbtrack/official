BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> fc3abb97b24a

INSERT INTO alembic_version (version_num) VALUES ('fc3abb97b24a') RETURNING alembic_version.version_num;

-- Running upgrade fc3abb97b24a -> f04026216180

-- 1) UUID (se ainda n�o tiver)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2) helper para updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

-- 3) atletas
CREATE TABLE IF NOT EXISTS athletes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL,
  created_by_membership_id uuid NOT NULL,
  full_name text NOT NULL,
  nickname text,
  birth_date date,
  position text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS trg_athletes_updated_at ON athletes;
CREATE TRIGGER trg_athletes_updated_at
BEFORE UPDATE ON athletes
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 4) sess�es de treino
CREATE TABLE IF NOT EXISTS training_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL,
  created_by_membership_id uuid NOT NULL,
  session_at timestamptz NOT NULL,
  main_objective text,
  planned_load int,          -- ex: carga planejada (0-10 ou outra escala)
  actual_load_avg int,       -- ex: m�dia realizada
  group_climate int,         -- ex: 1-5
  highlight text,
  next_corrections text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS trg_training_sessions_updated_at ON training_sessions;
CREATE TRIGGER trg_training_sessions_updated_at
BEFORE UPDATE ON training_sessions
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 5) presen�a + p�s-treino (carga interna)
CREATE TABLE IF NOT EXISTS attendance (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid NOT NULL REFERENCES training_sessions(id) ON DELETE CASCADE,
  athlete_id uuid NOT NULL REFERENCES athletes(id) ON DELETE CASCADE,
  organization_id uuid NOT NULL,
  created_by_membership_id uuid NOT NULL,
  status text NOT NULL CHECK (status IN ('presente','ausente','medico','lesionada')),
  rpe int CHECK (rpe BETWEEN 0 AND 10),
  internal_load int,         -- ex: rpe * minutos (se voc� usar)
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS trg_attendance_updated_at ON attendance;
CREATE TRIGGER trg_attendance_updated_at
BEFORE UPDATE ON attendance
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE INDEX IF NOT EXISTS idx_attendance_session ON attendance(session_id);
CREATE INDEX IF NOT EXISTS idx_attendance_athlete ON attendance(athlete_id);
CREATE INDEX IF NOT EXISTS idx_athletes_org ON athletes(organization_id);
CREATE INDEX IF NOT EXISTS idx_athletes_created_by_membership ON athletes(created_by_membership_id);
CREATE INDEX IF NOT EXISTS idx_training_sessions_org ON training_sessions(organization_id);
CREATE INDEX IF NOT EXISTS idx_training_sessions_created_by_membership ON training_sessions(created_by_membership_id);
CREATE INDEX IF NOT EXISTS idx_attendance_org ON attendance(organization_id);
CREATE INDEX IF NOT EXISTS idx_attendance_created_by_membership ON attendance(created_by_membership_id);;

UPDATE alembic_version SET version_num='f04026216180' WHERE alembic_version.version_num = 'fc3abb97b24a';

-- Running upgrade f04026216180 -> 9337cde7fe9e

-- wellness pr�-treino: 1 registro por atleta por sess�o

    CREATE TABLE IF NOT EXISTS wellness_pre (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

      session_id uuid NOT NULL REFERENCES training_sessions(id) ON DELETE CASCADE,
      athlete_id uuid NOT NULL REFERENCES athletes(id) ON DELETE CASCADE,
      organization_id uuid NOT NULL,
      created_by_membership_id uuid NOT NULL,

      sleep_hours numeric(4,1) CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
      sleep_quality int CHECK (sleep_quality BETWEEN 1 AND 5),

      fatigue int CHECK (fatigue BETWEEN 0 AND 10),
      stress int CHECK (stress BETWEEN 0 AND 10),
      muscle_soreness int CHECK (muscle_soreness BETWEEN 0 AND 10),

      pain boolean NOT NULL DEFAULT false,
      pain_level int CHECK (pain_level BETWEEN 0 AND 10),
      pain_location text,

      notes text,

      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    -- trigger updated_at (reaplic�vel)
    DROP TRIGGER IF EXISTS trg_wellness_pre_updated_at ON wellness_pre;

    CREATE TRIGGER trg_wellness_pre_updated_at
    BEFORE UPDATE ON wellness_pre
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

    CREATE INDEX IF NOT EXISTS idx_wellness_pre_session ON wellness_pre(session_id);
    CREATE INDEX IF NOT EXISTS idx_wellness_pre_athlete ON wellness_pre(athlete_id);
    CREATE INDEX IF NOT EXISTS idx_wellness_pre_org ON wellness_pre(organization_id);
    CREATE INDEX IF NOT EXISTS idx_wellness_pre_created_by_membership ON wellness_pre(created_by_membership_id);;

UPDATE alembic_version SET version_num='9337cde7fe9e' WHERE alembic_version.version_num = 'f04026216180';

-- Running upgrade 9337cde7fe9e -> ace919bc9d4f

CREATE TABLE IF NOT EXISTS wellness_post (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

      session_id uuid NOT NULL REFERENCES training_sessions(id) ON DELETE CASCADE,
      athlete_id uuid NOT NULL REFERENCES athletes(id) ON DELETE CASCADE,
      organization_id uuid NOT NULL,
      created_by_membership_id uuid NOT NULL,

      minutes int CHECK (minutes >= 0 AND minutes <= 300),

      rpe int CHECK (rpe BETWEEN 0 AND 10),

      -- voc� pode preencher manualmente OU calcular no app/consulta
      internal_load int CHECK (internal_load >= 0),

      fatigue_after int CHECK (fatigue_after BETWEEN 0 AND 10),
      mood_after int CHECK (mood_after BETWEEN 0 AND 10),

      notes text,

      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    DROP TRIGGER IF EXISTS trg_wellness_post_updated_at ON wellness_post;

    CREATE TRIGGER trg_wellness_post_updated_at
    BEFORE UPDATE ON wellness_post
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

    CREATE INDEX IF NOT EXISTS idx_wellness_post_session ON wellness_post(session_id);
    CREATE INDEX IF NOT EXISTS idx_wellness_post_athlete ON wellness_post(athlete_id);
    CREATE INDEX IF NOT EXISTS idx_wellness_post_org ON wellness_post(organization_id);
    CREATE INDEX IF NOT EXISTS idx_wellness_post_created_by_membership ON wellness_post(created_by_membership_id);

    CREATE OR REPLACE FUNCTION set_internal_load_wellness_post()
    RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.minutes IS NOT NULL AND NEW.rpe IS NOT NULL THEN
        NEW.internal_load := NEW.minutes * NEW.rpe;
      END IF;
      RETURN NEW;
    END;
    $$;

    DROP TRIGGER IF EXISTS trg_wellness_post_internal_load ON wellness_post;

    CREATE TRIGGER trg_wellness_post_internal_load
    BEFORE INSERT OR UPDATE ON wellness_post
    FOR EACH ROW EXECUTE FUNCTION set_internal_load_wellness_post();;

UPDATE alembic_version SET version_num='ace919bc9d4f' WHERE alembic_version.version_num = '9337cde7fe9e';

-- Running upgrade ace919bc9d4f -> ae379329cc50

-- 1) Migra dados existentes (se houver) de attendance -> wellness_post
    -- s� insere se n�o existir ainda um wellness_post para (session_id, athlete_id)
    INSERT INTO wellness_post (
      session_id,
      athlete_id,
      organization_id,
      created_by_membership_id,
      rpe,
      internal_load,
      notes
    )
    SELECT
      a.session_id,
      a.athlete_id,
      a.organization_id,
      a.created_by_membership_id,
      a.rpe,
      a.internal_load,
      a.notes
      FROM attendance a
     WHERE (a.rpe IS NOT NULL OR a.internal_load IS NOT NULL)
       AND NOT EXISTS (
           SELECT 1
             FROM wellness_post wp
            WHERE wp.session_id = a.session_id
              AND wp.athlete_id = a.athlete_id
       );

    -- 2) Remove as colunas da attendance (agora ela fica s� presen�a)
    ALTER TABLE attendance DROP COLUMN IF EXISTS rpe;
    ALTER TABLE attendance DROP COLUMN IF EXISTS internal_load;;

UPDATE alembic_version SET version_num='ae379329cc50' WHERE alembic_version.version_num = 'ace919bc9d4f';

-- Running upgrade ae379329cc50 -> a295501fa7f4

DROP VIEW IF EXISTS v_session_athlete_dashboard;
    CREATE VIEW v_session_athlete_dashboard AS
    SELECT
      ts.id              AS session_id,
      ts.session_at,
      ts.main_objective,
      ts.planned_load,
      ts.actual_load_avg,
      ts.group_climate,
      ts.highlight,
      ts.next_corrections,

      a.id               AS athlete_id,
      a.full_name,
      a.nickname,
      a.position,

      att.status         AS attendance_status,
      att.notes          AS attendance_notes,

      wpst.minutes,
      wpst.rpe,
      wpst.internal_load,
      wpst.fatigue_after,
      wpst.mood_after,
      wpst.notes         AS wellness_post_notes,

      to_jsonb(wpre)     AS wellness_pre_json,

      CASE att.status
        WHEN 'presente' THEN 'PRESENTE'
        WHEN 'ausente' THEN 'AUSENTE'
        WHEN 'medico' THEN 'DM'
        WHEN 'lesionada' THEN 'LESAO'
        ELSE 'OUTRO'
      END AS status_final,

      CASE
        WHEN att.status <> 'presente' THEN NULL
        WHEN wpst.minutes IS NOT NULL AND wpst.rpe IS NOT NULL THEN TRUE
        ELSE FALSE
      END AS load_ok

    FROM attendance att
    JOIN training_sessions ts ON ts.id = att.session_id
    JOIN athletes a ON a.id = att.athlete_id
    LEFT JOIN wellness_post wpst
      ON wpst.session_id = att.session_id AND wpst.athlete_id = att.athlete_id
    LEFT JOIN wellness_pre wpre
      ON wpre.session_id = att.session_id AND wpre.athlete_id = att.athlete_id;;

UPDATE alembic_version SET version_num='a295501fa7f4' WHERE alembic_version.version_num = 'ae379329cc50';

-- Running upgrade a295501fa7f4 -> 69362f0a01d4

DROP VIEW IF EXISTS public.v_training_session_summary;
    CREATE VIEW public.v_training_session_summary AS
    SELECT
      ts.id AS session_id,
      ts.session_at,
      ts.main_objective,

      COUNT(att.athlete_id)                                           AS total_registros,
      COUNT(*) FILTER (WHERE att.status = 'presente')                  AS presentes,
      COUNT(*) FILTER (WHERE att.status = 'ausente')                   AS ausentes,
      COUNT(*) FILTER (WHERE att.status = 'medico')                    AS dm,
      COUNT(*) FILTER (WHERE att.status = 'lesionada')                 AS lesionadas,

      AVG(wp.minutes) FILTER (WHERE att.status = 'presente')           AS avg_minutes,
      AVG(wp.rpe)     FILTER (WHERE att.status = 'presente')           AS avg_rpe,
      AVG(wp.internal_load) FILTER (WHERE att.status = 'presente')     AS avg_internal_load,

      COUNT(*) FILTER (
        WHERE att.status = 'presente'
          AND wp.minutes IS NOT NULL
          AND wp.rpe IS NOT NULL
      ) AS load_ok_count

    FROM public.training_sessions ts
    LEFT JOIN public.attendance att ON att.session_id = ts.id
    LEFT JOIN public.wellness_post wp
      ON wp.session_id = att.session_id AND wp.athlete_id = att.athlete_id
    GROUP BY ts.id, ts.session_at, ts.main_objective;;

UPDATE alembic_version SET version_num='69362f0a01d4' WHERE alembic_version.version_num = 'a295501fa7f4';

-- Running upgrade 69362f0a01d4 -> ec0615343f42

-- SEASONS
    CREATE TABLE IF NOT EXISTS public.seasons (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      organization_id uuid NOT NULL,
      created_by_membership_id uuid NOT NULL,
      year int NOT NULL UNIQUE,
      name text,
      starts_at date,
      ends_at date,
      CHECK (starts_at < ends_at),
      is_active boolean NOT NULL DEFAULT false,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    DROP TRIGGER IF EXISTS trg_seasons_updated_at ON public.seasons;
    CREATE TRIGGER trg_seasons_updated_at
    BEFORE UPDATE ON public.seasons
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

    -- CATEGORIES
    CREATE TABLE IF NOT EXISTS public.categories (
      id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
      code text NOT NULL UNIQUE,          -- ex: 'U14', 'U16'
      label text NOT NULL,               -- ex: 'Infantil', 'Cadete'
      min_age int,
      max_age int,
      CHECK (min_age <= max_age),
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    DROP TRIGGER IF EXISTS trg_categories_updated_at ON public.categories;
    CREATE TRIGGER trg_categories_updated_at
    BEFORE UPDATE ON public.categories
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

    -- TEAMS
    CREATE TABLE IF NOT EXISTS public.teams (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      organization_id uuid NOT NULL,
      created_by_membership_id uuid NOT NULL,
      season_id uuid NOT NULL REFERENCES public.seasons(id) ON DELETE RESTRICT,
      category_id int NOT NULL REFERENCES public.categories(id) ON DELETE RESTRICT,
      name text NOT NULL,                -- ex: 'IDEC', 'CEPRAEA' ou 'IDEC U14'
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now(),
      UNIQUE (season_id, category_id, name)
    );

    DROP TRIGGER IF EXISTS trg_teams_updated_at ON public.teams;
    CREATE TRIGGER trg_teams_updated_at
    BEFORE UPDATE ON public.teams
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

    CREATE INDEX IF NOT EXISTS idx_teams_season ON public.teams(season_id);
    CREATE INDEX IF NOT EXISTS idx_teams_category ON public.teams(category_id);
    CREATE INDEX IF NOT EXISTS idx_teams_org ON public.teams(organization_id);
    CREATE INDEX IF NOT EXISTS idx_teams_created_by_membership ON public.teams(created_by_membership_id);

    -- TEAM_REGISTRATIONS (inscricao)
    CREATE TABLE IF NOT EXISTS public.team_registrations (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      athlete_id uuid NOT NULL REFERENCES public.athletes(id) ON DELETE CASCADE,
      season_id uuid NOT NULL REFERENCES public.seasons(id) ON DELETE RESTRICT,
      category_id int NOT NULL REFERENCES public.categories(id) ON DELETE RESTRICT,
      team_id uuid NOT NULL REFERENCES public.teams(id) ON DELETE RESTRICT,
      organization_id uuid NOT NULL,
      created_by_membership_id uuid NOT NULL,
      role text,                         -- ex: 'goleira', 'pivo', etc (opcional)
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now(),
      UNIQUE (athlete_id, season_id, category_id)
    );

    DROP TRIGGER IF EXISTS trg_team_registrations_updated_at ON public.team_registrations;
    CREATE TRIGGER trg_team_registrations_updated_at
    BEFORE UPDATE ON public.team_registrations
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

    CREATE INDEX IF NOT EXISTS idx_team_reg_athlete ON public.team_registrations(athlete_id);
    CREATE INDEX IF NOT EXISTS idx_team_reg_team ON public.team_registrations(team_id);
    CREATE INDEX IF NOT EXISTS idx_team_reg_season ON public.team_registrations(season_id);
    CREATE INDEX IF NOT EXISTS idx_team_reg_org ON public.team_registrations(organization_id);
    CREATE INDEX IF NOT EXISTS idx_team_reg_created_by_membership ON public.team_registrations(created_by_membership_id);

    CREATE INDEX IF NOT EXISTS idx_seasons_org ON public.seasons(organization_id);
    CREATE INDEX IF NOT EXISTS idx_seasons_created_by_membership ON public.seasons(created_by_membership_id);;

UPDATE alembic_version SET version_num='ec0615343f42' WHERE alembic_version.version_num = '69362f0a01d4';

-- Running upgrade ec0615343f42 -> cee3af09d659

CREATE TABLE IF NOT EXISTS medical_cases (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      athlete_id uuid NOT NULL REFERENCES athletes(id) ON DELETE CASCADE,
      organization_id uuid NOT NULL,
      created_by_membership_id uuid NOT NULL,

      status text NOT NULL CHECK (status IN ('ativo','alta')),
      reason text,
      notes text,

      started_at date NOT NULL DEFAULT current_date,
      ended_at date,

      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now(),

      CHECK (ended_at IS NULL OR ended_at >= started_at)
    );

    CREATE INDEX IF NOT EXISTS idx_medical_cases_athlete ON medical_cases(athlete_id);
    CREATE INDEX IF NOT EXISTS idx_medical_cases_status ON medical_cases(status);
    CREATE INDEX IF NOT EXISTS idx_medical_cases_org ON medical_cases(organization_id);
    CREATE INDEX IF NOT EXISTS idx_medical_cases_created_by_membership ON medical_cases(created_by_membership_id);

    DROP TRIGGER IF EXISTS trg_medical_cases_updated_at ON medical_cases;
    CREATE TRIGGER trg_medical_cases_updated_at
    BEFORE UPDATE ON medical_cases
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();;

UPDATE alembic_version SET version_num='cee3af09d659' WHERE alembic_version.version_num = 'ec0615343f42';

-- Running upgrade cee3af09d659 -> d001c0ffee01

CREATE TABLE IF NOT EXISTS roles (
      id smallint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
      code text NOT NULL UNIQUE,
      name text NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    DROP TRIGGER IF EXISTS trg_roles_updated_at ON roles;
    CREATE TRIGGER trg_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();;

UPDATE alembic_version SET version_num='d001c0ffee01' WHERE alembic_version.version_num = 'cee3af09d659';

-- Running upgrade d001c0ffee01 -> d002c0ffee02

CREATE TABLE IF NOT EXISTS users (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      email text NOT NULL,
      full_name text,
      password_hash text,
      status text NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo','inativo','arquivado')),
      is_locked boolean NOT NULL DEFAULT false,
      expired_at timestamptz,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower ON users (lower(email));

    DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
    CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();;

UPDATE alembic_version SET version_num='d002c0ffee02' WHERE alembic_version.version_num = 'd001c0ffee01';

-- Running upgrade d002c0ffee02 -> d003c0ffee03

CREATE TABLE IF NOT EXISTS organizations (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      name text NOT NULL,
      owner_user_id uuid NOT NULL REFERENCES users(id),
      status text NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo','inativo','arquivado')),
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    CREATE INDEX IF NOT EXISTS idx_organizations_owner ON organizations(owner_user_id);

    DROP TRIGGER IF EXISTS trg_organizations_updated_at ON organizations;
    CREATE TRIGGER trg_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();;

UPDATE alembic_version SET version_num='d003c0ffee03' WHERE alembic_version.version_num = 'd002c0ffee02';

-- Running upgrade d003c0ffee03 -> d004c0ffee04

CREATE TABLE IF NOT EXISTS membership (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      organization_id uuid NOT NULL REFERENCES organizations(id),
      user_id uuid REFERENCES users(id),
      role_id smallint NOT NULL REFERENCES roles(id),
      status text NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo','inativo','arquivado')),
      start_date date DEFAULT current_date,
      end_date date CHECK (end_date IS NULL OR end_date >= start_date),
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    CREATE INDEX IF NOT EXISTS idx_membership_org ON membership(organization_id);
    CREATE INDEX IF NOT EXISTS idx_membership_user ON membership(user_id);
    CREATE INDEX IF NOT EXISTS idx_membership_role ON membership(role_id);

    -- Bloquear sobreposicao de vinculos ativos por usuario
    CREATE OR REPLACE FUNCTION trg_membership_no_overlap() RETURNS trigger AS $$
    DECLARE v_range daterange;
    BEGIN
      IF NEW.user_id IS NULL OR NEW.status <> 'ativo' THEN
        RETURN NEW;
      END IF;

      v_range := daterange(
        COALESCE(NEW.start_date, current_date),
        COALESCE(NEW.end_date, 'infinity'::date),
        '[]'
      );

      IF EXISTS (
        SELECT 1
          FROM membership m
         WHERE m.user_id = NEW.user_id
           AND m.status = 'ativo'
           AND (NEW.id IS NULL OR m.id <> NEW.id)
           AND daterange(
                 COALESCE(m.start_date, current_date),
                 COALESCE(m.end_date, 'infinity'::date),
                 '[]'
               ) && v_range
      ) THEN
        RAISE EXCEPTION 'Vinculo ativo sobreposto para o usuario';
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_membership_no_overlap ON membership;
    CREATE TRIGGER trg_membership_no_overlap
    BEFORE INSERT OR UPDATE ON membership
    FOR EACH ROW EXECUTE FUNCTION trg_membership_no_overlap();

    DROP TRIGGER IF EXISTS trg_membership_updated_at ON membership;
    CREATE TRIGGER trg_membership_updated_at
    BEFORE UPDATE ON membership
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();;

UPDATE alembic_version SET version_num='d004c0ffee04' WHERE alembic_version.version_num = 'd003c0ffee03';

-- Running upgrade d004c0ffee04 -> d005c0ffee05

CREATE TABLE IF NOT EXISTS permissions (
      id smallint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
      code text NOT NULL UNIQUE,
      description text,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    DROP TRIGGER IF EXISTS trg_permissions_updated_at ON permissions;
    CREATE TRIGGER trg_permissions_updated_at
    BEFORE UPDATE ON permissions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

    CREATE TABLE IF NOT EXISTS role_permissions (
      role_id smallint NOT NULL REFERENCES roles(id),
      permission_id smallint NOT NULL REFERENCES permissions(id),
      PRIMARY KEY (role_id, permission_id)
    );;

UPDATE alembic_version SET version_num='d005c0ffee05' WHERE alembic_version.version_num = 'd004c0ffee04';

-- Running upgrade d005c0ffee05 -> d006c0ffee06

CREATE TABLE IF NOT EXISTS competitions (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      organization_id uuid NOT NULL REFERENCES organizations(id),
      name text NOT NULL,
      kind text,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    CREATE INDEX IF NOT EXISTS idx_competitions_org ON competitions(organization_id);

    DROP TRIGGER IF EXISTS trg_competitions_updated_at ON competitions;
    CREATE TRIGGER trg_competitions_updated_at
    BEFORE UPDATE ON competitions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();;

UPDATE alembic_version SET version_num='d006c0ffee06' WHERE alembic_version.version_num = 'd005c0ffee05';

-- Running upgrade d006c0ffee06 -> d007c0ffee07

CREATE TABLE IF NOT EXISTS competition_seasons (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      competition_id uuid NOT NULL REFERENCES competitions(id),
      season_id uuid NOT NULL REFERENCES seasons(id),
      name text,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now(),
      UNIQUE (competition_id, season_id)
    );

    CREATE INDEX IF NOT EXISTS idx_competition_seasons_competition ON competition_seasons(competition_id);
    CREATE INDEX IF NOT EXISTS idx_competition_seasons_season ON competition_seasons(season_id);

    DROP TRIGGER IF EXISTS trg_competition_seasons_updated_at ON competition_seasons;
    CREATE TRIGGER trg_competition_seasons_updated_at
    BEFORE UPDATE ON competition_seasons
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();;

UPDATE alembic_version SET version_num='d007c0ffee07' WHERE alembic_version.version_num = 'd006c0ffee06';

-- Running upgrade d007c0ffee07 -> d008c0ffee08

CREATE TABLE IF NOT EXISTS matches (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      competition_season_id uuid NOT NULL REFERENCES competition_seasons(id),
      category_id int NOT NULL REFERENCES categories(id),
      match_at timestamptz NOT NULL,
      venue text,
      phase text,
      round text,
      status text NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled','finished','cancelled')),
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    CREATE INDEX IF NOT EXISTS idx_matches_competition_season ON matches(competition_season_id);
    CREATE INDEX IF NOT EXISTS idx_matches_category ON matches(category_id);

    DROP TRIGGER IF EXISTS trg_matches_updated_at ON matches;
    CREATE TRIGGER trg_matches_updated_at
    BEFORE UPDATE ON matches
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();;

UPDATE alembic_version SET version_num='d008c0ffee08' WHERE alembic_version.version_num = 'd007c0ffee07';

-- Running upgrade d008c0ffee08 -> d009c0ffee09

CREATE TABLE IF NOT EXISTS match_teams (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      match_id uuid NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
      team_id uuid NOT NULL REFERENCES teams(id),
      side text NOT NULL CHECK (side IN ('home','away')),
      score int NOT NULL DEFAULT 0,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now(),
      UNIQUE (match_id, side),
      UNIQUE (match_id, team_id)
    );

    CREATE INDEX IF NOT EXISTS idx_match_teams_match ON match_teams(match_id);
    CREATE INDEX IF NOT EXISTS idx_match_teams_team ON match_teams(team_id);

    DROP TRIGGER IF EXISTS trg_match_teams_updated_at ON match_teams;
    CREATE TRIGGER trg_match_teams_updated_at
    BEFORE UPDATE ON match_teams
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();;

UPDATE alembic_version SET version_num='d009c0ffee09' WHERE alembic_version.version_num = 'd008c0ffee08';

-- Running upgrade d009c0ffee09 -> d00ac0ffee0a

CREATE TABLE IF NOT EXISTS match_roster (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      match_id uuid NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
      team_id uuid NOT NULL REFERENCES teams(id),
      athlete_id uuid NOT NULL REFERENCES athletes(id),
      is_starter boolean DEFAULT false,
      played boolean DEFAULT true,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now(),
      UNIQUE (match_id, athlete_id)
    );

    CREATE INDEX IF NOT EXISTS idx_match_roster_match ON match_roster(match_id);
    CREATE INDEX IF NOT EXISTS idx_match_roster_team ON match_roster(team_id);
    CREATE INDEX IF NOT EXISTS idx_match_roster_athlete ON match_roster(athlete_id);

    DROP TRIGGER IF EXISTS trg_match_roster_updated_at ON match_roster;
    CREATE TRIGGER trg_match_roster_updated_at
    BEFORE UPDATE ON match_roster
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();;

UPDATE alembic_version SET version_num='d00ac0ffee0a' WHERE alembic_version.version_num = 'd009c0ffee09';

-- Running upgrade d00ac0ffee0a -> d00bc0ffee0b

CREATE TABLE IF NOT EXISTS match_events (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      match_id uuid NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
      team_id uuid REFERENCES teams(id),
      athlete_id uuid REFERENCES athletes(id),
      period smallint,
      second_in_match int,
      event_type text NOT NULL,
      points smallint DEFAULT 1,
      notes text,
      created_at timestamptz NOT NULL DEFAULT now()
    );

    CREATE INDEX IF NOT EXISTS idx_match_events_match ON match_events(match_id);
    CREATE INDEX IF NOT EXISTS idx_match_events_team ON match_events(team_id);
    CREATE INDEX IF NOT EXISTS idx_match_events_athlete ON match_events(athlete_id);;

UPDATE alembic_version SET version_num='d00bc0ffee0b' WHERE alembic_version.version_num = 'd00ac0ffee0a';

-- Running upgrade d00bc0ffee0b -> d00cc0ffee0c

-- 1) persons: entidade central
    CREATE TABLE IF NOT EXISTS persons (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      full_name text NOT NULL,
      birth_date date,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );

    DROP TRIGGER IF EXISTS trg_persons_updated_at ON persons;
    CREATE TRIGGER trg_persons_updated_at
    BEFORE UPDATE ON persons
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

    -- 2) users -> referenciar persons + superadmin �nico
    ALTER TABLE users ADD COLUMN IF NOT EXISTS person_id uuid DEFAULT gen_random_uuid();
    ALTER TABLE users ADD COLUMN IF NOT EXISTS is_superadmin boolean NOT NULL DEFAULT false;

    INSERT INTO persons (id, full_name, birth_date, created_at, updated_at)
    SELECT u.person_id, COALESCE(u.full_name, u.email), NULL, COALESCE(u.created_at, now()), COALESCE(u.updated_at, now())
    FROM users u
    LEFT JOIN persons p ON p.id = u.person_id
    WHERE p.id IS NULL;

    ALTER TABLE users ALTER COLUMN person_id SET NOT NULL;
    ALTER TABLE users ADD CONSTRAINT fk_users_person FOREIGN KEY (person_id) REFERENCES persons(id);

    CREATE UNIQUE INDEX IF NOT EXISTS idx_users_superadmin_unique ON users ((1)) WHERE is_superadmin;
    CREATE UNIQUE INDEX IF NOT EXISTS uq_users_id_person ON users (id, person_id);

    -- Garantir que sempre exista exatamente 1 superadmin
    CREATE OR REPLACE FUNCTION enforce_single_superadmin() RETURNS trigger AS $$
    DECLARE v_count int;
    BEGIN
      IF (TG_OP = 'DELETE' AND OLD.is_superadmin) OR
         (TG_OP = 'UPDATE' AND OLD.is_superadmin AND NEW.is_superadmin = false) THEN
        SELECT count(*) INTO v_count FROM users WHERE is_superadmin = true AND id <> OLD.id;
        IF v_count = 0 THEN
          RAISE EXCEPTION 'Nao e permitido remover o ultimo superadmin';
        END IF;
      END IF;

      IF TG_OP = 'DELETE' THEN
        RETURN OLD;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_enforce_single_superadmin ON users;
    CREATE TRIGGER trg_enforce_single_superadmin
    BEFORE UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION enforce_single_superadmin();

    -- 3) athletes -> referenciar persons
    ALTER TABLE athletes ADD COLUMN IF NOT EXISTS person_id uuid DEFAULT gen_random_uuid();

    INSERT INTO persons (id, full_name, birth_date, created_at, updated_at)
    SELECT a.person_id, a.full_name, a.birth_date, a.created_at, a.updated_at
    FROM athletes a
    LEFT JOIN persons p ON p.id = a.person_id
    WHERE p.id IS NULL;

    ALTER TABLE athletes ALTER COLUMN person_id SET NOT NULL;
    ALTER TABLE athletes ADD CONSTRAINT fk_athletes_person FOREIGN KEY (person_id) REFERENCES persons(id);

    -- 4) membership -> incluir person/season e chave �nica por pessoa/temporada/org
    ALTER TABLE membership ADD COLUMN IF NOT EXISTS person_id uuid;
    ALTER TABLE membership ADD COLUMN IF NOT EXISTS season_id uuid;

    UPDATE membership m
    SET person_id = u.person_id
    FROM users u
    WHERE m.person_id IS NULL AND u.id = m.user_id;

    ALTER TABLE membership
      ADD CONSTRAINT fk_membership_person FOREIGN KEY (person_id) REFERENCES persons(id);
    ALTER TABLE membership
      ADD CONSTRAINT fk_membership_season FOREIGN KEY (season_id) REFERENCES seasons(id) DEFERRABLE INITIALLY DEFERRED;

    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_membership_user_person'
      ) THEN
        ALTER TABLE membership
          ADD CONSTRAINT fk_membership_user_person
          FOREIGN KEY (user_id, person_id) REFERENCES users(id, person_id);
      END IF;
    END$$;

    ALTER TABLE membership DROP CONSTRAINT IF EXISTS membership_organization_id_user_id_key;
    CREATE UNIQUE INDEX IF NOT EXISTS uq_membership_org_person_season ON membership(organization_id, person_id, season_id);

    ALTER TABLE membership ALTER COLUMN person_id SET NOT NULL;

    -- Contexto organizacional e vinculo nos dominios operacionais
    DO $$
    BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_athletes_org') THEN
        ALTER TABLE athletes ADD CONSTRAINT fk_athletes_org FOREIGN KEY (organization_id) REFERENCES organizations(id);
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_athletes_created_by_membership') THEN
        ALTER TABLE athletes ADD CONSTRAINT fk_athletes_created_by_membership FOREIGN KEY (created_by_membership_id) REFERENCES membership(id);
      END IF;

      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_training_sessions_org') THEN
        ALTER TABLE training_sessions ADD CONSTRAINT fk_training_sessions_org FOREIGN KEY (organization_id) REFERENCES organizations(id);
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_training_sessions_created_by_membership') THEN
        ALTER TABLE training_sessions ADD CONSTRAINT fk_training_sessions_created_by_membership FOREIGN KEY (created_by_membership_id) REFERENCES membership(id);
      END IF;

      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_attendance_org') THEN
        ALTER TABLE attendance ADD CONSTRAINT fk_attendance_org FOREIGN KEY (organization_id) REFERENCES organizations(id);
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_attendance_created_by_membership') THEN
        ALTER TABLE attendance ADD CONSTRAINT fk_attendance_created_by_membership FOREIGN KEY (created_by_membership_id) REFERENCES membership(id);
      END IF;

      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_wellness_pre_org') THEN
        ALTER TABLE wellness_pre ADD CONSTRAINT fk_wellness_pre_org FOREIGN KEY (organization_id) REFERENCES organizations(id);
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_wellness_pre_created_by_membership') THEN
        ALTER TABLE wellness_pre ADD CONSTRAINT fk_wellness_pre_created_by_membership FOREIGN KEY (created_by_membership_id) REFERENCES membership(id);
      END IF;

      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_wellness_post_org') THEN
        ALTER TABLE wellness_post ADD CONSTRAINT fk_wellness_post_org FOREIGN KEY (organization_id) REFERENCES organizations(id);
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_wellness_post_created_by_membership') THEN
        ALTER TABLE wellness_post ADD CONSTRAINT fk_wellness_post_created_by_membership FOREIGN KEY (created_by_membership_id) REFERENCES membership(id);
      END IF;

      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_seasons_org') THEN
        ALTER TABLE seasons ADD CONSTRAINT fk_seasons_org FOREIGN KEY (organization_id) REFERENCES organizations(id);
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_seasons_created_by_membership') THEN
        ALTER TABLE seasons ADD CONSTRAINT fk_seasons_created_by_membership FOREIGN KEY (created_by_membership_id) REFERENCES membership(id) DEFERRABLE INITIALLY DEFERRED;
      END IF;

      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_teams_org') THEN
        ALTER TABLE teams ADD CONSTRAINT fk_teams_org FOREIGN KEY (organization_id) REFERENCES organizations(id);
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_teams_created_by_membership') THEN
        ALTER TABLE teams ADD CONSTRAINT fk_teams_created_by_membership FOREIGN KEY (created_by_membership_id) REFERENCES membership(id);
      END IF;

      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_team_registrations_org') THEN
        ALTER TABLE team_registrations ADD CONSTRAINT fk_team_registrations_org FOREIGN KEY (organization_id) REFERENCES organizations(id);
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_team_registrations_created_by_membership') THEN
        ALTER TABLE team_registrations ADD CONSTRAINT fk_team_registrations_created_by_membership FOREIGN KEY (created_by_membership_id) REFERENCES membership(id);
      END IF;

      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_medical_cases_org') THEN
        ALTER TABLE medical_cases ADD CONSTRAINT fk_medical_cases_org FOREIGN KEY (organization_id) REFERENCES organizations(id);
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_medical_cases_created_by_membership') THEN
        ALTER TABLE medical_cases ADD CONSTRAINT fk_medical_cases_created_by_membership FOREIGN KEY (created_by_membership_id) REFERENCES membership(id);
      END IF;
    END$$;;

UPDATE alembic_version SET version_num='d00cc0ffee0c' WHERE alembic_version.version_num = 'd00bc0ffee0b';

-- Running upgrade d00cc0ffee0c -> d00dc0ffee0d

-- Seed de roles b�sicos
    INSERT INTO roles (code, name)
    VALUES
      ('superadmin', 'Super Administrador'),
      ('dirigente', 'Dirigente'),
      ('coordenador', 'Coordenador'),
      ('treinador', 'Treinador'),
      ('atleta', 'Atleta')
    ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name;

    -- Garantir superadmin �nico (cria se n�o existir)
    DO $$
    DECLARE v_person uuid;
    DECLARE v_user uuid;
    BEGIN
      SELECT id INTO v_user FROM users WHERE is_superadmin = true LIMIT 1;
      IF v_user IS NULL THEN
        INSERT INTO persons (full_name) VALUES ('Super Admin Seed') RETURNING id INTO v_person;
        INSERT INTO users (person_id, email, full_name, is_superadmin, status)
        VALUES (v_person, 'superadmin@seed.local', 'Super Admin Seed', true, 'ativo')
        ON CONFLICT (lower(email)) DO NOTHING;
      END IF;
    END$$;

    -- membership: refor�ar status e season, �ndices de unicidade por papel
    UPDATE membership SET season_id = season_id WHERE season_id IS NOT NULL;
    ALTER TABLE membership ALTER COLUMN season_id SET NOT NULL;

    -- �ndices de unicidade por papel (resolver IDs e criar dinamicamente)
    DO $$
    DECLARE r_dir int; r_coord int; r_tre int; r_atl int;
    BEGIN
      SELECT id INTO r_dir FROM roles WHERE code = 'dirigente';
      SELECT id INTO r_coord FROM roles WHERE code = 'coordenador';
      SELECT id INTO r_tre FROM roles WHERE code = 'treinador';
      SELECT id INTO r_atl FROM roles WHERE code = 'atleta';

      EXECUTE 'DROP INDEX IF EXISTS uq_membership_staff_active_person';
      EXECUTE format(
        'CREATE UNIQUE INDEX uq_membership_staff_active_person ON membership(person_id) WHERE status = %L AND role_id IN (%s,%s,%s)',
        'ativo', r_dir, r_coord, r_tre
      );

      EXECUTE 'DROP INDEX IF EXISTS uq_membership_athlete_active_season';
      EXECUTE format(
        'CREATE UNIQUE INDEX uq_membership_athlete_active_season ON membership(person_id, season_id) WHERE status = %L AND role_id = %s',
        'ativo', r_atl
      );
    END$$;;

UPDATE alembic_version SET version_num='d00dc0ffee0d' WHERE alembic_version.version_num = 'd00cc0ffee0c';

-- Running upgrade d00dc0ffee0d -> d00ec0ffee0e

-- 1) Coluna de estado atual em athletes
    ALTER TABLE athletes
      ADD COLUMN IF NOT EXISTS state text NOT NULL DEFAULT 'ativa'
      CHECK (state IN ('ativa','lesionada','dispensada'));

    -- 2) Hist�rico de estados
    CREATE TABLE IF NOT EXISTS athlete_states (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      athlete_id uuid NOT NULL REFERENCES athletes(id) ON DELETE CASCADE,
      state text NOT NULL CHECK (state IN ('ativa','lesionada','dispensada')),
      reason text,
      notes text,
      started_at timestamptz NOT NULL DEFAULT now(),
      ended_at timestamptz,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now(),
      CHECK (ended_at IS NULL OR ended_at >= started_at)
    );

    -- Garantir 1 estado ativo por atleta
    DROP INDEX IF EXISTS uq_athlete_states_active;
    CREATE UNIQUE INDEX uq_athlete_states_active
      ON athlete_states(athlete_id)
      WHERE ended_at IS NULL;

    -- Trigger updated_at reaproveitando set_updated_at()
    DROP TRIGGER IF EXISTS trg_athlete_states_updated_at ON athlete_states;
    CREATE TRIGGER trg_athlete_states_updated_at
    BEFORE UPDATE ON athlete_states
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

    -- Trigger BEFORE INSERT para encerrar estado ativo anterior
    CREATE OR REPLACE FUNCTION close_active_athlete_state() RETURNS trigger AS $$
    BEGIN
      UPDATE athlete_states
         SET ended_at = COALESCE(NEW.started_at, now())
       WHERE athlete_id = NEW.athlete_id
         AND ended_at IS NULL;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_athlete_states_close_active ON athlete_states;
    CREATE TRIGGER trg_athlete_states_close_active
    BEFORE INSERT ON athlete_states
    FOR EACH ROW EXECUTE FUNCTION close_active_athlete_state();

    -- Trigger AFTER INSERT para sincronizar estado atual em athletes
    CREATE OR REPLACE FUNCTION sync_athlete_state_current() RETURNS trigger AS $$
    BEGIN
      UPDATE athletes SET state = NEW.state, updated_at = now()
       WHERE id = NEW.athlete_id;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_athlete_states_sync ON athlete_states;
    CREATE TRIGGER trg_athlete_states_sync
    AFTER INSERT ON athlete_states
    FOR EACH ROW EXECUTE FUNCTION sync_athlete_state_current();

    -- Encerrar vinculo da atleta ao marcar como dispensada
    CREATE OR REPLACE FUNCTION trg_athlete_state_dispense_membership() RETURNS trigger AS $$
    DECLARE v_role_atleta int;
    DECLARE v_person uuid;
    DECLARE v_end date;
    BEGIN
      IF NEW.state <> 'dispensada' THEN
        RETURN NEW;
      END IF;

      SELECT person_id INTO v_person FROM athletes WHERE id = NEW.athlete_id;
      IF v_person IS NULL THEN
        RETURN NEW;
      END IF;

      SELECT id INTO v_role_atleta FROM roles WHERE code = 'atleta';
      v_end := COALESCE(NEW.started_at::date, current_date);

      UPDATE membership m
         SET status = 'inativo',
             end_date = COALESCE(m.end_date, v_end)
       WHERE m.person_id = v_person
         AND m.role_id = v_role_atleta
         AND m.status = 'ativo'
         AND (m.end_date IS NULL OR m.end_date >= v_end);

      -- CORRECAO RAG V1.1 R13: Encerrar team_registrations
      UPDATE team_registrations tr
         SET end_at = v_end,
             updated_at = now()
       WHERE tr.athlete_id = NEW.athlete_id
         AND tr.end_at IS NULL;

      PERFORM log_audit_event(
        'athlete_state_dispense',
        NEW.athlete_id,
        'dispense_complete',
        NEW.notes,
        jsonb_build_object(
          'person_id', v_person,
          'dispensed_at', v_end,
          'reason', NEW.reason
        )
      );

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_athlete_state_dispense_membership ON athlete_states;
    CREATE TRIGGER trg_athlete_state_dispense_membership
    AFTER INSERT ON athlete_states
    FOR EACH ROW EXECUTE FUNCTION trg_athlete_state_dispense_membership();

    -- 3) Seed do hist�rico para atletas existentes (estado atual = state)
    INSERT INTO athlete_states (athlete_id, state, started_at, notes)
    SELECT a.id, a.state, COALESCE(a.created_at, now()), 'seed auto'
      FROM athletes a
     WHERE NOT EXISTS (
             SELECT 1 FROM athlete_states s
              WHERE s.athlete_id = a.id
            );;

UPDATE alembic_version SET version_num='d00ec0ffee0e' WHERE alembic_version.version_num = 'd00dc0ffee0d';

-- Running upgrade d00ec0ffee0e -> d00fc0ffee0f

-- === Fun��o helper: idade na data (anos completos) ===
    CREATE OR REPLACE FUNCTION age_in_years(bdate date, ref date)
    RETURNS int LANGUAGE plpgsql AS $$
    BEGIN
      IF bdate IS NULL OR ref IS NULL THEN
        RETURN NULL;
      END IF;
      RETURN EXTRACT(year FROM age(ref, bdate))::int;
    END;
    $$;

    -- === team_registrations: valida idade/categoria (n�o permitir abaixo do m�nimo) ===
    CREATE OR REPLACE FUNCTION trg_team_registrations_age_check() RETURNS trigger AS $$
    DECLARE v_birth date;
    DECLARE v_starts date;
    DECLARE v_min int;
    DECLARE v_max int;
    DECLARE v_age int;
    BEGIN
      SELECT birth_date INTO v_birth FROM athletes WHERE id = NEW.athlete_id;
      SELECT starts_at INTO v_starts FROM seasons WHERE id = NEW.season_id;
      SELECT min_age, max_age INTO v_min, v_max FROM categories WHERE id = NEW.category_id;
      v_age := age_in_years(v_birth, v_starts);
      IF v_age IS NULL THEN
        RAISE EXCEPTION 'Idade n�o encontrada para valida��o de categoria';
      END IF;
      IF v_min IS NOT NULL AND v_age < v_min THEN
        RAISE EXCEPTION 'Atleta com idade % abaixo do m�nimo % da categoria', v_age, v_min;
      END IF;
      IF v_max IS NOT NULL AND v_age > v_max THEN
        -- idade acima do m�ximo � permitida (atuar acima), n�o bloqueia
        RETURN NEW;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_team_registrations_age_check ON team_registrations;
    CREATE TRIGGER trg_team_registrations_age_check
    BEFORE INSERT OR UPDATE ON team_registrations
    FOR EACH ROW EXECUTE FUNCTION trg_team_registrations_age_check();

    -- === membership: atleta precisa de registro de time na temporada ===
    CREATE OR REPLACE FUNCTION trg_membership_require_team() RETURNS trigger AS $$
    DECLARE v_role_atleta int;
    DECLARE v_ath uuid;
    DECLARE v_exists boolean;
    BEGIN
      SELECT id INTO v_role_atleta FROM roles WHERE code = 'atleta';
      IF NEW.role_id != v_role_atleta OR NEW.status <> 'ativo' THEN
        RETURN NEW;
      END IF;

      SELECT id INTO v_ath FROM athletes WHERE person_id = NEW.person_id LIMIT 1;
      IF v_ath IS NULL THEN
        RAISE EXCEPTION 'Nenhum atleta vinculado � pessoa para membership';
      END IF;

      SELECT EXISTS (
        SELECT 1 FROM team_registrations tr
         WHERE tr.athlete_id = v_ath
           AND tr.season_id = NEW.season_id
      ) INTO v_exists;

      IF NOT v_exists THEN
        RAISE EXCEPTION 'Atleta precisa estar em pelo menos uma equipe na temporada';
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_membership_require_team ON membership;
    CREATE CONSTRAINT TRIGGER trg_membership_require_team
    AFTER INSERT OR UPDATE ON membership
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION trg_membership_require_team();

    -- === Treinos: bloquear edi��o ap�s 24h da realiza��o ===
    CREATE OR REPLACE FUNCTION trg_training_sessions_lock() RETURNS trigger AS $$
    BEGIN
      IF OLD.session_at IS NOT NULL AND (now() - OLD.session_at) > interval '24 hours' THEN
        RAISE EXCEPTION 'Treino n�o pode ser editado ap�s 24h da realiza��o';
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_training_sessions_lock ON training_sessions;
    CREATE TRIGGER trg_training_sessions_lock
    BEFORE UPDATE ON training_sessions
    FOR EACH ROW EXECUTE FUNCTION trg_training_sessions_lock();

    -- === Jogos: bloquear edi��o ap�s finalizado ===
    CREATE OR REPLACE FUNCTION trg_matches_lock_finished() RETURNS trigger AS $$
    BEGIN
      IF OLD.status = 'finished' THEN
        RAISE EXCEPTION 'Jogo finalizado n�o pode ser alterado';
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_matches_lock_finished ON matches;
    CREATE TRIGGER trg_matches_lock_finished
    BEFORE UPDATE ON matches
    FOR EACH ROW EXECUTE FUNCTION trg_matches_lock_finished();

    -- === Roster: m�ximo 16 por jogo e bloquear se jogo finalizado ===
    CREATE OR REPLACE FUNCTION trg_match_roster_constraints() RETURNS trigger AS $$
    DECLARE v_count int;
    DECLARE v_status text;
    BEGIN
      SELECT status INTO v_status FROM matches WHERE id = NEW.match_id;
      IF v_status = 'finished' THEN
        RAISE EXCEPTION 'Jogo finalizado n�o aceita altera��es de roster';
      END IF;
      SELECT count(*) INTO v_count FROM match_roster WHERE match_id = NEW.match_id;
      IF v_count >= 16 THEN
        RAISE EXCEPTION 'Roster do jogo atingiu o limite de 16 atletas';
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_match_roster_constraints ON match_roster;
    CREATE TRIGGER trg_match_roster_constraints
    BEFORE INSERT OR UPDATE ON match_roster
    FOR EACH ROW EXECUTE FUNCTION trg_match_roster_constraints();

    -- === Eventos: atleta deve estar no roster e jogo n�o finalizado ===
    CREATE OR REPLACE FUNCTION trg_match_events_constraints() RETURNS trigger AS $$
    DECLARE v_status text;
    DECLARE v_in_roster boolean;
    BEGIN
      SELECT status INTO v_status FROM matches WHERE id = NEW.match_id;
      IF v_status = 'finished' THEN
        RAISE EXCEPTION 'Jogo finalizado n�o aceita eventos novos';
      END IF;

      IF NEW.athlete_id IS NOT NULL THEN
        SELECT EXISTS (
          SELECT 1 FROM match_roster
           WHERE match_id = NEW.match_id
             AND athlete_id = NEW.athlete_id
        ) INTO v_in_roster;
        IF NOT v_in_roster THEN
          RAISE EXCEPTION 'Evento requer atleta presente no roster do jogo';
        END IF;
      END IF;

      IF NEW.team_id IS NOT NULL THEN
        PERFORM 1 FROM match_teams WHERE match_id = NEW.match_id AND team_id = NEW.team_id;
        IF NOT FOUND THEN
          RAISE EXCEPTION 'Evento requer equipe presente no jogo';
        END IF;
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_match_events_constraints ON match_events;
    CREATE TRIGGER trg_match_events_constraints
    BEFORE INSERT OR UPDATE ON match_events
    FOR EACH ROW EXECUTE FUNCTION trg_match_events_constraints();;

UPDATE alembic_version SET version_num='d00fc0ffee0f' WHERE alembic_version.version_num = 'd00ec0ffee0e';

-- Running upgrade d00fc0ffee0f -> d010c0ffee10

-- Audit log simples
    CREATE TABLE IF NOT EXISTS audit_logs (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      entity text NOT NULL,
      entity_id uuid,
      action text NOT NULL,
      justification text,
      context jsonb,
      created_at timestamptz NOT NULL DEFAULT now()
    );

    -- Campos de controle em treinos e jogos
    ALTER TABLE training_sessions ADD COLUMN IF NOT EXISTS admin_note text;
    ALTER TABLE matches ADD COLUMN IF NOT EXISTS admin_note text;
    ALTER TABLE matches ADD COLUMN IF NOT EXISTS finalized_at timestamptz;
    ALTER TABLE matches ADD COLUMN IF NOT EXISTS validated_at timestamptz;

    -- Ajustar lock de treino: permitir se houver admin_note
    CREATE OR REPLACE FUNCTION trg_training_sessions_lock() RETURNS trigger AS $$
    BEGIN
      IF OLD.session_at IS NOT NULL AND (now() - OLD.session_at) > interval '24 hours' THEN
        IF NEW.admin_note IS NULL THEN
          RAISE EXCEPTION 'Treino n�o pode ser editado ap�s 24h da realiza��o (faltou justificativa admin)';
        END IF;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Matches: exigir justificativa ao mudar status; marcar finalized_at/validated_at; bloquear edi��o depois de finished (j� havia trigger)
    CREATE OR REPLACE FUNCTION trg_matches_status_controls() RETURNS trigger AS $$
    BEGIN
      IF NEW.status IS DISTINCT FROM OLD.status THEN
        IF NEW.admin_note IS NULL THEN
          RAISE EXCEPTION 'Mudan�a de status de jogo requer justificativa em admin_note';
        END IF;
        IF NEW.status = 'finished' AND OLD.status <> 'finished' THEN
          NEW.finalized_at := COALESCE(NEW.finalized_at, now());
          NEW.validated_at := COALESCE(NEW.validated_at, now());
        END IF;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_matches_status_controls ON matches;
    CREATE TRIGGER trg_matches_status_controls
    BEFORE UPDATE ON matches
    FOR EACH ROW EXECUTE FUNCTION trg_matches_status_controls();

    -- Audit: log de mudan�as cr�ticas (match status, treino lock/atualiza��o p�s 24h, atleta estado)
    CREATE OR REPLACE FUNCTION log_audit_event(p_entity text, p_entity_id uuid, p_action text, p_just text, p_context jsonb) RETURNS void AS $$
    BEGIN
      INSERT INTO audit_logs(entity, entity_id, action, justification, context)
      VALUES (p_entity, p_entity_id, p_action, p_just, p_context);
    END;
    $$ LANGUAGE plpgsql;

    -- Log edi��ǜo de treino ap��s 24h (com admin_note)
    CREATE OR REPLACE FUNCTION trg_training_sessions_audit_late_edit() RETURNS trigger AS $$
    BEGIN
      IF OLD.session_at IS NOT NULL AND (now() - OLD.session_at) > interval '24 hours' THEN
        PERFORM log_audit_event(
          'training_session',
          NEW.id,
          'late_edit',
          NEW.admin_note,
          jsonb_build_object('old', row_to_json(OLD), 'new', row_to_json(NEW))
        );
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_training_sessions_audit_late_edit ON training_sessions;
    CREATE TRIGGER trg_training_sessions_audit_late_edit
    AFTER UPDATE ON training_sessions
    FOR EACH ROW EXECUTE FUNCTION trg_training_sessions_audit_late_edit();

    -- Log ao mudar status de jogo
    CREATE OR REPLACE FUNCTION trg_matches_audit() RETURNS trigger AS $$
    BEGIN
      IF NEW.status IS DISTINCT FROM OLD.status THEN
        PERFORM log_audit_event('match', NEW.id, 'status_change', NEW.admin_note, jsonb_build_object('old_status', OLD.status, 'new_status', NEW.status));
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_matches_audit ON matches;
    CREATE TRIGGER trg_matches_audit
    AFTER UPDATE ON matches
    FOR EACH ROW EXECUTE FUNCTION trg_matches_audit();

    -- Log ao inserir estado de atleta
    CREATE OR REPLACE FUNCTION trg_athlete_states_audit() RETURNS trigger AS $$
    BEGIN
      PERFORM log_audit_event('athlete_state', NEW.id, 'state_change', NEW.notes, jsonb_build_object('athlete_id', NEW.athlete_id, 'state', NEW.state, 'started_at', NEW.started_at));
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_athlete_states_audit ON athlete_states;
    CREATE TRIGGER trg_athlete_states_audit
    AFTER INSERT ON athlete_states
    FOR EACH ROW EXECUTE FUNCTION trg_athlete_states_audit();;

UPDATE alembic_version SET version_num='d010c0ffee10' WHERE alembic_version.version_num = 'd00fc0ffee0f';

-- Running upgrade d010c0ffee10 -> d011c0ffee11

-- Campos para soft delete em jogos e treinos
    ALTER TABLE matches ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE matches ADD COLUMN IF NOT EXISTS deleted_reason text;
    ALTER TABLE training_sessions ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE training_sessions ADD COLUMN IF NOT EXISTS deleted_reason text;

    -- Tipo de jogo (oficial/amistoso/treino-jogo)
    ALTER TABLE matches ADD COLUMN IF NOT EXISTS match_type text NOT NULL DEFAULT 'official'
      CHECK (match_type IN ('official','friendly','scrimmage'));

    -- Audit de soft delete: UPDATE set deleted_at exige admin_note/deleted_reason
    CREATE OR REPLACE FUNCTION trg_soft_delete_matches() RETURNS trigger AS $$
    BEGIN
      IF NEW.deleted_at IS DISTINCT FROM OLD.deleted_at OR NEW.deleted_reason IS DISTINCT FROM OLD.deleted_reason THEN
        IF NEW.deleted_at IS NOT NULL AND (NEW.admin_note IS NULL OR NEW.deleted_reason IS NULL) THEN
          RAISE EXCEPTION 'Exclus�o l�gica de jogo requer admin_note e deleted_reason';
        END IF;
        PERFORM log_audit_event('match', NEW.id, 'soft_delete', NEW.deleted_reason, jsonb_build_object('deleted_at', NEW.deleted_at));
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_soft_delete_matches ON matches;
    CREATE TRIGGER trg_soft_delete_matches
    BEFORE UPDATE ON matches
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_matches();

    CREATE OR REPLACE FUNCTION trg_soft_delete_training() RETURNS trigger AS $$
    BEGIN
      IF NEW.deleted_at IS DISTINCT FROM OLD.deleted_at OR NEW.deleted_reason IS DISTINCT FROM OLD.deleted_reason THEN
        IF NEW.deleted_at IS NOT NULL AND (NEW.admin_note IS NULL OR NEW.deleted_reason IS NULL) THEN
          RAISE EXCEPTION 'Exclus�o l�gica de treino requer admin_note e deleted_reason';
        END IF;
        PERFORM log_audit_event('training_session', NEW.id, 'soft_delete', NEW.deleted_reason, jsonb_build_object('deleted_at', NEW.deleted_at));
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_soft_delete_training ON training_sessions;
    CREATE TRIGGER trg_soft_delete_training
    BEFORE UPDATE ON training_sessions
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_training();

    -- Bloquear DELETE f�sico (jogos e treinos)
    CREATE OR REPLACE FUNCTION block_delete() RETURNS trigger AS $$
    BEGIN
      RAISE EXCEPTION 'Delete f�sico n�o permitido; use exclus�o l�gica (deleted_at/deleted_reason)';
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_block_delete_matches ON matches;
    CREATE TRIGGER trg_block_delete_matches
    BEFORE DELETE ON matches
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    DROP TRIGGER IF EXISTS trg_block_delete_training ON training_sessions;
    CREATE TRIGGER trg_block_delete_training
    BEFORE DELETE ON training_sessions
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    -- Ajuste match_events: admin_note e audit de corre��o
    ALTER TABLE match_events ADD COLUMN IF NOT EXISTS admin_note text;

    CREATE OR REPLACE FUNCTION trg_match_events_correction_audit() RETURNS trigger AS $$
    BEGIN
      IF TG_OP = 'UPDATE' THEN
        IF NEW.admin_note IS NULL THEN
          RAISE EXCEPTION 'Corre��o de evento requer admin_note';
        END IF;
        PERFORM log_audit_event('match_event', NEW.id, 'update', NEW.admin_note,
          jsonb_build_object('old', row_to_json(OLD), 'new', row_to_json(NEW)));
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_match_events_correction_audit ON match_events;
    CREATE TRIGGER trg_match_events_correction_audit
    BEFORE UPDATE ON match_events
    FOR EACH ROW EXECUTE FUNCTION trg_match_events_correction_audit();;

UPDATE alembic_version SET version_num='d011c0ffee11' WHERE alembic_version.version_num = 'd010c0ffee10';

-- Running upgrade d011c0ffee11 -> d012c0ffee12

-- 1) audit_logs: adicionar actor_user_id
    ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS actor_user_id uuid;
    ALTER TABLE audit_logs
      ADD CONSTRAINT fk_audit_logs_actor FOREIGN KEY (actor_user_id) REFERENCES users(id);

    -- 2) Atualizar log_audit_event para capturar ator de current_setting
    CREATE OR REPLACE FUNCTION log_audit_event(p_entity text, p_entity_id uuid, p_action text, p_just text, p_context jsonb) RETURNS void AS $$
    DECLARE v_actor uuid;
    BEGIN
      BEGIN
        v_actor := current_setting('app.current_user', true)::uuid;
      EXCEPTION WHEN others THEN
        v_actor := NULL;
      END;

      INSERT INTO audit_logs(entity, entity_id, action, justification, context, actor_user_id)
      VALUES (p_entity, p_entity_id, p_action, p_just, p_context, v_actor);
    END;
    $$ LANGUAGE plpgsql;

    -- 3) Soft delete extra em persons, athletes, membership, team_registrations, match_events
    ALTER TABLE persons ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE persons ADD COLUMN IF NOT EXISTS deleted_reason text;
    ALTER TABLE athletes ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE athletes ADD COLUMN IF NOT EXISTS deleted_reason text;
    ALTER TABLE membership ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE membership ADD COLUMN IF NOT EXISTS deleted_reason text;
    ALTER TABLE team_registrations ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE team_registrations ADD COLUMN IF NOT EXISTS deleted_reason text;
    ALTER TABLE match_events ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE match_events ADD COLUMN IF NOT EXISTS deleted_reason text;

    -- Unicidade ignorando registros com soft delete
    DROP INDEX IF EXISTS uq_membership_org_person_season;
    CREATE UNIQUE INDEX IF NOT EXISTS uq_membership_org_person_season
      ON membership(organization_id, person_id, season_id)
      WHERE deleted_at IS NULL;

    ALTER TABLE team_registrations DROP CONSTRAINT IF EXISTS team_registrations_athlete_id_season_id_category_id_key;
    CREATE UNIQUE INDEX IF NOT EXISTS uq_team_reg_active_athlete_season_category
      ON team_registrations(athlete_id, season_id, category_id)
      WHERE deleted_at IS NULL;

    DO $$
    DECLARE r_dir int; r_coord int; r_tre int; r_atl int;
    BEGIN
      SELECT id INTO r_dir FROM roles WHERE code = 'dirigente';
      SELECT id INTO r_coord FROM roles WHERE code = 'coordenador';
      SELECT id INTO r_tre FROM roles WHERE code = 'treinador';
      SELECT id INTO r_atl FROM roles WHERE code = 'atleta';

      EXECUTE 'DROP INDEX IF EXISTS uq_membership_staff_active_person';
      EXECUTE format(
        'CREATE UNIQUE INDEX uq_membership_staff_active_person ON membership(person_id) WHERE status = %L AND deleted_at IS NULL AND role_id IN (%s,%s,%s)',
        'ativo', r_dir, r_coord, r_tre
      );

      EXECUTE 'DROP INDEX IF EXISTS uq_membership_athlete_active_season';
      EXECUTE format(
        'CREATE UNIQUE INDEX uq_membership_athlete_active_season ON membership(person_id, season_id) WHERE status = %L AND deleted_at IS NULL AND role_id = %s',
        'ativo', r_atl
      );
    END$$;

    -- Fun��o gen�rica para soft delete audit�vel
    CREATE OR REPLACE FUNCTION trg_soft_delete_generic() RETURNS trigger AS $$
    BEGIN
      IF TG_OP = 'UPDATE' THEN
        IF NEW.deleted_at IS DISTINCT FROM OLD.deleted_at OR NEW.deleted_reason IS DISTINCT FROM OLD.deleted_reason THEN
          IF NEW.deleted_at IS NOT NULL AND NEW.deleted_reason IS NULL THEN
            RAISE EXCEPTION 'Exclus�o l�gica requer deleted_reason';
          END IF;
          PERFORM log_audit_event(TG_TABLE_NAME, NEW.id, 'soft_delete', NEW.deleted_reason, jsonb_build_object('deleted_at', NEW.deleted_at));
        END IF;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Aplicar triggers de soft delete gen�rica
    DROP TRIGGER IF EXISTS trg_soft_delete_persons ON persons;
    CREATE TRIGGER trg_soft_delete_persons
    BEFORE UPDATE ON persons
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();

    DROP TRIGGER IF EXISTS trg_soft_delete_athletes ON athletes;
    CREATE TRIGGER trg_soft_delete_athletes
    BEFORE UPDATE ON athletes
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();

    DROP TRIGGER IF EXISTS trg_soft_delete_membership ON membership;
    CREATE TRIGGER trg_soft_delete_membership
    BEFORE UPDATE ON membership
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();

    DROP TRIGGER IF EXISTS trg_soft_delete_team_reg ON team_registrations;
    CREATE TRIGGER trg_soft_delete_team_reg
    BEFORE UPDATE ON team_registrations
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();

    DROP TRIGGER IF EXISTS trg_soft_delete_match_events ON match_events;
    CREATE TRIGGER trg_soft_delete_match_events
    BEFORE UPDATE ON match_events
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();

    -- 4) Bloqueio de DELETE f�sico nas tabelas adicionais
    DROP TRIGGER IF EXISTS trg_block_delete_persons ON persons;
    CREATE TRIGGER trg_block_delete_persons
    BEFORE DELETE ON persons
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    DROP TRIGGER IF EXISTS trg_block_delete_athletes ON athletes;
    CREATE TRIGGER trg_block_delete_athletes
    BEFORE DELETE ON athletes
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    DROP TRIGGER IF EXISTS trg_block_delete_membership ON membership;
    CREATE TRIGGER trg_block_delete_membership
    BEFORE DELETE ON membership
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    DROP TRIGGER IF EXISTS trg_block_delete_team_reg ON team_registrations;
    CREATE TRIGGER trg_block_delete_team_reg
    BEFORE DELETE ON team_registrations
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    DROP TRIGGER IF EXISTS trg_block_delete_match_events ON match_events;
    CREATE TRIGGER trg_block_delete_match_events
    BEFORE DELETE ON match_events
    FOR EACH ROW EXECUTE FUNCTION block_delete();;

UPDATE alembic_version SET version_num='d012c0ffee12' WHERE alembic_version.version_num = 'd011c0ffee11';

-- Running upgrade d012c0ffee12 -> d013c0ffee13

-- Flag para permitir reabertura de jogo com justificativa
    ALTER TABLE matches ADD COLUMN IF NOT EXISTS allow_reopen boolean NOT NULL DEFAULT false;

    -- Reescrever lock de jogos finalizados: s� permite update se allow_reopen=true e admin_note presente
    CREATE OR REPLACE FUNCTION trg_matches_lock_finished() RETURNS trigger AS $$
    BEGIN
      IF OLD.status = 'finished' THEN
        IF NEW.status <> OLD.status THEN
          IF NEW.allow_reopen IS FALSE OR NEW.admin_note IS NULL THEN
            RAISE EXCEPTION 'Reabertura de jogo requer allow_reopen=true e admin_note';
          END IF;
        ELSE
          IF NEW.allow_reopen IS FALSE OR NEW.admin_note IS NULL THEN
            RAISE EXCEPTION 'Jogo finalizado n�o pode ser alterado (exceto reabertura com admin_note)';
          END IF;
        END IF;
      END IF;
      IF OLD.status = 'finished' THEN
        PERFORM log_audit_event(
          'match',
          NEW.id,
          'edit_finished',
          NEW.admin_note,
          jsonb_build_object('old', row_to_json(OLD), 'new', row_to_json(NEW))
        );
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Ajustar controle de status com auditoria de reabertura
    CREATE OR REPLACE FUNCTION trg_matches_status_controls() RETURNS trigger AS $$
    BEGIN
      IF NEW.status IS DISTINCT FROM OLD.status THEN
        IF NEW.admin_note IS NULL THEN
          RAISE EXCEPTION 'Mudan�a de status de jogo requer admin_note';
        END IF;
        IF OLD.status = 'finished' AND NEW.status <> 'finished' THEN
          IF NEW.allow_reopen IS FALSE THEN
            RAISE EXCEPTION 'Reabertura de jogo requer allow_reopen=true';
          END IF;
          PERFORM log_audit_event('match', NEW.id, 'status_reopen', NEW.admin_note, jsonb_build_object('old_status', OLD.status, 'new_status', NEW.status));
        ELSIF NEW.status = 'finished' AND OLD.status <> 'finished' THEN
          NEW.finalized_at := COALESCE(NEW.finalized_at, now());
          NEW.validated_at := COALESCE(NEW.validated_at, now());
        END IF;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Reescrever fun��o gen�rica de soft delete para auditar reativa��o (deleted_at volta a NULL)
    CREATE OR REPLACE FUNCTION trg_soft_delete_generic() RETURNS trigger AS $$
    BEGIN
      IF TG_OP = 'UPDATE' THEN
        IF (NEW.deleted_at IS DISTINCT FROM OLD.deleted_at) OR (NEW.deleted_reason IS DISTINCT FROM OLD.deleted_reason) THEN
          IF NEW.deleted_at IS NOT NULL THEN
            IF NEW.deleted_reason IS NULL THEN
              RAISE EXCEPTION 'Exclus�o l�gica requer deleted_reason';
            END IF;
            PERFORM log_audit_event(TG_TABLE_NAME, NEW.id, 'soft_delete', NEW.deleted_reason, jsonb_build_object('deleted_at', NEW.deleted_at));
          ELSIF OLD.deleted_at IS NOT NULL AND NEW.deleted_at IS NULL THEN
            PERFORM log_audit_event(TG_TABLE_NAME, NEW.id, 'reactivate', NULL, jsonb_build_object('reactivated_at', now()));
          END IF;
        END IF;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Auditoria de reativa��o de membership (status volta a 'ativo')
    CREATE OR REPLACE FUNCTION trg_membership_reactivate_audit() RETURNS trigger AS $$
    BEGIN
      IF OLD.status <> 'ativo' AND NEW.status = 'ativo' THEN
        PERFORM log_audit_event('membership', NEW.id, 'reactivate', NULL, jsonb_build_object('old_status', OLD.status, 'season_id', NEW.season_id));
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_membership_reactivate_audit ON membership;
    CREATE TRIGGER trg_membership_reactivate_audit
    AFTER UPDATE ON membership
    FOR EACH ROW EXECUTE FUNCTION trg_membership_reactivate_audit();

    -- Fun��o helper para app: bloquear opera��o sem membership ativo (exceto superadmin)
    CREATE OR REPLACE FUNCTION ensure_active_membership(p_user uuid) RETURNS void AS $$
    DECLARE v_super boolean;
    DECLARE v_has_active boolean;
    DECLARE v_person uuid;
    BEGIN
      SELECT is_superadmin, person_id INTO v_super, v_person FROM users WHERE id = p_user;
      IF v_super THEN
        RETURN;
      END IF;

      SELECT EXISTS (
        SELECT 1 FROM membership m
        WHERE m.person_id = v_person
          AND m.status = 'ativo'
      ) INTO v_has_active;

      IF NOT v_has_active THEN
        RAISE EXCEPTION 'Usu�rio sem v�nculo ativo';
      END IF;
    END;
    $$ LANGUAGE plpgsql;;

UPDATE alembic_version SET version_num='d013c0ffee13' WHERE alembic_version.version_num = 'd012c0ffee12';

-- Running upgrade d013c0ffee13 -> d014c0ffee14

-- audit_logs: immutable
    CREATE OR REPLACE FUNCTION block_audit_logs_mutation() RETURNS trigger AS $$
    BEGIN
      RAISE EXCEPTION 'audit_logs is immutable';
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_audit_logs_immutable ON audit_logs;
    CREATE TRIGGER trg_audit_logs_immutable
    BEFORE UPDATE OR DELETE ON audit_logs
    FOR EACH ROW EXECUTE FUNCTION block_audit_logs_mutation();

    -- soft delete expansion
    ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_users ON users;
    CREATE TRIGGER trg_soft_delete_users
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_users ON users;
    CREATE TRIGGER trg_block_delete_users
    BEFORE DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    ALTER TABLE organizations ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE organizations ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_organizations ON organizations;
    CREATE TRIGGER trg_soft_delete_organizations
    BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_organizations ON organizations;
    CREATE TRIGGER trg_block_delete_organizations
    BEFORE DELETE ON organizations
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    ALTER TABLE competitions ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE competitions ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_competitions ON competitions;
    CREATE TRIGGER trg_soft_delete_competitions
    BEFORE UPDATE ON competitions
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_competitions ON competitions;
    CREATE TRIGGER trg_block_delete_competitions
    BEFORE DELETE ON competitions
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    ALTER TABLE competition_seasons ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE competition_seasons ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_competition_seasons ON competition_seasons;
    CREATE TRIGGER trg_soft_delete_competition_seasons
    BEFORE UPDATE ON competition_seasons
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_competition_seasons ON competition_seasons;
    CREATE TRIGGER trg_block_delete_competition_seasons
    BEFORE DELETE ON competition_seasons
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    ALTER TABLE seasons ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE seasons ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_seasons ON seasons;
    CREATE TRIGGER trg_soft_delete_seasons
    BEFORE UPDATE ON seasons
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_seasons ON seasons;
    CREATE TRIGGER trg_block_delete_seasons
    BEFORE DELETE ON seasons
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    ALTER TABLE categories ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE categories ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_categories ON categories;
    CREATE TRIGGER trg_soft_delete_categories
    BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_categories ON categories;
    CREATE TRIGGER trg_block_delete_categories
    BEFORE DELETE ON categories
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    ALTER TABLE teams ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE teams ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_teams ON teams;
    CREATE TRIGGER trg_soft_delete_teams
    BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_teams ON teams;
    CREATE TRIGGER trg_block_delete_teams
    BEFORE DELETE ON teams
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    ALTER TABLE attendance ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE attendance ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_attendance ON attendance;
    CREATE TRIGGER trg_soft_delete_attendance
    BEFORE UPDATE ON attendance
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_attendance ON attendance;
    CREATE TRIGGER trg_block_delete_attendance
    BEFORE DELETE ON attendance
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    ALTER TABLE attendance DROP CONSTRAINT IF EXISTS attendance_session_id_athlete_id_key;
    CREATE UNIQUE INDEX IF NOT EXISTS uq_attendance_active_session_athlete
      ON attendance(session_id, athlete_id)
      WHERE deleted_at IS NULL;

    ALTER TABLE wellness_pre ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE wellness_pre ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_wellness_pre ON wellness_pre;
    CREATE TRIGGER trg_soft_delete_wellness_pre
    BEFORE UPDATE ON wellness_pre
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_wellness_pre ON wellness_pre;
    CREATE TRIGGER trg_block_delete_wellness_pre
    BEFORE DELETE ON wellness_pre
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    ALTER TABLE wellness_pre DROP CONSTRAINT IF EXISTS wellness_pre_session_id_athlete_id_key;
    CREATE UNIQUE INDEX IF NOT EXISTS uq_wellness_pre_active_session_athlete
      ON wellness_pre(session_id, athlete_id)
      WHERE deleted_at IS NULL;

    ALTER TABLE wellness_post ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE wellness_post ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_wellness_post ON wellness_post;
    CREATE TRIGGER trg_soft_delete_wellness_post
    BEFORE UPDATE ON wellness_post
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_wellness_post ON wellness_post;
    CREATE TRIGGER trg_block_delete_wellness_post
    BEFORE DELETE ON wellness_post
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    ALTER TABLE wellness_post DROP CONSTRAINT IF EXISTS wellness_post_session_id_athlete_id_key;
    CREATE UNIQUE INDEX IF NOT EXISTS uq_wellness_post_active_session_athlete
      ON wellness_post(session_id, athlete_id)
      WHERE deleted_at IS NULL;

    ALTER TABLE medical_cases ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE medical_cases ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_medical_cases ON medical_cases;
    CREATE TRIGGER trg_soft_delete_medical_cases
    BEFORE UPDATE ON medical_cases
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_medical_cases ON medical_cases;
    CREATE TRIGGER trg_block_delete_medical_cases
    BEFORE DELETE ON medical_cases
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    ALTER TABLE roles ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE roles ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_roles ON roles;
    CREATE TRIGGER trg_soft_delete_roles
    BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_roles ON roles;
    CREATE TRIGGER trg_block_delete_roles
    BEFORE DELETE ON roles
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    ALTER TABLE permissions ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE permissions ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP TRIGGER IF EXISTS trg_soft_delete_permissions ON permissions;
    CREATE TRIGGER trg_soft_delete_permissions
    BEFORE UPDATE ON permissions
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_permissions ON permissions;
    CREATE TRIGGER trg_block_delete_permissions
    BEFORE DELETE ON permissions
    FOR EACH ROW EXECUTE FUNCTION block_delete();;

UPDATE alembic_version SET version_num='d014c0ffee14' WHERE alembic_version.version_num = 'd013c0ffee13';

-- Running upgrade d014c0ffee14 -> d015c0ffee15

-- match_roster soft delete + uniqueness for active rows
    ALTER TABLE match_roster ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE match_roster ADD COLUMN IF NOT EXISTS deleted_reason text;
    ALTER TABLE match_roster DROP CONSTRAINT IF EXISTS match_roster_match_id_athlete_id_key;
    CREATE UNIQUE INDEX IF NOT EXISTS uq_match_roster_active_match_athlete
      ON match_roster(match_id, athlete_id)
      WHERE deleted_at IS NULL;
    DROP TRIGGER IF EXISTS trg_soft_delete_match_roster ON match_roster;
    CREATE TRIGGER trg_soft_delete_match_roster
    BEFORE UPDATE ON match_roster
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_match_roster ON match_roster;
    CREATE TRIGGER trg_block_delete_match_roster
    BEFORE DELETE ON match_roster
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    -- match_teams soft delete + uniqueness for active rows
    ALTER TABLE match_teams ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE match_teams ADD COLUMN IF NOT EXISTS deleted_reason text;
    ALTER TABLE match_teams DROP CONSTRAINT IF EXISTS match_teams_match_id_side_key;
    ALTER TABLE match_teams DROP CONSTRAINT IF EXISTS match_teams_match_id_team_id_key;
    CREATE UNIQUE INDEX IF NOT EXISTS uq_match_teams_active_match_side
      ON match_teams(match_id, side)
      WHERE deleted_at IS NULL;
    CREATE UNIQUE INDEX IF NOT EXISTS uq_match_teams_active_match_team
      ON match_teams(match_id, team_id)
      WHERE deleted_at IS NULL;
    DROP TRIGGER IF EXISTS trg_soft_delete_match_teams ON match_teams;
    CREATE TRIGGER trg_soft_delete_match_teams
    BEFORE UPDATE ON match_teams
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_match_teams ON match_teams;
    CREATE TRIGGER trg_block_delete_match_teams
    BEFORE DELETE ON match_teams
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    -- athlete_states soft delete + active index ignores deleted rows
    ALTER TABLE athlete_states ADD COLUMN IF NOT EXISTS deleted_at timestamptz;
    ALTER TABLE athlete_states ADD COLUMN IF NOT EXISTS deleted_reason text;
    DROP INDEX IF EXISTS uq_athlete_states_active;
    CREATE UNIQUE INDEX uq_athlete_states_active
      ON athlete_states(athlete_id)
      WHERE ended_at IS NULL AND deleted_at IS NULL;
    DROP TRIGGER IF EXISTS trg_soft_delete_athlete_states ON athlete_states;
    CREATE TRIGGER trg_soft_delete_athlete_states
    BEFORE UPDATE ON athlete_states
    FOR EACH ROW EXECUTE FUNCTION trg_soft_delete_generic();
    DROP TRIGGER IF EXISTS trg_block_delete_athlete_states ON athlete_states;
    CREATE TRIGGER trg_block_delete_athlete_states
    BEFORE DELETE ON athlete_states
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    -- role_permissions: current state with revoked_at
    ALTER TABLE role_permissions ADD COLUMN IF NOT EXISTS revoked_at timestamptz;
    ALTER TABLE role_permissions ADD COLUMN IF NOT EXISTS revoked_reason text;
    ALTER TABLE role_permissions ADD COLUMN IF NOT EXISTS admin_note text;

    CREATE OR REPLACE FUNCTION trg_role_permissions_audit() RETURNS trigger AS $$
    BEGIN
      IF NEW.role_id IS DISTINCT FROM OLD.role_id OR NEW.permission_id IS DISTINCT FROM OLD.permission_id THEN
        RAISE EXCEPTION 'role_permissions nao permite mudar role_id/permission_id';
      END IF;

      IF NEW.admin_note IS NULL THEN
        RAISE EXCEPTION 'role_permissions update requer admin_note';
      END IF;

      IF NEW.revoked_at IS DISTINCT FROM OLD.revoked_at OR NEW.revoked_reason IS DISTINCT FROM OLD.revoked_reason THEN
        IF NEW.revoked_at IS NOT NULL AND NEW.revoked_reason IS NULL THEN
          RAISE EXCEPTION 'Revogacao de permissao requer revoked_reason';
        END IF;

        IF NEW.revoked_at IS NOT NULL AND OLD.revoked_at IS NULL THEN
          PERFORM log_audit_event(
            'role_permission',
            NULL,
            'revoke',
            NEW.admin_note,
            jsonb_build_object(
              'role_id', NEW.role_id,
              'permission_id', NEW.permission_id,
              'revoked_at', NEW.revoked_at,
              'revoked_reason', NEW.revoked_reason
            )
          );
        ELSIF NEW.revoked_at IS NULL AND OLD.revoked_at IS NOT NULL THEN
          NEW.revoked_reason := NULL;
          PERFORM log_audit_event(
            'role_permission',
            NULL,
            'reactivate',
            NEW.admin_note,
            jsonb_build_object(
              'role_id', NEW.role_id,
              'permission_id', NEW.permission_id,
              'reactivated_at', now()
            )
          );
        ELSE
          PERFORM log_audit_event(
            'role_permission',
            NULL,
            'revoke_update',
            NEW.admin_note,
            jsonb_build_object(
              'role_id', NEW.role_id,
              'permission_id', NEW.permission_id,
              'old_revoked_at', OLD.revoked_at,
              'new_revoked_at', NEW.revoked_at,
              'old_revoked_reason', OLD.revoked_reason,
              'new_revoked_reason', NEW.revoked_reason
            )
          );
        END IF;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_role_permissions_audit ON role_permissions;
    CREATE TRIGGER trg_role_permissions_audit
    BEFORE UPDATE ON role_permissions
    FOR EACH ROW EXECUTE FUNCTION trg_role_permissions_audit();

    DROP TRIGGER IF EXISTS trg_block_delete_role_permissions ON role_permissions;
    CREATE TRIGGER trg_block_delete_role_permissions
    BEFORE DELETE ON role_permissions
    FOR EACH ROW EXECUTE FUNCTION block_delete();

    -- update constraints to ignore soft-deleted rows
    CREATE OR REPLACE FUNCTION trg_match_roster_constraints() RETURNS trigger AS $$
    DECLARE v_count int;
    DECLARE v_status text;
    BEGIN
      SELECT status INTO v_status FROM matches WHERE id = NEW.match_id;
      IF v_status = 'finished' THEN
        RAISE EXCEPTION 'Jogo finalizado nao aceita alteracoes de roster';
      END IF;
      IF NEW.deleted_at IS NULL THEN
        SELECT count(*) INTO v_count
          FROM match_roster
         WHERE match_id = NEW.match_id
           AND deleted_at IS NULL
           AND id <> NEW.id;
        IF v_count >= 16 THEN
          RAISE EXCEPTION 'Roster do jogo atingiu o limite de 16 atletas';
        END IF;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION trg_match_events_constraints() RETURNS trigger AS $$
    DECLARE v_status text;
    DECLARE v_in_roster boolean;
    BEGIN
      SELECT status INTO v_status FROM matches WHERE id = NEW.match_id;
      IF v_status = 'finished' THEN
        RAISE EXCEPTION 'Jogo finalizado nao aceita eventos novos';
      END IF;

      IF NEW.athlete_id IS NOT NULL THEN
        SELECT EXISTS (
          SELECT 1 FROM match_roster
           WHERE match_id = NEW.match_id
             AND athlete_id = NEW.athlete_id
             AND deleted_at IS NULL
        ) INTO v_in_roster;
        IF NOT v_in_roster THEN
          RAISE EXCEPTION 'Evento requer atleta presente no roster do jogo';
        END IF;
      END IF;

      IF NEW.team_id IS NOT NULL THEN
        PERFORM 1 FROM match_teams
         WHERE match_id = NEW.match_id
           AND team_id = NEW.team_id
           AND deleted_at IS NULL;
        IF NOT FOUND THEN
          RAISE EXCEPTION 'Evento requer equipe presente no jogo';
        END IF;
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;;

UPDATE alembic_version SET version_num='d015c0ffee15' WHERE alembic_version.version_num = 'd014c0ffee14';

-- Running upgrade d015c0ffee15 -> d016c0ffee16

DROP VIEW IF EXISTS v_session_athlete_dashboard;
    CREATE VIEW v_session_athlete_dashboard AS
    SELECT
      ts.id              AS session_id,
      ts.session_at,
      ts.main_objective,
      ts.planned_load,
      ts.actual_load_avg,
      ts.group_climate,
      ts.highlight,
      ts.next_corrections,

      a.id               AS athlete_id,
      a.full_name,
      a.nickname,
      a.position,

      att.status         AS attendance_status,
      att.notes          AS attendance_notes,

      wpst.minutes,
      wpst.rpe,
      wpst.internal_load,
      wpst.fatigue_after,
      wpst.mood_after,
      wpst.notes         AS wellness_post_notes,

      to_jsonb(wpre)     AS wellness_pre_json,

      CASE att.status
        WHEN 'presente' THEN 'PRESENTE'
        WHEN 'ausente' THEN 'AUSENTE'
        WHEN 'medico' THEN 'DM'
        WHEN 'lesionada' THEN 'LESAO'
        ELSE 'OUTRO'
      END AS status_final,

      CASE
        WHEN att.status <> 'presente' THEN NULL
        WHEN wpst.minutes IS NOT NULL AND wpst.rpe IS NOT NULL THEN TRUE
        ELSE FALSE
      END AS load_ok

    FROM attendance att
    JOIN training_sessions ts
      ON ts.id = att.session_id
     AND ts.deleted_at IS NULL
    JOIN athletes a
      ON a.id = att.athlete_id
     AND a.deleted_at IS NULL
    LEFT JOIN wellness_post wpst
      ON wpst.session_id = att.session_id
     AND wpst.athlete_id = att.athlete_id
     AND wpst.deleted_at IS NULL
    LEFT JOIN wellness_pre wpre
      ON wpre.session_id = att.session_id
     AND wpre.athlete_id = att.athlete_id
     AND wpre.deleted_at IS NULL
    WHERE att.deleted_at IS NULL;

    DROP VIEW IF EXISTS public.v_training_session_summary;
    CREATE VIEW public.v_training_session_summary AS
    SELECT
      ts.id AS session_id,
      ts.session_at,
      ts.main_objective,

      COUNT(att.athlete_id)                                           AS total_registros,
      COUNT(*) FILTER (WHERE att.status = 'presente')                  AS presentes,
      COUNT(*) FILTER (WHERE att.status = 'ausente')                   AS ausentes,
      COUNT(*) FILTER (WHERE att.status = 'medico')                    AS dm,
      COUNT(*) FILTER (WHERE att.status = 'lesionada')                 AS lesionadas,

      AVG(wp.minutes) FILTER (WHERE att.status = 'presente')           AS avg_minutes,
      AVG(wp.rpe)     FILTER (WHERE att.status = 'presente')           AS avg_rpe,
      AVG(wp.internal_load) FILTER (WHERE att.status = 'presente')     AS avg_internal_load,

      COUNT(*) FILTER (
        WHERE att.status = 'presente'
          AND wp.minutes IS NOT NULL
          AND wp.rpe IS NOT NULL
      ) AS load_ok_count

    FROM public.training_sessions ts
    LEFT JOIN public.attendance att
      ON att.session_id = ts.id
     AND att.deleted_at IS NULL
    LEFT JOIN public.wellness_post wp
      ON wp.session_id = att.session_id
     AND wp.athlete_id = att.athlete_id
     AND wp.deleted_at IS NULL
    WHERE ts.deleted_at IS NULL
    GROUP BY ts.id, ts.session_at, ts.main_objective;;

UPDATE alembic_version SET version_num='d016c0ffee16' WHERE alembic_version.version_num = 'd015c0ffee15';

-- Running upgrade d016c0ffee16 -> d017c0ffee17

CREATE OR REPLACE FUNCTION ensure_user_active_membership() RETURNS trigger AS $$
    DECLARE v_has_active boolean;
    BEGIN
      IF NEW.is_superadmin THEN
        RETURN NEW;
      END IF;

      SELECT EXISTS (
        SELECT 1
          FROM membership m
         WHERE m.person_id = NEW.person_id
           AND m.status = 'ativo'
           AND m.deleted_at IS NULL
           AND m.start_date <= current_date
           AND (m.end_date IS NULL OR m.end_date >= current_date)
      ) INTO v_has_active;

      IF NOT v_has_active THEN
        RAISE EXCEPTION 'Usuario sem vinculo ativo';
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_users_require_active_membership ON users;
    CREATE CONSTRAINT TRIGGER trg_users_require_active_membership
    AFTER INSERT OR UPDATE ON users
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION ensure_user_active_membership();;

UPDATE alembic_version SET version_num='d017c0ffee17' WHERE alembic_version.version_num = 'd016c0ffee16';

-- Running upgrade d017c0ffee17 -> d018c0ffee18

-- 1) Overlap por person_id ignorando soft delete
    DROP TRIGGER IF EXISTS trg_membership_no_overlap ON membership;
    DROP FUNCTION IF EXISTS trg_membership_no_overlap;

    CREATE OR REPLACE FUNCTION trg_membership_no_overlap() RETURNS trigger AS $$
    DECLARE v_range daterange;
    BEGIN
      IF NEW.person_id IS NULL OR NEW.status <> 'ativo' OR NEW.deleted_at IS NOT NULL THEN
        RETURN NEW;
      END IF;

      v_range := daterange(
        COALESCE(NEW.start_date, current_date),
        COALESCE(NEW.end_date, 'infinity'::date),
        '[]'
      );

      IF EXISTS (
        SELECT 1
          FROM membership m
         WHERE m.person_id = NEW.person_id
           AND m.status = 'ativo'
           AND m.deleted_at IS NULL
           AND (NEW.id IS NULL OR m.id <> NEW.id)
           AND daterange(
                 COALESCE(m.start_date, current_date),
                 COALESCE(m.end_date, 'infinity'::date),
                 '[]'
               ) && v_range
      ) THEN
        RAISE EXCEPTION 'Vinculo ativo sobreposto para a pessoa';
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER trg_membership_no_overlap
    BEFORE INSERT OR UPDATE ON membership
    FOR EACH ROW EXECUTE FUNCTION trg_membership_no_overlap();

    -- 2) Bloquear usuario nao-superadmin sem vinculo ativo ao inativar/expirar membership
    CREATE OR REPLACE FUNCTION trg_membership_require_active_user() RETURNS trigger AS $$
    DECLARE v_has_user boolean;
    DECLARE v_has_superadmin boolean;
    DECLARE v_has_active boolean;
    BEGIN
      IF NEW.person_id IS NULL THEN
        RETURN NULL;
      END IF;

      IF NEW.status = 'ativo'
         AND NEW.deleted_at IS NULL
         AND (NEW.end_date IS NULL OR NEW.end_date >= current_date) THEN
        RETURN NULL;
      END IF;

      SELECT EXISTS (
        SELECT 1 FROM users u WHERE u.person_id = NEW.person_id
      ) INTO v_has_user;

      IF NOT v_has_user THEN
        RETURN NULL;
      END IF;

      SELECT EXISTS (
        SELECT 1 FROM users u WHERE u.person_id = NEW.person_id AND u.is_superadmin = true
      ) INTO v_has_superadmin;

      IF v_has_superadmin THEN
        RETURN NULL;
      END IF;

      SELECT EXISTS (
        SELECT 1
          FROM membership m
         WHERE m.person_id = NEW.person_id
           AND m.status = 'ativo'
           AND m.deleted_at IS NULL
           AND (m.end_date IS NULL OR m.end_date >= current_date)
           AND m.id <> NEW.id
      ) INTO v_has_active;

      IF NOT v_has_active THEN
        RAISE EXCEPTION 'Usuario sem vinculo ativo nao pode permanecer ativo';
      END IF;

      RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_membership_require_active_user ON membership;
    CREATE CONSTRAINT TRIGGER trg_membership_require_active_user
    AFTER UPDATE OF status, end_date, deleted_at ON membership
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION trg_membership_require_active_user();;

UPDATE alembic_version SET version_num='d018c0ffee18' WHERE alembic_version.version_num = 'd017c0ffee17';

-- Running upgrade d018c0ffee18 -> 3e2898989f01

UPDATE alembic_version SET version_num='3e2898989f01' WHERE alembic_version.version_num = 'd018c0ffee18';

-- Running upgrade 3e2898989f01 -> d019c0ffee19

-- RF5.1: Canceled timestamp
        ALTER TABLE public.seasons
        ADD COLUMN IF NOT EXISTS canceled_at timestamptz;

        -- RF5.2: Interrupted timestamp
        ALTER TABLE public.seasons
        ADD COLUMN IF NOT EXISTS interrupted_at timestamptz;

        -- RDB4: Soft delete columns
        ALTER TABLE public.seasons
        ADD COLUMN IF NOT EXISTS deleted_at timestamptz;

        ALTER TABLE public.seasons
        ADD COLUMN IF NOT EXISTS deleted_reason text;

        -- Add comment for documentation
        COMMENT ON COLUMN public.seasons.canceled_at IS 'RF5.1: Timestamp when season was canceled';
        COMMENT ON COLUMN public.seasons.interrupted_at IS 'RF5.2: Timestamp when season was interrupted';
        COMMENT ON COLUMN public.seasons.deleted_at IS 'RDB4: Soft delete timestamp';
        COMMENT ON COLUMN public.seasons.deleted_reason IS 'RDB4: Reason for soft delete';;

UPDATE alembic_version SET version_num='d019c0ffee19' WHERE alembic_version.version_num = '3e2898989f01';

-- Running upgrade d019c0ffee19 -> d020c0ffee20

ALTER TABLE team_registrations ADD COLUMN start_at DATE;

ALTER TABLE team_registrations ADD COLUMN end_at DATE;

UPDATE team_registrations 
        SET start_at = COALESCE(created_at::date, CURRENT_DATE) 
        WHERE start_at IS NULL;

ALTER TABLE team_registrations ALTER COLUMN start_at SET NOT NULL;

ALTER TABLE team_registrations ADD CONSTRAINT ck_team_registrations_date_range_valid CHECK (end_at IS NULL OR start_at <= end_at);

CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE team_registrations
        ADD CONSTRAINT ex_team_registrations_no_overlap
        EXCLUDE USING gist (
            athlete_id WITH =,
            team_id WITH =,
            season_id WITH =,
            daterange(start_at, COALESCE(end_at, start_at), '[]') WITH &&
        ) WHERE deleted_at IS NULL;

CREATE INDEX ix_team_registrations_ctx ON team_registrations (athlete_id, team_id, season_id);

CREATE INDEX ix_team_registrations_range ON team_registrations (start_at, end_at);

UPDATE alembic_version SET version_num='d020c0ffee20' WHERE alembic_version.version_num = 'd019c0ffee19';

-- Running upgrade d020c0ffee20 -> d021c0ffee21

DROP INDEX IF EXISTS uq_team_reg_active_athlete_season_category;

CREATE UNIQUE INDEX uq_team_reg_active_athlete_team_season
        ON team_registrations(athlete_id, team_id, season_id)
        WHERE end_at IS NULL AND deleted_at IS NULL;;

UPDATE alembic_version SET version_num='d021c0ffee21' WHERE alembic_version.version_num = 'd020c0ffee20';

-- Running upgrade d021c0ffee21 -> 4af09f9d46a0

-- V_SEASONS_WITH_STATUS: Status derivado de temporadas conforme RAG 6.1.1
        CREATE OR REPLACE VIEW v_seasons_with_status AS
        SELECT
            s.*,
            CASE
                -- cancelada: campo cancelado preenchido
                WHEN s.canceled_at IS NOT NULL THEN 'cancelada'

                -- encerrada: passou da data de fim (independente de interrup��o)
                WHEN (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date > s.ends_at THEN 'encerrada'

                -- interrompida: campo interrompido preenchido e n�o cancelada
                WHEN s.interrupted_at IS NOT NULL THEN 'interrompida'

                -- ativa: dentro do per�odo e n�o interrompida/cancelada
                WHEN s.starts_at <= (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date
             AND (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date <= s.ends_at THEN 'ativa'

                -- planejada: antes do in�cio e n�o cancelada
                WHEN (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date < s.starts_at THEN 'planejada'

                -- fallback (n�o deveria ocorrer)
                ELSE 'desconhecido'
            END AS status_derivado,

            -- Flags booleanos para facilitar queries
            (s.canceled_at IS NOT NULL) AS is_canceled,
            (s.interrupted_at IS NOT NULL) AS is_interrupted,
            (s.starts_at <= (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date
             AND (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date <= s.ends_at
             AND s.canceled_at IS NULL AND s.interrupted_at IS NULL) AS is_active,
            ((CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date < s.starts_at AND s.canceled_at IS NULL) AS is_planned,
            ((CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date > s.ends_at) AS is_finished

        FROM public.seasons s
        WHERE s.deleted_at IS NULL;  -- N�o exibe temporadas deletadas logicamente

        COMMENT ON VIEW v_seasons_with_status IS
        'VIEW com status derivado de temporadas conforme RAG V1.1 se��o 6.1.1.
        Status poss�veis: planejada, ativa, interrompida, cancelada, encerrada.
        Considera campos canceled_at (RF5.1), interrupted_at (RF5.2) e datas do per�odo.
        Performance: recalcula status em tempo real; usar �ndices em starts_at/ends_at.';;

COMMENT ON FUNCTION enforce_single_superadmin() IS
'Trigger: Garante existencia de exatamente 1 Super Administrador no sistema. REF RAG: R3, RDB6. Bloqueia DELETE/UPDATE que remova o ultimo is_superadmin=true.';

COMMENT ON FUNCTION block_audit_logs_mutation() IS
'Trigger: Torna audit_logs absolutamente imutavel (append-only). REF RAG: R35, RDB5. Bloqueia UPDATE e DELETE.';

COMMENT ON FUNCTION block_delete() IS
'Trigger: Bloqueia DELETE fisico em matches/training_sessions. REF RAG: R29, RDB4. Forcando uso de deleted_at/deleted_reason.';

COMMENT ON FUNCTION sync_athlete_state_current() IS
'Trigger: Sincroniza estado atual da atleta apos insercao em athlete_states. REF RAG: R13, R14.';

COMMENT ON FUNCTION close_active_athlete_state() IS
'Trigger: Encerra estado ativo anterior ao inserir novo estado de atleta. REF RAG: R13. Garante 1 estado ativo por atleta.';

COMMENT ON FUNCTION trg_athlete_state_dispense_membership() IS
'Trigger: Ao marcar atleta dispensada, encerra team_registrations ativos. REF RAG: R13 V1.1, RDB10.';

COMMENT ON FUNCTION trg_membership_no_overlap() IS
'Trigger: Bloqueia sobreposicao temporal de vinculos ativos para mesmo usuario. REF RAG: R7, RDB9.';

COMMENT ON FUNCTION enforce_active_membership_for_users() IS
'Trigger: Garante que usuario (exceto superadmin) tenha vinculo ativo. REF RAG: R42, RF3.';

COMMENT ON FUNCTION trg_matches_status_controls() IS
'Trigger: Controla mudancas de status de jogos e exige justificativa. REF RAG: RD8, RF15 V1.1.';

COMMENT ON FUNCTION trg_match_roster_finalized_block() IS
'Trigger: Bloqueia alteracoes em match_roster se jogo esta finalizado. REF RAG: RD8, R19.';

COMMENT ON FUNCTION trg_match_events_finalized_block() IS
'Trigger: Bloqueia novos eventos em jogos finalizados. REF RAG: RD8, R19.';

COMMENT ON FUNCTION trg_match_events_correction_audit() IS
'Trigger: Exige admin_note obrigatorio ao corrigir estatisticas de jogo. REF RAG: R23, R24, RDB12.';

COMMENT ON FUNCTION trg_team_registrations_age_check() IS
'Trigger: Valida regra etaria obrigatoria para participacao em categorias. REF RAG: RD2, RD3, R16.';

COMMENT ON FUNCTION trg_soft_delete_reason_required() IS
'Trigger: Garante que deleted_reason e obrigatorio quando deleted_at e preenchido. REF RAG: RDB4.';

COMMENT ON FUNCTION public.set_updated_at() IS
'Atualiza coluna updated_at a cada UPDATE. Base das colunas temporais (RDB3).';

COMMENT ON FUNCTION public.set_internal_load_wellness_post() IS
'Calcula carga interna (minutes * rpe) em wellness_post antes de INSERT/UPDATE (metricas de treino R22).';

COMMENT ON FUNCTION public.trg_membership_no_overlap() IS
'Bloqueia sobreposicao de vinculos ativos por usuario (staff). Garante exclusividade de membership (R7, RDB9).';

COMMENT ON FUNCTION public.enforce_single_superadmin() IS
'Impede remocao/alteracao do ultimo superadmin. Garante unicidade e imutabilidade (R3, RDB6).';

COMMENT ON FUNCTION public.close_active_athlete_state() IS
'Fecha estado ativo anterior da atleta ao inserir novo registro de estado (R13: historico imutavel).';

COMMENT ON FUNCTION public.sync_athlete_state_current() IS
'Sincroniza o estado atual da atleta na tabela athletes apos inserir novo estado (R13).';

COMMENT ON FUNCTION public.trg_athlete_state_dispense_membership() IS
'Dispensa atleta: encerra vinculos ativos (membership e team_registrations) e registra auditoria (R13 V1.1, RP9, R35).';

COMMENT ON FUNCTION public.age_in_years(date, date) IS
'Idade em anos completos na data de referencia (RD1, RD2).';

COMMENT ON FUNCTION public.trg_team_registrations_age_check() IS
'Valida idade minima da categoria em team_registrations; nao bloqueia atuar acima (RD16, RDB11).';

COMMENT ON FUNCTION public.trg_membership_require_team() IS
'Exige pelo menos uma equipe na temporada para membership de atleta; CONSTRAINT TRIGGER DEFERRABLE (R38, RP18).';

COMMENT ON FUNCTION public.trg_training_sessions_lock() IS
'Bloqueia edicao de treino apos 24h; permite com admin_note quando aplicavel (R40, RDB13).';

COMMENT ON FUNCTION public.trg_matches_lock_finished() IS
'Bloqueia edicao de jogo finalizado (RF15, RDB13).';

COMMENT ON FUNCTION public.trg_match_roster_constraints() IS
'Limite maximo de 16 atletas no roster e bloqueio se jogo finalizado (RD18, RF14).';

COMMENT ON FUNCTION public.trg_match_events_constraints() IS
'Eventos exigem atleta no roster e equipe presente; jogo nao pode estar finalizado (RD4, RD20, RF14).';

COMMENT ON FUNCTION public.log_audit_event(text, uuid, text, text, jsonb) IS
'Insere log de auditoria inutavel: quem, quando, acao, contexto (R31, R32, R35, RDB5).';

COMMENT ON FUNCTION public.trg_matches_status_controls() IS
'Exige admin_note ao mudar status; marca finalized_at/validated_at em finished (RF14/RF15, RD85, RDB13).';

UPDATE alembic_version SET version_num='4af09f9d46a0' WHERE alembic_version.version_num = 'd021c0ffee21';

COMMIT;

