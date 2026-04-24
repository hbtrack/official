# Generated manually on 2026-04-24
# Adiciona UniqueConstraint parcial (WHERE deleted_at IS NULL) em WellnessPreModel
# para enforçar INV-TRAIN-009 ao nível de banco de dados.
# A constraint parcial permite soft-deletion: registros arquivados (deleted_at IS NOT NULL)
# não competem com novos registros ativos para o mesmo par (session_id, athlete_id).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("training", "0009_add_sleep_hours_to_wellness_pre"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="wellnesspremodel",
            constraint=models.UniqueConstraint(
                condition=models.Q(deleted_at__isnull=True),
                fields=["session_id", "athlete_id"],
                name="training_wellness_pre_unique_active_per_session_athlete",
            ),
        ),
    ]
