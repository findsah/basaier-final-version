# Generated by Django 2.2.17 on 2022-04-10 09:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20220410_1407'),
    ]

    operations = [
        migrations.RenameField(
            model_name='postimage',
            old_name='images',
            new_name='image',
        ),
    ]