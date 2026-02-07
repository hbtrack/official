"""
Teste manual de login - SEM usar o backend
"""
import os
import sys
from pathlib import Path

# Adiciona backend ao path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
import psycopg2
from passlib.context import CryptContext

# Carrega .env do backend
env_path = Path(__file__).parent.parent / 'backend' / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv('DATABASE_URL')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print("=" * 60)
print("TESTE MANUAL DE LOGIN")
print("=" * 60)
print(f"Database: {DATABASE_URL[:50]}...")
print()

# Conecta ao banco
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Busca super admin
email = "admin@hbtracking.com"
senha = "Admin@123"

cur.execute("""
    SELECT u.id, u.email, u.password_hash, u.is_superadmin
    FROM users u
    WHERE u.email = %s AND u.is_superadmin = true
""", (email,))

result = cur.fetchone()

if not result:
    print("ERRO: Super admin nao encontrado!")
    sys.exit(1)

user_id, db_email, password_hash, is_super = result

print(f"Usuario encontrado:")
print(f"  Email: {db_email}")
print(f"  ID: {user_id}")
print(f"  Superadmin: {is_super}")
print()

# Verifica senha
if pwd_context.verify(senha, password_hash):
    print("OK SENHA CORRETA!")
    print(f"  Credenciais: {email} / {senha}")
    print()
    print("PRONTO PARA LOGIN NO NAVEGADOR!")
else:
    print("ERRO: Senha incorreta!")

print("=" * 60)

cur.close()
conn.close()
