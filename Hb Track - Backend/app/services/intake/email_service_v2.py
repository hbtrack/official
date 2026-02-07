"""
Email Service V2 - Resend (convites e emails programáticos)

Objetivos:
- Enviar convites com token de ativação
- Enviar emails de boas-vindas institucionais
- Templates gerados em código (sem dependência de provider templates)
"""

import logging
from typing import Optional

from app.services.resend_client import ResendEmailClient

logger = logging.getLogger(__name__)


class EmailServiceV2:
    """
    Serviço profissional para envio de emails via Resend.

    Requisitos FASE 3:
    - Token single-use com expiry 48h (gerado em camada de domínio)
    - Assunto claro e copy curta
    - Assinatura institucional
    """

    def __init__(self):
        """Inicializa cliente Resend e remetente padrão."""
        from app.core.config import settings

        self.client = ResendEmailClient(
            api_key=settings.RESEND_API_KEY,
            from_email=settings.RESEND_FROM_EMAIL,
            from_name=getattr(settings, "RESEND_FROM_NAME", "HB Track"),
            reply_to=getattr(settings, "RESEND_REPLY_TO", None),
        )
        self.app_name = "HB Track"

    def send_invite_email(
        self,
        to_email: str,
        person_name: str,
        token: str,
        app_url: str,
        organization_name: str = None,
        role_name: str = None,
    ) -> bool:
        """
        Envia email de convite com link para definir senha.
        """
        activation_link = f"{app_url}/welcome?token={token}"

        logger.info(
            "Sending invite email via Resend",
            extra={
                "to": to_email,
                "person": person_name,
                "organization": organization_name,
                "role": role_name,
            },
        )

        subject = "Ative seu acesso ao HB Track"
        html_content = self._build_invite_html(
            person_name=person_name,
            activation_link=activation_link,
            organization_name=organization_name,
            role_name=role_name,
        )
        text_content = self._build_invite_text(
            person_name=person_name,
            activation_link=activation_link,
            organization_name=organization_name,
            role_name=role_name,
        )

        return self._send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    def send_welcome_email(
        self,
        to_email: str,
        person_name: str,
        organization_name: str = None,
    ) -> bool:
        """
        Envia email de boas-vindas simples (sem criação de usuário).
        """
        logger.info(
            "Sending welcome email via Resend",
            extra={
                "to": to_email,
                "person": person_name,
                "organization": organization_name,
            },
        )

        subject = "Bem-vindo ao HB Track"
        html_content = self._build_welcome_html(
            person_name=person_name,
            organization_name=organization_name,
        )
        text_content = self._build_welcome_text(
            person_name=person_name,
            organization_name=organization_name,
        )

        return self._send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Wrapper centralizado para envio e logging."""
        try:
            success = self.client.send(
                to_emails=to_email,
                subject=subject,
                html=html_content,
                text=text_content,
            )
            if success:
                logger.info(
                    "Email enviado via Resend",
                    extra={"to": to_email, "subject": subject},
                )
            return success
        except Exception as exc:
            logger.error(f"Erro ao enviar email via Resend para {to_email}: {exc}")
            return False

    def _build_invite_html(
        self,
        person_name: str,
        activation_link: str,
        organization_name: Optional[str],
        role_name: Optional[str],
    ) -> str:
        organization_line = f"<p class=\"text\"><strong>Organização:</strong> {organization_name}</p>" if organization_name else ""
        role_line = f"<p class=\"text\"><strong>Papel:</strong> {role_name}</p>" if role_name else ""

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Seja bem-vindo(a) ao {self.app_name}!</title>
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
            color: #FFFFFF !important;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            line-height: 1.2;
            transition: background-color 150ms ease-out;
        }}
        .highlight-link:hover {{
            background-color: #334155;
            color: #FFFFFF !important;
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
        <p class="title">Seja bem-vindo(a) ao {self.app_name}.</p>
        <p class="text">Olá {person_name},</p>
        <p class="text">Você foi convidado(a) a acessar o {self.app_name}. Use o link abaixo para criar sua senha e ativar seu acesso.</p>
        {organization_line}
        {role_line}
        <div class="highlight-link-container">
            <a href="{activation_link}" class="highlight-link">Criar senha</a>
        </div>
        <p class="text">O link expira em 48 horas por segurança.</p>
        <p class="text">Se você não reconhece este convite, ignore este email.</p>
        <div class="footer">
            <p>&copy; 2024 HB Track. Todos os direitos reservados.</p>
        </div>
    </div>
</body>
</html>"""

    def _build_invite_text(
        self,
        person_name: str,
        activation_link: str,
        organization_name: Optional[str],
        role_name: Optional[str],
    ) -> str:
        organization_line = f"Organização: {organization_name}\n" if organization_name else ""
        role_line = f"Papel: {role_name}\n" if role_name else ""

        return (
            f"Olá {person_name},\n\n"
            f"Você foi convidado(a) para acessar o {self.app_name}.\n"
            f"{organization_line}{role_line}"
            f"Crie sua senha no link: {activation_link}\n\n"
            "O link expira em 48 horas por segurança.\n"
            "Se não reconhecer este convite, pode ignorar este email.\n"
        )

    def _build_welcome_html(
        self,
        person_name: str,
        organization_name: Optional[str],
    ) -> str:
        organization_line = f"<p><strong>Organização:</strong> {organization_name}</p>" if organization_name else ""

        return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background: #f5f5f5;
      margin: 0;
      padding: 0;
      color: #1f2933;
    }}
    .container {{
      max-width: 640px;
      margin: 24px auto;
      background: #ffffff;
      border-radius: 10px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.08);
      overflow: hidden;
    }}
    .header {{
      background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%);
      color: #fff;
      padding: 26px 32px;
    }}
    .content {{
      padding: 32px;
      line-height: 1.7;
    }}
    .footer {{
      background: #0f172a;
      color: #cbd5e1;
      text-align: center;
      padding: 18px;
      font-size: 13px;
    }}
    .muted {{
      color: #52616b;
    }}
    .highlight {{
      padding: 14px;
      background: #f8fafc;
      border-left: 4px solid #64748b;
      border-radius: 6px;
      margin-top: 12px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Bem-vindo(a) ao {self.app_name}</h1>
    </div>
    <div class="content">
      <p>Olá {person_name},</p>
      <p>Seu cadastro foi recebido e você já faz parte da nossa base.</p>
      {organization_line}
      <div class="highlight">
        <p class="muted">Mantenha seus dados atualizados para receber convites e avisos importantes.</p>
      </div>
      <p class="muted">Se não reconhece este cadastro, ignore este email.</p>
    </div>
    <div class="footer">
      <strong>{self.app_name}</strong> — Dados que vencem Jogos
    </div>
  </div>
</body>
</html>
"""

    def _build_welcome_text(
        self,
        person_name: str,
        organization_name: Optional[str],
    ) -> str:
        organization_line = f"Organização: {organization_name}\n" if organization_name else ""
        return (
            f"Olá {person_name},\n\n"
            f"Bem-vindo(a) ao {self.app_name}.\n"
            f"{organization_line}"
            "Este contato confirma seu cadastro. Se não reconhecer, basta ignorar este email.\n"
        )

    def send_coach_assigned_email(
        self,
        to_email: str,
        coach_name: str,
        team_name: str,
        start_date: str,
        team_url: str,
        organization_name: Optional[str] = None,
    ) -> bool:
        """
        Envia email de notificação quando um coach é designado para uma equipe.
        
        Step 22: Template de email para notificar novo coach atribuído.
        
        Args:
            to_email: Email do coach
            coach_name: Nome completo do coach
            team_name: Nome da equipe
            start_date: Data de início (ISO format)
            team_url: URL para acessar a equipe
            organization_name: Nome da organização (opcional)
        
        Returns:
            bool: True se enviado com sucesso
        """
        logger.info(
            "Sending coach assigned email via Resend",
            extra={
                "to": to_email,
                "coach": coach_name,
                "team": team_name,
                "organization": organization_name,
            },
        )

        subject = f"Você foi designado como treinador da equipe {team_name}"
        html_content = self._build_coach_assigned_html(
            coach_name=coach_name,
            team_name=team_name,
            start_date=start_date,
            team_url=team_url,
            organization_name=organization_name,
        )
        text_content = self._build_coach_assigned_text(
            coach_name=coach_name,
            team_name=team_name,
            start_date=start_date,
            team_url=team_url,
            organization_name=organization_name,
        )

        return self._send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    def _build_coach_assigned_html(
        self,
        coach_name: str,
        team_name: str,
        start_date: str,
        team_url: str,
        organization_name: Optional[str],
    ) -> str:
        """Constrói HTML do email de atribuição de coach."""
        organization_line = f"<p class=\"text\"><strong>Organização:</strong> {organization_name}</p>" if organization_name else ""
        
        # Formatar data de início (assumindo ISO format YYYY-MM-DD)
        try:
            from datetime import datetime
            date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%d/%m/%Y')
        except:
            formatted_date = start_date
        
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Você foi designado como treinador</title>
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
        .highlight-box {{
            background-color: #F1F5F9;
            border-left: 4px solid #0F172A;
            padding: 16px;
            margin: 24px 0;
            border-radius: 4px;
        }}
        .highlight-box p {{
            margin: 8px 0;
            color: #334155;
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
            color: #FFFFFF !important;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            line-height: 1.2;
            transition: background-color 150ms ease-out;
        }}
        .highlight-link:hover {{
            background-color: #334155;
            color: #FFFFFF !important;
        }}
        .responsibilities {{
            margin-top: 24px;
        }}
        .responsibilities-title {{
            font-size: 16px;
            font-weight: 600;
            color: #0F172A;
            margin-bottom: 12px;
        }}
        .responsibilities ul {{
            margin: 0;
            padding-left: 20px;
            color: #475569;
        }}
        .responsibilities li {{
            margin-bottom: 8px;
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
        <p class="title">Você foi designado como treinador!</p>
        <p class="text">Olá {coach_name},</p>
        <p class="text">Você foi designado como treinador(a) responsável pela equipe <strong>{team_name}</strong>.</p>
        
        <div class="highlight-box">
            <p><strong>Equipe:</strong> {team_name}</p>
            {organization_line}
            <p><strong>Data de início:</strong> {formatted_date}</p>
        </div>
        
        <div class="highlight-link-container">
            <a href="{team_url}" class="highlight-link">Acessar Equipe</a>
        </div>
        
        <div class="responsibilities">
            <p class="responsibilities-title">Como treinador, você pode:</p>
            <ul>
                <li>Gerenciar atletas e convocações</li>
                <li>Agendar e acompanhar treinos</li>
                <li>Registrar jogos e estatísticas</li>
                <li>Monitorar wellness e desempenho dos atletas</li>
                <li>Acessar relatórios e análises da equipe</li>
            </ul>
        </div>
        
        <p class="text">Acesse o sistema para começar a gerenciar sua equipe.</p>
        
        <div class="footer">
            <p>&copy; 2024 HB Track. Todos os direitos reservados.</p>
        </div>
    </div>
</body>
</html>
"""

    def _build_coach_assigned_text(
        self,
        coach_name: str,
        team_name: str,
        start_date: str,
        team_url: str,
        organization_name: Optional[str],
    ) -> str:
        """Constrói versão texto plano do email de atribuição de coach."""
        organization_line = f"Organização: {organization_name}\n" if organization_name else ""
        
        try:
            from datetime import datetime
            date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%d/%m/%Y')
        except:
            formatted_date = start_date
        
        return (
            f"Olá {coach_name},\n\n"
            f"Você foi designado como treinador(a) responsável pela equipe {team_name}.\n\n"
            f"Equipe: {team_name}\n"
            f"{organization_line}"
            f"Data de início: {formatted_date}\n\n"
            f"Como treinador, você pode:\n"
            f"- Gerenciar atletas e convocações\n"
            f"- Agendar e acompanhar treinos\n"
            f"- Registrar jogos e estatísticas\n"
            f"- Monitorar wellness e desempenho dos atletas\n"
            f"- Acessar relatórios e análises da equipe\n\n"
            f"Acesse sua equipe: {team_url}\n\n"
            f"HB Track - Dados que vencem Jogos"
        )


# Singleton instance
email_service_v2 = EmailServiceV2()
