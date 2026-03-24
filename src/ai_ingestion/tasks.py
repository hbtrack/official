"""Tasks Celery — módulo ai_ingestion. Processamento de jobs de ingestion."""
from celery import shared_task


@shared_task(name="ai_ingestion.process_ingestion_job", bind=True, max_retries=3)
def process_ingestion_job(self, job_id: str) -> dict:
    """Processa um job de ingestion de dados externos em background."""
    from uuid import UUID
    from ai_ingestion.infrastructure.models import IngestionJobModel
    from datetime import datetime, timezone

    try:
        job = IngestionJobModel.objects.get(pk=UUID(job_id))
        job.status_label = "processing"
        job.save(update_fields=["status_label"])
        # Lógica real de processamento vai aqui (substituir stub)
        job.status_label = "completed"
        job.completed_at = datetime.now(tz=timezone.utc)
        job.save(update_fields=["status_label", "completed_at"])
        return {"status": "completed", "job_id": job_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5 * (2 ** self.request.retries))
