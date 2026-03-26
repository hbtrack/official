"""
Migration 0002 — identity_access: CHECK constraints de integridade.
INV-IAM-002: roleLabel entre os 5 canônicos (ADR-008).
INV-IAM-003 (Classe B): issued_at < expires_at via trigger PostgreSQL.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("identity_access", "0001_initial"),
    ]

    operations = [
        # ── UserRoleBindingModel ──────────────────────────────────────────────
        migrations.AddConstraint(
            model_name="userrolebindingmodel",
            constraint=models.CheckConstraint(
                check=models.Q(
                    role_label__in=[
                        "admin", "coordinator", "coach", "athlete", "member"
                    ]
                ),
                name="identity_access_role_binding_role_label_valid",
            ),
        ),
        # ── AuthSessionModel — Classe B: PL/pgSQL trigger ────────────────────
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION identity_access_check_session_dates()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.issued_at IS NOT NULL AND NEW.expires_at IS NOT NULL THEN
                    IF NEW.issued_at >= NEW.expires_at THEN
                        RAISE EXCEPTION 'INV-IAM-003: issued_at deve ser anterior a expires_at';
                    END IF;
                END IF;
                IF NEW.issued_at IS NOT NULL AND NEW.revoked_at IS NOT NULL THEN
                    IF NEW.revoked_at < NEW.issued_at THEN
                        RAISE EXCEPTION 'INV-IAM-003: revoked_at deve ser >= issued_at';
                    END IF;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS trg_identity_access_session_dates
                ON identity_access_auth_sessions;
            CREATE TRIGGER trg_identity_access_session_dates
                BEFORE INSERT OR UPDATE ON identity_access_auth_sessions
                FOR EACH ROW EXECUTE FUNCTION identity_access_check_session_dates();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS trg_identity_access_session_dates
                ON identity_access_auth_sessions;
            DROP FUNCTION IF EXISTS identity_access_check_session_dates();
            """,
        ),
    ]
