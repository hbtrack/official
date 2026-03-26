"""
Constraints de integridade — módulo medical.
INV-MED-001: record_label não pode ser vazio.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("medical", "0001_initial"),
    ]

    operations = [
        # record_label não pode ser string vazia
        migrations.AddConstraint(
            model_name="medicalrecordmodel",
            constraint=models.CheckConstraint(
                check=~models.Q(record_label=""),
                name="medical_record_label_nonempty",
            ),
        ),
    ]
