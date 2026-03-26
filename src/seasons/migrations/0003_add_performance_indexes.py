"""
Migration 0003 — seasons: índices de performance.
Task 4.2 — p95 < 200ms em listagens.

SeasonModel:
  - start_date: usado em Meta.ordering = ["-start_date"]
  - (organization_id, status_label): filtro composto mais comum em listSeasons
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seasons", "0002_add_constraints"),
    ]

    operations = [
        # start_date — ordering padrão do modelo
        migrations.AddIndex(
            model_name="seasonmodel",
            index=models.Index(
                fields=["start_date"],
                name="seasons_season_start_date_idx",
            ),
        ),
        # (organization_id, status_label) — filtro composto de listagens
        migrations.AddIndex(
            model_name="seasonmodel",
            index=models.Index(
                fields=["organization_id", "status_label"],
                name="seasons_season_org_status_idx",
            ),
        ),
    ]
