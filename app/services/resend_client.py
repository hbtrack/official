"""
Pequeno wrapper para envio de emails via Resend.

Responsabilidades:
- Centralizar configurações (api_key, remetente, reply-to)
- Expor método send que retorna bool em caso de sucesso/falha
"""

import logging
from typing import Optional, Sequence, Dict, Any

import resend

logger = logging.getLogger(__name__)


class ResendEmailClient:
    """Cliente simples para enviar emails usando Resend."""

    def __init__(
        self,
        api_key: Optional[str],
        from_email: str,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
    ):
        clean_key = api_key.strip().strip("'").strip('"') if api_key else None
        self.api_key = clean_key or None
        self.from_email = from_email
        self.from_name = from_name
        self.reply_to = reply_to

        if not self.api_key:
            logger.warning("RESEND_API_KEY não configurada; envios de email serão ignorados")

    def send(
        self,
        to_emails: Sequence[str] | str,
        subject: str,
        html: Optional[str] = None,
        text: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Envia email via Resend.

        Args:
            to_emails: Destinatário único ou lista
            subject: Assunto do email
            html: Conteúdo HTML (opcional)
            text: Conteúdo texto puro (opcional)
            headers: Headers adicionais (opcional)
        """
        if not self.api_key:
            logger.error("RESEND_API_KEY ausente; envio abortado")
            return False

        resend.api_key = self.api_key

        to_list = [to_emails] if isinstance(to_emails, str) else list(to_emails)

        payload: Dict[str, Any] = {
            "from": f"{self.from_name} <{self.from_email}>" if self.from_name else self.from_email,
            "to": to_list,
            "subject": subject,
        }

        if html:
            payload["html"] = html
        if text:
            payload["text"] = text
        if self.reply_to:
            payload["reply_to"] = self.reply_to
        if headers:
            payload["headers"] = headers

        try:
            response = resend.Emails.send(payload)
            response_id = response.get("id") if isinstance(response, dict) else str(response)

            logger.info(
                "Email enviado via Resend",
                extra={
                    "to": ",".join(to_list),
                    "subject": subject,
                    "response_id": response_id,
                },
            )
            return True
        except Exception as exc:
            logger.error(
                f"Erro ao enviar email via Resend para {to_list}: {exc}"
            )
            return False
