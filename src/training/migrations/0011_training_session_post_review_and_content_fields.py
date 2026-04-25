"""
Migration 0011 — training: campos de pós-revisão e conteúdo em TrainingSession.

Adiciona campos que existem na entidade de domínio TrainingSession mas estavam
ausentes do modelo ORM:

  - post_review_completed_by_user_id : UUID — quem completou a revisão
  - post_review_deadline_at          : datetime — prazo para revisão
  - post_review_completed            : bool — revisão concluída?
  - planned_content_snapshot         : JSON — snapshot do conteúdo planejado
  - objective_origin                 : str — origem do objetivo
  - continuity_notes                 : texto — notas de continuidade
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("training", "0010_add_unique_constraint_wellness_pre"),
    ]

    operations = [
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="post_review_completed_by_user_id",
            field=models.UUIDField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="post_review_deadline_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="post_review_completed",
            field=models.BooleanField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="planned_content_snapshot",
            field=models.JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="objective_origin",
            field=models.CharField(max_length=60, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="continuity_notes",
            field=models.TextField(null=True, blank=True),
        ),
    ]
