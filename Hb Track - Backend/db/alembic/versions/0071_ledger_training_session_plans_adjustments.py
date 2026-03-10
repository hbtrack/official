"""Ledger de sessao: training_session_plans + training_session_adjustments

Revision ID: 0071
Revises: 0070
Create Date: 2026-05-30 00:00:00.000000

Evidencia:
  - AR: AR_274 — Ledger de Sessao + Scheduler SKIP LOCKED

Changes:
  1. CREATE TABLE training_session_plans (append-only + imutavel via trigger)
  2. CREATE TABLE training_session_adjustments (append-only via trigger)
  3. Triggers de imutabilidade fisica: proibem UPDATE/DELETE em ambas as tabelas

Rationale:
  Ledger imutavel para rastreabilidade de planos de treino gerados pela IA.
  Imutabilidade fisica e obrigatoria (Gate 3) — apenas Python seria insuficiente.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0071"
down_revision = "0070"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # TABLE: training_session_plans                                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        "training_session_plans",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("training_sessions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "draft_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment="Referencia ao draft de IA de origem (rastreabilidade)",
        ),
        sa.Column(
            "plan_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_training_session_plans_session_id",
        "training_session_plans",
        ["session_id"],
    )

    # ------------------------------------------------------------------ #
    # TABLE: training_session_adjustments                                  #
    # ------------------------------------------------------------------ #
    op.create_table(
        "training_session_adjustments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "plan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("training_session_plans.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("training_sessions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "sequence_number",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "adjustment_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_training_session_adjustments_plan_id",
        "training_session_adjustments",
        ["plan_id"],
    )
    op.create_index(
        "ix_training_session_adjustments_session_id",
        "training_session_adjustments",
        ["session_id"],
    )

    # ------------------------------------------------------------------ #
    # IMUTABILIDADE FISICA — trigger proibe UPDATE/DELETE                  #
    # ------------------------------------------------------------------ #
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_immutable_ledger_row()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION
                'Operacao % proibida na tabela imutavel %: ledger append-only',
                TG_OP, TG_TABLE_NAME;
        END;
        $$;
    """)

    op.execute("""
        CREATE TRIGGER trg_training_session_plans_immutable
        BEFORE UPDATE OR DELETE ON training_session_plans
        FOR EACH ROW EXECUTE FUNCTION fn_immutable_ledger_row();
    """)

    op.execute("""
        CREATE TRIGGER trg_training_session_adjustments_immutable
        BEFORE UPDATE OR DELETE ON training_session_adjustments
        FOR EACH ROW EXECUTE FUNCTION fn_immutable_ledger_row();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_training_session_adjustments_immutable ON training_session_adjustments")
    op.execute("DROP TRIGGER IF EXISTS trg_training_session_plans_immutable ON training_session_plans")
    op.execute("DROP FUNCTION IF EXISTS fn_immutable_ledger_row()")
    op.drop_index("ix_training_session_adjustments_session_id", table_name="training_session_adjustments")
    op.drop_index("ix_training_session_adjustments_plan_id", table_name="training_session_adjustments")
    op.drop_table("training_session_adjustments")
    op.drop_index("ix_training_session_plans_session_id", table_name="training_session_plans")
    op.drop_table("training_session_plans")
