"""
Script para configurar senha do Super Admin
Execução: python scripts/setup_super_admin_password.py

Atualiza o password_hash do super admin no banco de dados
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
import secrets

# Carrega .env do backend
env_path = Path(__file__).parent.parent / 'backend' / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definido. Configure .env.")

# Configuração de hash (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_jwt_secret():
    """Gera um JWT_SECRET seguro"""
    return secrets.token_urlsafe(32)


def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha"""
    return pwd_context.hash(password)


def update_super_admin_password(password: str):
    """Atualiza senha do super admin no banco"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    try:
        # Gera hash da senha
        password_hash = hash_password(password)

        # Atualiza super admin
        cur.execute("""
            UPDATE users
            SET password_hash = %s,
                updated_at = now()
            WHERE is_superadmin = true
            RETURNING id, email
        """, (password_hash,))

        result = cur.fetchone()

        if not result:
            print("ERRO: Super admin não encontrado no banco!")
            return False

        conn.commit()

        user_id, email = result
        print("=" * 60)
        print("SENHA DO SUPER ADMIN ATUALIZADA COM SUCESSO!")
        print("=" * 60)
        print(f"User ID: {user_id}")
        print(f"Email: {email}")
        print(f"Senha: {password}")
        print()
        print("IMPORTANTE: Guarde essa senha em local seguro!")
        print("=" * 60)

        return True

    except Exception as e:
        conn.rollback()
        print(f"ERRO ao atualizar senha: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def check_jwt_secret():
    """Verifica se JWT_SECRET está configurado"""
    jwt_secret = os.getenv('JWT_SECRET')

    if not jwt_secret or jwt_secret == '<CHANGE_ME>':
        print()
        print("=" * 60)
        print("AVISO: JWT_SECRET não configurado!")
        print("=" * 60)
        print()
        new_secret = generate_jwt_secret()
        print(f"Adicione ao seu .env:")
        print(f"JWT_SECRET={new_secret}")
        print()
        print("=" * 60)
        return False

    return True


def main():
    print("=" * 60)
    print("CONFIGURAÇÃO DO SUPER ADMIN - HB TRACKING")
    print("=" * 60)
    print()

    # Verifica JWT_SECRET
    check_jwt_secret()

    # Solicita senha
    print("Digite a senha para o Super Admin:")
    print("(Mínimo 8 caracteres, recomendado usar letras, números e símbolos)")
    print()
    password = input("Senha: ").strip()

    if len(password) < 8:
        print("ERRO: Senha deve ter no mínimo 8 caracteres!")
        return

    print()
    confirm = input("Confirme a senha: ").strip()

    if password != confirm:
        print("ERRO: Senhas não coincidem!")
        return

    print()
    # Atualiza senha no banco
    update_super_admin_password(password)


if __name__ == '__main__':
    main()
