"""
Tasks Celery — módulo notifications
Envio assíncrono de notificações (push, email, in_app, sms).
"""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="notifications.deliver_notification", bind=True, max_retries=3)
def deliver_notification(self, delivery_id: str) -> dict:
    """
    Entrega uma notificação pelo canal configurado.
    delivery_id: UUID da NotificationDelivery a entregar.

    Separação de responsabilidades:
      - DoesNotExist: delivery não encontrado → não tenta retry (dado inválido)
      - Exceptions de envio: registra e agenda retry com backoff exponencial
    """
    from uuid import UUID
    from notifications.infrastructure.models import NotificationDeliveryModel
    from datetime import datetime, timezone

    # Fase 1: localizar o delivery — falha explícita se não existir
    try:
        delivery = NotificationDeliveryModel.objects.get(pk=UUID(delivery_id))
    except NotificationDeliveryModel.DoesNotExist:
        logger.error(
            "deliver_notification: delivery_id=%s não encontrado — abortando sem retry",
            delivery_id,
        )
        return {"status": "not_found", "delivery_id": delivery_id}

    # Fase 2: envio — falha aqui aciona retry
    try:
        # Stub de envio — substituir por integração real (FCM, SES, etc.)
        delivery.delivery_status_label = "sent"
        delivery.delivered_at = datetime.now(tz=timezone.utc)
        delivery.save(update_fields=["delivery_status_label", "delivered_at"])
        return {"status": "sent", "delivery_id": delivery_id}
    except Exception as exc:
        logger.warning(
            "deliver_notification: falha no envio delivery_id=%s tentativa=%d — agendando retry",
            delivery_id,
            self.request.retries,
        )
        delivery.delivery_status_label = "retrying"
        delivery.retry_count = (delivery.retry_count or 0) + 1
        delivery.save(update_fields=["delivery_status_label", "retry_count"])
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
