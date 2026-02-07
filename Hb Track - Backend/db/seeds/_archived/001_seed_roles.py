"""
Seed: Papéis do sistema (R4)
Regras: dirigente, coordenador, treinador, atleta

NOTA: Este seed verifica se os roles já existem (aplicados pela migração inicial).
"""
import sys
from pathlib import Path

# Adicionar backend ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.core.db import db_context


def seed_roles():
    with db_context() as session:
        # Verificar se já existem roles
        result = session.execute(text("SELECT COUNT(*) FROM roles"))
        count = result.scalar()

        if count > 0:
            print(f"❌ Roles já existem ({count} roles). Pulando seed.")
            return

        # Inserir roles (R4)
        session.execute(text("""
            INSERT INTO roles (code, name) VALUES
            ('dirigente', 'Dirigente'),
            ('coordenador', 'Coordenador'),
            ('treinador', 'Treinador'),
            ('atleta', 'Atleta')
            ON CONFLICT (code) DO NOTHING;
        """))
        print("[OK] Roles criados com sucesso!")


if __name__ == "__main__":
    seed_roles()
