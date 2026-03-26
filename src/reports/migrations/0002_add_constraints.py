"""
Constraints de integridade — módulo reports.
INV-REP: status_label FSM (VALID_STATUSES do domain/entities.py).
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="reportjobmodel",
            constraint=models.CheckConstraint(
                check=models.Q(status_label__in=[
                    "queued", "processing", "completed", "failed", "cancelled"
                ]),
                name="reports_job_status_label_valid",
            ),
        ),
    ]
