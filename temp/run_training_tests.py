"""
Script executor para rodar testes de invariantes/contratos TRAINING.
Resolve o ModuleNotFoundError de app.core.database antes de carregar o conftest.

USO: python temp/run_training_tests.py <test_path>
Exemplo: python temp/run_training_tests.py tests/training/invariants/test_inv_train_001_focus_sum_constraint.py
"""
import sys
import types
import os

# Muda para o diretório raiz do backend
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Hb Track - Backend")
os.chdir(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)

# PRÉ-PATCH: Cria stub vazio de app.core.database ANTES de qualquer import da app.
# Quando post_training.py faz `from app.core.database import get_db`, encontra este stub.
database_stub = types.ModuleType("app.core.database")
sys.modules["app.core.database"] = database_stub

# Agora importa get_db real de app.core.deps (não aciona app.main) e injeta no stub.
from app.core.deps import get_db  # noqa: E402
database_stub.get_db = get_db

import pytest  # noqa: E402

test_path = sys.argv[1] if len(sys.argv) > 1 else "tests/training/invariants/"
exit_code = pytest.main([test_path, "-v", "--tb=short"])
sys.exit(exit_code)
