# Generated by Django 2.2.17 on 2021-01-11 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0025_auto_20210107_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
    ]
