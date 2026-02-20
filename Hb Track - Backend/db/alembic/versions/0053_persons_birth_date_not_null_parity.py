"""persons birth_date NOT NULL + parity triggers

Revision ID: 0053
Revises: 0fb0f76b48a7
Create Date: 2026-02-20

AR: AR_003.5 — Migration: persons.birth_date NOT NULL + Trigger de Paridade com athletes
Steps: MIG-001 (pre-flight) → MIG-002 (backfill) → MIG-003 (verify) → MIG-004 (DDL NOT NULL)
       → MIG-005 (fn sync) → MIG-006 (trg sync) → MIG-007 (fn validate) → MIG-008 (trg validate)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0053'
down_revision: Union[str, Sequence[str], None] = '0fb0f76b48a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # ------------------------------------------------------------------
    # MIG-001: Pre-flight gate — PF-002 (non-athlete persons com NULL)
    # ------------------------------------------------------------------
    result_pf002 = conn.execute(sa.text("""
        SELECT COUNT(*) FROM persons p
        WHERE p.birth_date IS NULL AND p.deleted_at IS NULL
          AND NOT EXISTS (
              SELECT 1 FROM athletes a
              WHERE a.person_id = p.id AND a.deleted_at IS NULL
          )
    """)).scalar()
    if result_pf002 and result_pf002 > 0:
        rows = conn.execute(sa.text("""
            SELECT id, full_name FROM persons p
            WHERE p.birth_date IS NULL AND p.deleted_at IS NULL
              AND NOT EXISTS (
                  SELECT 1 FROM athletes a
                  WHERE a.person_id = p.id AND a.deleted_at IS NULL
              )
        """)).fetchall()
        raise RuntimeError(
            f'MIGRATION BLOCKED (PF-002): {result_pf002} non-athlete person(s) with NULL birth_date. '
            f'Correct manually before running: {[(str(r[0]), r[1]) for r in rows]}'
        )

    # ------------------------------------------------------------------
    # MIG-001: Pre-flight gate — PF-003 (divergência birth_date)
    # ------------------------------------------------------------------
    result_pf003 = conn.execute(sa.text("""
        SELECT COUNT(*) FROM athletes a
        JOIN persons p ON a.person_id = p.id
        WHERE p.birth_date IS NOT NULL AND p.birth_date != a.birth_date
          AND a.deleted_at IS NULL AND p.deleted_at IS NULL
    """)).scalar()
    if result_pf003 and result_pf003 > 0:
        rows = conn.execute(sa.text("""
            SELECT p.id, p.full_name, p.birth_date AS persons_bd, a.birth_date AS athletes_bd
            FROM athletes a JOIN persons p ON a.person_id = p.id
            WHERE p.birth_date IS NOT NULL AND p.birth_date != a.birth_date
              AND a.deleted_at IS NULL AND p.deleted_at IS NULL
        """)).fetchall()
        raise RuntimeError(
            f'MIGRATION BLOCKED (PF-003): {result_pf003} person(s) with birth_date divergence. '
            f'Resolve manually: {[(str(r[0]), r[1], str(r[2]), str(r[3])) for r in rows]}'
        )

    # ------------------------------------------------------------------
    # MIG-002: Backfill athletes.birth_date → persons.birth_date
    # ------------------------------------------------------------------
    op.execute(sa.text("""
        UPDATE persons p
        SET birth_date = a.birth_date,
            updated_at = now()
        FROM athletes a
        WHERE a.person_id = p.id
          AND p.birth_date IS NULL
          AND a.deleted_at IS NULL
          AND p.deleted_at IS NULL
    """))

    # ------------------------------------------------------------------
    # MIG-003: Verify backfill — must be 0 remaining NULLs for athletes
    # ------------------------------------------------------------------
    remaining = conn.execute(sa.text("""
        SELECT COUNT(*) FROM persons p
        JOIN athletes a ON a.person_id = p.id
        WHERE p.birth_date IS NULL AND a.deleted_at IS NULL
    """)).scalar()
    if remaining and remaining > 0:
        raise RuntimeError(
            f'BACKFILL INCOMPLETE (MIG-003): {remaining} athlete person(s) still have NULL birth_date.'
        )

    # ------------------------------------------------------------------
    # MIG-004: DDL — ALTER COLUMN birth_date SET NOT NULL
    # ------------------------------------------------------------------
    op.alter_column('persons', 'birth_date',
                    existing_type=sa.Date(),
                    nullable=False)

    # ------------------------------------------------------------------
    # MIG-005: Função fn_sync_birth_date_athletes_to_persons
    # ------------------------------------------------------------------
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION fn_sync_birth_date_athletes_to_persons()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.birth_date IS DISTINCT FROM OLD.birth_date THEN
                UPDATE persons
                SET birth_date = NEW.birth_date,
                    updated_at = now()
                WHERE id = NEW.person_id
                  AND deleted_at IS NULL;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    # ------------------------------------------------------------------
    # MIG-006: Trigger athletes → persons sync
    # ------------------------------------------------------------------
    op.execute(sa.text("""
        CREATE TRIGGER trg_sync_birth_date_athletes
        AFTER UPDATE OF birth_date ON athletes
        FOR EACH ROW
        EXECUTE FUNCTION fn_sync_birth_date_athletes_to_persons();
    """))

    # ------------------------------------------------------------------
    # MIG-007: Função fn_validate_birth_date_parity_on_person
    # ------------------------------------------------------------------
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION fn_validate_birth_date_parity_on_person()
        RETURNS TRIGGER AS $$
        DECLARE
            v_athlete_birth_date date;
        BEGIN
            SELECT a.birth_date INTO v_athlete_birth_date
            FROM athletes a
            WHERE a.person_id = NEW.id
              AND a.deleted_at IS NULL
            ORDER BY a.created_at DESC
            LIMIT 1;

            IF v_athlete_birth_date IS NOT NULL
               AND NEW.birth_date IS DISTINCT FROM v_athlete_birth_date THEN
                RAISE EXCEPTION
                    'INV-PARITY-001: persons.birth_date (%) deve ser igual a athletes.birth_date (%) para person_id=%',
                    NEW.birth_date, v_athlete_birth_date, NEW.id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    # ------------------------------------------------------------------
    # MIG-008: Trigger persons → athletes validation
    # ------------------------------------------------------------------
    op.execute(sa.text("""
        CREATE TRIGGER trg_validate_birth_date_persons
        BEFORE UPDATE OF birth_date ON persons
        FOR EACH ROW
        EXECUTE FUNCTION fn_validate_birth_date_parity_on_person();
    """))


def downgrade() -> None:
    # Remove triggers first, then functions, then revert DDL
    op.execute(sa.text('DROP TRIGGER IF EXISTS trg_validate_birth_date_persons ON persons;'))
    op.execute(sa.text('DROP FUNCTION IF EXISTS fn_validate_birth_date_parity_on_person();'))
    op.execute(sa.text('DROP TRIGGER IF EXISTS trg_sync_birth_date_athletes ON athletes;'))
    op.execute(sa.text('DROP FUNCTION IF EXISTS fn_sync_birth_date_athletes_to_persons();'))
    op.alter_column('persons', 'birth_date',
                    existing_type=sa.Date(),
                    nullable=True)
