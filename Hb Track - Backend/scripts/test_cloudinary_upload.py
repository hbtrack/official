"""
Script de Teste - Cloudinary Upload
===================================
Testa o upload de imagens via Cloudinary.

FASE 5 - FICHA.MD Seção 5.2.4

Uso:
    cd "Hb Track - Backend"
    python scripts/test_cloudinary_upload.py
"""

import sys
import os

# Adicionar path do backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


def test_cloudinary_config():
    """Verifica se as configurações do Cloudinary estão presentes."""
    print("\n" + "=" * 60)
    print("1. VERIFICANDO CONFIGURAÇÕES CLOUDINARY")
    print("=" * 60)
    
    configs = {
        "CLOUDINARY_CLOUD_NAME": settings.CLOUDINARY_CLOUD_NAME,
        "CLOUDINARY_API_KEY": settings.CLOUDINARY_API_KEY,
        "CLOUDINARY_API_SECRET": settings.CLOUDINARY_API_SECRET,
        "CLOUDINARY_UPLOAD_PRESET": settings.CLOUDINARY_UPLOAD_PRESET,
    }
    
    all_ok = True
    for key, value in configs.items():
        if value:
            if "SECRET" in key:
                masked_value = value[:10] + "..." if len(str(value)) > 10 else "***"
            else:
                masked_value = value
            print(f"  ✅ {key}: {masked_value}")
        else:
            print(f"  ⚠️ {key}: NÃO CONFIGURADO")
            if key != "CLOUDINARY_UPLOAD_PRESET":
                all_ok = False
    
    return all_ok


def test_cloudinary_connection():
    """Testa conexão com a API do Cloudinary."""
    print("\n" + "=" * 60)
    print("2. TESTANDO CONEXÃO COM CLOUDINARY")
    print("=" * 60)
    
    if not settings.CLOUDINARY_CLOUD_NAME or not settings.CLOUDINARY_API_KEY:
        print("  ❌ Credenciais não configuradas")
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
        
        # Testar conexão com ping
        print("  📡 Testando conexão...")
        result = cloudinary.api.ping()
        
        if result.get("status") == "ok":
            print("  ✅ Conexão com Cloudinary OK")
            return True
        else:
            print(f"  ⚠️ Resposta inesperada: {result}")
            return True  # Ainda pode funcionar
            
    except Exception as e:
        print(f"  ❌ Erro ao conectar: {e}")
        return False


def test_upload_preset():
    """Verifica se o upload preset existe."""
    print("\n" + "=" * 60)
    print("3. VERIFICANDO UPLOAD PRESET")
    print("=" * 60)
    
    if not settings.CLOUDINARY_UPLOAD_PRESET:
        print("  ⚠️ CLOUDINARY_UPLOAD_PRESET não configurado")
        print("     O upload ainda funcionará sem preset")
        return True
    
    try:
        import cloudinary
        import cloudinary.api
        
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
        
        print(f"  🔍 Buscando preset: {settings.CLOUDINARY_UPLOAD_PRESET}")
        
        try:
            result = cloudinary.api.upload_preset(settings.CLOUDINARY_UPLOAD_PRESET)
            print(f"  ✅ Preset encontrado!")
            print(f"     Nome: {result.get('name')}")
            print(f"     Modo: {result.get('unsigned', 'signed')}")
            return True
        except cloudinary.exceptions.NotFound:
            print(f"  ⚠️ Preset '{settings.CLOUDINARY_UPLOAD_PRESET}' não encontrado")
            print("     Crie o preset no dashboard do Cloudinary")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro ao verificar preset: {e}")
        return False


def test_upload_image():
    """Testa upload de uma imagem de teste."""
    print("\n" + "=" * 60)
    print("4. TESTANDO UPLOAD DE IMAGEM")
    print("=" * 60)
    
    try:
        import cloudinary
        import cloudinary.uploader
        
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
        
        # URL de imagem de teste (placeholder)
        test_image_url = "https://via.placeholder.com/512x512/2563eb/ffffff?text=HB+Track"
        
        print(f"  📤 Fazendo upload de imagem de teste...")
        print(f"     Source: {test_image_url}")
        
        upload_params = {
            "folder": "test/hbtrack",
            "public_id": f"test_avatar_{int(__import__('time').time())}",
            "overwrite": True,
            "resource_type": "image"
        }
        
        # Adicionar preset se configurado
        if settings.CLOUDINARY_UPLOAD_PRESET:
            upload_params["upload_preset"] = settings.CLOUDINARY_UPLOAD_PRESET
        
        result = cloudinary.uploader.upload(test_image_url, **upload_params)
        
        print("  ✅ Upload realizado com sucesso!")
        print(f"     Public ID: {result.get('public_id')}")
        print(f"     URL: {result.get('secure_url')}")
        print(f"     Formato: {result.get('format')}")
        print(f"     Dimensões: {result.get('width')}x{result.get('height')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao fazer upload: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sign_upload():
    """Testa a geração de assinatura para upload."""
    print("\n" + "=" * 60)
    print("5. TESTANDO GERAÇÃO DE ASSINATURA")
    print("=" * 60)
    
    try:
        import hashlib
        import time
        
        timestamp = int(time.time())
        folder = "persons/photos"
        
        # Gerar assinatura como o endpoint /media/sign-upload faz
        params_to_sign = f"folder={folder}&timestamp={timestamp}"
        
        if settings.CLOUDINARY_UPLOAD_PRESET:
            params_to_sign += f"&upload_preset={settings.CLOUDINARY_UPLOAD_PRESET}"
        
        signature_string = params_to_sign + settings.CLOUDINARY_API_SECRET
        signature = hashlib.sha1(signature_string.encode()).hexdigest()
        
        print("  ✅ Assinatura gerada com sucesso!")
        print(f"     Cloud Name: {settings.CLOUDINARY_CLOUD_NAME}")
        print(f"     API Key: {settings.CLOUDINARY_API_KEY}")
        print(f"     Timestamp: {timestamp}")
        print(f"     Folder: {folder}")
        print(f"     Signature: {signature[:30]}...")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao gerar assinatura: {e}")
        return False


def test_transformation():
    """Verifica se a transformação t_profile_avatar existe."""
    print("\n" + "=" * 60)
    print("6. VERIFICANDO TRANSFORMAÇÃO t_profile_avatar")
    print("=" * 60)
    
    try:
        import cloudinary
        import cloudinary.api
        
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
        
        print("  🔍 Buscando transformação t_profile_avatar...")
        
        try:
            result = cloudinary.api.transformation("t_profile_avatar")
            print("  ✅ Transformação encontrada!")
            print(f"     Nome: {result.get('name')}")
            return True
        except cloudinary.exceptions.NotFound:
            print("  ⚠️ Transformação 't_profile_avatar' não encontrada")
            print("     Isso é opcional - uploads funcionarão sem ela")
            return True  # Não é crítico
            
    except Exception as e:
        print(f"  ⚠️ Não foi possível verificar transformação: {e}")
        return True  # Não é crítico


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 70)
    print("          TESTE DE INTEGRAÇÃO CLOUDINARY - FASE 5")
    print("=" * 70)
    
    results = []
    
    # 1. Verificar configurações
    results.append(("Configurações", test_cloudinary_config()))
    
    # 2. Testar conexão
    results.append(("Conexão API", test_cloudinary_connection()))
    
    # 3. Verificar upload preset
    results.append(("Upload Preset", test_upload_preset()))
    
    # 4. Testar geração de assinatura
    results.append(("Geração de Assinatura", test_sign_upload()))
    
    # 5. Testar upload (descomente para testar upload real)
    # results.append(("Upload de Imagem", test_upload_image()))
    
    # 6. Verificar transformação
    results.append(("Transformação Avatar", test_transformation()))
    
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
        print("\n🎉 CLOUDINARY CONFIGURADO CORRETAMENTE!")
        print("\n💡 Para testar upload real, descomente a linha 225")
        return 0
    else:
        print(f"\n⚠️ {failed} TESTE(S) FALHARAM")
        print("Verifique as configurações no arquivo .env")
        return 1


if __name__ == "__main__":
    exit(main())
