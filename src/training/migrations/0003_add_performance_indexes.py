"""
Migration 0003 — training: índices de performance.
Task 4.2 — p95 < 200ms em listagens.

TrainingSessionModel:
  - deleted_at: soft-delete filter em todas as queries de listagem
  - (organization_id, deleted_at): filtro composto prioritário

WellnessPreModel / WellnessPostModel:
  - (session_id, athlete_id): lookup por sessão + atleta (INV-TRAIN-009/010)

ExecutionRecordModel:
  - (session_id, execution_type): filtro de registros por sessão e tipo

MesocycleModel:
  - season_id: filtro de mesociclos por temporada
  - (organization_id, season_id): filtro composto de listagens

MicrocycleModel:
  - team_id: filtro de microciclos por time
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("training", "0002_add_constraints"),
    ]

    operations = [
        # ── TrainingSessionModel ──────────────────────────────────────────────
        migrations.AddIndex(
            model_name="trainingsessionmodel",
            index=models.Index(
                fields=["deleted_at"],
                name="training_session_deleted_at_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="trainingsessionmodel",
            index=models.Index(
                fields=["organization_id", "deleted_at"],
                name="training_session_org_deleted_idx",
            ),
        ),
        # ── WellnessPreModel ──────────────────────────────────────────────────
        migrations.AddIndex(
            model_name="wellnesspremodel",
            index=models.Index(
                fields=["session_id", "athlete_id"],
                name="training_wellness_pre_sess_ath_idx",
            ),
        ),
        # ── WellnessPostModel ─────────────────────────────────────────────────
        migrations.AddIndex(
            model_name="wellnesspostmodel",
            index=models.Index(
                fields=["session_id", "athlete_id"],
                name="training_wellness_post_sess_ath_idx",
            ),
        ),
        # ── ExecutionRecordModel ──────────────────────────────────────────────
        migrations.AddIndex(
            model_name="executionrecordmodel",
            index=models.Index(
                fields=["session_id", "execution_type"],
                name="training_exec_record_sess_type_idx",
            ),
        ),
        # ── MesocycleModel ────────────────────────────────────────────────────
        migrations.AddIndex(
            model_name="mesocyclemodel",
            index=models.Index(
                fields=["season_id"],
                name="training_mesocycle_season_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="mesocyclemodel",
            index=models.Index(
                fields=["organization_id", "season_id"],
                name="training_mesocycle_org_season_idx",
            ),
        ),
        # ── MicrocycleModel ───────────────────────────────────────────────────
        migrations.AddIndex(
            model_name="microcyclemodel",
            index=models.Index(
                fields=["team_id"],
                name="training_microcycle_team_idx",
            ),
        ),
    ]
