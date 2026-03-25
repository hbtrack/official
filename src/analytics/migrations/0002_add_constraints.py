"""
Constraints de integridade — módulo analytics.
metric_key não pode ser vazio (INV-ANL-001).
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("analytics", "0001_initial"),
    ]

    operations = [
        # metric_key não pode ser string vazia
        migrations.AddConstraint(
            model_name="analyticssnapshotmodel",
            constraint=models.CheckConstraint(
                check=~models.Q(metric_key=""),
                name="analytics_snapshot_metric_key_nonempty",
            ),
        ),
    ]
