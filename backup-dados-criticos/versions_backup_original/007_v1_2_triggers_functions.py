"""V1.2 - Create triggers and database functions

Revision ID: 007_v1_2_triggers_functions
Revises: 006_v1_2_matches_events
Create Date: 2025-12-28 05:40:00

REGRAS_SISTEMAS_V1.2.md: RDB18 - Triggers obrigatórios
V1.2: updated_at, athlete_age, bloqueios, soft delete, audit_logs, auto-encerramento
"""
from alembic import op
import sqlalchemy as sa

revision = '007_v1_2_triggers_functions'
down_revision = '006_v1_2_matches_events'
branch_labels = None
depends_on = None


def upgrade():
    # ========== FUNÇÃO 1: updated_at automático ==========
    # RDB18.1: updated_at BEFORE UPDATE em todas as tabelas de domínio
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Lista de tabelas de domínio que precisam de updated_at
    domain_tables = [
        'organizations', 'persons', 'users', 'org_memberships',
        'athletes', 'teams', 'seasons', 'team_registrations',
        'training_sessions', 'attendance', 'wellness_pre', 'wellness_post',
        'matches'
    ]

    for table in domain_tables:
        op.execute(f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION trg_set_updated_at();
        """)

    # ========== FUNÇÃO 2: athlete_age_at_registration automático ==========
    # RDB18.2: athlete_age_at_registration ON INSERT/UPDATE (quando registered_at/birth_date mudam)
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_set_athlete_age_at_registration()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.birth_date IS NOT NULL AND NEW.registered_at IS NOT NULL THEN
                NEW.athlete_age_at_registration = EXTRACT(YEAR FROM AGE(NEW.registered_at, NEW.birth_date));
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_athletes_age_at_registration
        BEFORE INSERT OR UPDATE OF birth_date, registered_at ON athletes
        FOR EACH ROW
        EXECUTE FUNCTION trg_set_athlete_age_at_registration();
    """)

    # ========== FUNÇÃO 3: Bloqueio de UPDATE em matches finalizados ==========
    # RDB18.3: Bloqueio de UPDATE em matches com status=finished
    # Exceção: mudança para status=in_progress (reabertura) por Coordenador/Dirigente
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_block_finished_match_update()
        RETURNS TRIGGER AS $$
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
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_matches_block_finished_update
        BEFORE UPDATE ON matches
        FOR EACH ROW
        EXECUTE FUNCTION trg_block_finished_match_update();
    """)

    # ========== FUNÇÃO 4: Bloqueio de DELETE físico em tabelas com soft delete ==========
    # RDB18.4: Bloqueio de DELETE físico
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_block_physical_delete()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'DELETE físico bloqueado. Use soft delete (UPDATE deleted_at, deleted_reason) na tabela %.', TG_TABLE_NAME;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Lista de tabelas com soft delete
    soft_delete_tables = [
        'organizations', 'persons', 'users', 'org_memberships',
        'athletes', 'teams', 'seasons', 'team_registrations',
        'training_sessions', 'attendance', 'wellness_pre', 'wellness_post',
        'matches'
    ]

    for table in soft_delete_tables:
        op.execute(f"""
            CREATE TRIGGER trg_{table}_block_delete
            BEFORE DELETE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION trg_block_physical_delete();
        """)

    # ========== FUNÇÃO 5: Bloqueio de UPDATE/DELETE em audit_logs ==========
    # RDB18.5: Bloqueio de UPDATE/DELETE em audit_logs (append-only)
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_block_audit_logs_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_logs é append-only. UPDATE e DELETE são bloqueados. Operação tentada: %', TG_OP;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_audit_logs_block_update
        BEFORE UPDATE ON audit_logs
        FOR EACH ROW
        EXECUTE FUNCTION trg_block_audit_logs_modification();
    """)

    op.execute("""
        CREATE TRIGGER trg_audit_logs_block_delete
        BEFORE DELETE ON audit_logs
        FOR EACH ROW
        EXECUTE FUNCTION trg_block_audit_logs_modification();
    """)

    # ========== FUNÇÃO 6: Encerramento automático de team_registrations ==========
    # RDB18.6: Encerramento automático de team_registrations quando atleta muda para state=dispensada
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_auto_end_team_registrations_on_dispensada()
        RETURNS TRIGGER AS $$
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
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_athletes_auto_end_registrations
        AFTER UPDATE OF state ON athletes
        FOR EACH ROW
        EXECUTE FUNCTION trg_auto_end_team_registrations_on_dispensada();
    """)

    # ========== FUNÇÃO 7: Função auxiliar para contexto do usuário (app.current_user) ==========
    # Usado para auditoria e validações
    op.execute("""
        CREATE SCHEMA IF NOT EXISTS app;
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION app.current_user()
        RETURNS UUID AS $$
        BEGIN
            -- Retorna o user_id do contexto da sessão
            -- Backend deve setar isso via: SET LOCAL app.current_user_id = '<uuid>';
            RETURN current_setting('app.current_user_id', true)::UUID;
        EXCEPTION
            WHEN OTHERS THEN
                RETURN NULL;
        END;
        $$ LANGUAGE plpgsql STABLE;
    """)

    # ========== COMENTÁRIOS NAS FUNÇÕES ==========
    op.execute("""
        COMMENT ON FUNCTION trg_set_updated_at() IS
        'RDB18.1: Atualiza automaticamente updated_at em todas as tabelas de domínio.';
    """)

    op.execute("""
        COMMENT ON FUNCTION trg_set_athlete_age_at_registration() IS
        'RDB18.2: Calcula automaticamente athlete_age_at_registration quando birth_date ou registered_at mudam.';
    """)

    op.execute("""
        COMMENT ON FUNCTION trg_block_finished_match_update() IS
        'RDB18.3: Bloqueia UPDATE em matches com status=finished. Exceção: reabertura para in_progress.';
    """)

    op.execute("""
        COMMENT ON FUNCTION trg_block_physical_delete() IS
        'RDB18.4: Bloqueia DELETE físico em tabelas com soft delete. Força uso de deleted_at + deleted_reason.';
    """)

    op.execute("""
        COMMENT ON FUNCTION trg_block_audit_logs_modification() IS
        'RDB18.5: Bloqueia UPDATE e DELETE em audit_logs. Tabela append-only, absolutamente imutável.';
    """)

    op.execute("""
        COMMENT ON FUNCTION trg_auto_end_team_registrations_on_dispensada() IS
        'RDB18.6: Encerra automaticamente todos team_registrations ativos quando atleta muda para state=dispensada.';
    """)

    op.execute("""
        COMMENT ON FUNCTION app.current_user() IS
        'Função auxiliar: retorna UUID do usuário atual do contexto da sessão. Backend seta via SET LOCAL.';
    """)


def downgrade():
    # Drop triggers primeiro (ordem inversa da criação)
    op.execute("DROP TRIGGER IF EXISTS trg_athletes_auto_end_registrations ON athletes;")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_logs_block_delete ON audit_logs;")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_logs_block_update ON audit_logs;")

    soft_delete_tables = [
        'organizations', 'persons', 'users', 'org_memberships',
        'athletes', 'teams', 'seasons', 'team_registrations',
        'training_sessions', 'attendance', 'wellness_pre', 'wellness_post',
        'matches'
    ]
    for table in soft_delete_tables:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_block_delete ON {table};")

    op.execute("DROP TRIGGER IF EXISTS trg_matches_block_finished_update ON matches;")
    op.execute("DROP TRIGGER IF EXISTS trg_athletes_age_at_registration ON athletes;")

    domain_tables = [
        'organizations', 'persons', 'users', 'org_memberships',
        'athletes', 'teams', 'seasons', 'team_registrations',
        'training_sessions', 'attendance', 'wellness_pre', 'wellness_post',
        'matches'
    ]
    for table in domain_tables:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS app.current_user();")
    op.execute("DROP FUNCTION IF EXISTS trg_auto_end_team_registrations_on_dispensada();")
    op.execute("DROP FUNCTION IF EXISTS trg_block_audit_logs_modification();")
    op.execute("DROP FUNCTION IF EXISTS trg_block_physical_delete();")
    op.execute("DROP FUNCTION IF EXISTS trg_block_finished_match_update();")
    op.execute("DROP FUNCTION IF EXISTS trg_set_athlete_age_at_registration();")
    op.execute("DROP FUNCTION IF EXISTS trg_set_updated_at();")

    # Drop schema
    op.execute("DROP SCHEMA IF EXISTS app CASCADE;")
