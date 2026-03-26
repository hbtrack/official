"""
Constraints de integridade — módulo competitions.
INV-COMP: status_label FSM; start_date ≤ end_date (Classe B — domínio).
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("competitions", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="competitionmodel",
            constraint=models.CheckConstraint(
                check=models.Q(status_label__in=["draft", "active", "archived"]),
                name="competitions_competition_status_label_valid",
            ),
        ),
    ]
