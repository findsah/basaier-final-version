# Generated by Django 2.2.17 on 2022-04-10 09:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20220410_1403'),
    ]

    operations = [
        migrations.RenameField(
            model_name='postpdf',
            old_name='file',
            new_name='files',
        ),
    ]
