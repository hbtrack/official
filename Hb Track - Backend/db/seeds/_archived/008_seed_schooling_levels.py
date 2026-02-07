"""
Seed: Níveis de escolaridade (schooling_levels)
População dos 6 níveis de escolaridade baseado nos dados de backup
"""
import sys
from pathlib import Path

# Adicionar backend ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.core.db import db_context


def seed_schooling_levels():
    with db_context() as session:
        # Verificar se já existem níveis
        result = session.execute(text("SELECT COUNT(*) FROM schooling_levels"))
        count = result.scalar()

        if count > 0:
            print(f"[SKIP] Níveis de escolaridade já existem ({count} níveis). Pulando seed.")
            return

        # Inserir os 6 níveis de escolaridade
        schooling_data = [
            (1, '7EF', '7º ano do Ensino Fundamental'),
            (2, '8EF', '8º ano do Ensino Fundamental'), 
            (3, '9EF', '9º ano do Ensino Fundamental'),
            (4, '1EM', '1º ano do Ensino Médio'),
            (5, '2EM', '2º ano do Ensino Médio'),
            (6, '3EM', '3º ano do Ensino Médio'),
        ]

        # Inserir níveis
        for level_id, code, name in schooling_data:
            session.execute(text("""
                INSERT INTO schooling_levels (id, code, name, is_active)
                VALUES (:id, :code, :name, true)
            """), {
                'id': level_id,
                'code': code,
                'name': name
            })

        print(f"[OK] {len(schooling_data)} níveis de escolaridade criados!")


if __name__ == "__main__":
    seed_schooling_levels()