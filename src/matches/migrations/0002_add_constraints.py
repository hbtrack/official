"""
Constraints de integridade — módulo matches.
INV-MATCH: status_label FSM com 10 estados (DEC-MATCHES-002 / HBR-013).
"""
from django.db import migrations, models

_MATCH_STATUSES = [
    "SCHEDULED", "PRE_MATCH", "FIRST_HALF", "HALF_TIME",
    "SECOND_HALF", "OVERTIME_1", "OVERTIME_2", "PENALTIES",
    "COMPLETED", "CANCELLED",
]


class Migration(migrations.Migration):

    dependencies = [
        ("matches", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="matchmodel",
            constraint=models.CheckConstraint(
                check=models.Q(status_label__in=_MATCH_STATUSES),
                name="matches_match_status_label_valid",
            ),
        ),
    ]
