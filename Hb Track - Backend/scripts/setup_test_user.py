"""Script para criar dados de teste completos."""
from sqlalchemy import text
from app.core.db import engine

person_id = "8a99ff63-66e9-4d1b-b288-60332667467f"  # Super Admin Seed
org_id = "85b5a651-6677-4a6a-a08f-60e657a624a2"  # Clube Novo
role_id = 1  # Super Administrador

# UUIDs fixos para evitar dependência circular
membership_id = "11111111-1111-1111-1111-111111111111"
season_id = "22222222-2222-2222-2222-222222222222"

with engine.begin() as conn:
    # Verificar se já existe
    existing = conn.execute(text("SELECT id FROM membership WHERE id = :id"), {"id": membership_id}).fetchone()
    if existing:
        print("Dados de teste já existem!")
    else:
        # Inserir tudo de uma vez com UUIDs fixos usando INSERT com todos os campos obrigatórios
        # Season primeiro - com membership_id que ainda não existe (FK deferrable)
        conn.execute(text("""
            INSERT INTO seasons (id, organization_id, created_by_membership_id, year, name, starts_at, ends_at, is_active)
            VALUES (:season_id, :org_id, :membership_id, 2025, 'Temporada 2025', '2025-01-01', '2025-12-31', true)
            ON CONFLICT DO NOTHING
        """), {"season_id": season_id, "org_id": org_id, "membership_id": membership_id})
        print("Season criada!")
        
        # Membership com season_id
        conn.execute(text("""
            INSERT INTO membership (id, person_id, organization_id, season_id, role_id, status, start_date)
            VALUES (:membership_id, :person_id, :org_id, :season_id, :role_id, 'ativo', CURRENT_DATE)
            ON CONFLICT DO NOTHING
        """), {"membership_id": membership_id, "person_id": person_id, "org_id": org_id, "season_id": season_id, "role_id": role_id})
        print("Membership criado!")

# Verificar resultado
with engine.connect() as conn:
    print("\n=== Resultado ===")
    result = conn.execute(text("SELECT id, person_id, season_id, status FROM membership")).fetchall()
    print("Memberships:", result)
    result = conn.execute(text("SELECT id, year, name FROM seasons")).fetchall()
    print("Seasons:", result)
