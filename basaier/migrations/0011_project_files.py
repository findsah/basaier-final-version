# Generated by Django 4.0.3 on 2022-03-14 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basaier', '0010_project_isgift'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='files',
            field=models.FileField(default=0, upload_to=''),
        ),
    ]
