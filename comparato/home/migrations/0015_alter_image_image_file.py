# Generated by Django 5.0.3 on 2024-08-17 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0014_alter_notifs_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="image_file",
            field=models.CharField(blank=True, max_length=765, null=True),
        ),
    ]
