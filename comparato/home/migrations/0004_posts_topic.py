# Generated by Django 5.0.3 on 2024-07-14 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0003_posts"),
    ]

    operations = [
        migrations.AddField(
            model_name="posts",
            name="topic",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Self-Portraits", "Self-Portraits"),
                    ("Art", "Art"),
                    ("Fashion & Style", "Fashion & Style"),
                    ("Products", "Products"),
                    ("Creative Projects", "Creative Projects"),
                    ("Events", "Events"),
                    ("Photography Techniques", "Photography Techniques"),
                    ("Themes & Challenges", "Themes & Challenges"),
                    ("Inspiration & Ideas", "Inspiration & Ideas"),
                    ("Comparisons", "Comparisons"),
                ],
                null=True,
            ),
        ),
    ]
