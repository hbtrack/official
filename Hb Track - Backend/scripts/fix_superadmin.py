"""
Script para garantir que o superadmin tenha is_superadmin=true e senha correta
"""
import os
import sys
from pathlib import Path
import psycopg2
import bcrypt
from dotenv import load_dotenv

# Carrega .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv('DATABASE_URL_SYNC') or os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definido")

# Converte URL para psycopg2
DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
DATABASE_URL = DATABASE_URL.replace('postgresql+psycopg2://', 'postgresql://')

# Senha padrão: Admin@123
password = 'Admin@123'
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Atualizar is_superadmin=true e senha
cur.execute("""
    UPDATE users 
    SET is_superadmin = true, 
        password_hash = %s,
        status = 'ativo',
        is_locked = false
    WHERE email = 'admin@hbtracking.com'
""", (password_hash,))

affected = cur.rowcount
conn.commit()

if affected > 0:
    print(f'✅ Superadmin atualizado com sucesso!')
    print(f'   Email: admin@hbtracking.com')
    print(f'   Senha: Admin@123')
    print(f'   is_superadmin: true')
else:
    print(f'❌ Usuário admin@hbtracking.com não encontrado!')
    print(f'   Execute o seed inicial: python scripts/seed_v1_2_initial.py')

cur.close()
conn.close()
