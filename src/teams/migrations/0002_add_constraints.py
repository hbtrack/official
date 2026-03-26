"""
Migration 0002 — teams: CHECK constraints de integridade.
- status_label: FSM com 3 estados válidos (DRAFT, ACTIVE, ARCHIVED)
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teams", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="teammodel",
            constraint=models.CheckConstraint(
                check=models.Q(
                    status_label__in=["DRAFT", "ACTIVE", "ARCHIVED"]
                ),
                name="teams_team_status_label_valid",
            ),
        ),
    ]
