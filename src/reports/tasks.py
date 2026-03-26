"""Tasks Celery — módulo reports. Geração de relatórios em background."""
from celery import shared_task


@shared_task(name="reports.generate_report", bind=True, max_retries=2)
def generate_report(self, report_id: str) -> dict:
    """Gera um relatório em background e atualiza o status do registro."""
    from uuid import UUID
    from reports.infrastructure.models import ReportModel
    from datetime import datetime, timezone

    try:
        report = ReportModel.objects.get(pk=UUID(report_id))
        report.status_label = "generating"
        report.save(update_fields=["status_label"])
        # Lógica real de geração (PDF, Excel, etc.) vai aqui
        report.status_label = "ready"
        report.generated_at = datetime.now(tz=timezone.utc)
        report.save(update_fields=["status_label", "generated_at"])
        return {"status": "ready", "report_id": report_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
