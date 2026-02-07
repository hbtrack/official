"""Restore athlete_age_at_registration per REGRAS_SISTEMAS.md V1.1

Revision ID: e4_restore_age_at_reg
Revises: e3_fix_athletes_schema
Create Date: 2025-12-27 19:00:00

CORREÇÃO CRÍTICA: athlete_age_at_registration deve ser MANTIDO conforme REGRAS_SISTEMAS.md V1.1

Seção 4.1 - Atleta - Derivados/automáticos:
> athlete_age_at_registration: INT calculado por trigger (diff registered_at vs birth_date)

Seção 5.2 - Banco de Dados - Triggers:
> athlete_age_at_registration ON INSERT/UPDATE (somente quando registered_at/birth_date mudam)

Implementação:
1. Adicionar coluna athlete_age_at_registration INTEGER NOT NULL DEFAULT 0
2. Calcular valores existentes baseado em registered_at e birth_date
3. Criar trigger para calcular automaticamente em INSERT/UPDATE
4. Atualizar função trg_calculate_athlete_fields()
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e4_restore_age_at_reg'
down_revision: Union[str, None] = 'e3_fix_athletes_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ====================================================================
    # 1. ADICIONAR athlete_age_at_registration (INT calculado por trigger)
    # ====================================================================

    # Adicionar coluna (se não existir)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'athletes' AND column_name = 'athlete_age_at_registration'
            ) THEN
                ALTER TABLE athletes ADD COLUMN athlete_age_at_registration INTEGER NOT NULL DEFAULT 0;
            END IF;
        END $$;
    """)

    # ====================================================================
    # 2. CALCULAR VALORES EXISTENTES
    # ====================================================================

    # Calcular idade no momento do registro para atletas existentes
    op.execute("""
        UPDATE athletes
        SET athlete_age_at_registration = EXTRACT(YEAR FROM AGE(registered_at::DATE, birth_date))::INTEGER
        WHERE birth_date IS NOT NULL AND registered_at IS NOT NULL
    """)

    # ====================================================================
    # 3. ATUALIZAR TRIGGER PARA CALCULAR AUTOMATICAMENTE
    # ====================================================================

    # Atualizar função trg_calculate_athlete_fields() para calcular athlete_age_at_registration
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_calculate_athlete_fields()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Validar birth_date obrigatório
            IF NEW.birth_date IS NULL THEN
                RAISE EXCEPTION 'birth_date é obrigatório';
            END IF;

            -- Garantir registered_at se não fornecido
            IF NEW.registered_at IS NULL THEN
                NEW.registered_at := now();
            END IF;

            -- Calcular athlete_age_at_registration (idade no momento do registro)
            -- REGRAS_SISTEMAS.md V1.1 - Seção 4.1:
            -- "athlete_age_at_registration: INT calculado por trigger (diff registered_at vs birth_date)"
            NEW.athlete_age_at_registration := EXTRACT(YEAR FROM AGE(NEW.registered_at::DATE, NEW.birth_date))::INTEGER;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Garantir que trigger existe
    op.execute("""
        DROP TRIGGER IF EXISTS trg_before_insert_update_athlete ON athletes;
    """)

    op.execute("""
        CREATE TRIGGER trg_before_insert_update_athlete
        BEFORE INSERT OR UPDATE ON athletes
        FOR EACH ROW
        EXECUTE FUNCTION trg_calculate_athlete_fields();
    """)


def downgrade() -> None:
    # Remover coluna athlete_age_at_registration
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

    # Restaurar trigger simples (sem cálculo de age_at_registration)
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_calculate_athlete_fields()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Apenas validar birth_date
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
