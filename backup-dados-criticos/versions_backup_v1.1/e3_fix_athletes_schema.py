"""Fix athletes schema per RDB rules

Revision ID: e3_fix_athletes_schema
Revises: e2_athlete_state_history
Create Date: 2025-12-27 16:00:00

Ajustes críticos conforme RDB:
1. REMOVER category_id de athletes (RD1, RD2) - categoria é sazonal, vai para team_registrations
2. REMOVER athlete_age_at_registration (campo calculado, não persistir)
3. ADICIONAR category_id em team_registrations (FK categories)
4. AJUSTAR constraint de posição ofensiva: NULL obrigatório para goleiras (RD13)
5. ADICIONAR índice case-insensitive para athlete_email
6. ADICIONAR trigger para bloquear DELETE físico (RDB4)
7. ADICIONAR triggers de auditoria para INSERT/UPDATE/soft-delete
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = 'e3_fix_athletes_schema'
down_revision: Union[str, None] = 'e2_athlete_state_history'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ====================================================================
    # 1. MOVER category_id PARA team_registrations (RD1, RD2)
    # ====================================================================

    # Adicionar category_id em team_registrations (se ainda não existir)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'team_registrations' AND column_name = 'category_id'
            ) THEN
                ALTER TABLE team_registrations ADD COLUMN category_id INTEGER;
            END IF;
        END $$;
    """)

    # Criar FK (se ainda não existir)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE constraint_name = 'fk_team_registrations_category'
            ) THEN
                ALTER TABLE team_registrations
                ADD CONSTRAINT fk_team_registrations_category
                FOREIGN KEY (category_id) REFERENCES categories(id);
            END IF;
        END $$;
    """)

    # Migrar dados existentes: copiar category_id de athletes para team_registrations
    op.execute("""
        UPDATE team_registrations tr
        SET category_id = a.category_id
        FROM athletes a
        WHERE tr.athlete_id = a.id
          AND a.category_id IS NOT NULL
    """)

    # Tornar category_id NOT NULL em team_registrations após popular
    # NOTA: Comentado porque pode haver registros sem categoria ainda
    # op.alter_column('team_registrations', 'category_id', nullable=False)

    # Remover category_id de athletes (agora obsoleto) - SE EXISTIR
    op.execute("ALTER TABLE athletes DROP CONSTRAINT IF EXISTS fk_athletes_category")
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'athletes' AND column_name = 'category_id'
            ) THEN
                ALTER TABLE athletes DROP COLUMN category_id;
            END IF;
        END $$;
    """)

    # ====================================================================
    # 2. REMOVER athlete_age_at_registration (campo calculado) - SE EXISTIR
    # ====================================================================

    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'athletes' AND column_name = 'athlete_age_at_registration'
            ) THEN
                ALTER TABLE athletes DROP COLUMN athlete_age_at_registration;
            END IF;
        END $$;
    """)

    # ====================================================================
    # 3. AJUSTAR CONSTRAINT DE POSIÇÃO OFENSIVA (RD13)
    # ====================================================================

    # Remover constraint antiga (se existir)
    op.execute("ALTER TABLE athletes DROP CONSTRAINT IF EXISTS ck_athletes_offensive_position_required")

    # Nova constraint: goleiras (id=5) DEVEM ter posição ofensiva NULL
    op.create_check_constraint(
        'ck_athletes_goalkeeper_no_offensive',
        'athletes',
        """
        (main_defensive_position_id = 5 AND main_offensive_position_id IS NULL)
        OR
        (main_defensive_position_id != 5 AND main_offensive_position_id IS NOT NULL)
        """
    )

    # ====================================================================
    # 4. ÍNDICE CASE-INSENSITIVE PARA athlete_email
    # ====================================================================

    # Remover índice antigo
    op.drop_index('ux_athletes_email', table_name='athletes')

    # Criar índice case-insensitive
    op.execute("""
        CREATE UNIQUE INDEX ux_athletes_email_lower
        ON athletes (lower(athlete_email))
        WHERE athlete_email IS NOT NULL AND deleted_at IS NULL
    """)

    # ====================================================================
    # 5. TRIGGER PARA BLOQUEAR DELETE FÍSICO (RDB4)
    # ====================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_physical_delete_athletes()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'DELETE físico não permitido em athletes (RDB4). Use soft delete.';
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_prevent_delete_athletes
        BEFORE DELETE ON athletes
        FOR EACH ROW
        EXECUTE FUNCTION prevent_physical_delete_athletes();
    """)

    # ====================================================================
    # 6. TRIGGERS DE AUDITORIA (RDB5, R31-R32)
    # ====================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION trg_audit_athletes()
        RETURNS TRIGGER AS $$
        BEGIN
            IF (TG_OP = 'INSERT') THEN
                PERFORM log_audit(
                    'athletes',
                    NEW.id,
                    'INSERT',
                    NULL,
                    to_jsonb(NEW),
                    'Criação de atleta'
                );
                RETURN NEW;

            ELSIF (TG_OP = 'UPDATE') THEN
                -- Detectar soft delete
                IF (OLD.deleted_at IS NULL AND NEW.deleted_at IS NOT NULL) THEN
                    PERFORM log_audit(
                        'athletes',
                        NEW.id,
                        'SOFT_DELETE',
                        to_jsonb(OLD),
                        to_jsonb(NEW),
                        NEW.deleted_reason
                    );
                ELSE
                    -- Update normal
                    PERFORM log_audit(
                        'athletes',
                        NEW.id,
                        'UPDATE',
                        to_jsonb(OLD),
                        to_jsonb(NEW),
                        'Atualização de atleta'
                    );
                END IF;
                RETURN NEW;
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_audit_athletes_after
        AFTER INSERT OR UPDATE ON athletes
        FOR EACH ROW
        EXECUTE FUNCTION trg_audit_athletes();
    """)

    # ====================================================================
    # 7. ATUALIZAR TRIGGER DE CÁLCULO (sem athlete_age_at_registration)
    # ====================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION trg_calculate_athlete_fields()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Apenas validar birth_date (cálculos são feitos em runtime)
            IF NEW.birth_date IS NULL THEN
                RAISE EXCEPTION 'birth_date é obrigatório';
            END IF;

            -- Garantir registered_at se não fornecido
            IF NEW.registered_at IS NULL THEN
                NEW.registered_at := now();
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    # Reverter triggers
    op.execute("DROP TRIGGER IF EXISTS trg_audit_athletes_after ON athletes")
    op.execute("DROP FUNCTION IF EXISTS trg_audit_athletes()")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_delete_athletes ON athletes")
    op.execute("DROP FUNCTION IF EXISTS prevent_physical_delete_athletes()")

    # Reverter índice email
    op.execute("DROP INDEX IF EXISTS ux_athletes_email_lower")
    op.create_index(
        'ux_athletes_email',
        'athletes',
        [sa.text('lower(athlete_email)')],
        unique=True,
        postgresql_where=sa.text('athlete_email IS NOT NULL')
    )

    # Reverter constraint posição
    op.drop_constraint('ck_athletes_goalkeeper_no_offensive', 'athletes', type_='check')
    op.create_check_constraint(
        'ck_athletes_offensive_position_required',
        'athletes',
        'main_defensive_position_id = 5 OR main_offensive_position_id IS NOT NULL'
    )

    # Reverter athlete_age_at_registration
    op.add_column('athletes', sa.Column('athlete_age_at_registration', sa.Integer(), nullable=True))

    # Reverter category_id
    op.add_column('athletes', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_athletes_category', 'athletes', 'categories', ['category_id'], ['id'])

    # Copiar de volta de team_registrations
    op.execute("""
        UPDATE athletes a
        SET category_id = (
            SELECT tr.category_id
            FROM team_registrations tr
            WHERE tr.athlete_id = a.id
              AND tr.deleted_at IS NULL
            ORDER BY tr.created_at DESC
            LIMIT 1
        )
    """)

    # Remover de team_registrations
    op.drop_constraint('fk_team_registrations_category', 'team_registrations', type_='foreignkey')
    op.drop_column('team_registrations', 'category_id')
