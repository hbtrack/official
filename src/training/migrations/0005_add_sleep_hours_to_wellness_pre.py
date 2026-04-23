# Generated for HB Track training wellness_pre alignment

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("training", "0004_remove_trainingsessionmodel_training_session_status_valid_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="wellnesspremodel",
            name="sleep_hours",
            field=models.FloatField(null=True, blank=True),
        ),
    ]
