from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_remove_userprofilemodel_users_profile_role_label_valid_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofilemodel",
            name="avatar_url",
            field=models.URLField(blank=True, default="", max_length=2048),
        ),
    ]
