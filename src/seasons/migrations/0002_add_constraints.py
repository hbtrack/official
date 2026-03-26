"""
Migration 0002 — seasons: CHECK constraints de integridade.
- start_date <= end_date (INV-SEAS-002)
- status_label: FSM com 3 estados válidos
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seasons", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="seasonmodel",
            constraint=models.CheckConstraint(
                check=models.Q(end_date__gte=models.F("start_date")),
                name="seasons_season_start_lte_end",
            ),
        ),
        migrations.AddConstraint(
            model_name="seasonmodel",
            constraint=models.CheckConstraint(
                check=models.Q(
                    status_label__in=["DRAFT", "ACTIVE", "ARCHIVED"]
                ),
                name="seasons_season_status_label_valid",
            ),
        ),
    ]
