"""
Constraints de integridade — módulo notifications.
INV-NOT: delivery_status_label FSM; retry_count >= 0.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="notificationdeliverymodel",
            constraint=models.CheckConstraint(
                check=models.Q(delivery_status_label__in=[
                    "queued", "sent", "failed", "retrying"
                ]),
                name="notifications_delivery_status_label_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="notificationdeliverymodel",
            constraint=models.CheckConstraint(
                check=models.Q(retry_count__gte=0),
                name="notifications_delivery_retry_count_non_negative",
            ),
        ),
    ]
