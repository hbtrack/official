"""Ensure roles.code exists with unique index

Revision ID: e6_add_roles_code
Revises: e5_update_user_membership_trigger
Create Date: 2025-12-28 00:00:00
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e6_add_roles_code"
down_revision: Union[str, None] = "e5_update_user_membership_trigger"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1
              FROM information_schema.columns
             WHERE table_name = 'roles'
               AND column_name = 'code'
          ) THEN
            ALTER TABLE roles ADD COLUMN code text;
          END IF;
        END $$;
        """
    )

    op.execute(
        """
        UPDATE roles
           SET code = CASE lower(name)
             WHEN 'dirigente' THEN 'dirigente'
             WHEN 'coordenador' THEN 'coordenador'
             WHEN 'treinador' THEN 'treinador'
             WHEN 'atleta' THEN 'atleta'
             ELSE lower(regexp_replace(name, '\\s+', '_', 'g'))
           END
         WHERE code IS NULL;
        """
    )

    op.execute(
        """
        ALTER TABLE roles
        ALTER COLUMN code SET NOT NULL;
        """
    )

    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_roles_code
        ON roles (lower(code));
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ux_roles_code;")
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1
              FROM information_schema.columns
             WHERE table_name = 'roles'
               AND column_name = 'code'
          ) THEN
            ALTER TABLE roles DROP COLUMN code;
          END IF;
        END $$;
        """
    )
