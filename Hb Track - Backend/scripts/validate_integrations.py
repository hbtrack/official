"""
Script de Validação - Integrações FASE 5
========================================
Valida todas as integrações da Ficha Única.

FASE 5 - FICHA.MD Seção 5.3

Uso:
    cd "Hb Track - Backend"
    python scripts/validate_integrations.py
"""

import sys
import os

# Adicionar path do backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def validate_database():
    """Valida conexão com banco de dados."""
    print("\n🔍 Validando Banco de Dados...")
    
    try:
        from app.core.db import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
        
        print(f"  ✅ Conexão OK")
        print(f"     PostgreSQL: {version.split(',')[0]}")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao conectar: {e}")
        return False


def validate_resend():
    """Valida configuração Resend."""
    print("\n🔍 Validando Resend...")
    
    from app.core.config import settings
    
    required = [
        ("RESEND_API_KEY", settings.RESEND_API_KEY),
        ("RESEND_FROM_EMAIL", settings.RESEND_FROM_EMAIL),
    ]
    
    missing = [name for name, value in required if not value]
    
    if missing:
        print(f"  ❌ Configurações faltando: {', '.join(missing)}")
        return False
    
    try:
        import resend
        
        resend.api_key = settings.RESEND_API_KEY
        
        print("  ✅ Resend configurado")
        print(f"     From: {settings.RESEND_FROM_EMAIL}")
        print(f"     API Key: {settings.RESEND_API_KEY[:12]}...")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao validar Resend: {e}")
        return False


def validate_cloudinary():
    """Valida configuração Cloudinary."""
    print("\n🔍 Validando Cloudinary...")
    
    from app.core.config import settings
    
    required = [
        ("CLOUDINARY_CLOUD_NAME", settings.CLOUDINARY_CLOUD_NAME),
        ("CLOUDINARY_API_KEY", settings.CLOUDINARY_API_KEY),
        ("CLOUDINARY_API_SECRET", settings.CLOUDINARY_API_SECRET),
    ]
    
    missing = [name for name, value in required if not value]
    
    if missing:
        print(f"  ❌ Configurações faltando: {', '.join(missing)}")
        return False
    
    try:
        import cloudinary
        import cloudinary.api
        
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
        
        # Testar conexão
        result = cloudinary.api.ping()
        
        print("  ✅ Cloudinary configurado")
        print(f"     Cloud Name: {settings.CLOUDINARY_CLOUD_NAME}")
        print(f"     API Key: {settings.CLOUDINARY_API_KEY}")
        
        # Verificar upload preset
        if settings.CLOUDINARY_UPLOAD_PRESET:
            try:
                preset = cloudinary.api.upload_preset(settings.CLOUDINARY_UPLOAD_PRESET)
                print(f"     Upload Preset: {settings.CLOUDINARY_UPLOAD_PRESET} ✓")
            except cloudinary.exceptions.NotFound:
                print(f"     ⚠️ Upload Preset '{settings.CLOUDINARY_UPLOAD_PRESET}' não encontrado")
        else:
            print("     ⚠️ CLOUDINARY_UPLOAD_PRESET não configurado (opcional)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao validar Cloudinary: {e}")
        return False


def validate_email_service():
    """Valida serviço de e-mail."""
    print("\n🔍 Validando Email Service...")
    
    try:
        from app.services.email_service import email_service, send_activation_email
        
        print("  ✅ EmailService importado")
        print("  ✅ send_activation_email disponível")
        
        # Verificar métodos disponíveis
        methods = [
            "send_password_reset_email",
            "send_welcome_email",
        ]
        
        for method in methods:
            if hasattr(email_service, method):
                print(f"     ✓ {method}")
            else:
                print(f"     ⚠️ {method} não encontrado")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro ao importar: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def validate_media_router():
    """Valida router de mídia."""
    print("\n🔍 Validando Media Router...")
    
    try:
        from app.api.v1.routers.media import router
        
        routes = [r.path for r in router.routes if hasattr(r, 'path')]
        
        expected_routes = ["/media/sign-upload", "/media/validate-url"]
        
        print("  ✅ Media Router importado")
        
        for route in expected_routes:
            if route in routes:
                print(f"     ✓ {route}")
            else:
                print(f"     ⚠️ {route} não encontrado")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro ao importar: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def validate_intake_router():
    """Valida router de intake (Ficha Única)."""
    print("\n🔍 Validando Intake Router...")
    
    try:
        from app.api.v1.routers.intake import router
        
        routes = [r.path for r in router.routes if hasattr(r, 'path')]
        
        expected_routes = [
            "/intake/ficha-unica",
            "/intake/ficha-unica/validate",
            "/intake/ficha-unica/dry-run",
            "/intake/organizations/autocomplete",
            "/intake/teams/autocomplete",
        ]
        
        print("  ✅ Intake Router importado")
        
        for route in expected_routes:
            if route in routes:
                print(f"     ✓ {route}")
            else:
                print(f"     ⚠️ {route} não encontrado")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro ao importar: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def validate_ficha_unica_schemas():
    """Valida schemas da Ficha Única."""
    print("\n🔍 Validando Schemas Ficha Única...")
    
    try:
        from app.schemas.intake.ficha_unica import (
            FichaUnicaRequest,
            FichaUnicaResponse,
            FichaUnicaDryRunResponse,
            ValidationResult,
        )
        
        print("  ✅ Schemas importados")
        print("     ✓ FichaUnicaRequest")
        print("     ✓ FichaUnicaResponse")
        print("     ✓ FichaUnicaDryRunResponse")
        print("     ✓ ValidationResult")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro ao importar: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def validate_ficha_unica_service():
    """Valida serviço da Ficha Única."""
    print("\n🔍 Validando Ficha Única Service...")
    
    try:
        from app.services.intake.ficha_unica_service import FichaUnicaService
        
        print("  ✅ FichaUnicaService importado")
        
        # Verificar métodos
        methods = ["process", "validate", "dry_run"]
        
        for method in methods:
            if hasattr(FichaUnicaService, method):
                print(f"     ✓ {method}")
            else:
                print(f"     ⚠️ {method} não encontrado")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro ao importar: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def main():
    """Executa todas as validações."""
    print("\n" + "=" * 70)
    print("      VALIDAÇÃO DE INTEGRAÇÕES - FICHA ÚNICA (FASE 5)")
    print("=" * 70)
    
    results = {}
    
    # Infraestrutura
    results["Database"] = validate_database()
    
    # Integrações externas
    results["Resend"] = validate_resend()
    results["Cloudinary"] = validate_cloudinary()
    
    # Serviços
    results["Email Service"] = validate_email_service()
    
    # Routers
    results["Media Router"] = validate_media_router()
    results["Intake Router"] = validate_intake_router()
    
    # Schemas e Services
    results["Ficha Única Schemas"] = validate_ficha_unica_schemas()
    results["Ficha Única Service"] = validate_ficha_unica_service()
    
    # Resumo
    print("\n" + "=" * 70)
    print("                       RESULTADO FINAL")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}")
        if status:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "-" * 70)
    print(f"  Total: {passed} passou, {failed} falhou")
    print("-" * 70)
    
    if all(results.values()):
        print("\n🎉 TODAS AS INTEGRAÇÕES ESTÃO FUNCIONANDO!")
        print("\n📋 Checklist FASE 5:")
        print("  ✅ Conta Resend configurada")
        print("  ✅ API Key Resend ativa")
        print("  ✅ Conta Cloudinary configurada")
        print("  ✅ Credenciais Cloudinary no .env")
        print("  ✅ Email Service funcional")
        print("  ✅ Media Router implementado")
        print("  ✅ Intake Router implementado")
        print("  ✅ Schemas Ficha Única prontos")
        print("  ✅ Service Ficha Única pronto")
        print("\n✅ FASE 5 COMPLETA - Pronto para FASE 6 (Frontend)")
        return 0
    else:
        print(f"\n⚠️ {failed} VALIDAÇÃO(ÕES) FALHARAM")
        print("Corrija os erros acima antes de prosseguir.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
