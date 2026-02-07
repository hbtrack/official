--
-- PostgreSQL database dump
--

\restrict R0Tiyv2c1Gqb6RtZvhCLRx3WBg9KkM6448C0Zv7TgfWaLbJA8qxPFrw1AQ4YCiL

-- Dumped from database version 17.7 (bdc8956)
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: app; Type: SCHEMA; Schema: -; Owner: neondb_owner
--

CREATE SCHEMA app;


ALTER SCHEMA app OWNER TO neondb_owner;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'RDB1: Extensão para funções criptográficas, incluindo gen_random_uuid() usado em PKs UUID.';


--
-- Name: current_user(); Type: FUNCTION; Schema: app; Owner: neondb_owner
--

CREATE FUNCTION app."current_user"() RETURNS uuid
    LANGUAGE plpgsql STABLE
    AS $$
        BEGIN
            -- Retorna o user_id do contexto da sessão
            -- Backend deve setar isso via: SET LOCAL app.current_user_id = '<uuid>';
            RETURN current_setting('app.current_user_id', true)::UUID;
        EXCEPTION
            WHEN OTHERS THEN
                RETURN NULL;
        END;
        $$;


ALTER FUNCTION app."current_user"() OWNER TO neondb_owner;

--
-- Name: FUNCTION "current_user"(); Type: COMMENT; Schema: app; Owner: neondb_owner
--

COMMENT ON FUNCTION app."current_user"() IS 'Função auxiliar: retorna UUID do usuário atual do contexto da sessão. Backend seta via SET LOCAL.';


--
-- Name: trg_auto_end_team_registrations_on_dispensada(); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.trg_auto_end_team_registrations_on_dispensada() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            -- Se mudou de 'ativa' ou 'arquivada' para 'dispensada'
            IF OLD.state != 'dispensada' AND NEW.state = 'dispensada' THEN
                -- Encerra todos os team_registrations ativos desta atleta
                UPDATE team_registrations
                SET
                    end_at = now(),
                    updated_at = now()
                WHERE
                    athlete_id = NEW.id
                    AND end_at IS NULL
                    AND deleted_at IS NULL;

                -- Log: registra quantos vínculos foram encerrados
                RAISE NOTICE 'Atleta % mudou para dispensada. % team_registrations ativos foram encerrados automaticamente.',
                    NEW.id,
                    (SELECT COUNT(*) FROM team_registrations WHERE athlete_id = NEW.id AND end_at = now()::date);
            END IF;

            RETURN NEW;
        END;
        $$;


ALTER FUNCTION public.trg_auto_end_team_registrations_on_dispensada() OWNER TO neondb_owner;

--
-- Name: FUNCTION trg_auto_end_team_registrations_on_dispensada(); Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON FUNCTION public.trg_auto_end_team_registrations_on_dispensada() IS 'RDB18.6: Encerra automaticamente todos team_registrations ativos quando atleta muda para state=dispensada.';


--
-- Name: trg_block_audit_logs_modification(); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.trg_block_audit_logs_modification() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            RAISE EXCEPTION 'audit_logs é append-only. UPDATE e DELETE são bloqueados. Operação tentada: %', TG_OP;
        END;
        $$;


ALTER FUNCTION public.trg_block_audit_logs_modification() OWNER TO neondb_owner;

--
-- Name: FUNCTION trg_block_audit_logs_modification(); Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON FUNCTION public.trg_block_audit_logs_modification() IS 'RDB18.5: Bloqueia UPDATE e DELETE em audit_logs. Tabela append-only, absolutamente imutável.';


--
-- Name: trg_block_finished_match_update(); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.trg_block_finished_match_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            -- Permite mudança de 'finished' para 'in_progress' (reabertura)
            IF OLD.status = 'finished' AND NEW.status != 'finished' THEN
                -- Permitir apenas mudança para 'in_progress' (reabertura)
                IF NEW.status = 'in_progress' THEN
                    -- Auditoria será feita pelo backend
                    RETURN NEW;
                ELSE
                    RAISE EXCEPTION 'Jogo finalizado só pode ser reaberto para status in_progress. Status atual: %, tentou mudar para: %',
                        OLD.status, NEW.status;
                END IF;
            END IF;

            -- Bloqueia qualquer UPDATE se status for 'finished' e não for reabertura
            IF OLD.status = 'finished' AND NEW.status = 'finished' THEN
                RAISE EXCEPTION 'Não é permitido alterar jogo com status finished. Use reabertura administrativa (status -> in_progress) para editar.';
            END IF;

            RETURN NEW;
        END;
        $$;


ALTER FUNCTION public.trg_block_finished_match_update() OWNER TO neondb_owner;

--
-- Name: FUNCTION trg_block_finished_match_update(); Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON FUNCTION public.trg_block_finished_match_update() IS 'RDB18.3: Bloqueia UPDATE em matches com status=finished. Exceção: reabertura para in_progress.';


--
-- Name: trg_block_physical_delete(); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.trg_block_physical_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            RAISE EXCEPTION 'DELETE físico bloqueado. Use soft delete (UPDATE deleted_at, deleted_reason) na tabela %.', TG_TABLE_NAME;
        END;
        $$;


ALTER FUNCTION public.trg_block_physical_delete() OWNER TO neondb_owner;

--
-- Name: FUNCTION trg_block_physical_delete(); Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON FUNCTION public.trg_block_physical_delete() IS 'RDB18.4: Bloqueia DELETE físico em tabelas com soft delete. Força uso de deleted_at + deleted_reason.';


--
-- Name: trg_set_athlete_age_at_registration(); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.trg_set_athlete_age_at_registration() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF NEW.birth_date IS NOT NULL AND NEW.registered_at IS NOT NULL THEN
                NEW.athlete_age_at_registration = EXTRACT(YEAR FROM AGE(NEW.registered_at, NEW.birth_date));
            END IF;
            RETURN NEW;
        END;
        $$;


ALTER FUNCTION public.trg_set_athlete_age_at_registration() OWNER TO neondb_owner;

--
-- Name: FUNCTION trg_set_athlete_age_at_registration(); Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON FUNCTION public.trg_set_athlete_age_at_registration() IS 'RDB18.2: Calcula automaticamente athlete_age_at_registration quando birth_date ou registered_at mudam.';


--
-- Name: trg_set_updated_at(); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.trg_set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$;


ALTER FUNCTION public.trg_set_updated_at() OWNER TO neondb_owner;

--
-- Name: FUNCTION trg_set_updated_at(); Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON FUNCTION public.trg_set_updated_at() IS 'RDB18.1: Atualiza automaticamente updated_at em todas as tabelas de domínio.';


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: neondb_owner
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO neondb_owner;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: advantage_states; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.advantage_states (
    code character varying(32) NOT NULL,
    delta_players smallint NOT NULL,
    description character varying(255)
);


ALTER TABLE public.advantage_states OWNER TO neondb_owner;

--
-- Name: TABLE advantage_states; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.advantage_states IS 'Estados de vantagem numérica. Lookup table.';


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO neondb_owner;

--
-- Name: athletes; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.athletes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    person_id uuid NOT NULL,
    state character varying(20) DEFAULT 'ativa'::character varying NOT NULL,
    injured boolean DEFAULT false NOT NULL,
    medical_restriction boolean DEFAULT false NOT NULL,
    suspended_until date,
    load_restricted boolean DEFAULT false NOT NULL,
    athlete_name character varying(100) NOT NULL,
    birth_date date NOT NULL,
    athlete_nickname character varying(50),
    shirt_number integer,
    main_defensive_position_id integer,
    secondary_defensive_position_id integer,
    main_offensive_position_id integer,
    secondary_offensive_position_id integer,
    schooling_id integer,
    guardian_name character varying(100),
    guardian_phone character varying(20),
    athlete_photo_path character varying(500),
    registered_at timestamp with time zone DEFAULT now() NOT NULL,
    athlete_age_at_registration integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    organization_id uuid,
    CONSTRAINT ck_athletes_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_athletes_shirt_number CHECK (((shirt_number IS NULL) OR ((shirt_number >= 1) AND (shirt_number <= 99)))),
    CONSTRAINT ck_athletes_state CHECK (((state)::text = ANY ((ARRAY['ativa'::character varying, 'dispensada'::character varying, 'arquivada'::character varying])::text[])))
);


ALTER TABLE public.athletes OWNER TO neondb_owner;

--
-- Name: TABLE athletes; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.athletes IS 'Atletas. V1.2: estado base + flags (injured, medical_restriction, suspended_until, load_restricted).';


--
-- Name: COLUMN athletes.athlete_photo_path; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.athletes.athlete_photo_path IS 'DEPRECATED (31/12/2025): Use person_media para fotos de atletas. Este campo será removido em versão futura. Novo fluxo: POST /api/v1/persons/{person_id}/media com media_type=profile_photo';


--
-- Name: attendance; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.attendance (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    training_session_id uuid NOT NULL,
    team_registration_id uuid NOT NULL,
    athlete_id uuid NOT NULL,
    presence_status character varying(32) NOT NULL,
    minutes_effective smallint,
    comment text,
    source character varying(32) DEFAULT 'manual'::character varying NOT NULL,
    participation_type character varying(32),
    reason_absence character varying(32),
    is_medical_restriction boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_user_id uuid NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    CONSTRAINT ck_attendance_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_attendance_participation_type CHECK (((participation_type IS NULL) OR ((participation_type)::text = ANY ((ARRAY['full'::character varying, 'partial'::character varying, 'adapted'::character varying, 'did_not_train'::character varying])::text[])))),
    CONSTRAINT ck_attendance_reason CHECK (((reason_absence IS NULL) OR ((reason_absence)::text = ANY ((ARRAY['medico'::character varying, 'escola'::character varying, 'familiar'::character varying, 'opcional'::character varying, 'outro'::character varying])::text[])))),
    CONSTRAINT ck_attendance_source CHECK (((source)::text = ANY ((ARRAY['manual'::character varying, 'import'::character varying, 'correction'::character varying])::text[]))),
    CONSTRAINT ck_attendance_status CHECK (((presence_status)::text = ANY ((ARRAY['present'::character varying, 'absent'::character varying])::text[])))
);


ALTER TABLE public.attendance OWNER TO neondb_owner;

--
-- Name: TABLE attendance; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.attendance IS 'Presença por treino. V1.2: sem convocação formal; lista gerada por team_registrations ativos.';


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.audit_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity character varying(64) NOT NULL,
    entity_id uuid,
    action character varying(64) NOT NULL,
    actor_id uuid,
    context jsonb,
    old_value jsonb,
    new_value jsonb,
    justification text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO neondb_owner;

--
-- Name: TABLE audit_logs; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.audit_logs IS 'Logs de auditoria. R35: absolutamente imutável (RDB5: append-only).';


--
-- Name: categories; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    max_age integer NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT ck_categories_max_age_positive CHECK ((max_age > 0))
);


ALTER TABLE public.categories OWNER TO neondb_owner;

--
-- Name: TABLE categories; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.categories IS 'Categorias esportivas. V1.2: sem min_age, apenas max_age.';


--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO neondb_owner;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: defensive_positions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.defensive_positions (
    id integer NOT NULL,
    code character varying(32) NOT NULL,
    name character varying(64) NOT NULL,
    abbreviation character varying(10),
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.defensive_positions OWNER TO neondb_owner;

--
-- Name: TABLE defensive_positions; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.defensive_positions IS 'Posições defensivas. RD13: ID=5 é Goleira.';


--
-- Name: defensive_positions_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.defensive_positions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.defensive_positions_id_seq OWNER TO neondb_owner;

--
-- Name: defensive_positions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.defensive_positions_id_seq OWNED BY public.defensive_positions.id;


--
-- Name: email_queue; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.email_queue (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    template_type character varying(50) NOT NULL,
    to_email character varying(255) NOT NULL,
    template_data jsonb NOT NULL,
    status character varying(20) NOT NULL,
    attempts integer NOT NULL,
    max_attempts integer NOT NULL,
    next_retry_at timestamp with time zone,
    last_error text,
    sent_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_user_id uuid
);


ALTER TABLE public.email_queue OWNER TO neondb_owner;

--
-- Name: TABLE email_queue; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.email_queue IS 'Fila de emails com retry automático';


--
-- Name: COLUMN email_queue.template_type; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.email_queue.template_type IS 'invite, welcome, reset_password';


--
-- Name: COLUMN email_queue.template_data; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.email_queue.template_data IS 'Dados dinâmicos do template';


--
-- Name: COLUMN email_queue.status; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.email_queue.status IS 'pending, sent, failed, cancelled';


--
-- Name: COLUMN email_queue.attempts; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.email_queue.attempts IS 'Número de tentativas';


--
-- Name: COLUMN email_queue.max_attempts; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.email_queue.max_attempts IS 'Máximo de tentativas';


--
-- Name: COLUMN email_queue.next_retry_at; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.email_queue.next_retry_at IS 'Próxima tentativa';


--
-- Name: COLUMN email_queue.last_error; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.email_queue.last_error IS 'Última mensagem de erro';


--
-- Name: COLUMN email_queue.sent_at; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.email_queue.sent_at IS 'Quando foi enviado';


--
-- Name: event_subtypes; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.event_subtypes (
    code character varying(64) NOT NULL,
    event_type_code character varying(64) NOT NULL,
    description character varying(255) NOT NULL
);


ALTER TABLE public.event_subtypes OWNER TO neondb_owner;

--
-- Name: TABLE event_subtypes; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.event_subtypes IS 'Subtipos de evento (shot_6m, shot_9m, shot_wing, turnover_pass, etc.).';


--
-- Name: event_types; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.event_types (
    code character varying(64) NOT NULL,
    description character varying(255) NOT NULL,
    is_shot boolean NOT NULL,
    is_possession_ending boolean NOT NULL
);


ALTER TABLE public.event_types OWNER TO neondb_owner;

--
-- Name: TABLE event_types; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.event_types IS 'Tipos de evento (shot, goal, goalkeeper_save, turnover, foul, etc.).';


--
-- Name: idempotency_keys; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.idempotency_keys (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    key character varying(255) NOT NULL,
    endpoint character varying(255) NOT NULL,
    request_hash character varying(64) NOT NULL,
    response_json jsonb,
    status_code integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.idempotency_keys OWNER TO neondb_owner;

--
-- Name: TABLE idempotency_keys; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.idempotency_keys IS 'Controle de idempotência para retry seguro. FICHA.MD Fase 1.2';


--
-- Name: COLUMN idempotency_keys.key; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.idempotency_keys.key IS 'Chave única de idempotência fornecida pelo cliente (geralmente UUID)';


--
-- Name: COLUMN idempotency_keys.endpoint; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.idempotency_keys.endpoint IS 'Endpoint da API onde a chave foi utilizada';


--
-- Name: COLUMN idempotency_keys.request_hash; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.idempotency_keys.request_hash IS 'Hash SHA-256 do payload para validar consistência';


--
-- Name: COLUMN idempotency_keys.response_json; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.idempotency_keys.response_json IS 'Resposta completa para replay em caso de retry';


--
-- Name: COLUMN idempotency_keys.status_code; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.idempotency_keys.status_code IS 'Código HTTP da resposta armazenada';


--
-- Name: COLUMN idempotency_keys.created_at; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.idempotency_keys.created_at IS 'Data/hora do registro (para limpeza periódica)';


--
-- Name: match_attendance; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.match_attendance (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    match_id uuid NOT NULL,
    match_roster_id uuid NOT NULL,
    athlete_id uuid NOT NULL,
    played boolean DEFAULT false NOT NULL,
    minutes_played smallint,
    started boolean,
    comment text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_user_id uuid NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    CONSTRAINT ck_match_attendance_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_match_attendance_minutes CHECK (((minutes_played IS NULL) OR ((minutes_played >= 0) AND (minutes_played <= 80))))
);


ALTER TABLE public.match_attendance OWNER TO neondb_owner;

--
-- Name: match_events; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.match_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    match_id uuid NOT NULL,
    team_id uuid NOT NULL,
    opponent_team_id uuid,
    athlete_id uuid,
    assisting_athlete_id uuid,
    secondary_athlete_id uuid,
    period_number smallint NOT NULL,
    game_time_seconds integer NOT NULL,
    phase_of_play character varying(32) NOT NULL,
    possession_id uuid,
    advantage_state character varying(32) NOT NULL,
    score_our smallint NOT NULL,
    score_opponent smallint NOT NULL,
    event_type character varying(64) NOT NULL,
    event_subtype character varying(64),
    outcome character varying(64) NOT NULL,
    is_shot boolean NOT NULL,
    is_goal boolean NOT NULL,
    x_coord numeric(5,2),
    y_coord numeric(5,2),
    related_event_id uuid,
    source character varying(32) NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_user_id uuid NOT NULL,
    CONSTRAINT ck_match_events_period CHECK ((period_number >= 1)),
    CONSTRAINT ck_match_events_score_opponent CHECK ((score_opponent >= 0)),
    CONSTRAINT ck_match_events_score_our CHECK ((score_our >= 0)),
    CONSTRAINT ck_match_events_source CHECK (((source)::text = ANY ((ARRAY['live'::character varying, 'video'::character varying, 'post_game_correction'::character varying])::text[]))),
    CONSTRAINT ck_match_events_time CHECK ((game_time_seconds >= 0)),
    CONSTRAINT ck_match_events_x_coord CHECK (((x_coord IS NULL) OR ((x_coord >= (0)::numeric) AND (x_coord <= (100)::numeric)))),
    CONSTRAINT ck_match_events_y_coord CHECK (((y_coord IS NULL) OR ((y_coord >= (0)::numeric) AND (y_coord <= (100)::numeric))))
);


ALTER TABLE public.match_events OWNER TO neondb_owner;

--
-- Name: TABLE match_events; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.match_events IS 'Eventos de jogo lance a lance. Coração analítico: reconstrói jogo, contexto tático e gera estatísticas.';


--
-- Name: match_periods; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.match_periods (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    match_id uuid NOT NULL,
    number smallint NOT NULL,
    duration_seconds integer NOT NULL,
    period_type character varying(32) NOT NULL,
    CONSTRAINT ck_match_periods_duration CHECK ((duration_seconds > 0)),
    CONSTRAINT ck_match_periods_number CHECK ((number >= 1)),
    CONSTRAINT ck_match_periods_type CHECK (((period_type)::text = ANY ((ARRAY['regular'::character varying, 'extra_time'::character varying, 'shootout_7m'::character varying])::text[])))
);


ALTER TABLE public.match_periods OWNER TO neondb_owner;

--
-- Name: TABLE match_periods; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.match_periods IS 'Estrutura de tempo dos jogos (1º tempo, 2º tempo, prorrogação, 7m).';


--
-- Name: match_possessions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.match_possessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    match_id uuid NOT NULL,
    team_id uuid NOT NULL,
    start_period_number smallint NOT NULL,
    start_time_seconds integer NOT NULL,
    end_period_number smallint NOT NULL,
    end_time_seconds integer NOT NULL,
    start_score_our smallint NOT NULL,
    start_score_opponent smallint NOT NULL,
    end_score_our smallint NOT NULL,
    end_score_opponent smallint NOT NULL,
    result character varying(32) NOT NULL,
    CONSTRAINT ck_match_possessions_end_period CHECK ((end_period_number >= start_period_number)),
    CONSTRAINT ck_match_possessions_end_time CHECK ((end_time_seconds >= 0)),
    CONSTRAINT ck_match_possessions_result CHECK (((result)::text = ANY ((ARRAY['goal'::character varying, 'turnover'::character varying, 'seven_meter_won'::character varying, 'time_over'::character varying])::text[]))),
    CONSTRAINT ck_match_possessions_start_period CHECK ((start_period_number >= 1)),
    CONSTRAINT ck_match_possessions_start_time CHECK ((start_time_seconds >= 0))
);


ALTER TABLE public.match_possessions OWNER TO neondb_owner;

--
-- Name: TABLE match_possessions; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.match_possessions IS 'Sequências de posse de bola. Base para análise tática de eficiência.';


--
-- Name: match_roster; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.match_roster (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    match_id uuid NOT NULL,
    team_id uuid NOT NULL,
    athlete_id uuid NOT NULL,
    jersey_number smallint NOT NULL,
    is_starting boolean,
    is_goalkeeper boolean NOT NULL,
    is_available boolean NOT NULL,
    notes text,
    CONSTRAINT ck_match_roster_jersey CHECK ((jersey_number > 0))
);


ALTER TABLE public.match_roster OWNER TO neondb_owner;

--
-- Name: TABLE match_roster; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.match_roster IS 'Súmula/convocação oficial. Define quais atletas estão elegíveis para o jogo.';


--
-- Name: match_teams; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.match_teams (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    match_id uuid NOT NULL,
    team_id uuid NOT NULL,
    is_home boolean NOT NULL,
    is_our_team boolean NOT NULL
);


ALTER TABLE public.match_teams OWNER TO neondb_owner;

--
-- Name: TABLE match_teams; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.match_teams IS 'Ponte jogo ↔ equipes. Identifica quais equipes jogaram e com qual papel.';


--
-- Name: matches; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.matches (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    season_id uuid NOT NULL,
    competition_id uuid,
    match_date date NOT NULL,
    start_time time without time zone,
    venue character varying(120),
    phase character varying(32) NOT NULL,
    status character varying(32) NOT NULL,
    home_team_id uuid NOT NULL,
    away_team_id uuid NOT NULL,
    our_team_id uuid NOT NULL,
    final_score_home smallint,
    final_score_away smallint,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_user_id uuid NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    CONSTRAINT ck_matches_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_matches_different_teams CHECK ((home_team_id <> away_team_id)),
    CONSTRAINT ck_matches_our_team CHECK (((our_team_id = home_team_id) OR (our_team_id = away_team_id))),
    CONSTRAINT ck_matches_phase CHECK (((phase)::text = ANY ((ARRAY['group'::character varying, 'semifinal'::character varying, 'final'::character varying, 'friendly'::character varying])::text[]))),
    CONSTRAINT ck_matches_score_away CHECK (((final_score_away IS NULL) OR (final_score_away >= 0))),
    CONSTRAINT ck_matches_score_home CHECK (((final_score_home IS NULL) OR (final_score_home >= 0))),
    CONSTRAINT ck_matches_status CHECK (((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in_progress'::character varying, 'finished'::character varying, 'cancelled'::character varying])::text[])))
);


ALTER TABLE public.matches OWNER TO neondb_owner;

--
-- Name: TABLE matches; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.matches IS 'Jogos oficiais. Ponto de partida para convocação, súmula, eventos, estatísticas e relatórios.';


--
-- Name: medical_cases; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.medical_cases (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    athlete_id uuid NOT NULL,
    reason character varying(500),
    status character varying(50) DEFAULT 'ativo'::character varying,
    notes text,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    ended_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    organization_id uuid,
    created_by_user_id uuid,
    CONSTRAINT ck_medical_cases_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT medical_cases_status_check CHECK (((status)::text = ANY ((ARRAY['ativo'::character varying, 'resolvido'::character varying, 'em_acompanhamento'::character varying])::text[])))
);


ALTER TABLE public.medical_cases OWNER TO neondb_owner;

--
-- Name: TABLE medical_cases; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.medical_cases IS 'Casos médicos de atletas. V1.2: RDB4 compliant (soft delete + deleted_reason).';


--
-- Name: team_registrations; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.team_registrations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    athlete_id uuid NOT NULL,
    team_id uuid NOT NULL,
    start_at timestamp with time zone DEFAULT now() NOT NULL,
    end_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    created_by_user_id uuid,
    CONSTRAINT ck_team_registrations_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL))))
);


ALTER TABLE public.team_registrations OWNER TO neondb_owner;

--
-- Name: TABLE team_registrations; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.team_registrations IS 'Vínculos de atletas com equipes. V1.2: múltiplos vínculos ativos simultâneos permitidos.';


--
-- Name: teams; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.teams (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    organization_id uuid NOT NULL,
    name character varying(120) NOT NULL,
    category_id integer NOT NULL,
    gender character varying(16) NOT NULL,
    is_our_team boolean DEFAULT true NOT NULL,
    active_from date,
    active_until date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_user_id uuid,
    deleted_at timestamp with time zone,
    deleted_reason text,
    CONSTRAINT ck_teams_active_dates CHECK (((active_from IS NULL) OR (active_until IS NULL) OR (active_from <= active_until))),
    CONSTRAINT ck_teams_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_teams_gender CHECK (((gender)::text = ANY ((ARRAY['masculino'::character varying, 'feminino'::character varying])::text[])))
);


ALTER TABLE public.teams OWNER TO neondb_owner;

--
-- Name: TABLE teams; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.teams IS 'Equipes esportivas. V1.2: sem season_id; gender obrigatório.';


--
-- Name: training_sessions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.training_sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    organization_id uuid NOT NULL,
    team_id uuid,
    season_id uuid,
    session_at timestamp with time zone NOT NULL,
    duration_planned_minutes smallint,
    location character varying(120),
    session_type character varying(32) NOT NULL,
    main_objective character varying(255),
    secondary_objective text,
    planned_load smallint,
    group_climate smallint,
    notes text,
    phase_focus_defense boolean DEFAULT false,
    phase_focus_attack boolean DEFAULT false,
    phase_focus_transition_offense boolean DEFAULT false,
    phase_focus_transition_defense boolean DEFAULT false,
    intensity_target smallint,
    session_block character varying(32),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_user_id uuid NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    focus_attack_positional_pct numeric(5,2),
    focus_defense_positional_pct numeric(5,2),
    focus_transition_offense_pct numeric(5,2),
    focus_transition_defense_pct numeric(5,2),
    focus_attack_technical_pct numeric(5,2),
    focus_defense_technical_pct numeric(5,2),
    focus_physical_pct numeric(5,2),
    microcycle_id uuid,
    status character varying DEFAULT '''draft'''::character varying NOT NULL,
    closed_at timestamp with time zone,
    closed_by_user_id uuid,
    deviation_justification text,
    planning_deviation_flag boolean DEFAULT false NOT NULL,
    CONSTRAINT check_training_session_status CHECK (((status)::text = ANY ((ARRAY['draft'::character varying, 'in_progress'::character varying, 'closed'::character varying, 'readonly'::character varying])::text[]))),
    CONSTRAINT ck_training_sessions_climate CHECK (((group_climate IS NULL) OR ((group_climate >= 1) AND (group_climate <= 5)))),
    CONSTRAINT ck_training_sessions_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_training_sessions_focus_attack_positional_range CHECK (((focus_attack_positional_pct IS NULL) OR ((focus_attack_positional_pct >= (0)::numeric) AND (focus_attack_positional_pct <= (100)::numeric)))),
    CONSTRAINT ck_training_sessions_focus_attack_technical_range CHECK (((focus_attack_technical_pct IS NULL) OR ((focus_attack_technical_pct >= (0)::numeric) AND (focus_attack_technical_pct <= (100)::numeric)))),
    CONSTRAINT ck_training_sessions_focus_defense_positional_range CHECK (((focus_defense_positional_pct IS NULL) OR ((focus_defense_positional_pct >= (0)::numeric) AND (focus_defense_positional_pct <= (100)::numeric)))),
    CONSTRAINT ck_training_sessions_focus_defense_technical_range CHECK (((focus_defense_technical_pct IS NULL) OR ((focus_defense_technical_pct >= (0)::numeric) AND (focus_defense_technical_pct <= (100)::numeric)))),
    CONSTRAINT ck_training_sessions_focus_physical_range CHECK (((focus_physical_pct IS NULL) OR ((focus_physical_pct >= (0)::numeric) AND (focus_physical_pct <= (100)::numeric)))),
    CONSTRAINT ck_training_sessions_focus_total_sum CHECK ((((((((COALESCE(focus_attack_positional_pct, (0)::numeric) + COALESCE(focus_defense_positional_pct, (0)::numeric)) + COALESCE(focus_transition_offense_pct, (0)::numeric)) + COALESCE(focus_transition_defense_pct, (0)::numeric)) + COALESCE(focus_attack_technical_pct, (0)::numeric)) + COALESCE(focus_defense_technical_pct, (0)::numeric)) + COALESCE(focus_physical_pct, (0)::numeric)) <= (120)::numeric)),
    CONSTRAINT ck_training_sessions_focus_transition_defense_range CHECK (((focus_transition_defense_pct IS NULL) OR ((focus_transition_defense_pct >= (0)::numeric) AND (focus_transition_defense_pct <= (100)::numeric)))),
    CONSTRAINT ck_training_sessions_focus_transition_offense_range CHECK (((focus_transition_offense_pct IS NULL) OR ((focus_transition_offense_pct >= (0)::numeric) AND (focus_transition_offense_pct <= (100)::numeric)))),
    CONSTRAINT ck_training_sessions_intensity CHECK (((intensity_target IS NULL) OR ((intensity_target >= 1) AND (intensity_target <= 5)))),
    CONSTRAINT ck_training_sessions_type CHECK (((session_type)::text = ANY ((ARRAY['quadra'::character varying, 'fisico'::character varying, 'video'::character varying, 'reuniao'::character varying, 'teste'::character varying])::text[])))
);


ALTER TABLE public.training_sessions OWNER TO neondb_owner;

--
-- Name: TABLE training_sessions; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.training_sessions IS 'Treinos. V1.2: team_id e season_id opcionais (treinos organizacionais, avaliações, captação).';


--
-- Name: COLUMN training_sessions.focus_attack_positional_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.focus_attack_positional_pct IS 'Percentual aproximado (0-100) do tempo dedicado ao foco Ataque Posicionado. Usado em análise estratégica /statistics/teams.';


--
-- Name: COLUMN training_sessions.focus_defense_positional_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.focus_defense_positional_pct IS 'Percentual aproximado (0-100) do tempo dedicado ao foco Defesa Posicionada. Usado em análise estratégica /statistics/teams.';


--
-- Name: COLUMN training_sessions.focus_transition_offense_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.focus_transition_offense_pct IS 'Percentual aproximado (0-100) do tempo dedicado ao foco Transição Ofensiva. Usado em análise estratégica /statistics/teams.';


--
-- Name: COLUMN training_sessions.focus_transition_defense_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.focus_transition_defense_pct IS 'Percentual aproximado (0-100) do tempo dedicado ao foco Transição Defensiva. Usado em análise estratégica /statistics/teams.';


--
-- Name: COLUMN training_sessions.focus_attack_technical_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.focus_attack_technical_pct IS 'Percentual aproximado (0-100) do tempo dedicado ao foco Ataque Técnico. Usado em análise estratégica /statistics/teams.';


--
-- Name: COLUMN training_sessions.focus_defense_technical_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.focus_defense_technical_pct IS 'Percentual aproximado (0-100) do tempo dedicado ao foco Defesa Técnica. Usado em análise estratégica /statistics/teams.';


--
-- Name: COLUMN training_sessions.focus_physical_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.focus_physical_pct IS 'Percentual aproximado (0-100) do tempo dedicado ao foco Treino Físico. Usado em análise estratégica /statistics/teams.';


--
-- Name: COLUMN training_sessions.microcycle_id; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.microcycle_id IS 'FK para microciclo (planejamento semanal)';


--
-- Name: COLUMN training_sessions.status; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.status IS 'Estado: draft, in_progress, closed, readonly';


--
-- Name: COLUMN training_sessions.closed_at; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.closed_at IS 'Timestamp de fechamento';


--
-- Name: COLUMN training_sessions.closed_by_user_id; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.closed_by_user_id IS 'Usuário que fechou a sessão';


--
-- Name: COLUMN training_sessions.deviation_justification; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.deviation_justification IS 'Justificativa de desvio em relação ao planejamento';


--
-- Name: COLUMN training_sessions.planning_deviation_flag; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_sessions.planning_deviation_flag IS 'Flag de desvio significativo (≥20pts ou ≥30% agregado)';


--
-- Name: mv_athlete_summary; Type: MATERIALIZED VIEW; Schema: public; Owner: neondb_owner
--

CREATE MATERIALIZED VIEW public.mv_athlete_summary AS
 SELECT ath.id AS athlete_id,
    ath.person_id,
    ath.athlete_name,
    ath.birth_date,
    ath.state,
    ath.injured,
    ath.medical_restriction,
    ath.suspended_until,
    ath.load_restricted,
    ath.main_defensive_position_id,
    ( SELECT t.organization_id
           FROM (public.teams t
             JOIN public.team_registrations tr2 ON ((tr2.team_id = t.id)))
          WHERE ((tr2.athlete_id = ath.id) AND (tr2.end_at IS NULL) AND (tr2.deleted_at IS NULL))
         LIMIT 1) AS organization_id,
    count(DISTINCT a.training_session_id) AS total_sessions,
    count(DISTINCT
        CASE
            WHEN ((a.presence_status)::text = 'present'::text) THEN a.training_session_id
            ELSE NULL::uuid
        END) AS sessions_present,
    count(DISTINCT
        CASE
            WHEN ((a.presence_status)::text = 'absent'::text) THEN a.training_session_id
            ELSE NULL::uuid
        END) AS sessions_absent,
        CASE
            WHEN (count(DISTINCT a.training_session_id) > 0) THEN round((((count(DISTINCT
            CASE
                WHEN ((a.presence_status)::text = 'present'::text) THEN a.training_session_id
                ELSE NULL::uuid
            END))::numeric / (count(DISTINCT a.training_session_id))::numeric) * (100)::numeric), 2)
            ELSE (0)::numeric
        END AS attendance_rate,
    COALESCE(avg(a.minutes_effective) FILTER (WHERE ((a.presence_status)::text = 'present'::text)), (0)::numeric) AS avg_minutes_per_session,
    COALESCE(sum(a.minutes_effective) FILTER (WHERE ((a.presence_status)::text = 'present'::text)), (0)::bigint) AS total_minutes,
    max(ts.session_at) FILTER (WHERE ((a.presence_status)::text = 'present'::text)) AS last_session_date,
    ath.created_at,
    ath.updated_at
   FROM ((public.athletes ath
     LEFT JOIN public.attendance a ON (((a.athlete_id = ath.id) AND (a.deleted_at IS NULL))))
     LEFT JOIN public.training_sessions ts ON (((a.training_session_id = ts.id) AND (ts.deleted_at IS NULL))))
  WHERE (ath.deleted_at IS NULL)
  GROUP BY ath.id, ath.person_id, ath.athlete_name, ath.birth_date, ath.state, ath.injured, ath.medical_restriction, ath.suspended_until, ath.load_restricted, ath.main_defensive_position_id, ath.created_at, ath.updated_at
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_athlete_summary OWNER TO neondb_owner;

--
-- Name: offensive_positions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.offensive_positions (
    id integer NOT NULL,
    code character varying(32) NOT NULL,
    name character varying(64) NOT NULL,
    abbreviation character varying(10),
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.offensive_positions OWNER TO neondb_owner;

--
-- Name: TABLE offensive_positions; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.offensive_positions IS 'Posições ofensivas.';


--
-- Name: mv_athlete_training_summary; Type: MATERIALIZED VIEW; Schema: public; Owner: neondb_owner
--

CREATE MATERIALIZED VIEW public.mv_athlete_training_summary AS
 SELECT id AS athlete_id,
    person_id,
    athlete_name AS full_name,
    athlete_nickname AS nickname,
    birth_date,
    (EXTRACT(year FROM age((CURRENT_DATE)::timestamp with time zone, (birth_date)::timestamp with time zone)))::integer AS current_age,
    ( SELECT t.organization_id
           FROM (public.team_registrations tr
             JOIN public.teams t ON ((t.id = tr.team_id)))
          WHERE ((tr.athlete_id = a.id) AND (tr.end_at IS NULL))
         LIMIT 1) AS organization_id,
    state AS current_state,
    NULL::uuid AS current_season_id,
    ( SELECT tr.team_id
           FROM public.team_registrations tr
          WHERE ((tr.athlete_id = a.id) AND (tr.end_at IS NULL))
         LIMIT 1) AS current_team_id,
    ( SELECT op.name
           FROM public.offensive_positions op
          WHERE (op.id = a.main_offensive_position_id)) AS "position",
    NULL::character varying AS expected_category_code,
    0 AS total_sessions,
    0 AS sessions_presente,
    0 AS sessions_ausente,
    0 AS sessions_dm,
    0 AS sessions_lesionada,
    0.0 AS attendance_rate,
    NULL::timestamp without time zone AS last_session_at,
    NULL::numeric AS avg_sleep_hours,
    NULL::numeric AS avg_sleep_quality,
    NULL::numeric AS avg_fatigue_pre,
    NULL::numeric AS avg_stress,
    NULL::numeric AS avg_muscle_soreness,
    NULL::numeric AS last_sleep_hours,
    NULL::numeric AS last_fatigue,
    NULL::numeric AS avg_fatigue_after,
    NULL::numeric AS avg_mood_after,
    NULL::numeric AS avg_internal_load,
    NULL::numeric AS avg_rpe,
    NULL::numeric AS avg_minutes,
    NULL::numeric AS load_7d,
    NULL::numeric AS load_28d,
    NULL::numeric AS last_internal_load,
    (COALESCE(( SELECT count(*) AS count
           FROM public.medical_cases mc
          WHERE ((mc.athlete_id = a.id) AND ((mc.status)::text = 'ativo'::text) AND (mc.deleted_at IS NULL))), (0)::bigint))::integer AS active_medical_cases
   FROM public.athletes a
  WHERE (deleted_at IS NULL)
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_athlete_training_summary OWNER TO neondb_owner;

--
-- Name: mv_medical_summary; Type: MATERIALIZED VIEW; Schema: public; Owner: neondb_owner
--

CREATE MATERIALIZED VIEW public.mv_medical_summary AS
 SELECT t.organization_id,
    tr.team_id,
    count(DISTINCT
        CASE
            WHEN (ath.injured = true) THEN ath.id
            ELSE NULL::uuid
        END) AS injured_count,
    count(DISTINCT
        CASE
            WHEN (ath.medical_restriction = true) THEN ath.id
            ELSE NULL::uuid
        END) AS medical_restriction_count,
    count(DISTINCT
        CASE
            WHEN ((ath.suspended_until IS NOT NULL) AND (ath.suspended_until > CURRENT_DATE)) THEN ath.id
            ELSE NULL::uuid
        END) AS suspended_count,
    count(DISTINCT
        CASE
            WHEN (ath.load_restricted = true) THEN ath.id
            ELSE NULL::uuid
        END) AS load_restricted_count,
    count(DISTINCT
        CASE
            WHEN ((ath.state)::text = 'ativa'::text) THEN ath.id
            ELSE NULL::uuid
        END) AS active_athletes,
    count(DISTINCT
        CASE
            WHEN (((ath.state)::text = 'ativa'::text) AND (ath.injured = false) AND (ath.medical_restriction = false) AND ((ath.suspended_until IS NULL) OR (ath.suspended_until <= CURRENT_DATE))) THEN ath.id
            ELSE NULL::uuid
        END) AS fully_available_count,
    max(ath.updated_at) AS last_update
   FROM ((public.athletes ath
     JOIN public.team_registrations tr ON (((tr.athlete_id = ath.id) AND (tr.end_at IS NULL) AND (tr.deleted_at IS NULL))))
     JOIN public.teams t ON (((tr.team_id = t.id) AND (t.deleted_at IS NULL))))
  WHERE (ath.deleted_at IS NULL)
  GROUP BY t.organization_id, tr.team_id
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_medical_summary OWNER TO neondb_owner;

--
-- Name: mv_training_performance; Type: MATERIALIZED VIEW; Schema: public; Owner: neondb_owner
--

CREATE MATERIALIZED VIEW public.mv_training_performance AS
 SELECT ts.id AS session_id,
    ts.organization_id,
    ts.season_id,
    ts.team_id,
    ts.session_at,
    ts.main_objective,
    ts.planned_load,
    ts.group_climate,
    count(DISTINCT a.athlete_id) AS total_athletes,
    count(DISTINCT
        CASE
            WHEN ((a.presence_status)::text = 'present'::text) THEN a.athlete_id
            ELSE NULL::uuid
        END) AS presentes,
    count(DISTINCT
        CASE
            WHEN ((a.presence_status)::text = 'absent'::text) THEN a.athlete_id
            ELSE NULL::uuid
        END) AS ausentes,
    count(DISTINCT
        CASE
            WHEN ((ath.medical_restriction = true) AND ((a.presence_status)::text = 'present'::text)) THEN a.athlete_id
            ELSE NULL::uuid
        END) AS dm,
    count(DISTINCT
        CASE
            WHEN (ath.injured = true) THEN a.athlete_id
            ELSE NULL::uuid
        END) AS lesionadas,
        CASE
            WHEN (count(DISTINCT a.athlete_id) > 0) THEN round((((count(DISTINCT
            CASE
                WHEN ((a.presence_status)::text = 'present'::text) THEN a.athlete_id
                ELSE NULL::uuid
            END))::numeric / (count(DISTINCT a.athlete_id))::numeric) * (100)::numeric), 2)
            ELSE (0)::numeric
        END AS attendance_rate,
    COALESCE(avg(a.minutes_effective) FILTER (WHERE ((a.presence_status)::text = 'present'::text)), (0)::numeric) AS avg_minutes,
    COALESCE((ts.planned_load)::integer, 0) AS avg_rpe,
    COALESCE((((ts.planned_load)::numeric * COALESCE(avg(a.minutes_effective) FILTER (WHERE ((a.presence_status)::text = 'present'::text)), (0)::numeric)) / (10)::numeric), (0)::numeric) AS avg_internal_load,
    (0)::numeric AS stddev_internal_load,
    count(DISTINCT
        CASE
            WHEN ((a.presence_status)::text = 'present'::text) THEN a.athlete_id
            ELSE NULL::uuid
        END) AS load_ok_count,
        CASE
            WHEN (count(DISTINCT a.athlete_id) > 0) THEN round((((count(DISTINCT
            CASE
                WHEN (a.minutes_effective IS NOT NULL) THEN a.athlete_id
                ELSE NULL::uuid
            END))::numeric / (NULLIF(count(DISTINCT
            CASE
                WHEN ((a.presence_status)::text = 'present'::text) THEN a.athlete_id
                ELSE NULL::uuid
            END), 0))::numeric) * (100)::numeric), 2)
            ELSE (0)::numeric
        END AS data_completeness_pct,
    (0)::numeric AS avg_fatigue_after,
    (0)::numeric AS avg_mood_after,
    ts.created_at,
    ts.updated_at
   FROM ((public.training_sessions ts
     LEFT JOIN public.attendance a ON (((a.training_session_id = ts.id) AND (a.deleted_at IS NULL))))
     LEFT JOIN public.athletes ath ON (((a.athlete_id = ath.id) AND (ath.deleted_at IS NULL))))
  WHERE (ts.deleted_at IS NULL)
  GROUP BY ts.id, ts.organization_id, ts.season_id, ts.team_id, ts.session_at, ts.main_objective, ts.planned_load, ts.group_climate, ts.created_at, ts.updated_at
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_training_performance OWNER TO neondb_owner;

--
-- Name: mv_wellness_summary; Type: MATERIALIZED VIEW; Schema: public; Owner: neondb_owner
--

CREATE MATERIALIZED VIEW public.mv_wellness_summary AS
 SELECT ts.organization_id,
    ts.team_id,
    ts.season_id,
    date_trunc('week'::text, ts.session_at) AS week_start,
    count(DISTINCT ts.id) AS total_sessions,
    count(DISTINCT a.athlete_id) FILTER (WHERE ((a.presence_status)::text = 'present'::text)) AS unique_athletes,
    COALESCE(avg(ts.group_climate), (0)::numeric) AS avg_group_climate,
    (0)::numeric AS avg_fatigue_pre,
    (0)::numeric AS avg_fatigue_post,
    (0)::numeric AS avg_mood_pre,
    (0)::numeric AS avg_mood_post,
    (0)::numeric AS avg_sleep_quality,
    (0)::numeric AS avg_muscle_soreness,
    0 AS high_fatigue_count,
    0 AS low_mood_count,
    0 AS poor_sleep_count
   FROM (public.training_sessions ts
     LEFT JOIN public.attendance a ON (((a.training_session_id = ts.id) AND (a.deleted_at IS NULL))))
  WHERE (ts.deleted_at IS NULL)
  GROUP BY ts.organization_id, ts.team_id, ts.season_id, (date_trunc('week'::text, ts.session_at))
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_wellness_summary OWNER TO neondb_owner;

--
-- Name: offensive_positions_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.offensive_positions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.offensive_positions_id_seq OWNER TO neondb_owner;

--
-- Name: offensive_positions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.offensive_positions_id_seq OWNED BY public.offensive_positions.id;


--
-- Name: org_memberships; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.org_memberships (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    person_id uuid NOT NULL,
    role_id integer NOT NULL,
    organization_id uuid NOT NULL,
    start_at timestamp with time zone DEFAULT now() NOT NULL,
    end_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    created_by_user_id uuid,
    CONSTRAINT ck_org_memberships_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL))))
);


ALTER TABLE public.org_memberships OWNER TO neondb_owner;

--
-- Name: TABLE org_memberships; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.org_memberships IS 'Vínculos organizacionais (staff). V1.2: sem season_id; apenas org+person+role.';


--
-- Name: organizations; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.organizations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(100) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    CONSTRAINT ck_organizations_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL))))
);


ALTER TABLE public.organizations OWNER TO neondb_owner;

--
-- Name: TABLE organizations; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.organizations IS 'Clubes/organizações esportivas. V1.2: suporta múltiplos clubes desde V1.';


--
-- Name: password_resets; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.password_resets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    token text NOT NULL,
    token_type text DEFAULT 'reset'::text NOT NULL,
    used boolean DEFAULT false NOT NULL,
    used_at timestamp with time zone,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    CONSTRAINT ck_password_resets_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_password_resets_token_type CHECK ((token_type = ANY (ARRAY['reset'::text, 'welcome'::text])))
);


ALTER TABLE public.password_resets OWNER TO neondb_owner;

--
-- Name: TABLE password_resets; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.password_resets IS 'Email-based password reset tokens. R29: soft delete. Token expires in 24h.';


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.permissions (
    id smallint NOT NULL,
    code character varying(64) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.permissions OWNER TO neondb_owner;

--
-- Name: TABLE permissions; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.permissions IS 'R24: Permissões do sistema. Aplicadas via papéis através de role_permissions.';


--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.permissions_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permissions_id_seq OWNER TO neondb_owner;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: person_addresses; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.person_addresses (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    person_id uuid NOT NULL,
    address_type character varying(50) NOT NULL,
    street character varying(200) NOT NULL,
    number character varying(20),
    complement character varying(100),
    neighborhood character varying(100),
    city character varying(100) NOT NULL,
    state character varying(2) NOT NULL,
    postal_code character varying(10),
    country character varying(100) DEFAULT 'Brasil'::character varying NOT NULL,
    is_primary boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    created_by_user_id uuid,
    CONSTRAINT ck_person_addresses_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_person_addresses_type CHECK (((address_type)::text = ANY ((ARRAY['residencial_1'::character varying, 'residencial_2'::character varying, 'comercial'::character varying, 'outro'::character varying])::text[])))
);


ALTER TABLE public.person_addresses OWNER TO neondb_owner;

--
-- Name: TABLE person_addresses; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.person_addresses IS 'Endereços da pessoa. Suporta múltiplos endereços (residencial_1, residencial_2).';


--
-- Name: COLUMN person_addresses.created_by_user_id; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.person_addresses.created_by_user_id IS 'Usuário que criou o registro. R30/R31: auditoria obrigatória.';


--
-- Name: person_contacts; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.person_contacts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    person_id uuid NOT NULL,
    contact_type character varying(50) NOT NULL,
    contact_value character varying(200) NOT NULL,
    is_primary boolean DEFAULT false NOT NULL,
    is_verified boolean DEFAULT false NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    created_by_user_id uuid,
    CONSTRAINT ck_person_contacts_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_person_contacts_type CHECK (((contact_type)::text = ANY ((ARRAY['telefone'::character varying, 'email'::character varying, 'whatsapp'::character varying, 'outro'::character varying])::text[])))
);


ALTER TABLE public.person_contacts OWNER TO neondb_owner;

--
-- Name: TABLE person_contacts; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.person_contacts IS 'Contatos da pessoa (telefone, email, whatsapp). Suporta múltiplos contatos por pessoa.';


--
-- Name: COLUMN person_contacts.created_by_user_id; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.person_contacts.created_by_user_id IS 'Usuário que criou o registro. R30/R31: auditoria obrigatória.';


--
-- Name: person_documents; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.person_documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    person_id uuid NOT NULL,
    document_type character varying(50) NOT NULL,
    document_number character varying(100) NOT NULL,
    issuing_authority character varying(100),
    issue_date date,
    expiry_date date,
    document_file_url text,
    is_verified boolean DEFAULT false NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    created_by_user_id uuid,
    CONSTRAINT ck_person_documents_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_person_documents_type CHECK (((document_type)::text = ANY ((ARRAY['cpf'::character varying, 'rg'::character varying, 'cnh'::character varying, 'passaporte'::character varying, 'certidao_nascimento'::character varying, 'titulo_eleitor'::character varying, 'outro'::character varying])::text[])))
);


ALTER TABLE public.person_documents OWNER TO neondb_owner;

--
-- Name: TABLE person_documents; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.person_documents IS 'Documentos oficiais da pessoa (CPF, RG, CNH, passaporte).';


--
-- Name: COLUMN person_documents.created_by_user_id; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.person_documents.created_by_user_id IS 'Usuário que criou o registro. R30/R31: auditoria obrigatória.';


--
-- Name: person_media; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.person_media (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    person_id uuid NOT NULL,
    media_type character varying(50) NOT NULL,
    file_url text NOT NULL,
    file_name character varying(255),
    file_size integer,
    mime_type character varying(100),
    is_primary boolean DEFAULT false NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    created_by_user_id uuid,
    CONSTRAINT ck_person_media_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_person_media_type CHECK (((media_type)::text = ANY ((ARRAY['foto_perfil'::character varying, 'foto_documento'::character varying, 'video'::character varying, 'outro'::character varying])::text[])))
);


ALTER TABLE public.person_media OWNER TO neondb_owner;

--
-- Name: TABLE person_media; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.person_media IS 'Mídias da pessoa (fotos de perfil, documentos digitalizados).';


--
-- Name: COLUMN person_media.created_by_user_id; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.person_media.created_by_user_id IS 'Usuário que criou o registro. R30/R31: auditoria obrigatória.';


--
-- Name: persons; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.persons (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    full_name text NOT NULL,
    birth_date date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    gender character varying(20),
    nationality character varying(100) DEFAULT 'brasileira'::character varying,
    notes text,
    CONSTRAINT ck_persons_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_persons_gender CHECK (((gender IS NULL) OR ((gender)::text = ANY ((ARRAY['masculino'::character varying, 'feminino'::character varying, 'outro'::character varying, 'prefiro_nao_dizer'::character varying])::text[]))))
);


ALTER TABLE public.persons OWNER TO neondb_owner;

--
-- Name: TABLE persons; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.persons IS 'R1: Pessoas físicas do sistema. Identidade básica (nome, gênero, nascimento). V1.2: normalizada.';


--
-- Name: COLUMN persons.first_name; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.persons.first_name IS 'Primeiro nome da pessoa';


--
-- Name: COLUMN persons.last_name; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.persons.last_name IS 'Sobrenome da pessoa';


--
-- Name: COLUMN persons.gender; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.persons.gender IS 'Gênero: masculino, feminino, outro, prefiro_nao_dizer';


--
-- Name: COLUMN persons.nationality; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.persons.nationality IS 'Nacionalidade (default: brasileira)';


--
-- Name: COLUMN persons.notes; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.persons.notes IS 'Observações gerais sobre a pessoa';


--
-- Name: phases_of_play; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.phases_of_play (
    code character varying(32) NOT NULL,
    description character varying(255) NOT NULL
);


ALTER TABLE public.phases_of_play OWNER TO neondb_owner;

--
-- Name: TABLE phases_of_play; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.phases_of_play IS 'Fases do jogo. Lookup table fixa com 4 fases.';


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.role_permissions (
    role_id smallint NOT NULL,
    permission_id smallint NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO neondb_owner;

--
-- Name: TABLE role_permissions; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.role_permissions IS 'R24: Junction table papel ↔ permissão. Define o que cada papel pode fazer no sistema conforme REGRAS.md V1.2.';


--
-- Name: roles; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.roles (
    id smallint NOT NULL,
    code character varying(32) NOT NULL,
    name character varying(64) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.roles OWNER TO neondb_owner;

--
-- Name: TABLE roles; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.roles IS 'R4: Papéis do sistema. Lookup table técnica (sem soft delete). Papéis fixos: Dirigente, Coordenador, Treinador, Atleta.';


--
-- Name: COLUMN roles.code; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.roles.code IS 'Código único do papel (dirigente, coordenador, treinador, atleta).';


--
-- Name: COLUMN roles.description; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.roles.description IS 'Descrição detalhada das responsabilidades do papel conforme REGRAS.md.';


--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.roles_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO neondb_owner;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: schooling_levels; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.schooling_levels (
    id integer NOT NULL,
    code character varying(32) NOT NULL,
    name character varying(64) NOT NULL,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.schooling_levels OWNER TO neondb_owner;

--
-- Name: TABLE schooling_levels; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.schooling_levels IS 'Níveis de escolaridade.';


--
-- Name: schooling_levels_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.schooling_levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schooling_levels_id_seq OWNER TO neondb_owner;

--
-- Name: schooling_levels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.schooling_levels_id_seq OWNED BY public.schooling_levels.id;


--
-- Name: seasons; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.seasons (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    team_id uuid NOT NULL,
    name character varying(120) NOT NULL,
    year integer NOT NULL,
    competition_type character varying(32),
    start_date date NOT NULL,
    end_date date NOT NULL,
    canceled_at timestamp with time zone,
    interrupted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_user_id uuid,
    deleted_at timestamp with time zone,
    deleted_reason text,
    CONSTRAINT ck_seasons_dates CHECK ((start_date < end_date)),
    CONSTRAINT ck_seasons_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL))))
);


ALTER TABLE public.seasons OWNER TO neondb_owner;

--
-- Name: TABLE seasons; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.seasons IS 'Temporadas por equipe. V1.2: team_id FK (não organization_id); múltiplas competições simultâneas.';


--
-- Name: COLUMN seasons.canceled_at; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.seasons.canceled_at IS 'RF5.1: Cancelamento pré-início (apenas se sem dados vinculados)';


--
-- Name: COLUMN seasons.interrupted_at; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.seasons.interrupted_at IS 'RF5.2: Interrupção pós-início (força maior)';


--
-- Name: training_cycles; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.training_cycles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    organization_id uuid NOT NULL,
    team_id uuid NOT NULL,
    type character varying NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    objective text,
    notes text,
    status character varying DEFAULT '''active'''::character varying NOT NULL,
    parent_cycle_id uuid,
    created_by_user_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    CONSTRAINT check_cycle_dates CHECK ((start_date < end_date)),
    CONSTRAINT check_cycle_status CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'completed'::character varying, 'cancelled'::character varying])::text[]))),
    CONSTRAINT check_cycle_type CHECK (((type)::text = ANY ((ARRAY['macro'::character varying, 'meso'::character varying])::text[])))
);


ALTER TABLE public.training_cycles OWNER TO neondb_owner;

--
-- Name: COLUMN training_cycles.type; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_cycles.type IS 'Tipo: ''macro'' ou ''meso''';


--
-- Name: COLUMN training_cycles.objective; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_cycles.objective IS 'Objetivo estratégico do ciclo';


--
-- Name: COLUMN training_cycles.status; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_cycles.status IS 'Status: active, completed, cancelled';


--
-- Name: COLUMN training_cycles.parent_cycle_id; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_cycles.parent_cycle_id IS 'FK para macrociclo (apenas mesociclos)';


--
-- Name: training_microcycles; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.training_microcycles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    organization_id uuid NOT NULL,
    team_id uuid NOT NULL,
    week_start date NOT NULL,
    week_end date NOT NULL,
    cycle_id uuid,
    planned_focus_attack_positional_pct numeric(5,2),
    planned_focus_defense_positional_pct numeric(5,2),
    planned_focus_transition_offense_pct numeric(5,2),
    planned_focus_transition_defense_pct numeric(5,2),
    planned_focus_attack_technical_pct numeric(5,2),
    planned_focus_defense_technical_pct numeric(5,2),
    planned_focus_physical_pct numeric(5,2),
    planned_weekly_load integer,
    microcycle_type character varying,
    notes text,
    created_by_user_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    CONSTRAINT check_microcycle_dates CHECK ((week_start < week_end))
);


ALTER TABLE public.training_microcycles OWNER TO neondb_owner;

--
-- Name: COLUMN training_microcycles.week_start; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_microcycles.week_start IS 'Início da semana (seg)';


--
-- Name: COLUMN training_microcycles.week_end; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_microcycles.week_end IS 'Fim da semana (dom)';


--
-- Name: COLUMN training_microcycles.cycle_id; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_microcycles.cycle_id IS 'FK para mesociclo';


--
-- Name: COLUMN training_microcycles.planned_focus_attack_positional_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_microcycles.planned_focus_attack_positional_pct IS 'Percentual planejado de foco em ataque posicionado (0-100)';


--
-- Name: COLUMN training_microcycles.planned_focus_defense_positional_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_microcycles.planned_focus_defense_positional_pct IS 'Percentual planejado de foco em defesa posicionada (0-100)';


--
-- Name: COLUMN training_microcycles.planned_focus_transition_offense_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_microcycles.planned_focus_transition_offense_pct IS 'Percentual planejado de foco em transição ofensiva (0-100)';


--
-- Name: COLUMN training_microcycles.planned_focus_transition_defense_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_microcycles.planned_focus_transition_defense_pct IS 'Percentual planejado de foco em transição defensiva (0-100)';


--
-- Name: COLUMN training_microcycles.planned_focus_attack_technical_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_microcycles.planned_focus_attack_technical_pct IS 'Percentual planejado de foco em ataque técnico (0-100)';


--
-- Name: COLUMN training_microcycles.planned_focus_defense_technical_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_microcycles.planned_focus_defense_technical_pct IS 'Percentual planejado de foco em defesa técnica (0-100)';


--
-- Name: COLUMN training_microcycles.planned_focus_physical_pct; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_microcycles.planned_focus_physical_pct IS 'Percentual planejado de foco em treino físico (0-100)';


--
-- Name: COLUMN training_microcycles.planned_weekly_load; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_microcycles.planned_weekly_load IS 'Carga planejada da semana (RPE × minutos)';


--
-- Name: COLUMN training_microcycles.microcycle_type; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON COLUMN public.training_microcycles.microcycle_type IS 'Tipo: carga_alta, recuperacao, pre_jogo, etc.';


--
-- Name: users; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    person_id uuid NOT NULL,
    email character varying(255) NOT NULL,
    password_hash text,
    is_superadmin boolean DEFAULT false NOT NULL,
    is_locked boolean DEFAULT false NOT NULL,
    status character varying(20) DEFAULT 'ativo'::character varying NOT NULL,
    expired_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    CONSTRAINT ck_users_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_users_status CHECK (((status)::text = ANY ((ARRAY['ativo'::character varying, 'inativo'::character varying, 'arquivado'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO neondb_owner;

--
-- Name: TABLE users; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.users IS 'Usuários com acesso ao sistema. R2, R3: Super Admin único e vitalício (RDB6).';


--
-- Name: wellness_post; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.wellness_post (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    organization_id uuid NOT NULL,
    training_session_id uuid NOT NULL,
    athlete_id uuid NOT NULL,
    session_rpe smallint NOT NULL,
    fatigue_after smallint NOT NULL,
    mood_after smallint NOT NULL,
    muscle_soreness_after smallint,
    notes text,
    perceived_intensity smallint,
    flag_medical_followup boolean DEFAULT false,
    filled_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_user_id uuid NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    CONSTRAINT ck_wellness_post_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_wellness_post_fatigue CHECK (((fatigue_after >= 0) AND (fatigue_after <= 10))),
    CONSTRAINT ck_wellness_post_intensity CHECK (((perceived_intensity IS NULL) OR ((perceived_intensity >= 1) AND (perceived_intensity <= 5)))),
    CONSTRAINT ck_wellness_post_mood CHECK (((mood_after >= 0) AND (mood_after <= 10))),
    CONSTRAINT ck_wellness_post_rpe CHECK (((session_rpe >= 0) AND (session_rpe <= 10))),
    CONSTRAINT ck_wellness_post_soreness CHECK (((muscle_soreness_after IS NULL) OR ((muscle_soreness_after >= 0) AND (muscle_soreness_after <= 10))))
);


ALTER TABLE public.wellness_post OWNER TO neondb_owner;

--
-- Name: TABLE wellness_post; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.wellness_post IS 'Bem-estar pós-treino. V1.2: atleta preenche depois do treino, 1 por atleta × sessão.';


--
-- Name: wellness_pre; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.wellness_pre (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    organization_id uuid NOT NULL,
    training_session_id uuid NOT NULL,
    athlete_id uuid NOT NULL,
    sleep_hours numeric(4,1) NOT NULL,
    sleep_quality smallint NOT NULL,
    fatigue_pre smallint NOT NULL,
    stress_level smallint NOT NULL,
    muscle_soreness smallint NOT NULL,
    notes text,
    menstrual_cycle_phase character varying(32),
    readiness_score smallint,
    filled_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_user_id uuid NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_reason text,
    CONSTRAINT ck_wellness_pre_deleted_reason CHECK ((((deleted_at IS NULL) AND (deleted_reason IS NULL)) OR ((deleted_at IS NOT NULL) AND (deleted_reason IS NOT NULL)))),
    CONSTRAINT ck_wellness_pre_fatigue CHECK (((fatigue_pre >= 0) AND (fatigue_pre <= 10))),
    CONSTRAINT ck_wellness_pre_menstrual CHECK (((menstrual_cycle_phase IS NULL) OR ((menstrual_cycle_phase)::text = ANY ((ARRAY['folicular'::character varying, 'lutea'::character varying, 'menstruacao'::character varying, 'nao_informa'::character varying])::text[])))),
    CONSTRAINT ck_wellness_pre_readiness CHECK (((readiness_score IS NULL) OR ((readiness_score >= 0) AND (readiness_score <= 10)))),
    CONSTRAINT ck_wellness_pre_sleep_hours CHECK (((sleep_hours >= (0)::numeric) AND (sleep_hours <= (24)::numeric))),
    CONSTRAINT ck_wellness_pre_sleep_quality CHECK (((sleep_quality >= 1) AND (sleep_quality <= 5))),
    CONSTRAINT ck_wellness_pre_soreness CHECK (((muscle_soreness >= 0) AND (muscle_soreness <= 10))),
    CONSTRAINT ck_wellness_pre_stress CHECK (((stress_level >= 0) AND (stress_level <= 10)))
);


ALTER TABLE public.wellness_pre OWNER TO neondb_owner;

--
-- Name: TABLE wellness_pre; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON TABLE public.wellness_pre IS 'Bem-estar pré-treino. V1.2: atleta preenche antes do treino, 1 por atleta × sessão.';


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: defensive_positions id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.defensive_positions ALTER COLUMN id SET DEFAULT nextval('public.defensive_positions_id_seq'::regclass);


--
-- Name: offensive_positions id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.offensive_positions ALTER COLUMN id SET DEFAULT nextval('public.offensive_positions_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: schooling_levels id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.schooling_levels ALTER COLUMN id SET DEFAULT nextval('public.schooling_levels_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: email_queue email_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.email_queue
    ADD CONSTRAINT email_queue_pkey PRIMARY KEY (id);


--
-- Name: idempotency_keys idempotency_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.idempotency_keys
    ADD CONSTRAINT idempotency_keys_pkey PRIMARY KEY (id);


--
-- Name: match_attendance match_attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_attendance
    ADD CONSTRAINT match_attendance_pkey PRIMARY KEY (id);


--
-- Name: medical_cases medical_cases_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.medical_cases
    ADD CONSTRAINT medical_cases_pkey PRIMARY KEY (id);


--
-- Name: password_resets password_resets_token_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT password_resets_token_key UNIQUE (token);


--
-- Name: person_addresses person_addresses_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.person_addresses
    ADD CONSTRAINT person_addresses_pkey PRIMARY KEY (id);


--
-- Name: person_contacts person_contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.person_contacts
    ADD CONSTRAINT person_contacts_pkey PRIMARY KEY (id);


--
-- Name: person_documents person_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.person_documents
    ADD CONSTRAINT person_documents_pkey PRIMARY KEY (id);


--
-- Name: person_media person_media_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.person_media
    ADD CONSTRAINT person_media_pkey PRIMARY KEY (id);


--
-- Name: advantage_states pk_advantage_states; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.advantage_states
    ADD CONSTRAINT pk_advantage_states PRIMARY KEY (code);


--
-- Name: athletes pk_athletes; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.athletes
    ADD CONSTRAINT pk_athletes PRIMARY KEY (id);


--
-- Name: attendance pk_attendance; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT pk_attendance PRIMARY KEY (id);


--
-- Name: audit_logs pk_audit_logs; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT pk_audit_logs PRIMARY KEY (id);


--
-- Name: categories pk_categories; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT pk_categories PRIMARY KEY (id);


--
-- Name: defensive_positions pk_defensive_positions; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.defensive_positions
    ADD CONSTRAINT pk_defensive_positions PRIMARY KEY (id);


--
-- Name: event_subtypes pk_event_subtypes; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.event_subtypes
    ADD CONSTRAINT pk_event_subtypes PRIMARY KEY (code);


--
-- Name: event_types pk_event_types; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.event_types
    ADD CONSTRAINT pk_event_types PRIMARY KEY (code);


--
-- Name: match_events pk_match_events; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT pk_match_events PRIMARY KEY (id);


--
-- Name: match_periods pk_match_periods; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_periods
    ADD CONSTRAINT pk_match_periods PRIMARY KEY (id);


--
-- Name: match_possessions pk_match_possessions; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_possessions
    ADD CONSTRAINT pk_match_possessions PRIMARY KEY (id);


--
-- Name: match_roster pk_match_roster; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_roster
    ADD CONSTRAINT pk_match_roster PRIMARY KEY (id);


--
-- Name: match_teams pk_match_teams; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_teams
    ADD CONSTRAINT pk_match_teams PRIMARY KEY (id);


--
-- Name: matches pk_matches; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT pk_matches PRIMARY KEY (id);


--
-- Name: offensive_positions pk_offensive_positions; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.offensive_positions
    ADD CONSTRAINT pk_offensive_positions PRIMARY KEY (id);


--
-- Name: org_memberships pk_org_memberships; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.org_memberships
    ADD CONSTRAINT pk_org_memberships PRIMARY KEY (id);


--
-- Name: organizations pk_organizations; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT pk_organizations PRIMARY KEY (id);


--
-- Name: password_resets pk_password_resets; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT pk_password_resets PRIMARY KEY (id);


--
-- Name: permissions pk_permissions; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT pk_permissions PRIMARY KEY (id);


--
-- Name: persons pk_persons; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.persons
    ADD CONSTRAINT pk_persons PRIMARY KEY (id);


--
-- Name: phases_of_play pk_phases_of_play; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.phases_of_play
    ADD CONSTRAINT pk_phases_of_play PRIMARY KEY (code);


--
-- Name: role_permissions pk_role_permissions; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT pk_role_permissions PRIMARY KEY (role_id, permission_id);


--
-- Name: roles pk_roles; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT pk_roles PRIMARY KEY (id);


--
-- Name: schooling_levels pk_schooling_levels; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.schooling_levels
    ADD CONSTRAINT pk_schooling_levels PRIMARY KEY (id);


--
-- Name: seasons pk_seasons; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT pk_seasons PRIMARY KEY (id);


--
-- Name: team_registrations pk_team_registrations; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.team_registrations
    ADD CONSTRAINT pk_team_registrations PRIMARY KEY (id);


--
-- Name: teams pk_teams; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT pk_teams PRIMARY KEY (id);


--
-- Name: training_sessions pk_training_sessions; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_sessions
    ADD CONSTRAINT pk_training_sessions PRIMARY KEY (id);


--
-- Name: users pk_users; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT pk_users PRIMARY KEY (id);


--
-- Name: wellness_post pk_wellness_post; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.wellness_post
    ADD CONSTRAINT pk_wellness_post PRIMARY KEY (id);


--
-- Name: wellness_pre pk_wellness_pre; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.wellness_pre
    ADD CONSTRAINT pk_wellness_pre PRIMARY KEY (id);


--
-- Name: training_cycles training_cycles_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_cycles
    ADD CONSTRAINT training_cycles_pkey PRIMARY KEY (id);


--
-- Name: training_microcycles training_microcycles_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_microcycles
    ADD CONSTRAINT training_microcycles_pkey PRIMARY KEY (id);


--
-- Name: idempotency_keys uq_idempotency_key_endpoint; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.idempotency_keys
    ADD CONSTRAINT uq_idempotency_key_endpoint UNIQUE (key, endpoint);


--
-- Name: categories ux_categories_name; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT ux_categories_name UNIQUE (name);


--
-- Name: defensive_positions ux_defensive_positions_code; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.defensive_positions
    ADD CONSTRAINT ux_defensive_positions_code UNIQUE (code);


--
-- Name: offensive_positions ux_offensive_positions_code; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.offensive_positions
    ADD CONSTRAINT ux_offensive_positions_code UNIQUE (code);


--
-- Name: permissions ux_permissions_code; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT ux_permissions_code UNIQUE (code);


--
-- Name: roles ux_roles_code; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT ux_roles_code UNIQUE (code);


--
-- Name: roles ux_roles_name; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT ux_roles_name UNIQUE (name);


--
-- Name: schooling_levels ux_schooling_levels_code; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.schooling_levels
    ADD CONSTRAINT ux_schooling_levels_code UNIQUE (code);


--
-- Name: idx_athletes_org_deleted; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_athletes_org_deleted ON public.athletes USING btree (organization_id, deleted_at) WHERE (deleted_at IS NULL);


--
-- Name: idx_attendance_session; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_attendance_session ON public.attendance USING btree (training_session_id);


--
-- Name: idx_medical_cases_athlete; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_medical_cases_athlete ON public.medical_cases USING btree (athlete_id);


--
-- Name: idx_medical_cases_athlete_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_medical_cases_athlete_id ON public.medical_cases USING btree (athlete_id);


--
-- Name: idx_medical_cases_organization_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_medical_cases_organization_id ON public.medical_cases USING btree (organization_id);


--
-- Name: idx_medical_cases_started_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_medical_cases_started_at ON public.medical_cases USING btree (started_at);


--
-- Name: idx_medical_cases_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_medical_cases_status ON public.medical_cases USING btree (status);


--
-- Name: idx_mv_athlete_training_summary_org; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_mv_athlete_training_summary_org ON public.mv_athlete_training_summary USING btree (organization_id);


--
-- Name: idx_mv_athlete_training_summary_pk; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX idx_mv_athlete_training_summary_pk ON public.mv_athlete_training_summary USING btree (athlete_id);


--
-- Name: idx_mv_athlete_training_summary_state; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_mv_athlete_training_summary_state ON public.mv_athlete_training_summary USING btree (current_state);


--
-- Name: idx_team_registrations_athlete_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_team_registrations_athlete_active ON public.team_registrations USING btree (athlete_id, deleted_at) WHERE (deleted_at IS NULL);


--
-- Name: idx_team_registrations_team_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_team_registrations_team_active ON public.team_registrations USING btree (team_id, deleted_at) WHERE (deleted_at IS NULL);


--
-- Name: idx_training_cycles_dates; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_cycles_dates ON public.training_cycles USING btree (start_date, end_date);


--
-- Name: idx_training_cycles_org; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_cycles_org ON public.training_cycles USING btree (organization_id);


--
-- Name: idx_training_cycles_parent; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_cycles_parent ON public.training_cycles USING btree (parent_cycle_id);


--
-- Name: idx_training_cycles_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_cycles_status ON public.training_cycles USING btree (status);


--
-- Name: idx_training_cycles_team; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_cycles_team ON public.training_cycles USING btree (team_id);


--
-- Name: idx_training_cycles_type; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_cycles_type ON public.training_cycles USING btree (type);


--
-- Name: idx_training_microcycles_cycle; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_microcycles_cycle ON public.training_microcycles USING btree (cycle_id);


--
-- Name: idx_training_microcycles_dates; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_microcycles_dates ON public.training_microcycles USING btree (week_start, week_end);


--
-- Name: idx_training_microcycles_org; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_microcycles_org ON public.training_microcycles USING btree (organization_id);


--
-- Name: idx_training_microcycles_team; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_microcycles_team ON public.training_microcycles USING btree (team_id);


--
-- Name: idx_training_sessions_deviation_flag; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_sessions_deviation_flag ON public.training_sessions USING btree (planning_deviation_flag);


--
-- Name: idx_training_sessions_microcycle; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_sessions_microcycle ON public.training_sessions USING btree (microcycle_id);


--
-- Name: idx_training_sessions_org; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_sessions_org ON public.training_sessions USING btree (organization_id, deleted_at) WHERE (deleted_at IS NULL);


--
-- Name: idx_training_sessions_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_sessions_status ON public.training_sessions USING btree (status);


--
-- Name: idx_training_sessions_team_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_training_sessions_team_date ON public.training_sessions USING btree (team_id, session_at DESC, deleted_at) WHERE (deleted_at IS NULL);


--
-- Name: ix_athletes_birth_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_athletes_birth_date ON public.athletes USING btree (birth_date);


--
-- Name: ix_athletes_medical_flags; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_athletes_medical_flags ON public.athletes USING btree (organization_id) WHERE ((deleted_at IS NULL) AND ((injured = true) OR (medical_restriction = true) OR (load_restricted = true)));


--
-- Name: ix_athletes_organization_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_athletes_organization_active ON public.athletes USING btree (organization_id) WHERE ((deleted_at IS NULL) AND (organization_id IS NOT NULL));


--
-- Name: ix_athletes_organization_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_athletes_organization_id ON public.athletes USING btree (organization_id) WHERE (deleted_at IS NULL);


--
-- Name: ix_athletes_person_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_athletes_person_id ON public.athletes USING btree (person_id);


--
-- Name: ix_athletes_person_id_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_athletes_person_id_active ON public.athletes USING btree (person_id) WHERE (deleted_at IS NULL);


--
-- Name: ix_athletes_state; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_athletes_state ON public.athletes USING btree (state);


--
-- Name: ix_athletes_state_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_athletes_state_active ON public.athletes USING btree (state) WHERE (deleted_at IS NULL);


--
-- Name: ix_attendance_athlete_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_attendance_athlete_id ON public.attendance USING btree (athlete_id);


--
-- Name: ix_attendance_athlete_session_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_attendance_athlete_session_active ON public.attendance USING btree (athlete_id, training_session_id) WHERE (deleted_at IS NULL);


--
-- Name: ix_attendance_training_session_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_attendance_training_session_id ON public.attendance USING btree (training_session_id);


--
-- Name: ix_audit_logs_actor_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_logs_actor_id ON public.audit_logs USING btree (actor_id);


--
-- Name: ix_audit_logs_created_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: ix_audit_logs_entity; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_logs_entity ON public.audit_logs USING btree (entity);


--
-- Name: ix_audit_logs_entity_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_logs_entity_id ON public.audit_logs USING btree (entity_id);


--
-- Name: ix_email_queue_created_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_email_queue_created_at ON public.email_queue USING btree (created_at);


--
-- Name: ix_email_queue_next_retry; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_email_queue_next_retry ON public.email_queue USING btree (next_retry_at) WHERE ((status)::text = 'pending'::text);


--
-- Name: ix_email_queue_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_email_queue_status ON public.email_queue USING btree (status);


--
-- Name: ix_email_queue_to_email; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_email_queue_to_email ON public.email_queue USING btree (to_email);


--
-- Name: ix_event_subtypes_event_type_code; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_event_subtypes_event_type_code ON public.event_subtypes USING btree (event_type_code);


--
-- Name: ix_idempotency_keys_created_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_idempotency_keys_created_at ON public.idempotency_keys USING btree (created_at);


--
-- Name: INDEX ix_idempotency_keys_created_at; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON INDEX public.ix_idempotency_keys_created_at IS 'Índice para otimizar limpeza de registros antigos via cron job';


--
-- Name: ix_idempotency_keys_key; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_idempotency_keys_key ON public.idempotency_keys USING btree (key);


--
-- Name: ix_idempotency_keys_key_endpoint; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_idempotency_keys_key_endpoint ON public.idempotency_keys USING btree (key, endpoint);


--
-- Name: ix_match_attendance_athlete_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_attendance_athlete_id ON public.match_attendance USING btree (athlete_id);


--
-- Name: ix_match_attendance_athlete_match_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_attendance_athlete_match_active ON public.match_attendance USING btree (athlete_id, match_id) WHERE ((deleted_at IS NULL) AND (played = true));


--
-- Name: ix_match_attendance_match_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_attendance_match_id ON public.match_attendance USING btree (match_id);


--
-- Name: ix_match_events_athlete_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_events_athlete_id ON public.match_events USING btree (athlete_id);


--
-- Name: ix_match_events_event_type; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_events_event_type ON public.match_events USING btree (event_type);


--
-- Name: ix_match_events_match_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_events_match_id ON public.match_events USING btree (match_id);


--
-- Name: ix_match_events_phase_of_play; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_events_phase_of_play ON public.match_events USING btree (phase_of_play);


--
-- Name: ix_match_events_team_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_events_team_id ON public.match_events USING btree (team_id);


--
-- Name: ix_match_periods_match_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_periods_match_id ON public.match_periods USING btree (match_id);


--
-- Name: ix_match_possessions_match_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_possessions_match_id ON public.match_possessions USING btree (match_id);


--
-- Name: ix_match_possessions_team_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_possessions_team_id ON public.match_possessions USING btree (team_id);


--
-- Name: ix_match_roster_athlete_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_roster_athlete_id ON public.match_roster USING btree (athlete_id);


--
-- Name: ix_match_roster_match_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_roster_match_id ON public.match_roster USING btree (match_id);


--
-- Name: ix_match_teams_match_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_teams_match_id ON public.match_teams USING btree (match_id);


--
-- Name: ix_match_teams_team_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_match_teams_team_id ON public.match_teams USING btree (team_id);


--
-- Name: ix_matches_away_team_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_matches_away_team_id ON public.matches USING btree (away_team_id);


--
-- Name: ix_matches_home_team_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_matches_home_team_id ON public.matches USING btree (home_team_id);


--
-- Name: ix_matches_match_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_matches_match_date ON public.matches USING btree (match_date);


--
-- Name: ix_matches_season_date_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_matches_season_date_active ON public.matches USING btree (season_id, match_date) WHERE (deleted_at IS NULL);


--
-- Name: ix_matches_season_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_matches_season_id ON public.matches USING btree (season_id);


--
-- Name: ix_matches_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_matches_status ON public.matches USING btree (status);


--
-- Name: ix_medical_cases_athlete_status_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_medical_cases_athlete_status_active ON public.medical_cases USING btree (athlete_id, status) WHERE ((deleted_at IS NULL) AND ((status)::text = ANY ((ARRAY['ativo'::character varying, 'em_acompanhamento'::character varying])::text[])));


--
-- Name: ix_mv_athlete_summary_org; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_mv_athlete_summary_org ON public.mv_athlete_summary USING btree (organization_id);


--
-- Name: ix_mv_training_performance_org; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_mv_training_performance_org ON public.mv_training_performance USING btree (organization_id);


--
-- Name: ix_org_memberships_org_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_org_memberships_org_active ON public.org_memberships USING btree (organization_id) WHERE (deleted_at IS NULL);


--
-- Name: ix_org_memberships_organization_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_org_memberships_organization_id ON public.org_memberships USING btree (organization_id);


--
-- Name: ix_org_memberships_person_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_org_memberships_person_active ON public.org_memberships USING btree (person_id) WHERE (deleted_at IS NULL);


--
-- Name: ix_org_memberships_person_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_org_memberships_person_id ON public.org_memberships USING btree (person_id);


--
-- Name: ix_org_memberships_person_org_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_org_memberships_person_org_active ON public.org_memberships USING btree (person_id, organization_id) WHERE ((deleted_at IS NULL) AND (end_at IS NULL));


--
-- Name: ix_org_memberships_role_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_org_memberships_role_id ON public.org_memberships USING btree (role_id);


--
-- Name: ix_organizations_name; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_organizations_name ON public.organizations USING btree (name);


--
-- Name: ix_organizations_name_trgm; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_organizations_name_trgm ON public.organizations USING gin (name public.gin_trgm_ops) WHERE (deleted_at IS NULL);


--
-- Name: ix_password_resets_expires_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_password_resets_expires_at ON public.password_resets USING btree (expires_at);


--
-- Name: ix_password_resets_token; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_password_resets_token ON public.password_resets USING btree (token);


--
-- Name: ix_password_resets_user_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_password_resets_user_id ON public.password_resets USING btree (user_id);


--
-- Name: ix_person_addresses_city_state; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_addresses_city_state ON public.person_addresses USING btree (city, state);


--
-- Name: ix_person_addresses_created_by_user_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_addresses_created_by_user_id ON public.person_addresses USING btree (created_by_user_id);


--
-- Name: ix_person_addresses_deleted_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_addresses_deleted_at ON public.person_addresses USING btree (deleted_at);


--
-- Name: ix_person_addresses_person_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_addresses_person_id ON public.person_addresses USING btree (person_id);


--
-- Name: ix_person_contacts_created_by_user_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_contacts_created_by_user_id ON public.person_contacts USING btree (created_by_user_id);


--
-- Name: ix_person_contacts_deleted_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_contacts_deleted_at ON public.person_contacts USING btree (deleted_at);


--
-- Name: ix_person_contacts_email_lower; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_contacts_email_lower ON public.person_contacts USING btree (lower((contact_value)::text)) WHERE (((contact_type)::text = 'email'::text) AND (deleted_at IS NULL));


--
-- Name: ix_person_contacts_person_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_contacts_person_id ON public.person_contacts USING btree (person_id);


--
-- Name: ix_person_contacts_type_value; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_contacts_type_value ON public.person_contacts USING btree (contact_type, contact_value);


--
-- Name: ix_person_contacts_type_value_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_contacts_type_value_active ON public.person_contacts USING btree (contact_type, contact_value) WHERE (deleted_at IS NULL);


--
-- Name: ix_person_contacts_value; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_contacts_value ON public.person_contacts USING btree (contact_value) WHERE (deleted_at IS NULL);


--
-- Name: ix_person_contacts_value_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_contacts_value_active ON public.person_contacts USING btree (contact_value) WHERE (deleted_at IS NULL);


--
-- Name: ix_person_documents_cpf_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_documents_cpf_active ON public.person_documents USING btree (document_number) WHERE (((document_type)::text = 'cpf'::text) AND (deleted_at IS NULL));


--
-- Name: ix_person_documents_created_by_user_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_documents_created_by_user_id ON public.person_documents USING btree (created_by_user_id);


--
-- Name: ix_person_documents_deleted_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_documents_deleted_at ON public.person_documents USING btree (deleted_at);


--
-- Name: ix_person_documents_number; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_documents_number ON public.person_documents USING btree (document_number);


--
-- Name: ix_person_documents_person_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_documents_person_id ON public.person_documents USING btree (person_id);


--
-- Name: ix_person_documents_rg_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_documents_rg_active ON public.person_documents USING btree (document_number) WHERE (((document_type)::text = 'rg'::text) AND (deleted_at IS NULL));


--
-- Name: ix_person_documents_type; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_documents_type ON public.person_documents USING btree (document_type);


--
-- Name: ix_person_documents_type_number; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_documents_type_number ON public.person_documents USING btree (document_type, document_number) WHERE (deleted_at IS NULL);


--
-- Name: ix_person_media_created_by_user_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_media_created_by_user_id ON public.person_media USING btree (created_by_user_id);


--
-- Name: ix_person_media_deleted_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_media_deleted_at ON public.person_media USING btree (deleted_at);


--
-- Name: ix_person_media_person_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_media_person_id ON public.person_media USING btree (person_id);


--
-- Name: ix_person_media_person_type; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_media_person_type ON public.person_media USING btree (person_id, media_type) WHERE (deleted_at IS NULL);


--
-- Name: ix_person_media_type; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_person_media_type ON public.person_media USING btree (media_type);


--
-- Name: ix_persons_birth_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_persons_birth_date ON public.persons USING btree (birth_date);


--
-- Name: ix_persons_deleted_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_persons_deleted_at ON public.persons USING btree (deleted_at);


--
-- Name: ix_persons_first_name; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_persons_first_name ON public.persons USING btree (first_name);


--
-- Name: ix_persons_first_name_trgm; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_persons_first_name_trgm ON public.persons USING gin (first_name public.gin_trgm_ops) WHERE (deleted_at IS NULL);


--
-- Name: ix_persons_full_name_trgm; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_persons_full_name_trgm ON public.persons USING gin (full_name public.gin_trgm_ops) WHERE (deleted_at IS NULL);


--
-- Name: INDEX ix_persons_full_name_trgm; Type: COMMENT; Schema: public; Owner: neondb_owner
--

COMMENT ON INDEX public.ix_persons_full_name_trgm IS 'Índice trigram para busca fuzzy de pessoas (autocomplete). FICHA.MD 1.6';


--
-- Name: ix_persons_last_name; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_persons_last_name ON public.persons USING btree (last_name);


--
-- Name: ix_persons_last_name_trgm; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_persons_last_name_trgm ON public.persons USING gin (last_name public.gin_trgm_ops) WHERE (deleted_at IS NULL);


--
-- Name: ix_seasons_team_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_seasons_team_id ON public.seasons USING btree (team_id);


--
-- Name: ix_seasons_year; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_seasons_year ON public.seasons USING btree (year);


--
-- Name: ix_team_registrations_athlete_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_team_registrations_athlete_active ON public.team_registrations USING btree (athlete_id) WHERE ((end_at IS NULL) AND (deleted_at IS NULL));


--
-- Name: ix_team_registrations_athlete_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_team_registrations_athlete_id ON public.team_registrations USING btree (athlete_id);


--
-- Name: ix_team_registrations_period; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_team_registrations_period ON public.team_registrations USING btree (start_at, end_at) WHERE (deleted_at IS NULL);


--
-- Name: ix_team_registrations_team_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_team_registrations_team_active ON public.team_registrations USING btree (team_id) WHERE ((end_at IS NULL) AND (deleted_at IS NULL));


--
-- Name: ix_team_registrations_team_athlete_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_team_registrations_team_athlete_active ON public.team_registrations USING btree (team_id, athlete_id) WHERE ((end_at IS NULL) AND (deleted_at IS NULL));


--
-- Name: ix_team_registrations_team_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_team_registrations_team_id ON public.team_registrations USING btree (team_id);


--
-- Name: ix_teams_category_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_teams_category_id ON public.teams USING btree (category_id);


--
-- Name: ix_teams_name_trgm; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_teams_name_trgm ON public.teams USING gin (name public.gin_trgm_ops) WHERE (deleted_at IS NULL);


--
-- Name: ix_teams_organization_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_teams_organization_active ON public.teams USING btree (organization_id) WHERE (deleted_at IS NULL);


--
-- Name: ix_teams_organization_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_teams_organization_id ON public.teams USING btree (organization_id);


--
-- Name: ix_training_sessions_organization_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_training_sessions_organization_id ON public.training_sessions USING btree (organization_id);


--
-- Name: ix_training_sessions_season_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_training_sessions_season_id ON public.training_sessions USING btree (season_id);


--
-- Name: ix_training_sessions_session_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_training_sessions_session_at ON public.training_sessions USING btree (session_at);


--
-- Name: ix_training_sessions_team_date_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_training_sessions_team_date_active ON public.training_sessions USING btree (team_id, session_at) WHERE (deleted_at IS NULL);


--
-- Name: ix_training_sessions_team_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_training_sessions_team_id ON public.training_sessions USING btree (team_id);


--
-- Name: ix_training_sessions_team_season_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_training_sessions_team_season_date ON public.training_sessions USING btree (team_id, season_id, session_at) WHERE (deleted_at IS NULL);


--
-- Name: ix_users_person_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_users_person_id ON public.users USING btree (person_id);


--
-- Name: ix_wellness_post_athlete_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_wellness_post_athlete_id ON public.wellness_post USING btree (athlete_id);


--
-- Name: ix_wellness_post_athlete_session_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_wellness_post_athlete_session_active ON public.wellness_post USING btree (athlete_id, training_session_id, created_at) WHERE (deleted_at IS NULL);


--
-- Name: ix_wellness_post_training_session_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_wellness_post_training_session_id ON public.wellness_post USING btree (training_session_id);


--
-- Name: ix_wellness_pre_athlete_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_wellness_pre_athlete_id ON public.wellness_pre USING btree (athlete_id);


--
-- Name: ix_wellness_pre_training_session_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_wellness_pre_training_session_id ON public.wellness_pre USING btree (training_session_id);


--
-- Name: uq_person_addresses_primary; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX uq_person_addresses_primary ON public.person_addresses USING btree (person_id) WHERE ((is_primary = true) AND (deleted_at IS NULL));


--
-- Name: uq_person_contacts_primary_per_type; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX uq_person_contacts_primary_per_type ON public.person_contacts USING btree (person_id, contact_type) WHERE ((is_primary = true) AND (deleted_at IS NULL));


--
-- Name: uq_person_documents_per_type; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX uq_person_documents_per_type ON public.person_documents USING btree (person_id, document_type, document_number) WHERE (deleted_at IS NULL);


--
-- Name: uq_person_media_primary_per_type; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX uq_person_media_primary_per_type ON public.person_media USING btree (person_id, media_type) WHERE ((is_primary = true) AND (deleted_at IS NULL));


--
-- Name: ux_mv_athlete_summary_athlete; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ux_mv_athlete_summary_athlete ON public.mv_athlete_summary USING btree (athlete_id);


--
-- Name: ux_mv_training_performance_session; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ux_mv_training_performance_session ON public.mv_training_performance USING btree (session_id);


--
-- Name: ux_org_memberships_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ux_org_memberships_active ON public.org_memberships USING btree (person_id, organization_id, role_id) WHERE ((end_at IS NULL) AND (deleted_at IS NULL));


--
-- Name: ux_team_registrations_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ux_team_registrations_active ON public.team_registrations USING btree (athlete_id, team_id) WHERE ((end_at IS NULL) AND (deleted_at IS NULL));


--
-- Name: ux_users_email; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ux_users_email ON public.users USING btree (lower((email)::text));


--
-- Name: ux_users_superadmin; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ux_users_superadmin ON public.users USING btree (is_superadmin) WHERE ((is_superadmin = true) AND (deleted_at IS NULL));


--
-- Name: ux_wellness_post_session_athlete; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ux_wellness_post_session_athlete ON public.wellness_post USING btree (training_session_id, athlete_id) WHERE (deleted_at IS NULL);


--
-- Name: ux_wellness_pre_session_athlete; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ux_wellness_pre_session_athlete ON public.wellness_pre USING btree (training_session_id, athlete_id) WHERE (deleted_at IS NULL);


--
-- Name: athletes trg_athletes_age_at_registration; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_athletes_age_at_registration BEFORE INSERT OR UPDATE OF birth_date, registered_at ON public.athletes FOR EACH ROW EXECUTE FUNCTION public.trg_set_athlete_age_at_registration();


--
-- Name: athletes trg_athletes_auto_end_registrations; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_athletes_auto_end_registrations AFTER UPDATE OF state ON public.athletes FOR EACH ROW EXECUTE FUNCTION public.trg_auto_end_team_registrations_on_dispensada();


--
-- Name: athletes trg_athletes_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_athletes_block_delete BEFORE DELETE ON public.athletes FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: athletes trg_athletes_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_athletes_updated_at BEFORE UPDATE ON public.athletes FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: attendance trg_attendance_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_attendance_block_delete BEFORE DELETE ON public.attendance FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: attendance trg_attendance_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_attendance_updated_at BEFORE UPDATE ON public.attendance FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: audit_logs trg_audit_logs_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_audit_logs_block_delete BEFORE DELETE ON public.audit_logs FOR EACH ROW EXECUTE FUNCTION public.trg_block_audit_logs_modification();


--
-- Name: audit_logs trg_audit_logs_block_update; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_audit_logs_block_update BEFORE UPDATE ON public.audit_logs FOR EACH ROW EXECUTE FUNCTION public.trg_block_audit_logs_modification();


--
-- Name: email_queue trg_email_queue_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_email_queue_updated_at BEFORE UPDATE ON public.email_queue FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: match_attendance trg_match_attendance_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_match_attendance_block_delete BEFORE DELETE ON public.match_attendance FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: match_attendance trg_match_attendance_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_match_attendance_updated_at BEFORE UPDATE ON public.match_attendance FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: matches trg_matches_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_matches_block_delete BEFORE DELETE ON public.matches FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: matches trg_matches_block_finished_update; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_matches_block_finished_update BEFORE UPDATE ON public.matches FOR EACH ROW EXECUTE FUNCTION public.trg_block_finished_match_update();


--
-- Name: matches trg_matches_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_matches_updated_at BEFORE UPDATE ON public.matches FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: medical_cases trg_medical_cases_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_medical_cases_block_delete BEFORE DELETE ON public.medical_cases FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: medical_cases trg_medical_cases_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_medical_cases_updated_at BEFORE UPDATE ON public.medical_cases FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: org_memberships trg_org_memberships_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_org_memberships_block_delete BEFORE DELETE ON public.org_memberships FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: org_memberships trg_org_memberships_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_org_memberships_updated_at BEFORE UPDATE ON public.org_memberships FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: organizations trg_organizations_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_organizations_block_delete BEFORE DELETE ON public.organizations FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: organizations trg_organizations_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_organizations_updated_at BEFORE UPDATE ON public.organizations FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: permissions trg_permissions_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_permissions_updated_at BEFORE UPDATE ON public.permissions FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: person_addresses trg_person_addresses_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_person_addresses_block_delete BEFORE DELETE ON public.person_addresses FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: person_addresses trg_person_addresses_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_person_addresses_updated_at BEFORE UPDATE ON public.person_addresses FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: person_contacts trg_person_contacts_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_person_contacts_block_delete BEFORE DELETE ON public.person_contacts FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: person_contacts trg_person_contacts_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_person_contacts_updated_at BEFORE UPDATE ON public.person_contacts FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: person_documents trg_person_documents_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_person_documents_block_delete BEFORE DELETE ON public.person_documents FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: person_documents trg_person_documents_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_person_documents_updated_at BEFORE UPDATE ON public.person_documents FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: person_media trg_person_media_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_person_media_block_delete BEFORE DELETE ON public.person_media FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: person_media trg_person_media_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_person_media_updated_at BEFORE UPDATE ON public.person_media FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: persons trg_persons_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_persons_block_delete BEFORE DELETE ON public.persons FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: persons trg_persons_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_persons_updated_at BEFORE UPDATE ON public.persons FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: roles trg_roles_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_roles_updated_at BEFORE UPDATE ON public.roles FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: seasons trg_seasons_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_seasons_block_delete BEFORE DELETE ON public.seasons FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: seasons trg_seasons_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_seasons_updated_at BEFORE UPDATE ON public.seasons FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: team_registrations trg_team_registrations_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_team_registrations_block_delete BEFORE DELETE ON public.team_registrations FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: team_registrations trg_team_registrations_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_team_registrations_updated_at BEFORE UPDATE ON public.team_registrations FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: teams trg_teams_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_teams_block_delete BEFORE DELETE ON public.teams FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: teams trg_teams_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_teams_updated_at BEFORE UPDATE ON public.teams FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: training_sessions trg_training_sessions_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_training_sessions_block_delete BEFORE DELETE ON public.training_sessions FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: training_sessions trg_training_sessions_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_training_sessions_updated_at BEFORE UPDATE ON public.training_sessions FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: users trg_users_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_users_block_delete BEFORE DELETE ON public.users FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: users trg_users_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: wellness_post trg_wellness_post_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_wellness_post_block_delete BEFORE DELETE ON public.wellness_post FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: wellness_post trg_wellness_post_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_wellness_post_updated_at BEFORE UPDATE ON public.wellness_post FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: wellness_pre trg_wellness_pre_block_delete; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_wellness_pre_block_delete BEFORE DELETE ON public.wellness_pre FOR EACH ROW EXECUTE FUNCTION public.trg_block_physical_delete();


--
-- Name: wellness_pre trg_wellness_pre_updated_at; Type: TRIGGER; Schema: public; Owner: neondb_owner
--

CREATE TRIGGER trg_wellness_pre_updated_at BEFORE UPDATE ON public.wellness_pre FOR EACH ROW EXECUTE FUNCTION public.trg_set_updated_at();


--
-- Name: athletes athletes_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.athletes
    ADD CONSTRAINT athletes_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: athletes fk_athletes_main_defensive_position_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.athletes
    ADD CONSTRAINT fk_athletes_main_defensive_position_id FOREIGN KEY (main_defensive_position_id) REFERENCES public.defensive_positions(id) ON DELETE SET NULL;


--
-- Name: athletes fk_athletes_main_offensive_position_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.athletes
    ADD CONSTRAINT fk_athletes_main_offensive_position_id FOREIGN KEY (main_offensive_position_id) REFERENCES public.offensive_positions(id) ON DELETE SET NULL;


--
-- Name: athletes fk_athletes_person_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.athletes
    ADD CONSTRAINT fk_athletes_person_id FOREIGN KEY (person_id) REFERENCES public.persons(id) ON DELETE RESTRICT;


--
-- Name: athletes fk_athletes_schooling_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.athletes
    ADD CONSTRAINT fk_athletes_schooling_id FOREIGN KEY (schooling_id) REFERENCES public.schooling_levels(id) ON DELETE SET NULL;


--
-- Name: athletes fk_athletes_secondary_defensive_position_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.athletes
    ADD CONSTRAINT fk_athletes_secondary_defensive_position_id FOREIGN KEY (secondary_defensive_position_id) REFERENCES public.defensive_positions(id) ON DELETE SET NULL;


--
-- Name: athletes fk_athletes_secondary_offensive_position_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.athletes
    ADD CONSTRAINT fk_athletes_secondary_offensive_position_id FOREIGN KEY (secondary_offensive_position_id) REFERENCES public.offensive_positions(id) ON DELETE SET NULL;


--
-- Name: attendance fk_attendance_athlete_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT fk_attendance_athlete_id FOREIGN KEY (athlete_id) REFERENCES public.athletes(id) ON DELETE RESTRICT;


--
-- Name: attendance fk_attendance_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT fk_attendance_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: attendance fk_attendance_team_registration_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT fk_attendance_team_registration_id FOREIGN KEY (team_registration_id) REFERENCES public.team_registrations(id) ON DELETE RESTRICT;


--
-- Name: attendance fk_attendance_training_session_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT fk_attendance_training_session_id FOREIGN KEY (training_session_id) REFERENCES public.training_sessions(id) ON DELETE RESTRICT;


--
-- Name: audit_logs fk_audit_logs_actor_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT fk_audit_logs_actor_id FOREIGN KEY (actor_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: email_queue fk_email_queue_created_by_user; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.email_queue
    ADD CONSTRAINT fk_email_queue_created_by_user FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: event_subtypes fk_event_subtypes_event_type_code; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.event_subtypes
    ADD CONSTRAINT fk_event_subtypes_event_type_code FOREIGN KEY (event_type_code) REFERENCES public.event_types(code) ON DELETE RESTRICT;


--
-- Name: match_events fk_match_events_advantage_state; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_advantage_state FOREIGN KEY (advantage_state) REFERENCES public.advantage_states(code) ON DELETE RESTRICT;


--
-- Name: match_events fk_match_events_assisting_athlete_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_assisting_athlete_id FOREIGN KEY (assisting_athlete_id) REFERENCES public.athletes(id) ON DELETE RESTRICT;


--
-- Name: match_events fk_match_events_athlete_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_athlete_id FOREIGN KEY (athlete_id) REFERENCES public.athletes(id) ON DELETE RESTRICT;


--
-- Name: match_events fk_match_events_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: match_events fk_match_events_event_subtype; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_event_subtype FOREIGN KEY (event_subtype) REFERENCES public.event_subtypes(code) ON DELETE RESTRICT;


--
-- Name: match_events fk_match_events_event_type; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_event_type FOREIGN KEY (event_type) REFERENCES public.event_types(code) ON DELETE RESTRICT;


--
-- Name: match_events fk_match_events_match_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_match_id FOREIGN KEY (match_id) REFERENCES public.matches(id) ON DELETE CASCADE;


--
-- Name: match_events fk_match_events_opponent_team_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_opponent_team_id FOREIGN KEY (opponent_team_id) REFERENCES public.teams(id) ON DELETE RESTRICT;


--
-- Name: match_events fk_match_events_phase_of_play; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_phase_of_play FOREIGN KEY (phase_of_play) REFERENCES public.phases_of_play(code) ON DELETE RESTRICT;


--
-- Name: match_events fk_match_events_possession_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_possession_id FOREIGN KEY (possession_id) REFERENCES public.match_possessions(id) ON DELETE SET NULL;


--
-- Name: match_events fk_match_events_related_event_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_related_event_id FOREIGN KEY (related_event_id) REFERENCES public.match_events(id) ON DELETE SET NULL;


--
-- Name: match_events fk_match_events_secondary_athlete_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_secondary_athlete_id FOREIGN KEY (secondary_athlete_id) REFERENCES public.athletes(id) ON DELETE RESTRICT;


--
-- Name: match_events fk_match_events_team_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT fk_match_events_team_id FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE RESTRICT;


--
-- Name: match_periods fk_match_periods_match_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_periods
    ADD CONSTRAINT fk_match_periods_match_id FOREIGN KEY (match_id) REFERENCES public.matches(id) ON DELETE CASCADE;


--
-- Name: match_possessions fk_match_possessions_match_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_possessions
    ADD CONSTRAINT fk_match_possessions_match_id FOREIGN KEY (match_id) REFERENCES public.matches(id) ON DELETE CASCADE;


--
-- Name: match_possessions fk_match_possessions_team_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_possessions
    ADD CONSTRAINT fk_match_possessions_team_id FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE RESTRICT;


--
-- Name: match_roster fk_match_roster_athlete_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_roster
    ADD CONSTRAINT fk_match_roster_athlete_id FOREIGN KEY (athlete_id) REFERENCES public.athletes(id) ON DELETE RESTRICT;


--
-- Name: match_roster fk_match_roster_match_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_roster
    ADD CONSTRAINT fk_match_roster_match_id FOREIGN KEY (match_id) REFERENCES public.matches(id) ON DELETE CASCADE;


--
-- Name: match_roster fk_match_roster_team_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_roster
    ADD CONSTRAINT fk_match_roster_team_id FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE RESTRICT;


--
-- Name: match_teams fk_match_teams_match_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_teams
    ADD CONSTRAINT fk_match_teams_match_id FOREIGN KEY (match_id) REFERENCES public.matches(id) ON DELETE CASCADE;


--
-- Name: match_teams fk_match_teams_team_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_teams
    ADD CONSTRAINT fk_match_teams_team_id FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE RESTRICT;


--
-- Name: matches fk_matches_away_team_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT fk_matches_away_team_id FOREIGN KEY (away_team_id) REFERENCES public.teams(id) ON DELETE RESTRICT;


--
-- Name: matches fk_matches_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT fk_matches_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: matches fk_matches_home_team_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT fk_matches_home_team_id FOREIGN KEY (home_team_id) REFERENCES public.teams(id) ON DELETE RESTRICT;


--
-- Name: matches fk_matches_our_team_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT fk_matches_our_team_id FOREIGN KEY (our_team_id) REFERENCES public.teams(id) ON DELETE RESTRICT;


--
-- Name: matches fk_matches_season_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT fk_matches_season_id FOREIGN KEY (season_id) REFERENCES public.seasons(id) ON DELETE RESTRICT;


--
-- Name: medical_cases fk_medical_cases_organization; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.medical_cases
    ADD CONSTRAINT fk_medical_cases_organization FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: org_memberships fk_org_memberships_created_by_user; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.org_memberships
    ADD CONSTRAINT fk_org_memberships_created_by_user FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: org_memberships fk_org_memberships_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.org_memberships
    ADD CONSTRAINT fk_org_memberships_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE RESTRICT;


--
-- Name: org_memberships fk_org_memberships_person_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.org_memberships
    ADD CONSTRAINT fk_org_memberships_person_id FOREIGN KEY (person_id) REFERENCES public.persons(id) ON DELETE RESTRICT;


--
-- Name: org_memberships fk_org_memberships_role_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.org_memberships
    ADD CONSTRAINT fk_org_memberships_role_id FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE RESTRICT;


--
-- Name: password_resets fk_password_resets_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT fk_password_resets_user_id FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: person_addresses fk_person_addresses_created_by_user; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.person_addresses
    ADD CONSTRAINT fk_person_addresses_created_by_user FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: person_contacts fk_person_contacts_created_by_user; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.person_contacts
    ADD CONSTRAINT fk_person_contacts_created_by_user FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: person_documents fk_person_documents_created_by_user; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.person_documents
    ADD CONSTRAINT fk_person_documents_created_by_user FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: person_media fk_person_media_created_by_user; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.person_media
    ADD CONSTRAINT fk_person_media_created_by_user FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: role_permissions fk_role_permissions_permission_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT fk_role_permissions_permission_id FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: role_permissions fk_role_permissions_role_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT fk_role_permissions_role_id FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: seasons fk_seasons_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT fk_seasons_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: seasons fk_seasons_team_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT fk_seasons_team_id FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE RESTRICT;


--
-- Name: team_registrations fk_team_registrations_athlete_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.team_registrations
    ADD CONSTRAINT fk_team_registrations_athlete_id FOREIGN KEY (athlete_id) REFERENCES public.athletes(id) ON DELETE RESTRICT;


--
-- Name: team_registrations fk_team_registrations_created_by_user; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.team_registrations
    ADD CONSTRAINT fk_team_registrations_created_by_user FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: team_registrations fk_team_registrations_team_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.team_registrations
    ADD CONSTRAINT fk_team_registrations_team_id FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE RESTRICT;


--
-- Name: teams fk_teams_category_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT fk_teams_category_id FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE RESTRICT;


--
-- Name: teams fk_teams_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT fk_teams_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: teams fk_teams_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT fk_teams_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE RESTRICT;


--
-- Name: training_sessions fk_training_sessions_closed_by; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_sessions
    ADD CONSTRAINT fk_training_sessions_closed_by FOREIGN KEY (closed_by_user_id) REFERENCES public.users(id);


--
-- Name: training_sessions fk_training_sessions_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_sessions
    ADD CONSTRAINT fk_training_sessions_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: training_sessions fk_training_sessions_microcycle; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_sessions
    ADD CONSTRAINT fk_training_sessions_microcycle FOREIGN KEY (microcycle_id) REFERENCES public.training_microcycles(id);


--
-- Name: training_sessions fk_training_sessions_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_sessions
    ADD CONSTRAINT fk_training_sessions_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE RESTRICT;


--
-- Name: training_sessions fk_training_sessions_season_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_sessions
    ADD CONSTRAINT fk_training_sessions_season_id FOREIGN KEY (season_id) REFERENCES public.seasons(id) ON DELETE RESTRICT;


--
-- Name: training_sessions fk_training_sessions_team_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_sessions
    ADD CONSTRAINT fk_training_sessions_team_id FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE RESTRICT;


--
-- Name: users fk_users_person_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_person_id FOREIGN KEY (person_id) REFERENCES public.persons(id) ON DELETE RESTRICT;


--
-- Name: wellness_post fk_wellness_post_athlete_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.wellness_post
    ADD CONSTRAINT fk_wellness_post_athlete_id FOREIGN KEY (athlete_id) REFERENCES public.athletes(id) ON DELETE RESTRICT;


--
-- Name: wellness_post fk_wellness_post_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.wellness_post
    ADD CONSTRAINT fk_wellness_post_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: wellness_post fk_wellness_post_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.wellness_post
    ADD CONSTRAINT fk_wellness_post_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE RESTRICT;


--
-- Name: wellness_post fk_wellness_post_training_session_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.wellness_post
    ADD CONSTRAINT fk_wellness_post_training_session_id FOREIGN KEY (training_session_id) REFERENCES public.training_sessions(id) ON DELETE RESTRICT;


--
-- Name: wellness_pre fk_wellness_pre_athlete_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.wellness_pre
    ADD CONSTRAINT fk_wellness_pre_athlete_id FOREIGN KEY (athlete_id) REFERENCES public.athletes(id) ON DELETE RESTRICT;


--
-- Name: wellness_pre fk_wellness_pre_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.wellness_pre
    ADD CONSTRAINT fk_wellness_pre_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: wellness_pre fk_wellness_pre_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.wellness_pre
    ADD CONSTRAINT fk_wellness_pre_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE RESTRICT;


--
-- Name: wellness_pre fk_wellness_pre_training_session_id; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.wellness_pre
    ADD CONSTRAINT fk_wellness_pre_training_session_id FOREIGN KEY (training_session_id) REFERENCES public.training_sessions(id) ON DELETE RESTRICT;


--
-- Name: match_attendance match_attendance_athlete_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_attendance
    ADD CONSTRAINT match_attendance_athlete_id_fkey FOREIGN KEY (athlete_id) REFERENCES public.athletes(id) ON DELETE RESTRICT;


--
-- Name: match_attendance match_attendance_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_attendance
    ADD CONSTRAINT match_attendance_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: match_attendance match_attendance_match_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_attendance
    ADD CONSTRAINT match_attendance_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(id) ON DELETE CASCADE;


--
-- Name: match_attendance match_attendance_match_roster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.match_attendance
    ADD CONSTRAINT match_attendance_match_roster_id_fkey FOREIGN KEY (match_roster_id) REFERENCES public.match_roster(id) ON DELETE RESTRICT;


--
-- Name: medical_cases medical_cases_athlete_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.medical_cases
    ADD CONSTRAINT medical_cases_athlete_id_fkey FOREIGN KEY (athlete_id) REFERENCES public.athletes(id) ON DELETE CASCADE;


--
-- Name: medical_cases medical_cases_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.medical_cases
    ADD CONSTRAINT medical_cases_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: person_addresses person_addresses_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.person_addresses
    ADD CONSTRAINT person_addresses_person_id_fkey FOREIGN KEY (person_id) REFERENCES public.persons(id) ON DELETE CASCADE;


--
-- Name: person_contacts person_contacts_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.person_contacts
    ADD CONSTRAINT person_contacts_person_id_fkey FOREIGN KEY (person_id) REFERENCES public.persons(id) ON DELETE CASCADE;


--
-- Name: person_documents person_documents_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.person_documents
    ADD CONSTRAINT person_documents_person_id_fkey FOREIGN KEY (person_id) REFERENCES public.persons(id) ON DELETE CASCADE;


--
-- Name: person_media person_media_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.person_media
    ADD CONSTRAINT person_media_person_id_fkey FOREIGN KEY (person_id) REFERENCES public.persons(id) ON DELETE CASCADE;


--
-- Name: training_cycles training_cycles_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_cycles
    ADD CONSTRAINT training_cycles_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: training_cycles training_cycles_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_cycles
    ADD CONSTRAINT training_cycles_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: training_cycles training_cycles_parent_cycle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_cycles
    ADD CONSTRAINT training_cycles_parent_cycle_id_fkey FOREIGN KEY (parent_cycle_id) REFERENCES public.training_cycles(id);


--
-- Name: training_cycles training_cycles_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_cycles
    ADD CONSTRAINT training_cycles_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id);


--
-- Name: training_microcycles training_microcycles_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_microcycles
    ADD CONSTRAINT training_microcycles_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: training_microcycles training_microcycles_cycle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_microcycles
    ADD CONSTRAINT training_microcycles_cycle_id_fkey FOREIGN KEY (cycle_id) REFERENCES public.training_cycles(id);


--
-- Name: training_microcycles training_microcycles_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_microcycles
    ADD CONSTRAINT training_microcycles_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: training_microcycles training_microcycles_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.training_microcycles
    ADD CONSTRAINT training_microcycles_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

\unrestrict R0Tiyv2c1Gqb6RtZvhCLRx3WBg9KkM6448C0Zv7TgfWaLbJA8qxPFrw1AQ4YCiL

