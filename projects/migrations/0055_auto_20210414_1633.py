# Generated by Django 2.2.17 on 2021-04-14 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0054_auto_20210414_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='is_defined',
            field=models.BooleanField(default=False),
        ),
    ]
