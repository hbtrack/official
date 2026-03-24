"""
Constraints de integridade — módulo ai_ingestion.
INV-AI: status_label FSM (VALID_STATUSES do domain/entities.py).
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai_ingestion", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="ingestionjobmodel",
            constraint=models.CheckConstraint(
                check=models.Q(status_label__in=[
                    "queued", "processing", "completed", "failed"
                ]),
                name="ai_ingestion_job_status_label_valid",
            ),
        ),
    ]
