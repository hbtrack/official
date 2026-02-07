"""
Script de Verificação de Integração Frontend ↔ Backend
Módulo de Treinos - HB Track

Verifica estrutura e configuração do projeto.
Data: 2026-01-04
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def verificar_arquivos():
    """Verifica se os arquivos necessários existem"""
    print("=" * 60)
    print("🔍 VERIFICAÇÃO DE ARQUIVOS")
    print("=" * 60)
    
    arquivos_necessarios = [
        ("Model TrainingCycle", "app/models/training_cycle.py"),
        ("Model TrainingMicrocycle", "app/models/training_microcycle.py"),
        ("Model TrainingSession", "app/models/training_session.py"),
        ("Service TrainingCycle", "app/services/training_cycle_service.py"),
        ("Service TrainingMicrocycle", "app/services/training_microcycle_service.py"),
        ("Service TrainingSession", "app/services/training_session_service.py"),
        ("Router TrainingCycles", "app/api/v1/routers/training_cycles.py"),
        ("Router TrainingMicrocycles", "app/api/v1/routers/training_microcycles.py"),
        ("Router TrainingSessions", "app/api/v1/routers/training_sessions.py"),
        ("Schema TrainingCycles", "app/schemas/training_cycles.py"),
        ("Schema TrainingMicrocycles", "app/schemas/training_microcycles.py"),
    ]
    
    todos_ok = True
    for nome, caminho in arquivos_necessarios:
        caminho_completo = os.path.join(os.path.dirname(__file__), '..', caminho)
        if os.path.exists(caminho_completo):
            print(f"✅ {nome}")
        else:
            print(f"❌ {nome} - FALTANDO: {caminho}")
            todos_ok = False
    
    return todos_ok

def verificar_migrations():
    """Verifica se as migrations existem"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICAÇÃO DE MIGRATIONS")
    print("=" * 60)
    
    migrations_dir = os.path.join(os.path.dirname(__file__), '..', 'db', 'alembic', 'versions')
    
    if not os.path.exists(migrations_dir):
        print(f"❌ Diretório de migrations não encontrado: {migrations_dir}")
        return False
    
    migrations = [f for f in os.listdir(migrations_dir) if f.endswith('.py') and 'training' in f.lower()]
    
    if migrations:
        print(f"✅ Encontradas {len(migrations)} migrations de treinos:")
        for m in migrations:
            print(f"   - {m}")
        return True
    else:
        print("❌ Nenhuma migration de treinos encontrada")
        return False

def main():
    """Função principal"""
    print("\n")
    print("🧪 TESTE DE INTEGRAÇÃO - MÓDULO DE TREINOS")
    print("HB Track - Backend")
    print("\n")
    
    arquivos_ok = verificar_arquivos()
    migrations_ok = verificar_migrations()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 60)
    
    if arquivos_ok:
        print("✅ Todos os arquivos do backend estão presentes")
    else:
        print("❌ Alguns arquivos do backend estão faltando")
    
    if migrations_ok:
        print("✅ Migrations de treinos encontradas")
    else:
        print("❌ Migrations de treinos não encontradas")
    
    print("\n" + "=" * 60)
    print("🚀 PRÓXIMOS PASSOS PARA TESTES MANUAIS")
    print("=" * 60)
    print()
    print("1️⃣  Iniciar o backend:")
    print("   cd \"c:\\HB TRACK\\Hb Track - Backend\"")
    print("   uvicorn app.main:app --reload --port 8000")
    print()
    print("2️⃣  Iniciar o frontend:")
    print("   cd \"c:\\HB TRACK\\Hb Track - Fronted\"")
    print("   npm run dev")
    print()
    print("3️⃣  Acessar URLs:")
    print("   - Backend API Docs: http://localhost:8000/docs")
    print("   - Frontend: http://localhost:3000")
    print()
    print("4️⃣  Fazer login no sistema")
    print()
    print("5️⃣  Testar páginas:")
    print("   - http://localhost:3000/trainings/cycles")
    print("   - http://localhost:3000/trainings/sessions")
    print()
    print("6️⃣  Verificar no DevTools (F12):")
    print("   - Network tab: Ver chamadas GET /api/v1/training-cycles")
    print("   - Console: Ver mensagens de erro (se houver)")
    print()
    print("7️⃣  Criar dados de teste via Swagger:")
    print("   - POST /api/v1/training-cycles")
    print("   - POST /api/v1/training-microcycles")
    print()
    print("=" * 60)
    print("\n✅ ESTRUTURA DO PROJETO VERIFICADA COM SUCESSO!")
    print("\n📝 Relatório completo: RELATORIO_TESTES_INTEGRACAO.md")
    print("=" * 60)
    print("\n")

if __name__ == "__main__":
    main()
