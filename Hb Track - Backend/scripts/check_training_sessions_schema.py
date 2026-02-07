"""
Script para verificar a estrutura real da tabela training_sessions no banco
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n=== ESTRUTURA REAL DA TABELA training_sessions ===\n")
    
    # Buscar colunas
    cur.execute("""
        SELECT 
            column_name, 
            data_type, 
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = 'training_sessions' 
        ORDER BY ordinal_position
    """)
    
    print(f"{'COLUNA':<35} {'TIPO':<25} {'NULL':<8} {'DEFAULT'}")
    print("-" * 100)
    
    for row in cur.fetchall():
        col_name, data_type, is_nullable, col_default = row
        default_str = str(col_default)[:40] if col_default else '-'
        print(f"{col_name:<35} {data_type:<25} {is_nullable:<8} {default_str}")
    
    # Verificar constraints
    print("\n=== CONSTRAINTS ===\n")
    cur.execute("""
        SELECT 
            conname as constraint_name,
            pg_get_constraintdef(oid) as constraint_def
        FROM pg_constraint
        WHERE conrelid = 'training_sessions'::regclass
        ORDER BY conname
    """)
    
    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"ERRO: {e}")
