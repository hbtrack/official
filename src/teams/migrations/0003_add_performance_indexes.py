"""
Migration 0003 — teams: índices de performance.
Task 4.2 — p95 < 200ms em listagens.

TeamModel:
  - (organization_id, status_label): filtro composto mais comum em listTeams
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teams", "0002_add_constraints"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="teammodel",
            index=models.Index(
                fields=["organization_id", "status_label"],
                name="teams_team_org_status_idx",
            ),
        ),
    ]
