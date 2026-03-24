"""Tasks Celery — módulo audit. Retenção e exportação de logs de auditoria."""
from celery import shared_task


@shared_task(name="audit.purge_expired_entries")
def purge_expired_entries() -> dict:
    """Remove entradas de auditoria além da janela de retenção (política: 7 anos)."""
    from datetime import datetime, timedelta, timezone
    from audit.infrastructure.models import AuditLogModel

    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=365 * 7)
    deleted, _ = AuditLogModel.objects.filter(created_at__lt=cutoff).delete()
    return {"status": "purged", "deleted": deleted}


@shared_task(name="audit.export_audit_log")
def export_audit_log(from_date: str, to_date: str, requester_id: str) -> dict:
    """Exporta logs de auditoria de um período para storage externo."""
    # Stub — integrar com S3/GCS para exportação real
    return {"status": "exported", "from": from_date, "to": to_date}
