"""
Constraints de integridade — módulo wellness.
INV-WELL: scores PSE/readiness [1-10]; sleep_hours [0-24].
"""
from django.db import migrations, models


def _nullable_range(field: str, lo, hi) -> models.Q:
    return models.Q(**{f"{field}__isnull": True}) | models.Q(
        **{f"{field}__gte": lo, f"{field}__lte": hi}
    )


class Migration(migrations.Migration):

    dependencies = [
        ("wellness", "0001_initial"),
    ]

    operations = [
        # readiness_score NOT NULL 1-10
        migrations.AddConstraint(
            model_name="wellnessentrymodel",
            constraint=models.CheckConstraint(
                check=models.Q(readiness_score__gte=1, readiness_score__lte=10),
                name="wellness_entry_readiness_score_range",
            ),
        ),
        # fatigue_score NULL or 1-10
        migrations.AddConstraint(
            model_name="wellnessentrymodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("fatigue_score", 1, 10),
                name="wellness_entry_fatigue_score_range",
            ),
        ),
        # pain_score NULL or 1-10
        migrations.AddConstraint(
            model_name="wellnessentrymodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("pain_score", 1, 10),
                name="wellness_entry_pain_score_range",
            ),
        ),
        # recovery_score NULL or 1-10
        migrations.AddConstraint(
            model_name="wellnessentrymodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("recovery_score", 1, 10),
                name="wellness_entry_recovery_score_range",
            ),
        ),
        # sleep_hours NULL or 0.0-24.0
        migrations.AddConstraint(
            model_name="wellnessentrymodel",
            constraint=models.CheckConstraint(
                check=_nullable_range("sleep_hours", 0, 24),
                name="wellness_entry_sleep_hours_range",
            ),
        ),
    ]
