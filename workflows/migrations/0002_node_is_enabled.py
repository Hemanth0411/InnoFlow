# Generated by Django 5.1.6 on 2025-04-17 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='is_enabled',
            field=models.BooleanField(default=True),
        ),
    ]
