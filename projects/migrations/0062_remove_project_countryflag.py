# Generated by Django 2.2.17 on 2022-03-29 10:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0061_auto_20220329_1505'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='countryFlag',
        ),
    ]
