# Generated by Django 2.0.3 on 2020-12-17 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_auto_20201217_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sponsorshipprojects',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('TransGender', 'TransGender')], max_length=11),
        ),
    ]
