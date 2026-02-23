import os
import time
import re
import argparse
from datetime import datetime

# Configurações de Cores ANSI
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

INDEX_PATH = "docs/hbtrack/_INDEX.md"

# Mapeamento de Gatilhos por Agente
TRIGGERS = {
    "architect": ["PROPOSTA", "🔲 PENDENTE", "STUB"],
    "executor": ["🔲 PENDENTE"],
    "testador": ["🏗️ EM_EXECUCAO"]
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def parse_index():
    if not os.path.exists(INDEX_PATH):
        return []
    
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    ars = []
    # Regex para capturar as linhas da tabela: | ID | Título | Status | Evidence |
    pattern = re.compile(r'\|\s*(AR_\d+(?:\.\d+)?)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|')
    
    for line in content:
        match = pattern.search(line)
        if match:
            ars.append({
                "id": match.group(1).strip(),
                "title": match.group(2).strip()[:40],
                "status": match.group(3).strip(),
                "evidence": match.group(4).strip()
            })
    return ars

def render_dashboard(mode, ars):
    clear_screen()
    now = datetime.now().strftime("%H:%M:%S")
    
    print(f"{Colors.BOLD}{Colors.HEADER}=== HB TRACK SENTINELA v1.2.0 - {now} ==={Colors.END}")
    print(f"{Colors.BOLD}MODO ATIVO: {Colors.CYAN}{mode.upper()}{Colors.END}")
    print("-" * 80)
    print(f"{Colors.BOLD}{'ID':<8} | {'STATUS':<15} | {'TÍTULO'}{Colors.END}")
    print("-" * 80)

    action_items = []
    
    for ar in ars:
        color = Colors.END
        if "✅" in ar['status']: color = Colors.GREEN
        elif "🏗️" in ar['status']: color = Colors.YELLOW
        elif "🔴" in ar['status'] or "❌" in ar['status']: color = Colors.RED
        elif "PROPOSTA" in ar['status'] or "PENDENTE" in ar['status']: color = Colors.CYAN
        
        print(f"{ar['id']:<8} | {color}{ar['status']:<15}{Colors.END} | {ar['title']}")
        
        # Verifica se esta AR é um gatilho para o modo atual
        if any(token in ar['status'] for token in TRIGGERS.get(mode, [])):
            # Evita que o Executor pegue algo que o Arquiteto ainda não planejou
            if mode == "executor" and "PENDENTE" in ar['status'] and "—" in ar['evidence']:
                continue
            action_items.append(ar['id'])

    print("-" * 80)
    
    if action_items:
        print(f"{Colors.BOLD}{Colors.YELLOW}👉 AÇÃO REQUERIDA: {mode.upper()} deve processar: {', '.join(action_items)}{Colors.END}")
        # Escreve o arquivo de dispatch para os agentes lerem
        with open(f"_reports/dispatch/{mode}.todo", "w", encoding='utf-8') as f:
            f.write("\n".join(action_items))
    else:
        print(f"{Colors.GREEN}☕ AGUARDANDO: Nenhuma tarefa na fila para {mode}.{Colors.END}")
        if os.path.exists(f"_reports/dispatch/{mode}.todo"):
            os.remove(f"_reports/dispatch/{mode}.todo")

def main():
    parser = argparse.ArgumentParser(description="Sentinela de Fluxo HB Track")
    parser.add_argument("--mode", choices=["architect", "executor", "testador"], required=True)
    parser.add_argument("--loop", type=int, default=5, help="Segundos entre atualizações")
    args = parser.parse_args()

    # Garante que a pasta de dispatch existe
    os.makedirs("_reports/dispatch", exist_ok=True)

    try:
        while True:
            ars = parse_index()
            render_dashboard(args.mode, ars)
            time.sleep(args.loop)
    except KeyboardInterrupt:
        print(f"\n{Colors.BLUE}Sentinela finalizada pelo usuário.{Colors.END}")

if __name__ == "__main__":
    main()
    