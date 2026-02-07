"""
Script para verificar usuarios no banco de dados
"""
import psycopg2
from urllib.parse import urlparse

# String de conexao do .env
DATABASE_URL = "postgresql://neondb_owner:npg_PrN5buzBWya1@ep-steep-bread-ad9uwqio-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Parse da URL
result = urlparse(DATABASE_URL)
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port

print("=" * 60)
print("VERIFICANDO USUARIOS NO BANCO DE DADOS")
print("=" * 60)

try:
    # Conectar ao banco
    conn = psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )

    cursor = conn.cursor()

    # Buscar usuarios
    cursor.execute("""
        SELECT u.id, u.email, u.is_superadmin, u.status, p.full_name
        FROM users u
        LEFT JOIN persons p ON u.person_id = p.id
        WHERE u.deleted_at IS NULL
        ORDER BY u.created_at DESC
        LIMIT 5
    """)

    users = cursor.fetchall()

    print(f"\nUsuarios encontrados: {len(users)}\n")

    for user in users:
        user_id, email, is_superadmin, status, full_name = user
        print(f"Email: {email}")
        print(f"  ID: {user_id}")
        print(f"  Nome: {full_name}")
        print(f"  Status: {status}")
        print(f"  Super Admin: {is_superadmin}")
        print()

    cursor.close()
    conn.close()

    print("=" * 60)
    print("\nDica: Use um dos emails acima para fazer login no frontend")

except Exception as e:
    print(f"ERRO ao conectar ao banco: {e}")
