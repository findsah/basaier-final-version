# Generated by Django 2.2.17 on 2021-01-14 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0033_auto_20210113_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='compaigns',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
