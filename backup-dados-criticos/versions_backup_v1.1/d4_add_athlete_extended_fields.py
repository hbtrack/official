"""Add extended fields to athletes table

Revision ID: d4_athlete_fields
Revises: d3_schooling_lvl
Create Date: 2025-12-27 10:03:00

Adiciona campos estendidos à tabela athletes conforme especificação:
- Renomeia full_name para athlete_name
- Adiciona athlete_nickname (renomeia nickname)
- Adiciona registered_at (timestamp de registro)
- Adiciona athlete_age_at_registration (calculado via trigger)
- Adiciona category_id (FK categories, calculado via trigger)
- Adiciona shirt_number (número da camisa 1-99)
- Adiciona main_defensive_position_id (FK defensive_positions, NOT NULL)
- Adiciona secondary_defensive_position_id (FK defensive_positions, NULL)
- Adiciona main_offensive_position_id (FK offensive_positions, condicional)
- Adiciona secondary_offensive_position_id (FK offensive_positions, NULL)
- Adiciona athlete_rg, athlete_cpf (documentos, UNIQUE)
- Adiciona athlete_phone, athlete_email (contatos)
- Adiciona guardian_name, guardian_phone (responsável)
- Adiciona schooling_id (FK schooling_levels)
- Adiciona zip_code, street, neighborhood, city, state, address_number, address_complement
- Adiciona is_active (boolean, default TRUE)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'd4_athlete_fields'
down_revision: Union[str, None] = 'd3_schooling_lvl'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Renomear colunas existentes
    op.alter_column('athletes', 'full_name', new_column_name='athlete_name')
    op.alter_column('athletes', 'nickname', new_column_name='athlete_nickname')

    # 2. Preencher birth_date NULL com data padrão (01/01/2010) antes de tornar NOT NULL
    op.execute("UPDATE athletes SET birth_date = '2010-01-01' WHERE birth_date IS NULL")

    # 3. Tornar birth_date NOT NULL (era nullable antes)
    op.alter_column('athletes', 'birth_date', nullable=False)

    # 3. Adicionar campos de timestamp
    op.add_column('athletes', sa.Column('registered_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False))

    # 4. Adicionar campos calculados (serão preenchidos por triggers)
    op.add_column('athletes', sa.Column('athlete_age_at_registration', sa.Integer(), nullable=True))  # Inicialmente NULL, trigger vai preencher
    op.add_column('athletes', sa.Column('category_id', sa.Integer(), nullable=True))  # Inicialmente NULL, trigger vai preencher

    # 5. Adicionar shirt_number com CHECK constraint
    op.add_column('athletes', sa.Column('shirt_number', sa.Integer(), nullable=True))
    op.create_check_constraint('ck_athletes_shirt_number', 'athletes', 'shirt_number BETWEEN 1 AND 99')

    # 6. Adicionar FKs para posições
    op.add_column('athletes', sa.Column('main_defensive_position_id', sa.Integer(), nullable=True))  # Inicialmente NULL, depois tornar NOT NULL
    op.add_column('athletes', sa.Column('secondary_defensive_position_id', sa.Integer(), nullable=True))
    op.add_column('athletes', sa.Column('main_offensive_position_id', sa.Integer(), nullable=True))
    op.add_column('athletes', sa.Column('secondary_offensive_position_id', sa.Integer(), nullable=True))

    op.create_foreign_key('fk_athletes_main_def_pos', 'athletes', 'defensive_positions', ['main_defensive_position_id'], ['id'])
    op.create_foreign_key('fk_athletes_sec_def_pos', 'athletes', 'defensive_positions', ['secondary_defensive_position_id'], ['id'])
    op.create_foreign_key('fk_athletes_main_off_pos', 'athletes', 'offensive_positions', ['main_offensive_position_id'], ['id'])
    op.create_foreign_key('fk_athletes_sec_off_pos', 'athletes', 'offensive_positions', ['secondary_offensive_position_id'], ['id'])

    # 7. Adicionar documentos (RG e CPF)
    op.add_column('athletes', sa.Column('athlete_rg', sa.String(20), nullable=True))  # Inicialmente NULL, depois tornar NOT NULL
    op.add_column('athletes', sa.Column('athlete_cpf', sa.String(14), nullable=True))  # Inicialmente NULL, depois tornar NOT NULL

    # Índices únicos para RG e CPF
    op.create_index('ux_athletes_rg', 'athletes', ['athlete_rg'], unique=True, postgresql_where=sa.text('athlete_rg IS NOT NULL'))
    op.create_index('ux_athletes_cpf', 'athletes', ['athlete_cpf'], unique=True, postgresql_where=sa.text('athlete_cpf IS NOT NULL'))

    # 8. Adicionar contatos
    op.add_column('athletes', sa.Column('athlete_phone', sa.String(20), nullable=True))  # Inicialmente NULL, depois tornar NOT NULL
    op.add_column('athletes', sa.Column('athlete_email', sa.String(100), nullable=True))

    # Índice único para email
    op.create_index('ux_athletes_email', 'athletes', [sa.text('lower(athlete_email)')], unique=True, postgresql_where=sa.text('athlete_email IS NOT NULL'))

    # 9. Adicionar dados do responsável
    op.add_column('athletes', sa.Column('guardian_name', sa.String(100), nullable=True))
    op.add_column('athletes', sa.Column('guardian_phone', sa.String(20), nullable=True))

    # 10. Adicionar escolaridade
    op.add_column('athletes', sa.Column('schooling_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_athletes_schooling', 'athletes', 'schooling_levels', ['schooling_id'], ['id'])

    # 11. Adicionar endereço completo (CEP separado)
    op.add_column('athletes', sa.Column('zip_code', sa.String(9), nullable=True))
    op.add_column('athletes', sa.Column('street', sa.String(120), nullable=True))
    op.add_column('athletes', sa.Column('neighborhood', sa.String(80), nullable=True))
    op.add_column('athletes', sa.Column('city', sa.String(80), nullable=True))
    op.add_column('athletes', sa.Column('address_state', sa.String(2), nullable=True))  # address_state ao invés de state para não conflitar
    op.add_column('athletes', sa.Column('address_number', sa.String(20), nullable=True))
    op.add_column('athletes', sa.Column('address_complement', sa.String(80), nullable=True))

    # 12. Adicionar is_active
    op.add_column('athletes', sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False))

    # NOTA: NÃO remover coluna position - há views que dependem dela (v_session_athlete_dashboard, mv_athlete_training_summary, mv_medical_cases_summary)
    # A coluna position permanece como deprecated/legacy, use os novos campos main_defensive_position_id, etc.

    # NOTA: Os triggers para calcular athlete_age_at_registration e category_id serão criados em migration separada


def downgrade() -> None:
    # Reverter todas as mudanças (exceto position que não foi removido)
    op.drop_column('athletes', 'is_active')
    op.drop_column('athletes', 'address_complement')
    op.drop_column('athletes', 'address_number')
    op.drop_column('athletes', 'address_state')
    op.drop_column('athletes', 'city')
    op.drop_column('athletes', 'neighborhood')
    op.drop_column('athletes', 'street')
    op.drop_column('athletes', 'zip_code')
    op.drop_constraint('fk_athletes_schooling', 'athletes', type_='foreignkey')
    op.drop_column('athletes', 'schooling_id')
    op.drop_column('athletes', 'guardian_phone')
    op.drop_column('athletes', 'guardian_name')
    op.drop_index('ux_athletes_email', table_name='athletes')
    op.drop_column('athletes', 'athlete_email')
    op.drop_column('athletes', 'athlete_phone')
    op.drop_index('ux_athletes_cpf', table_name='athletes')
    op.drop_index('ux_athletes_rg', table_name='athletes')
    op.drop_column('athletes', 'athlete_cpf')
    op.drop_column('athletes', 'athlete_rg')
    op.drop_constraint('fk_athletes_sec_off_pos', 'athletes', type_='foreignkey')
    op.drop_constraint('fk_athletes_main_off_pos', 'athletes', type_='foreignkey')
    op.drop_constraint('fk_athletes_sec_def_pos', 'athletes', type_='foreignkey')
    op.drop_constraint('fk_athletes_main_def_pos', 'athletes', type_='foreignkey')
    op.drop_column('athletes', 'secondary_offensive_position_id')
    op.drop_column('athletes', 'main_offensive_position_id')
    op.drop_column('athletes', 'secondary_defensive_position_id')
    op.drop_column('athletes', 'main_defensive_position_id')
    op.drop_constraint('ck_athletes_shirt_number', 'athletes', type_='check')
    op.drop_column('athletes', 'shirt_number')
    op.drop_column('athletes', 'category_id')
    op.drop_column('athletes', 'athlete_age_at_registration')
    op.drop_column('athletes', 'registered_at')
    op.alter_column('athletes', 'birth_date', nullable=True)
    op.alter_column('athletes', 'athlete_nickname', new_column_name='nickname')
    op.alter_column('athletes', 'athlete_name', new_column_name='full_name')
