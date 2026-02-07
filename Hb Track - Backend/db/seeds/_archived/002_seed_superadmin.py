"""
Seed: Super Administrador único (R3, RDB6)
Seed inicial deve criar EXATAMENTE 1 superadmin

NOTA: Este seed verifica se o superadmin já existe (aplicado pela migração inicial).
"""
import sys
from pathlib import Path

# Adicionar backend ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.core.db import db_context
import uuid


def seed_superadmin():
    with db_context() as session:
        # Verificar se já existe superadmin (RDB6)
        result = session.execute(text(
            "SELECT COUNT(*) FROM users WHERE is_superadmin = true"
        ))
        count = result.scalar()

        if count > 0:
            print(f"❌ Super Admin já existe ({count} superadmin(s)). Pulando seed.")
            return

        # Criar pessoa
        person_id = uuid.uuid4()
        session.execute(text("""
            INSERT INTO persons (id, full_name, first_name, last_name, birth_date)
            VALUES (:id, 'Super Administrador', 'Super', 'Administrador', NULL)
        """), {"id": person_id})

        # Criar usuário superadmin
        session.execute(text("""
            INSERT INTO users (person_id, email, is_superadmin, status)
            VALUES (:person_id, 'admin@hbtracking.com', true, 'ativo')
        """), {"person_id": person_id})

        # Criar organização (R34 - clube único na V1)
        org_id = uuid.uuid4()
        session.execute(text("""
            INSERT INTO organizations (id, name)
            VALUES (:org_id, 'Clube HB Tracking')
        """), {"org_id": org_id})

        print("[OK] Super Administrador criado!")
        print(f"   Email: admin@hbtracking.com")
        print(f"   Person ID: {person_id}")


if __name__ == "__main__":
    seed_superadmin()
