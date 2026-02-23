#!/usr/bin/env python3
"""Scan global para tokens proibidos no repositório."""
from pathlib import Path
import sys

# Tokens proibidos
FORBIDDEN_TOKENS = [
    '_reports/audit',
    '🔬 EM TESTE',
]

# Diretórios excluídos do scan
EXCLUDE_DIRS = (
    'docs/_legacy/',
    '.git/',
    'node_modules/',
    '.venv/',
    '_reports/',
    'temp/',
    '__pycache__/',
    '.pytest_cache/',
    'test-results/',
    'playwright-report/',
    'docs/hbtrack/evidence/',
)

# Extensões de arquivos texto para escanear
TEXT_EXTENSIONS = {
    '.md', '.py', '.json', '.yaml', '.yml', '.txt', '.sh', '.ps1',
    '.js', '.ts', '.tsx', '.jsx', '.css', '.html', '.sql'
}

# Tamanho máximo de arquivo (1MB)
MAX_FILE_SIZE = 1024 * 1024

def scan_repo():
    hits = []
    for p in Path('.').rglob('*'):
        s = p.as_posix().replace('\\', '/')
        
        # Pular diretórios excluídos
        if any(s.startswith(e) for e in EXCLUDE_DIRS):
            continue
        
        if p.is_file():
            # Só escanear arquivos texto
            if p.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            
            # Pular arquivos muito grandes
            try:
                if p.stat().st_size > MAX_FILE_SIZE:
                    continue
            except:
                continue
            
            try:
                t = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            
            for token in FORBIDDEN_TOKENS:
                if token in t:
                    hits.append((token, s))
    
    if hits:
        print('❌ FAIL - Forbidden tokens found:')
        for token, path in hits:
            print(f'  {token} -> {path}')
        sys.exit(2)
    
    print('✅ PASS - No forbidden tokens found')
    sys.exit(0)

if __name__ == '__main__':
    scan_repo()
