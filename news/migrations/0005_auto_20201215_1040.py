# Generated by Django 2.0.3 on 2020-12-15 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20201127_0739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sciencenews',
            name='content',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='sciencenews',
            name='contentEn',
            field=models.TextField(blank=True),
        ),
    ]
