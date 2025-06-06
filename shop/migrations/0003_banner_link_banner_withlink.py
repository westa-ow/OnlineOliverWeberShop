# Generated by Django 5.0 on 2024-11-21 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0002_alter_banner_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="banner",
            name="link",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="banner",
            name="withLink",
            field=models.BooleanField(default=False),
        ),
    ]
