# Generated by Django 2.2.17 on 2021-01-11 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0027_auto_20210111_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='category',
            field=models.ManyToManyField(to='projects.Category'),
        ),
    ]
