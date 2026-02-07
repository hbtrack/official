"""
Script para verificar status atual dos dados E2E no banco hb_track_dev
"""
import psycopg2
from datetime import datetime

def check_e2e_status():
    conn = psycopg2.connect('postgresql://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_dev')
    cur = conn.cursor()
    
    print("=" * 80)
    print(f"VERIFICAÇÃO DE DADOS E2E - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 1. Verificar equipes E2E
    cur.execute("SELECT COUNT(*) FROM teams WHERE name LIKE 'E2E-%' AND deleted_at IS NULL")
    teams_count = cur.fetchone()[0]
    print(f"\n1. EQUIPES E2E: {teams_count}")
    
    if teams_count > 0:
        cur.execute("""
            SELECT id, name, category_id, gender 
            FROM teams 
            WHERE name LIKE 'E2E-%' AND deleted_at IS NULL 
            ORDER BY name
        """)
        print("   Equipes encontradas:")
        for row in cur.fetchall():
            print(f"   - {row[1]} (ID: {row[0]}, Cat: {row[2]}, Gênero: {row[3]})")
    
    # 2. Verificar equipe do coordenador especificamente
    cur.execute("""
        SELECT id, name, category_id, gender 
        FROM teams 
        WHERE id = '88888888-8888-8888-8884-000000000002'
    """)
    coord_team = cur.fetchone()
    print(f"\n2. EQUIPE DO COORDENADOR:")
    if coord_team:
        print(f"   - {coord_team[1]} (ID: {coord_team[0]}, Cat: {coord_team[2]}, Gênero: {coord_team[3]})")
        
        # Contar atletas desta equipe
        cur.execute("""
            SELECT COUNT(*) 
            FROM athletes a
            JOIN team_registrations tr ON a.id = tr.athlete_id
            WHERE tr.team_id = '88888888-8888-8888-8884-000000000002'
            AND a.deleted_at IS NULL
        """)
        athletes_count = cur.fetchone()[0]
        print(f"   - Atletas: {athletes_count}")
    else:
        print("   - NÃO ENCONTRADA")
    
    # 3. Total de atletas
    cur.execute("SELECT COUNT(*) FROM athletes WHERE deleted_at IS NULL")
    total_athletes = cur.fetchone()[0]
    print(f"\n3. TOTAL DE ATLETAS: {total_athletes}")
    
    # 4. Verificar usuários E2E
    cur.execute("""
        SELECT COUNT(*) 
        FROM users u
        JOIN persons p ON u.person_id = p.id
        WHERE p.full_name LIKE 'E2E %'
    """)
    users_count = cur.fetchone()[0]
    print(f"\n4. USUÁRIOS E2E: {users_count}")
    
    # 5. Verificar treinos E2E
    cur.execute("""
        SELECT COUNT(*) 
        FROM training_sessions 
        WHERE main_objective LIKE 'E2E-%' AND deleted_at IS NULL
    """)
    trainings_count = cur.fetchone()[0]
    print(f"\n5. TREINOS E2E: {trainings_count}")
    
    # 6. Verificar jogos E2E
    cur.execute("""
        SELECT COUNT(*) 
        FROM matches 
        WHERE notes LIKE 'E2E-%' AND deleted_at IS NULL
    """)
    matches_count = cur.fetchone()[0]
    print(f"\n6. JOGOS E2E: {matches_count}")
    
    # 7. Verificar triggers que bloqueiam DELETE
    cur.execute("""
        SELECT trigger_name, event_manipulation, event_object_table
        FROM information_schema.triggers
        WHERE trigger_schema = 'public'
        AND trigger_name LIKE '%prevent%delete%'
        ORDER BY event_object_table, trigger_name
    """)
    triggers = cur.fetchall()
    print(f"\n7. TRIGGERS QUE BLOQUEIAM DELETE: {len(triggers)}")
    for trigger in triggers:
        print(f"   - {trigger[0]} on {trigger[2]} ({trigger[1]})")
    
    print("\n" + "=" * 80)
    
    conn.close()

if __name__ == '__main__':
    check_e2e_status()
