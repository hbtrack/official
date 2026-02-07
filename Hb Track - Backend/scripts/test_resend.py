"""
Script de Teste - Resend
========================
Valida configuração e (opcionalmente) envia um email de teste via Resend.

Uso:
    cd "Hb Track - Backend"
    python scripts/test_resend.py

Para enviar um email real defina RUN_RESEND_SEND_TEST=1 no ambiente.
"""

import os
import sys

# Adicionar path do backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.services.email_service import email_service, send_activation_email

# Flag para envio real (evita mandar email sem querer)
ENABLE_LIVE_SEND = os.getenv("RUN_RESEND_SEND_TEST") == "1"


def test_resend_config() -> bool:
    """Verifica se as configurações do Resend estão presentes."""
    print("\n" + "=" * 60)
    print("1. VERIFICANDO CONFIGURAÇÕES RESEND")
    print("=" * 60)

    configs = {
        "RESEND_API_KEY": settings.RESEND_API_KEY,
        "RESEND_FROM_EMAIL": settings.RESEND_FROM_EMAIL,
        "RESEND_FROM_NAME": getattr(settings, "RESEND_FROM_NAME", None),
    }

    all_ok = True
    for key, value in configs.items():
        if value:
            masked = str(value)
            masked_value = masked[:6] + "..." if len(masked) > 9 else masked
            print(f"  [OK] {key}: {masked_value}")
        else:
            print(f"  [WARN] {key}: NÃO CONFIGURADO")
            if key in ["RESEND_API_KEY", "RESEND_FROM_EMAIL"]:
                all_ok = False

    return all_ok


def test_send_email() -> bool:
    """Envia um email real de boas-vindas usando email_service (opcional)."""
    print("\n" + "=" * 60)
    print("2. TESTANDO ENVIO (OPCIONAL)")
    print("=" * 60)

    if not ENABLE_LIVE_SEND:
        print("  [WARN] RUN_RESEND_SEND_TEST não está definido. Pulando envio real.")
        return True

    if not settings.RESEND_API_KEY:
        print("  ⚠ RESEND_API_KEY não configurada")
        return False

    try:
        test_email = settings.RESEND_FROM_EMAIL
        test_link = f"{settings.FRONTEND_URL}/new-password?token=test-token-123"
        test_name = "Usuário de Teste"

        print(f"  -> Enviando para: {test_email}")
        success = email_service.send_welcome_email(
            user_email=test_email,
            reset_link=test_link,
            user_name=test_name,
        )

        if success:
            print("  [OK] Email enviado com sucesso! Verifique a caixa de entrada/spam.")
        else:
            print("  [WARN] Falha ao enviar email de teste.")
        return success

    except Exception as exc:
        print(f"  [WARN] Erro ao enviar: {exc}")
        return False


def test_activation_email() -> bool:
    """Testa a função send_activation_email da Ficha Única."""
    print("\n" + "=" * 60)
    print("3. TESTANDO send_activation_email (FICHA ÚNICA)")
    print("=" * 60)

    try:
        test_email = settings.RESEND_FROM_EMAIL
        test_name = "Atleta Teste"
        test_token = "activation-token-abc123"

        print(f"  -> Email: {test_email}")
        print(f"  -> Nome: {test_name}")
        print(f"  -> Token: {test_token[:20]}...")

        success = send_activation_email(
            user_email=test_email,
            person_name=test_name,
            activation_token=test_token,
            organization_name="HB Track Clube",
        )

        if success:
            print("  [OK] Email de ativação enviado com sucesso!")
            return True
        else:
            print("  [WARN] Falha ao enviar email de ativação")
            return False

    except ImportError as exc:
        print(f"  [WARN] Função send_activation_email não encontrada: {exc}")
        return False
    except Exception as exc:
        print(f"  [WARN] Erro: {exc}")
        return False


def main() -> int:
    """Executa testes de configuração/envio."""
    print("\n" + "=" * 70)
    print("           TESTE DE INTEGRAÇÃO RESEND")
    print("=" * 70)

    results = []

    # 1. Verificar configurações
    results.append(("Configurações", test_resend_config()))

    # 2. Enviar email de teste (opcional)
    results.append(("Envio de Email", test_send_email()))

    # 3. Testar função de ativação (usa serviço principal)
    results.append(("send_activation_email", test_activation_email()))

    # Resumo
    print("\n" + "=" * 70)
    print("                         RESUMO")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    for name, result in results:
        status = "[OK] PASS" if result else "[WARN] FAIL"
        print(f"  {status} - {name}")

    print("\n" + "-" * 70)
    print(f"  Total: {passed} passou, {failed} falhou")
    print("-" * 70)

    if failed == 0:
        print("\n[OK] RESEND CONFIGURADO CORRETAMENTE!")
        if not ENABLE_LIVE_SEND:
            print("[INFO] Para testar envio real, execute com RUN_RESEND_SEND_TEST=1.")
        return 0
    else:
        print("\n[WARN] Alguns testes falharam. Verifique as configurações no arquivo .env")
        return 1


if __name__ == "__main__":
    exit(main())
