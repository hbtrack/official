"""
Migration 0007 — training: campos de execução em TrainingSession.

Adiciona os 12 campos de execução/resultado que existem na entidade de domínio
TrainingSession mas estavam ausentes do modelo ORM e do banco de dados.

Campos adicionados em training_sessions:
  - started_at           : datetime — quando a sessão foi iniciada
  - ended_at             : datetime — quando a sessão foi encerrada
  - closed_at            : datetime — quando foi fechada administrativamente
  - closed_by_user_id    : UUID — quem fechou
  - deviation_justification : texto — justificativa de desvio do planejado
  - planning_deviation_flag : bool — houve desvio do planejamento?
  - duration_actual_minutes : int — duração real em minutos
  - execution_outcome    : str — resultado da execução (enum textual)
  - delay_minutes        : int — atraso em relação ao planejado
  - cancellation_reason  : str — motivo de cancelamento
  - actual_load_recorded : int — carga real registrada
  - post_review_completed_at : datetime — quando a revisão pós-sessão foi concluída

Índice adicionado:
  - (session_at, id): tie-break determinístico para paginação por cursor.
    Sem este índice, sessões com mesmo session_at são perdidas ou duplicadas
    na paginação (V12).
"""
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("training", "0006_recommendation_and_ineligibility_models"),
    ]

    operations = [
        # ── Campos de execução ────────────────────────────────────────────────
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="started_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="ended_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="closed_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="closed_by_user_id",
            field=models.UUIDField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="deviation_justification",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="planning_deviation_flag",
            field=models.BooleanField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="duration_actual_minutes",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="execution_outcome",
            field=models.CharField(max_length=40, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="delay_minutes",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="cancellation_reason",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="actual_load_recorded",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="trainingsessionmodel",
            name="post_review_completed_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        # ── Índice composto para paginação por cursor (V12) ───────────────────
        migrations.AddIndex(
            model_name="trainingsessionmodel",
            index=models.Index(
                fields=["session_at", "id"],
                name="training_session_at_id_idx",
            ),
        ),
    ]
