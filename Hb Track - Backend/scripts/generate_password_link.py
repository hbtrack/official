"""
Script utilitário para gerar link de redefinição/ativação e (opcionalmente) disparar email via Resend.

Uso:
  python scripts/generate_password_link.py --email davi.sermenho@gmail.com --type reset --send 0
  python scripts/generate_password_link.py --email davi.sermenho@gmail.com --type welcome --send 1

Parâmetros:
  --email   (obrigatório) email do usuário já cadastrado
  --type    reset (1h) ou welcome (48h). Default: reset
  --send    1 para enviar email via Resend; 0 apenas imprime o link. Default: 0
"""

import argparse
import sys

# Garantir path do backend
sys.path.insert(0, ".")

from app.core.db import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.services.password_reset_service import PasswordResetService
from app.services.email_service import email_service


def main() -> int:
    parser = argparse.ArgumentParser(description="Gerar link de redefinição/ativação de senha.")
    parser.add_argument("--email", required=True, help="Email do usuário existente")
    parser.add_argument("--type", choices=["reset", "welcome"], default="reset", help="Tipo de link")
    parser.add_argument("--send", type=int, choices=[0, 1], default=0, help="Enviar email (1) ou só imprimir (0)")
    args = parser.parse_args()

    email_lower = args.email.lower().strip()
    token_type = args.type
    expires_hours = 1 if token_type == "reset" else 48
    path = "/new-password?token=" if token_type == "reset" else "/set-password?token="

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email_lower, User.deleted_at.is_(None)).first()
        if not user:
            print(f"[WARN] Usuário não encontrado: {email_lower}")
            return 1

        reset_service = PasswordResetService(db)
        reset = reset_service.create_reset_token(
            user_id=user.id,
            token_type=token_type,
            expires_in_hours=expires_hours,
        )

        link = f"{settings.FRONTEND_URL}{path}{reset.token}"
        print(f"[OK] Link gerado ({token_type}, expira em {expires_hours}h):\n{link}")

        if args.send == 1:
            if token_type == "reset":
                sent = email_service.send_password_reset_email(
                    user_email=email_lower,
                    reset_link=link,
                    user_name=user.person.full_name if user.person else None,
                )
            else:
                sent = email_service.send_welcome_email(
                    user_email=email_lower,
                    reset_link=link,
                    user_name=user.person.full_name if user.person else None,
                )
            status = "[OK]" if sent else "[WARN]"
            print(f"{status} Email enviado para {email_lower}")

        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
