"""
Script para testar conexão com o banco de dados
"""
import sys
import psycopg2

def test_connection(db_url):
    """Testa conexão com o banco"""
    print("=" * 60)
    print("TESTE DE CONEXAO COM O BANCO")
    print("=" * 60)
    print()
    print(f"URL: {db_url[:50]}...")
    print()

    try:
        print("Conectando...")
        conn = psycopg2.connect(db_url)
        print("OK Conexao estabelecida!")

        cur = conn.cursor()

        # Testa query simples
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"PostgreSQL version: {version[:50]}...")

        # Verifica users
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        print(f"Total de usuarios: {user_count}")

        # Verifica super admin
        cur.execute("SELECT COUNT(*) FROM users WHERE is_superadmin = true")
        admin_count = cur.fetchone()[0]
        print(f"Super admins: {admin_count}")

        cur.close()
        conn.close()

        print()
        print("=" * 60)
        print("TESTE CONCLUIDO COM SUCESSO!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"ERRO: {e}")
        print()
        print("=" * 60)
        print("TESTE FALHOU!")
        print("=" * 60)
        print()
        print("Possiveiveis causas:")
        print("1. Senha do banco incorreta")
        print("2. Banco pausado (Neon free tier)")
        print("3. Rede bloqueada")
        print()
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        db_url = sys.argv[1]
    else:
        import os
        from dotenv import load_dotenv
        from pathlib import Path

        env_path = Path(__file__).parent.parent / 'backend' / '.env'
        load_dotenv(dotenv_path=env_path)
        db_url = os.getenv('DATABASE_URL')

        if not db_url:
            print("ERRO: DATABASE_URL nao definido!")
            print("Use: python test_db_connection.py 'postgresql://...'")
            sys.exit(1)

    success = test_connection(db_url)
    sys.exit(0 if success else 1)
