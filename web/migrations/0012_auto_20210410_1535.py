# Generated by Django 2.2.17 on 2021-04-10 12:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0011_delete_sponsorship'),
    ]

    operations = [
        migrations.DeleteModel(
            name='masjidPageDetails',
        ),
        migrations.DeleteModel(
            name='topImages',
        ),
        migrations.DeleteModel(
            name='whoWeAre',
        ),
    ]
