"""
Script para testar envio de emails via SMTP (Amazon SES ou outro provedor).

Uso:
    python scripts/test_email.py email@exemplo.com

Variáveis esperadas no .env:
    SMTP_HOST
    SMTP_PORT (ex.: 587 para STARTTLS)
    SMTP_USER
    SMTP_PASS
    EMAIL_FROM
"""

import os
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def load_settings():
    """Carrega e valida variáveis de ambiente necessárias para SMTP."""
    settings = {
        "host": os.getenv("SMTP_HOST"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER"),
        "password": os.getenv("SMTP_PASS"),
        "sender": os.getenv("EMAIL_FROM"),
    }

    missing = [k for k, v in settings.items() if not v and k != "port"]
    if missing:
        print(f"[ERRO] Variáveis ausentes: {', '.join(missing)}")
        return None
    return settings


def test_email_connection(settings):
    """Abre conexão SMTP e encerra (teste rápido)."""
    print("[INFO] Testando conexão SMTP...")
    try:
        with smtplib.SMTP(settings["host"], settings["port"], timeout=15) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(settings["user"], settings["password"])
        print("[OK] Conexão e autenticação SMTP bem-sucedidas.")
        return True
    except Exception as exc:
        print(f"[ERRO] Falha na conexão/autenticação SMTP: {exc}")
        return False


def send_test_email(settings, to_email: str):
    """Envia email de teste simples."""
    print(f"[INFO] Enviando email de teste para {to_email}...")

    msg = MIMEMultipart("alternative")
    msg["From"] = settings["sender"]
    msg["To"] = to_email
    msg["Subject"] = "Teste de email - HB Track"

    html = """
    <h3>HB Track - Teste de Email</h3>
    <p>Se você recebeu esta mensagem, o envio via SMTP está funcionando.</p>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(settings["host"], settings["port"], timeout=15) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(settings["user"], settings["password"])
            server.send_message(msg)
        print("[OK] Email enviado com sucesso.")
        return True
    except Exception as exc:
        print(f"[ERRO] Falha ao enviar email: {exc}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/test_email.py email@exemplo.com")
        sys.exit(1)

    to_email = sys.argv[1]
    settings = load_settings()
    if not settings:
        sys.exit(1)

    print("=" * 60)
    print("TESTE DE ENVIO DE EMAIL - SMTP (SES/OUTROS)")
    print("=" * 60)

    if not test_email_connection(settings):
        sys.exit(1)

    success = send_test_email(settings, to_email)

    print("\n" + "=" * 60)
    if success:
        print("[OK] TODOS OS TESTES PASSARAM")
    else:
        print("[ERRO] ALGUNS TESTES FALHARAM")
    print("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
