"""Relax ensure_user_active_membership for planned seasons

Revision ID: e5_update_user_membership_trigger
Revises: e4_restore_age_at_reg
Create Date: 2025-12-28 00:00:00

Permite criar usuario com membership iniciado no futuro (temporada planejada).
Operacoes continuam bloqueadas via regra de negocio (R42) no backend.
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e5_update_user_membership_trigger"
down_revision: Union[str, None] = "e4_restore_age_at_reg"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION ensure_user_active_membership()
        RETURNS trigger AS $$
        DECLARE v_has_membership boolean;
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
               AND (m.end_date IS NULL OR m.end_date >= current_date)
          ) INTO v_has_membership;

          IF NOT v_has_membership THEN
            RAISE EXCEPTION 'Usuario sem vinculo ativo';
          END IF;

          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION ensure_user_active_membership()
        RETURNS trigger AS $$
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
        """
    )
