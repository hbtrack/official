from sqlalchemy import create_engine, text
from app.core.config import settings

# Usar DATABASE_URL do settings
engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    # Verificar se tabela existe
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'team_memberships' 
        ORDER BY ordinal_position
    """))
    
    columns = result.fetchall()
    
    if columns:
        print("✅ Tabela team_memberships EXISTE no banco!")
        print("\nColunas:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
    else:
        print("❌ Tabela team_memberships NÃO EXISTE no banco")
