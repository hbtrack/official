"""V1.2 - Update categories data

Revision ID: 008_v1_2_update_categories
Revises: 007_v1_2_triggers_functions
Create Date: 2025-12-28 06:30:00

Corrige categorias oficiais do handebol:
- Mirim (12), Infantil (14), Cadete (16), Juvenil (18), Júnior (21), Adulto (36), Master (60)
"""
from alembic import op
import sqlalchemy as sa

revision = '008_v1_2_update_categories'
down_revision = '007_v1_2_triggers_functions'
branch_labels = None
depends_on = None


def upgrade():
    # Remove categorias antigas
    op.execute("DELETE FROM categories;")

    # Insere categorias corretas
    op.execute("""
        INSERT INTO categories (id, name, max_age, is_active)
        VALUES
            (1, 'Mirim', 12, true),
            (2, 'Infantil', 14, true),
            (3, 'Cadete', 16, true),
            (4, 'Juvenil', 18, true),
            (5, 'Júnior', 21, true),
            (6, 'Adulto', 36, true),
            (7, 'Master', 60, true)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            max_age = EXCLUDED.max_age;
    """)

    # Reseta sequence para próximo ID
    op.execute("SELECT setval('categories_id_seq', 7, true);")


def downgrade():
    # Volta para categorias antigas (4 categorias)
    op.execute("DELETE FROM categories;")

    op.execute("""
        INSERT INTO categories (id, name, max_age, is_active)
        VALUES
            (1, 'Infantil', 14, true),
            (2, 'Cadete', 16, true),
            (3, 'Juvenil', 19, true),
            (4, 'Adulto', 99, true)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            max_age = EXCLUDED.max_age;
    """)

    op.execute("SELECT setval('categories_id_seq', 4, true);")
