# Generated by Django 2.2.17 on 2022-04-06 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteer',
            name='relativeRelation',
            field=models.CharField(max_length=255, null=True),
        ),
    ]