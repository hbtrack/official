"""Serviço de email via Resend (reset e boas-vindas) com layout aprovado pelo cliente."""

import logging
from typing import Optional

from app.services.resend_client import ResendEmailClient

logger = logging.getLogger(__name__)


class EmailService:
    """Serviço para envio de emails via Resend."""

    def __init__(self):
        from app.core.config import settings

        self.client = ResendEmailClient(
            api_key=settings.RESEND_API_KEY,
            from_email=settings.RESEND_FROM_EMAIL,
            from_name=getattr(settings, "RESEND_FROM_NAME", "HB Track"),
            reply_to=getattr(settings, "RESEND_REPLY_TO", None),
        )
        self.from_email = settings.RESEND_FROM_EMAIL

    def send_password_reset_email(
        self,
        user_email: str,
        reset_link: str,
        user_name: Optional[str] = None,
    ) -> bool:
        """Email de recuperação de senha (link válido por 1h)."""
        try:
            subject = "Recuperação de Senha - HB Track"
            html_content = self._generate_reset_password_html(
                reset_link=reset_link,
                user_name=user_name,
            )
            text_content = f"""
Olá{f" {user_name}" if user_name else ""},

Recebemos uma solicitação para redefinir a senha da sua conta no HB Track.
Para criar uma nova senha com segurança, utilize o link abaixo (válido por 1 hora):

{reset_link}

Se você não solicitou a redefinição, ignore este e-mail. Nenhuma alteração será feita.

HB Track — Dados que vencem Jogos
"""

            success = self.client.send(
                to_emails=user_email,
                subject=subject,
                html=html_content,
                text=text_content,
            )
            if success:
                logger.info("Password reset email sent", extra={"to": user_email})
            return success

        except Exception as exc:
            logger.error(
                "Erro ao enviar email de reset de senha",
                extra={"to": user_email, "error": str(exc)},
            )
            return False

    def send_welcome_email(
        self,
        user_email: str,
        reset_link: str,
        user_name: Optional[str] = None,
    ) -> bool:
        """Email de boas-vindas com instruções para criar senha (link válido por 48h)."""
        try:
            subject = "Seja bem-vindo(a) ao HB Track"

            html_content = self._generate_welcome_html(
                reset_link=reset_link,
                user_name=user_name,
            )

            text_content = f"""
Olá{f" {user_name}" if user_name else ""},

Sua conta no HB Track foi criada com sucesso.
Use o link abaixo (válido por 48 horas) para concluir o primeiro acesso e definir sua senha:

{reset_link}

Se você não reconhece este cadastro, basta ignorar esta mensagem.

HB Track — Dados que vencem Jogos
"""

            success = self.client.send(
                to_emails=user_email,
                subject=subject,
                html=html_content,
                text=text_content,
            )
            if success:
                logger.info("Welcome email sent", extra={"to": user_email})
            return success

        except Exception as exc:
            logger.error(
                "Erro ao enviar email de boas-vindas",
                extra={"to": user_email, "error": str(exc)},
            )
            return False

    def _generate_reset_password_html(
        self,
        reset_link: str,
        user_name: Optional[str] = None,
    ) -> str:
        """Template HTML solicitado para reset de senha (1h)."""
        saudacao = f"Olá, {user_name}" if user_name else "Olá,"
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redefinição de senha - HB Track</title>
    <style>
        body {{
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #F8FAFC;
            color: #0F172A;
            line-height: 1.4;
            font-size: 14px;
            font-weight: 400;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background-color: #FFFFFF;
            padding: 32px;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(15,23,42,0.1);
            border: 1px solid rgba(51,65,85,0.12);
        }}
        .header {{
            text-align: center;
            margin-bottom: 24px;
        }}
        .logo {{
            font-size: 28px;
            font-weight: 600;
            color: #0F172A;
            text-decoration: none;
            display: block;
        }}
        .title {{
            font-size: 22px;
            font-weight: 600;
            margin-top: 24px;
            color: #0F172A;
        }}
        .text {{
            font-size: 14px;
            font-weight: 400;
            margin-bottom: 16px;
            color: #475569;
        }}
        .highlight-link-container {{
            text-align: center;
            margin-top: 32px;
            margin-bottom: 32px;
        }}
        .highlight-link {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #0F172A;
            color: #F8FAFC;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            line-height: 1.2;
            transition: background-color 150ms ease-out;
        }}
        .highlight-link:hover {{
            background-color: #334155;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 12px;
            color: #64748B;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="logo">HB TRACK</span>
        </div>
        <p class="title">Redefinição de senha solicitada</p>
        <p class="text">{saudacao}</p>
        <p class="text">Recebemos uma solicitação para redefinir a senha da sua conta no HB Track.</p>
        <p class="text">Para criar uma nova senha com segurança, clique no link abaixo:</p>
        <div class="highlight-link-container">
            <a href="{reset_link}" class="highlight-link">Redefinir senha</a>
        </div>
        <p class="text">O link expira em 1 hora por segurança.</p>
        <p class="text">Se você não solicitou essa ação, ignore este email. Nenhuma alteração será realizada.</p>
        <div class="footer">
            <p>&copy; 2024 HB Track. Todos os direitos reservados.</p>
        </div>
    </div>
</body>
</html>"""

    def _generate_welcome_html(
        self,
        reset_link: str,
        user_name: Optional[str] = None,
    ) -> str:
        """Template HTML solicitado para boas-vindas (48h)."""
        saudacao = f"Olá, {user_name}" if user_name else "Olá,"
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Seja bem-vindo(a) ao HB Track!</title>
    <style>
        body {{
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #F8FAFC;
            color: #0F172A;
            line-height: 1.4;
            font-size: 14px;
            font-weight: 400;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background-color: #FFFFFF;
            padding: 32px;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(15,23,42,0.1);
            border: 1px solid rgba(51,65,85,0.12);
        }}
        .header {{
            text-align: center;
            margin-bottom: 24px;
        }}
        .logo {{
            font-size: 28px;
            font-weight: 600;
            color: #0F172A;
            text-decoration: none;
            display: block;
        }}
        .title {{
            font-size: 22px;
            font-weight: 600;
            margin-top: 24px;
            color: #0F172A;
        }}
        .text {{
            font-size: 14px;
            font-weight: 400;
            margin-bottom: 16px;
            color: #475569;
        }}
        .highlight-link-container {{
            text-align: center;
            margin-top: 32px;
            margin-bottom: 32px;
        }}
        .highlight-link {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #0F172A;
            color: #F8FAFC;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            line-height: 1.2;
            transition: background-color 150ms ease-out;
        }}
        .highlight-link:hover {{
            background-color: #334155;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 12px;
            color: #64748B;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="logo">HB TRACK</span>
        </div>
        <p class="title">Seja bem-vindo(a) ao HB Track.</p>
        <p class="text">{saudacao}</p>
        <p class="text">Sua conta foi criada com sucesso e já está pronta para uso.</p>
        <p class="text">O HB Track é a plataforma oficial para organização, acompanhamento e análise da rotina esportiva da sua equipe, reunindo informações de treinos, jogos e evolução individual.</p>
        <p class="text">Clique no link abaixo para acessar a plataforma e concluir seu primeiro acesso.</p>
        <div class="highlight-link-container">
            <a href="{reset_link}" class="highlight-link">Acessar plataforma</a>
        </div>
        <p class="text">O link expira em 48 horas por segurança.</p>
        <p class="text">Após o login, você verá apenas as áreas compatíveis com o seu perfil no sistema.</p>
        <p class="text">Em caso de dúvidas, procure a comissão técnica, a coordenação da equipe ou o suporte do sistema.</p>
        <div class="footer">
            <p>&copy; 2024 HB Track. Todos os direitos reservados.</p>
        </div>
    </div>
</body>
</html>"""


# Singleton instance
email_service = EmailService()
