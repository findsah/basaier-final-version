# Generated by Django 2.2.17 on 2021-04-15 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0055_auto_20210414_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='sponsorship',
            name='categoryEn',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
