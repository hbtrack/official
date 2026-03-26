"""
Constraints de integridade — módulo audit.
INV-AUD-001: action não pode ser vazio.
INV-AUD-002: append-only enforced a nível de modelo (save/delete bloqueados).
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("audit", "0001_initial"),
    ]

    operations = [
        # action não pode ser string vazia
        migrations.AddConstraint(
            model_name="auditentrymodel",
            constraint=models.CheckConstraint(
                check=~models.Q(action=""),
                name="audit_entry_action_nonempty",
            ),
        ),
    ]
