"""
Script para listar todos os usuários e suas credenciais
"""
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('.env'))
url = os.getenv('DATABASE_URL_SYNC').replace('postgresql+psycopg2://', 'postgresql://').replace('postgresql+asyncpg://', 'postgresql://')

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    
    print("\n" + "="*80)
    print("TODOS OS USUÁRIOS NO SISTEMA")
    print("="*80 + "\n")
    
    cur.execute("""
        SELECT u.id, u.email, u.is_superadmin, u.is_active, u.status, p.full_name
        FROM users u
        JOIN persons p ON u.person_id = p.id
        ORDER BY u.is_superadmin DESC, u.created_at
    """)
    
    users = cur.fetchall()
    
    if not users:
        print("❌ NENHUM USUÁRIO ENCONTRADO NO BANCO!\n")
    else:
        print(f"Total: {len(users)} usuários encontrados\n")
        
        for user in users:
            user_id, email, is_superadmin, is_active, status, full_name = user
            
            print(f"{'🔑 SUPERADMIN' if is_superadmin else '👤 USER'}: {email}")
            print(f"   Nome: {full_name}")
            print(f"   ID: {user_id}")
            print(f"   Ativo: {'✅ Sim' if is_active else '❌ Não'}")
            print(f"   Status: {status}")
            print()
    
    print("="*80)
    print("CREDENCIAIS PADRÃO:")
    print("   Super Admin: adm@handballtrack.app / Admin@123!")
    print("   Usuários de teste: <usuario>@idec.com / <Role>@123!")
    print("="*80 + "\n")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERRO: {e}\n")
