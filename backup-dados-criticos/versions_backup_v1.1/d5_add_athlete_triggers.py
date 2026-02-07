"""Add triggers for automatic calculations in athletes

Revision ID: d5_athlete_triggers
Revises: d4_athlete_fields
Create Date: 2025-12-27 10:04:00

Cria triggers para cálculos automáticos em athletes:
1. Trigger para calcular athlete_age_at_registration (idade no momento do registro)
2. Trigger para calcular e setar category_id automaticamente pela idade
3. Constraint condicional: main_offensive_position_id obrigatório exceto para goleiras
4. Atualizar registros existentes com valores calculados
5. Tornar campos obrigatórios após preencher dados existentes
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5_athlete_triggers'
down_revision: Union[str, None] = 'd4_athlete_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Criar função para calcular idade
    op.execute("""
    CREATE OR REPLACE FUNCTION calculate_age(birth_date DATE, reference_date DATE)
    RETURNS INTEGER AS $$
    BEGIN
        RETURN EXTRACT(YEAR FROM AGE(reference_date, birth_date))::INTEGER;
    END;
    $$ LANGUAGE plpgsql IMMUTABLE;
    """)

    # 2. Criar função para obter category_id pela idade
    op.execute("""
    CREATE OR REPLACE FUNCTION get_category_by_age(age INTEGER)
    RETURNS INTEGER AS $$
    BEGIN
        -- Buscar categoria onde age está entre min_age e max_age
        RETURN (
            SELECT id
            FROM categories
            WHERE age >= COALESCE(min_age, 0)
            AND (max_age IS NULL OR age <= max_age)
            AND deleted_at IS NULL
            ORDER BY min_age DESC
            LIMIT 1
        );
    END;
    $$ LANGUAGE plpgsql STABLE;
    """)

    # 3. Criar trigger function para calcular e setar campos automáticos
    op.execute("""
    CREATE OR REPLACE FUNCTION trg_calculate_athlete_fields()
    RETURNS TRIGGER AS $$
    BEGIN
        -- Calcular idade no momento do registro
        IF NEW.birth_date IS NOT NULL AND NEW.registered_at IS NOT NULL THEN
            NEW.athlete_age_at_registration := calculate_age(NEW.birth_date, NEW.registered_at::DATE);
        END IF;

        -- Setar category_id automaticamente
        IF NEW.athlete_age_at_registration IS NOT NULL THEN
            NEW.category_id := get_category_by_age(NEW.athlete_age_at_registration);
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # 4. Criar trigger BEFORE INSERT OR UPDATE
    op.execute("""
    CREATE TRIGGER trg_before_insert_update_athlete
    BEFORE INSERT OR UPDATE ON athletes
    FOR EACH ROW
    EXECUTE FUNCTION trg_calculate_athlete_fields();
    """)

    # 5. Atualizar registros existentes (se houver)
    op.execute("""
    UPDATE athletes
    SET athlete_age_at_registration = calculate_age(birth_date, registered_at::DATE),
        category_id = get_category_by_age(calculate_age(birth_date, registered_at::DATE))
    WHERE birth_date IS NOT NULL AND registered_at IS NOT NULL;
    """)

    # 6. Criar CHECK constraint condicional:
    # main_offensive_position_id obrigatório EXCETO para goleiras (defensive_position_id = 5)
    op.create_check_constraint(
        'ck_athletes_offensive_position_required',
        'athletes',
        'main_defensive_position_id = 5 OR main_offensive_position_id IS NOT NULL'
    )

    # 7. Agora tornar category_id NOT NULL (após preencher)
    op.alter_column('athletes', 'category_id', nullable=False)

    # 8. Criar FK para category_id
    op.create_foreign_key('fk_athletes_category', 'athletes', 'categories', ['category_id'], ['id'])


def downgrade() -> None:
    # Reverter na ordem inversa
    op.drop_constraint('fk_athletes_category', 'athletes', type_='foreignkey')
    op.alter_column('athletes', 'category_id', nullable=True)
    op.drop_constraint('ck_athletes_offensive_position_required', 'athletes', type_='check')
    op.execute('DROP TRIGGER IF EXISTS trg_before_insert_update_athlete ON athletes')
    op.execute('DROP FUNCTION IF EXISTS trg_calculate_athlete_fields()')
    op.execute('DROP FUNCTION IF EXISTS get_category_by_age(INTEGER)')
    op.execute('DROP FUNCTION IF EXISTS calculate_age(DATE, DATE)')
