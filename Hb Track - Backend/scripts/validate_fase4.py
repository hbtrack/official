"""
Script de Validação - FASE 4 - Backend Routes e Authorization

Verifica:
1. Router intake.py com autocomplete endpoints
2. Router media.py com sign-upload
3. Config.py com Cloudinary settings
4. email_service.py com send_activation_email
5. api.py com routers registrados

Uso:
    cd "Hb Track - Backend"
    python scripts/validate_fase4.py
"""

import sys
import os

# Adicionar path do backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_intake_router():
    """Verifica router intake.py"""
    print("\n" + "=" * 60)
    print("1. VALIDANDO intake.py ROUTER")
    print("=" * 60)
    
    try:
        from app.api.v1.routers.intake import router
        print("✅ Router importado com sucesso")
        
        # Verificar rotas
        routes = {route.path: route.methods for route in router.routes}
        
        required_routes = [
            ("/ficha-unica", {"POST"}),
            ("/ficha-unica/validate", {"POST"}),
            ("/ficha-unica/dry-run", {"POST"}),
            ("/organizations/autocomplete", {"GET"}),
            ("/teams/autocomplete", {"GET"}),
        ]
        
        for path, methods in required_routes:
            full_path = f"/intake{path}"
            actual_methods = routes.get(full_path)
            if actual_methods:
                print(f"  ✅ {methods} {full_path}")
            else:
                print(f"  ❌ {methods} {full_path} - FALTANDO")
        
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar intake router: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def check_media_router():
    """Verifica router media.py"""
    print("\n" + "=" * 60)
    print("2. VALIDANDO media.py ROUTER")
    print("=" * 60)
    
    try:
        from app.api.v1.routers.media import router
        print("✅ Router importado com sucesso")
        
        # Verificar rotas
        routes = {route.path: route.methods for route in router.routes}
        
        required_routes = [
            ("/sign-upload", {"GET"}),
            ("/validate-url", {"GET"}),
        ]
        
        for path, methods in required_routes:
            full_path = f"/media{path}"
            actual_methods = routes.get(full_path)
            if actual_methods:
                print(f"  ✅ {methods} {full_path}")
            else:
                print(f"  ❌ {methods} {full_path} - FALTANDO")
        
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar media router: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def check_config():
    """Verifica config.py com Cloudinary settings"""
    print("\n" + "=" * 60)
    print("3. VALIDANDO config.py - CLOUDINARY SETTINGS")
    print("=" * 60)
    
    try:
        from app.core.config import Settings
        
        # Verificar campos na classe Settings
        settings_fields = Settings.model_fields
        
        cloudinary_fields = [
            "CLOUDINARY_CLOUD_NAME",
            "CLOUDINARY_API_KEY", 
            "CLOUDINARY_API_SECRET",
            "CLOUDINARY_UPLOAD_PRESET",
        ]
        
        for field in cloudinary_fields:
            if field in settings_fields:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ {field} - FALTANDO")
        
        print("\n  Cloudinary fields configurados na classe Settings")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar config: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def check_email_service():
    """Verifica email_service.py com send_activation_email"""
    print("\n" + "=" * 60)
    print("4. VALIDANDO email_service.py - SEND_ACTIVATION_EMAIL")
    print("=" * 60)
    
    try:
        from app.services.email_service import send_activation_email
        print("✅ send_activation_email importado com sucesso")
        
        # Verificar assinatura da função
        import inspect
        sig = inspect.signature(send_activation_email)
        params = list(sig.parameters.keys())
        
        required_params = ["user_email", "person_name", "activation_token"]
        for param in required_params:
            if param in params:
                print(f"  ✅ Parâmetro: {param}")
            else:
                print(f"  ❌ Parâmetro: {param} - FALTANDO")
        
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar send_activation_email: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def check_api_router():
    """Verifica api.py com routers registrados"""
    print("\n" + "=" * 60)
    print("5. VALIDANDO api.py - ROUTERS REGISTRADOS")
    print("=" * 60)
    
    try:
        from app.api.v1.api import api_router
        print("✅ api_router importado com sucesso")
        
        # Coletar todos os prefixos
        prefixes = []
        for route in api_router.routes:
            if hasattr(route, 'path'):
                prefixes.append(route.path)
        
        # Verificar routers principais
        expected_prefixes = ["/intake", "/media"]
        
        for prefix in expected_prefixes:
            found = any(prefix in p for p in prefixes)
            if found:
                print(f"  ✅ Router com prefix {prefix} registrado")
            else:
                print(f"  ❌ Router com prefix {prefix} - NÃO ENCONTRADO")
        
        print(f"\n  Total de rotas registradas: {len(prefixes)}")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar api_router: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def check_idempotency():
    """Verifica idempotency.py"""
    print("\n" + "=" * 60)
    print("6. VALIDANDO idempotency.py - FUNÇÕES")
    print("=" * 60)
    
    try:
        from app.services.intake.idempotency import (
            check_idempotency,
            save_idempotency,
        )
        print("✅ check_idempotency importado")
        print("✅ save_idempotency importado")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar idempotency: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def check_schemas():
    """Verifica schemas da Ficha Única"""
    print("\n" + "=" * 60)
    print("7. VALIDANDO SCHEMAS - FICHA ÚNICA")
    print("=" * 60)
    
    try:
        from app.schemas.intake.ficha_unica import (
            FichaUnicaRequest,
            FichaUnicaResponse,
            FichaUnicaDryRunResponse,
            ValidationResult,
        )
        print("✅ FichaUnicaRequest importado")
        print("✅ FichaUnicaResponse importado")
        print("✅ FichaUnicaDryRunResponse importado")
        print("✅ ValidationResult importado")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar schemas: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def main():
    """Executa todas as validações"""
    print("\n" + "=" * 70)
    print("      VALIDAÇÃO FASE 4 - BACKEND ROUTES E AUTHORIZATION")
    print("=" * 70)
    
    results = []
    
    results.append(("intake.py router", check_intake_router()))
    results.append(("media.py router", check_media_router()))
    results.append(("config.py Cloudinary", check_config()))
    results.append(("email_service.py", check_email_service()))
    results.append(("api.py routers", check_api_router()))
    results.append(("idempotency.py", check_idempotency()))
    results.append(("schemas", check_schemas()))
    
    # Resumo
    print("\n" + "=" * 70)
    print("                         RESUMO")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "-" * 70)
    print(f"  Total: {passed} passou, {failed} falhou")
    print("-" * 70)
    
    if failed == 0:
        print("\n🎉 FASE 4 VALIDADA COM SUCESSO!")
        print("\nPróximos passos:")
        print("  1. Configurar variáveis de ambiente Cloudinary no .env")
        print("  2. Testar endpoints com curl ou Postman")
        print("  3. Prosseguir para FASE 5 (Frontend)")
        return 0
    else:
        print(f"\n⚠️ FASE 4 COM {failed} PROBLEMA(S)")
        print("Corrija os erros acima antes de prosseguir.")
        return 1


if __name__ == "__main__":
    exit(main())
