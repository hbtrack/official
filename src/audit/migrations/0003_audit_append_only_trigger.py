"""
Trigger PostgreSQL — módulo audit.
INV-AUD-002 (banco): trigger que bloqueia UPDATE e DELETE direto no banco,
complementando o enforcement da camada de aplicação.
"""
from django.db import migrations

_CREATE_TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION audit_entry_append_only()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        RAISE EXCEPTION 'INV-AUD-002: audit_entry is append-only; UPDATE is forbidden';
    ELSIF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'INV-AUD-002: audit_entry is append-only; DELETE is forbidden';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_audit_entry_append_only ON audit_entry;
CREATE TRIGGER trg_audit_entry_append_only
    BEFORE UPDATE OR DELETE ON audit_entry
    FOR EACH ROW EXECUTE FUNCTION audit_entry_append_only();
"""

_DROP_TRIGGER_SQL = """
DROP TRIGGER IF EXISTS trg_audit_entry_append_only ON audit_entry;
DROP FUNCTION IF EXISTS audit_entry_append_only();
"""


class Migration(migrations.Migration):

    dependencies = [
        ("audit", "0002_add_constraints"),
    ]

    operations = [
        migrations.RunSQL(
            sql=_CREATE_TRIGGER_SQL,
            reverse_sql=_DROP_TRIGGER_SQL,
        ),
    ]
