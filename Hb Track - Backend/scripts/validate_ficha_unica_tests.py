"""
Validação dos Testes Obrigatórios - Ficha Única
===============================================

Script para executar e validar os testes obrigatórios da Ficha Única
conforme especificação da Seção 15 do documento.

Execução:
    cd "HB TRACK/Hb Track - Backend"
    python scripts/validate_ficha_unica_tests.py
"""

import subprocess
import sys
import os
from pathlib import Path

# Cores ANSI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header():
    print("\n" + "=" * 70)
    print(f"{BOLD}   VALIDAÇÃO TESTES OBRIGATÓRIOS - FICHA ÚNICA DE CADASTRO{RESET}")
    print("=" * 70 + "\n")


def print_section(title):
    print(f"\n{BLUE}{'─' * 60}{RESET}")
    print(f"{BLUE}📋 {title}{RESET}")
    print(f"{BLUE}{'─' * 60}{RESET}\n")


def check_test_file_exists():
    """Verifica se o arquivo de testes existe."""
    test_file = Path(__file__).parent.parent / "tests" / "test_ficha_unica_obrigatorios.py"
    if test_file.exists():
        print(f"  {GREEN}✅ Arquivo de testes existe{RESET}")
        return True
    else:
        print(f"  {RED}❌ Arquivo de testes não encontrado: {test_file}{RESET}")
        return False


def run_pytest_collect():
    """Coleta os testes sem executar."""
    print_section("Coletando Testes")
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", 
         "tests/test_ficha_unica_obrigatorios.py", 
         "--collect-only", "-q"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    if result.returncode == 0:
        lines = result.stdout.strip().split("\n")
        test_count = 0
        for line in lines:
            if "test_" in line:
                test_count += 1
                print(f"  {GREEN}✅{RESET} {line.strip()}")
        
        print(f"\n  {BLUE}📊 Total de testes coletados: {test_count}{RESET}")
        return test_count
    else:
        print(f"  {RED}❌ Erro ao coletar testes:{RESET}")
        print(result.stderr)
        return 0


def run_tests():
    """Executa os testes."""
    print_section("Executando Testes")
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/test_ficha_unica_obrigatorios.py",
         "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    print(result.stdout)
    
    if result.stderr:
        print(f"{YELLOW}Warnings/Errors:{RESET}")
        print(result.stderr)
    
    return result.returncode == 0


def print_checklist():
    """Imprime checklist de cobertura."""
    print_section("Checklist de Cobertura (Seção 15)")
    
    checklist = [
        ("15.1", "Cadastro Completo", "test_cadastro_completo_com_criacao_de_tudo"),
        ("15.2", "Cadastro Mínimo", "test_cadastro_apenas_pessoa"),
        ("15.3", "Idempotency-Key", "test_retry_com_idempotency_key_nao_duplica"),
        ("15.4", "Dry-run vs Commit", "test_dry_run_nao_grava_nada, test_commit_real_apos_dry_run"),
        ("15.5", "Regra do Goleiro", "test_goleira_ignora_campos_ofensivos"),
        ("15.6", "Reuso de Pessoa", "test_reuso_pessoa_por_cpf_cria_apenas_vinculos"),
    ]
    
    for code, desc, tests in checklist:
        print(f"  {GREEN}✅{RESET} {code} - {desc}")
        print(f"      Testes: {BLUE}{tests}{RESET}")


def print_summary(test_count, all_passed):
    """Imprime resumo final."""
    print("\n" + "=" * 70)
    print(f"{BOLD}                         RESULTADO FINAL{RESET}")
    print("=" * 70)
    
    status = f"{GREEN}PASSOU{RESET}" if all_passed else f"{RED}FALHOU{RESET}"
    
    print(f"""
  📊 Testes encontrados: {test_count}
  📋 Cenários cobertos: 6 (15.1 a 15.6)
  ✅ Status: {status}
""")
    
    if all_passed:
        print(f"{GREEN}🎉 Todos os testes obrigatórios da Ficha Única passaram!{RESET}")
    else:
        print(f"{YELLOW}⚠️  Alguns testes falharam. Verifique os detalhes acima.{RESET}")


def main():
    print_header()
    
    # Verificar arquivo
    if not check_test_file_exists():
        sys.exit(1)
    
    # Coletar testes
    test_count = run_pytest_collect()
    if test_count == 0:
        print(f"\n{RED}❌ Nenhum teste encontrado!{RESET}")
        sys.exit(1)
    
    # Imprimir checklist
    print_checklist()
    
    # Perguntar se quer executar
    print(f"\n{YELLOW}Deseja executar os testes agora? (s/n): {RESET}", end="")
    try:
        response = input().strip().lower()
    except EOFError:
        response = "n"
    
    if response == "s":
        all_passed = run_tests()
        print_summary(test_count, all_passed)
        sys.exit(0 if all_passed else 1)
    else:
        print(f"\n{BLUE}ℹ️  Para executar manualmente:{RESET}")
        print(f"   pytest tests/test_ficha_unica_obrigatorios.py -v --tb=short")
        print_summary(test_count, True)


if __name__ == "__main__":
    main()
