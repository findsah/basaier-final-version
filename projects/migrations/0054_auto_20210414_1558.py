# Generated by Django 2.2.17 on 2021-04-14 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0053_auto_20210414_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_compaign',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='active_compaign',
            field=models.BooleanField(default=False),
        ),
    ]
