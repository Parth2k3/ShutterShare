# Generated by Django 5.0.3 on 2024-07-14 18:59

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_app", "0002_user_bio_user_followers_user_following_user_posts"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="followers",
            field=models.ManyToManyField(
                blank=True, related_name="user_followers", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="following",
            field=models.ManyToManyField(
                blank=True, related_name="user_following", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
