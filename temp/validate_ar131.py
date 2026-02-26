#!/usr/bin/env python3
"""AR_131 validation script - Testa se get_staged_ars() existe e funciona"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "run"))

try:
    from hb_cli import get_staged_ars
    
    # Testa função get_staged_ars
    repo_root = Path(__file__).parent.parent
    result = get_staged_ars(repo_root)
    
    # Valida retorno
    assert isinstance(result, list), f"get_staged_ars deve retornar list, retornou {type(result)}"
    assert all(isinstance(item, str) for item in result), "Todos itens devem ser strings"
    
    print(f"✓ get_staged_ars() funcional: {len(result)} ARs staged")
    print(f"✓ ARs detectadas: {result}")
    sys.exit(0)
except Exception as e:
    print(f"✗ Erro: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
