"""
Script de Validação da FASE 0 - Pré-requisitos e Preparação do Ambiente
Referência: FICHA.MD - Seção 0.5 Checklist Fase 0
"""
import os
import sys
import subprocess
from pathlib import Path

# Cores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_mark(status: bool) -> str:
    return f"{GREEN}✅{RESET}" if status else f"{RED}❌{RESET}"

def warn_mark() -> str:
    return f"{YELLOW}⚠️{RESET}"

def print_header(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def check_python_version():
    """Verificar Python 3.11+"""
    version = sys.version_info
    status = version.major == 3 and version.minor >= 11
    print(f"{check_mark(status)} Python {version.major}.{version.minor}.{version.micro} (mínimo: 3.11+)")
    return status


def check_node_version():
    """Verificar Node.js 18+"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        version_str = result.stdout.strip().lstrip('v')
        major = int(version_str.split('.')[0])
        status = major >= 18
        print(f"{check_mark(status)} Node.js {version_str} (mínimo: 18+)")
        return status
    except Exception as e:
        print(f"{check_mark(False)} Node.js não encontrado: {e}")
        return False


def check_backend_dependencies():
    """Verificar dependências do backend"""
    deps = [
        ('resend', 'Resend (email)'),
        ('cloudinary', 'Cloudinary (imagens)'),
        ('multipart', 'python-multipart (upload)')
    ]
    
    all_ok = True
    for module, name in deps:
        try:
            __import__(module)
            print(f"{check_mark(True)} {name}")
        except ImportError:
            print(f"{check_mark(False)} {name} - não instalado")
            all_ok = False
    
    return all_ok


def check_backend_directories():
    """Verificar estrutura de diretórios do backend"""
    base = Path(__file__).parent.parent
    
    dirs = [
        'app/api/v1/routers',
        'app/services/intake',
        'app/schemas/intake',
        'app/models',
        'tests',
    ]
    
    all_ok = True
    for d in dirs:
        path = base / d
        exists = path.exists()
        if not exists:
            all_ok = False
        print(f"{check_mark(exists)} {d}/")
    
    return all_ok


def check_backend_env():
    """Verificar variáveis de ambiente do backend"""
    base = Path(__file__).parent.parent
    env_path = base / '.env'
    
    if not env_path.exists():
        print(f"{check_mark(False)} Arquivo .env não encontrado")
        return False
    
    print(f"{check_mark(True)} Arquivo .env encontrado")
    
    # Verificar variáveis essenciais
    env_content = env_path.read_text()
    
    required_vars = [
        ('DATABASE_URL', 'Banco de dados'),
        ('JWT_SECRET', 'Segurança JWT'),
        ('RESEND_API_KEY', 'Resend Email'),
        ('CLOUDINARY_CLOUD_NAME', 'Cloudinary Cloud'),
        ('CLOUDINARY_API_KEY', 'Cloudinary API Key'),
        ('FRONTEND_URL', 'URL do Frontend'),
    ]
    
    all_ok = True
    for var, name in required_vars:
        if var in env_content and f"{var}=" in env_content:
            # Verificar se não está vazio ou com placeholder
            lines = [l for l in env_content.split('\n') if l.startswith(f'{var}=')]
            if lines:
                value = lines[0].split('=', 1)[1].strip()
                if value and not value.startswith('xxx') and value != '':
                    print(f"  {check_mark(True)} {var} ({name})")
                else:
                    print(f"  {warn_mark()} {var} ({name}) - configurar valor")
        else:
            print(f"  {check_mark(False)} {var} ({name}) - não encontrado")
            all_ok = False
    
    return all_ok


def check_frontend_directories():
    """Verificar estrutura de diretórios do frontend"""
    # Assumindo que estamos no backend, o frontend está em ../Hb Track - Fronted
    base = Path(__file__).parent.parent.parent / 'Hb Track - Fronted'
    
    if not base.exists():
        print(f"{check_mark(False)} Diretório frontend não encontrado: {base}")
        return False
    
    dirs = [
        'src/components/FichaUnicaWizard',
        'src/components/FichaUnicaWizard/steps',
    ]
    
    all_ok = True
    for d in dirs:
        path = base / d
        exists = path.exists()
        if not exists:
            all_ok = False
        print(f"{check_mark(exists)} {d}/")
    
    return all_ok


def check_frontend_env():
    """Verificar variáveis de ambiente do frontend"""
    base = Path(__file__).parent.parent.parent / 'Hb Track - Fronted'
    env_path = base / '.env.local'
    
    if not env_path.exists():
        print(f"{check_mark(False)} Arquivo .env.local não encontrado")
        return False
    
    print(f"{check_mark(True)} Arquivo .env.local encontrado")
    
    env_content = env_path.read_text()
    
    required_vars = [
        ('NEXT_PUBLIC_API_URL', 'URL da API'),
        ('NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME', 'Cloudinary Cloud'),
    ]
    
    all_ok = True
    for var, name in required_vars:
        if var in env_content:
            print(f"  {check_mark(True)} {var} ({name})")
        else:
            print(f"  {warn_mark()} {var} ({name}) - recomendado")
    
    return all_ok


def main():
    print("\n" + "=" * 60)
    print("  VALIDAÇÃO DA FASE 0 - FICHA ÚNICA")
    print("  Pré-requisitos e Preparação do Ambiente")
    print("=" * 60)
    
    results = {}
    
    # 1. Requisitos de Sistema
    print_header("0.1 REQUISITOS DE SISTEMA")
    results['python'] = check_python_version()
    results['node'] = check_node_version()
    
    # 2. Estrutura Backend
    print_header("0.2 ESTRUTURA DE DIRETÓRIOS - BACKEND")
    results['backend_dirs'] = check_backend_directories()
    
    # 3. Estrutura Frontend
    print_header("0.2 ESTRUTURA DE DIRETÓRIOS - FRONTEND")
    results['frontend_dirs'] = check_frontend_directories()
    
    # 4. Variáveis de Ambiente Backend
    print_header("0.3 VARIÁVEIS DE AMBIENTE - BACKEND")
    results['backend_env'] = check_backend_env()
    
    # 5. Variáveis de Ambiente Frontend
    print_header("0.3 VARIÁVEIS DE AMBIENTE - FRONTEND")
    results['frontend_env'] = check_frontend_env()
    
    # 6. Dependências Backend
    print_header("0.4 DEPENDÊNCIAS - BACKEND")
    results['backend_deps'] = check_backend_dependencies()
    
    # Resumo
    print_header("RESUMO - CHECKLIST FASE 0")
    
    checklist = [
        ('Python 3.11+ instalado', results.get('python', False)),
        ('Node.js 18+ instalado', results.get('node', False)),
        ('Estrutura backend criada', results.get('backend_dirs', False)),
        ('Estrutura frontend criada', results.get('frontend_dirs', False)),
        ('Variáveis backend configuradas', results.get('backend_env', False)),
        ('Variáveis frontend configuradas', results.get('frontend_env', False)),
        ('Dependências backend instaladas', results.get('backend_deps', False)),
    ]
    
    all_passed = True
    for item, status in checklist:
        print(f"{check_mark(status)} {item}")
        if not status:
            all_passed = False
    
    print()
    if all_passed:
        print(f"{GREEN}🎉 FASE 0 CONCLUÍDA COM SUCESSO!{RESET}")
        print(f"   Pronto para executar a FASE 1: Banco de Dados e Migrations")
        return 0
    else:
        print(f"{YELLOW}⚠️  Alguns itens precisam de atenção.{RESET}")
        print(f"   Revise os itens marcados com ❌ antes de prosseguir.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
