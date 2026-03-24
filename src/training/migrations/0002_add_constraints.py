"""
Migration 0002 — training: CHECK constraints de integridade.
INV-TRAIN-006: status_label com 7 estados FSM canônicos.
INV-TRAIN: planned_load, intensity_target, group_climate em [1..10] quando presentes.
Wellness: readiness, sleep_quality, mood, fatigue, muscle_soreness,
          perceived_exertion, enjoyment, technical_learning em [1..10].
"""
from django.db import migrations, models


def _nullable_range(field: str, lo: int, hi: int) -> models.Q:
    """Q que aceita NULL ou valor no intervalo [lo, hi]."""
    return models.Q(**{f"{field}__isnull": True}) | models.Q(
        **{f"{field}__gte": lo, f"{field}__lte": hi}
    )


class Migration(migrations.Migration):

    dependencies = [
        ("training", "0001_initial"),
    ]

    operations = [
        # ── TrainingSessionModel ─────────────────────────────────────────────
        migrations.AddConstraint(
            model_name="trainingsessionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(
                    status__in=[
                        "DRAFT", "SCHEDULED", "PUBLISHED",
                        "IN_PROGRESS", "COMPLETED", "CANCELLED", "ARCHIVED",
                    ]
                ),
                name="training_session_status_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="trainingsessionmodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("planned_load", 1, 10),
                name="training_session_planned_load_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="trainingsessionmodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("intensity_target", 1, 10),
                name="training_session_intensity_target_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="trainingsessionmodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("group_climate", 1, 10),
                name="training_session_group_climate_range",
            ),
        ),
        # ── WellnessPreModel ─────────────────────────────────────────────────
        migrations.AddConstraint(
            model_name="wellnesspremodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("readiness", 1, 10),
                name="training_wellness_pre_readiness_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="wellnesspremodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("sleep_quality", 1, 10),
                name="training_wellness_pre_sleep_quality_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="wellnesspremodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("mood", 1, 10),
                name="training_wellness_pre_mood_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="wellnesspremodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("fatigue", 1, 10),
                name="training_wellness_pre_fatigue_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="wellnesspremodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("muscle_soreness", 1, 10),
                name="training_wellness_pre_muscle_soreness_range",
            ),
        ),
        # ── WellnessPostModel ────────────────────────────────────────────────
        migrations.AddConstraint(
            model_name="wellnesspostmodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("perceived_exertion", 1, 10),
                name="training_wellness_post_perceived_exertion_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="wellnesspostmodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("enjoyment", 1, 10),
                name="training_wellness_post_enjoyment_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="wellnesspostmodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("technical_learning", 1, 10),
                name="training_wellness_post_technical_learning_range",
            ),
        ),
    ]
