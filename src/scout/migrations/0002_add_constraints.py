"""
Constraints de integridade — módulo scout.
INV-SCOUT: duration_ms >= 0 quando não nulo (duração não pode ser negativa).
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scout", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="scouteventmodel",
            constraint=models.CheckConstraint(
                check=models.Q(duration_ms__isnull=True) | models.Q(duration_ms__gte=0),
                name="scout_event_duration_ms_non_negative",
            ),
        ),
    ]
