#!/usr/bin/env python3
"""
Teste negativo: validar comportamento do snapshot com diretórios inexistentes.
"""
from pathlib import Path
import sys

# Import functions from generate_context_snapshot
try:
    from . import config
    from . import generate_context_snapshot as gcs
except ImportError:
    import config
    import generate_context_snapshot as gcs

def test_nonexistent_tests_dir():
    """Test behavior when tests directory doesn't exist."""
    # Temporarily override BACKEND_TESTS_DIR
    original = config.BACKEND_TESTS_DIR
    config.BACKEND_TESTS_DIR = Path("c:/FAKE_NONEXISTENT_DIR_12345")
    
    # Patch the module-level import
    gcs.BACKEND_TESTS_DIR = config.BACKEND_TESTS_DIR
    
    try:
        result = gcs.get_test_stats()
        
        print("=" * 80)
        print("TESTE NEGATIVO: Diretório de testes INEXISTENTE")
        print("=" * 80)
        print(f"test_files_found: {result.get('test_files_found')}")
        print(f"pytest_collect_only_status: {result.get('pytest_collect_only_status')}")
        print(f"pytest_collect_only_reason: {result.get('pytest_collect_only_reason')}")
        print(f"recent_tests: {result.get('recent_tests')}")
        print()
        
        # Validations
        assert result['test_files_found'] == 0, "Esperado: 0 test files"
        assert "does not exist" in result['recent_tests'], "Esperado: mensagem 'does not exist'"
        assert result['pytest_collect_only_status'] == "SKIPPED", "Esperado: SKIPPED"
        
        print("✅ PASS: Comportamento correto com diretório inexistente")
        print("   - test_files_found = 0")
        print("   - pytest_collect_only_status = SKIPPED")
        print("   - Mensagem clara 'directory does not exist'")
        print("   - Sem stacktrace ou erro")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Exception inesperada: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original
        config.BACKEND_TESTS_DIR = original
        gcs.BACKEND_TESTS_DIR = original

def test_file_structure_missing_dir():
    """Test file structure with missing directory."""
    original = config.BACKEND_MODELS_DIR
    config.BACKEND_MODELS_DIR = Path("c:/FAKE_NONEXISTENT_DIR_12345")
    gcs.BACKEND_MODELS_DIR = config.BACKEND_MODELS_DIR
    
    try:
        result = gcs.get_file_structure()
        
        print("=" * 80)
        print("TESTE NEGATIVO: Diretório de models INEXISTENTE")
        print("=" * 80)
        print(f"app/models: {result.get('app/models', 'N/A')}")
        print()
        
        assert "does not exist" in result.get('app/models', ''), "Esperado: 'does not exist'"
        
        print("✅ PASS: FILE STRUCTURE reporta corretamente diretório faltante")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Exception inesperada: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        config.BACKEND_MODELS_DIR = original
        gcs.BACKEND_MODELS_DIR = original

if __name__ == "__main__":
    passed = 0
    failed = 0
    
    if test_nonexistent_tests_dir():
        passed += 1
    else:
        failed += 1
    
    print()
    
    if test_file_structure_missing_dir():
        passed += 1
    else:
        failed += 1
    
    print()
    print("=" * 80)
    print(f"RESULTADO FINAL: {passed} passed, {failed} failed")
    print("=" * 80)
    
    sys.exit(0 if failed == 0 else 1)
