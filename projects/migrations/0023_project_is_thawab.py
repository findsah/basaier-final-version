# Generated by Django 2.2 on 2020-12-31 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0022_auto_20201231_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_thawab',
            field=models.BooleanField(default=0),
        ),
    ]
