# Generated by Django 2.2.17 on 2021-01-11 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0026_auto_20210111_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='category',
            field=models.ManyToManyField(related_name='category', to='projects.Category'),
        ),
    ]
